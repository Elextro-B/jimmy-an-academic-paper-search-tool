import json
import os
from flask import Flask, redirect, render_template, request
import pymupdf
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATA_FILE = "pdf_data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


def search_my_pdfs(keyword):
    results = []

    with open(DATA_FILE, "r") as f:
        all_pdfs = json.load(f)

    for pdf in all_pdfs:
        if keyword and keyword.lower() in pdf["text"].lower():
            results.append(pdf["filename"])
    return results


# 1. Root route for searching
@app.route("/", methods=["GET", "POST"])
def home():
    search_results = None
    query = ""

    if request.method == "POST":
        query = request.form.get("query")
        search_results = search_my_pdfs(query)

    return render_template("index.html", query=query, results=search_results)


# 2. Upload route for ingesting PDFs
@app.route("/upload", methods=["GET", "POST"])
def upload_pdfs():
    if request.method == "POST":
        uploaded_files = request.files.getlist("pdf_files")

        with open(DATA_FILE, "r") as f:
            existing_data = json.load(f)

        for file in uploaded_files:
            if file and file.filename.endswith(".pdf"):
                safe_filename = secure_filename(file.filename)

                stream = file.read()
                doc = pymupdf.open(stream=stream, filetype="pdf")

                extracted_text = ""
                for page in doc:
                    extracted_text += page.get_text() + "\n"

                existing_data.append(
                    {"filename": safe_filename, "text": extracted_text}
                )

        with open(DATA_FILE, "w") as f:
            json.dump(existing_data, f)

        return "Files successfully ingested with PyMuPDF! <a href='/'>Go to search</a>"

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(debug=True)