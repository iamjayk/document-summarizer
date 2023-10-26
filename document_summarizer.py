import langchain.schema
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import pipeline
from langchain.llms import HuggingFacePipeline
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, Docx2txtLoader
from langchain.embeddings import HuggingFaceInstructEmbeddings


class DocumentSummarizer:
    def __init__(self):
        self.local_llm = self.create_local_llm()
        self.documents = None

    def get_tokenizer_and_model(self):
        model_name = "google/flan-t5-large"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        return tokenizer, model

    def create_text_to_text_pipeline(self):
        tokenizer, model = self.get_tokenizer_and_model()
        pipe = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=512,
            repetition_penalty=1.15
        )
        return pipe

    def create_local_llm(self):
        local_llm = HuggingFacePipeline(pipeline=self.create_text_to_text_pipeline())
        return local_llm

    def load_documents(self, doc_type):
        print(f"Loading documents...")
        documents = []
        if doc_type == 'resume':
            pdf_loader = DirectoryLoader(path="./documents/resume", glob="./*.pdf", loader_cls=PyPDFLoader)
            documents = pdf_loader.load()
        elif doc_type == 'report':
            word_loader = DirectoryLoader(path="./documents/reports", glob="./*.docx", loader_cls=Docx2txtLoader)
            documents = word_loader.load()
        return documents

    def get_split_documents(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(documents)
        return texts

    def get_hugging_face_embeddings(self):
        embedding_model_name = 'hkunlp/instructor-base'
        instructor_embeddings = HuggingFaceInstructEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={"device": "cpu"}
        )
        return instructor_embeddings

    def create_vector_db(self, doc_type):
        documents = self.load_documents(doc_type)
        split_documents = self.get_split_documents(documents=documents)
        persist_directory = 'db'
        embedding = self.get_hugging_face_embeddings()

        # Create instance and store embeddings in directory
        vectordb = Chroma.from_documents(documents=split_documents, embedding=embedding, persist_directory=persist_directory)
        vectordb.persist()
        # Release memory
        vectordb = None

        # Re-create new instance by using persisted db
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
        return vectordb


    def configure_retrieval_system(self, doc_type):
        vectordb = self.create_vector_db(doc_type)
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.local_llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        return qa_chain

    def query(self, q, doc_type):
        qa_chain = self.configure_retrieval_system(doc_type)
        response = qa_chain(q)
        result: str = response.get("result")

        source_file: [langchain.schema.document.Document] = response.get("source_documents")
        file_source = source_file[0].metadata.get('source')
        page_no = source_file[0].metadata.get('page')
        page_content = source_file[0].page_content

        return {
            "Match result criteria": result,
            "Query": q,
            "File": file_source,
            "Reference": {
                "Page Number": page_no,
                "Content": page_content
            }
        }