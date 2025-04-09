import os
from flask import Flask, request, redirect, url_for, render_template, flash , session
from werkzeug.utils import secure_filename
from transformers import pipeline
import pandas as pd  


qa_pipeline = pipeline("question-answering")
app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form.get('question')
    file_path = session.get('uploaded_file')  

    if not question:
        return "No question provided", 400
    if not file_path:
        return "No Excel file found", 400
    try:
        # Read the Excel file and convert to plain text
        df = pd.read_excel(file_path)
        excel_text = df.to_csv(index=False)
  # Convert whole sheet to string
    except Exception as e:
        return f"Failed to read Excel file: {str(e)}", 500

    result = qa_pipeline(question=question, context=excel_text)
    return result['answer']

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['uploaded_file'] = filepath 
        flash('File successfully uploaded')
        return render_template('upload.html', uploaded=True)
    else:
        flash('Only Excel files (.xls, .xlsx) are allowed')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True, port=5050)
 



