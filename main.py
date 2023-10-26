from flask import Flask, request, jsonify
from document_summarizer import DocumentSummarizer

resume_summarizer = DocumentSummarizer()
app = Flask(__name__)

@app.route('/summarize', methods=["POST"])
def process_query():
    try:
        input_json = request.get_json(force=True)
        query = input_json["query"]
        doc_type = input_json["doc_type"]
        result = resume_summarizer.query(query, doc_type=doc_type)
        return result
    except Exception as error:
        print(error)
        return jsonify({"Status": f"Failure -- some error occured, {error}"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8095, debug=True)
