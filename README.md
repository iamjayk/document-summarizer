# Document summarizing engine
- ### Query engine for a bunch of resume (.pdf)
- ### Summarise huge document(s) (.docx) and output into a given datastructure
> Ideally 2 would be its own thing. Since DD (Dictator Daniel)
> has been putting immense amount of pressure to demo in a day,
> it's done in the same class.
---
## Structure
> Copy the required documents to their appropriate folders,<br/>
- `Resume` files in `.pdf` format to `documents/resume`
- `Report` files in `.docx` format to `documents/reports`
---
- main.py #Runs the dev server
- document_summarizer.py #loads documents, splits, initialises vectordb, and queries for documents.
- documents
  - resume/*.pdf #For prototype 1, query for files based on criteria
  - reports/*.docx #For prototype 2, summarising huge documents
---
## Running it locally
> Ideally, create a virtual environment by running <br/>
> python -m venv .venv
```commandline
python -m venv .venv

pip install -r requirements.txt
python main.py
```
> Runs on http://127.0.0.1:8095


## API
#### Request
```
METHOD: POST
HOST:         http://127.0.0.1:8095
Content-Type: application/json
RAW-BODY:

{
    "query": String,
    "doc_type": "resume" | "document"
}
```


#### Response
>This structure works for 1st one, for summarising resume.
> The Second one, for summarising huge documents, 
> needs more work to output the required data structure for consumption/generating a file in the requird format. 
```
{
    "Match result criteria": String,
    "Query": String,
    "File": String, #Filename 
    "Reference": { 
        "Page Number": Number,
        "Content": String
    }
}
```

#### Example Request
```
{
    "query": "which resume would be a good fit for a marketing job?",
    "doc_type": "resume"
}
```
#### Example Response
```
{
    "File": "documents/resume/....-Resume.pdf",
    "Match result criteria": "Results -driven and motivated marketing professional with one year of experience and a recent Bachelor of Commerce degree",
    "Query": "which resume would be a good fit for a marketing job?",
    "Reference": {
        "Content": ".....",
        "Page Number": 0
    }
}
```

# TODO (AFAIK)
### Common
- Play around with the `pipeline` parameters (temperature, top_p, etc) to tweak the results
[huggingface_pipelines](https://python.langchain.com/docs/integrations/llms/huggingface_pipelines)
### Second prototype - Summarising .docx files
- Internally build a function to query the required fields for the output.
- Return the required datastructure. 
