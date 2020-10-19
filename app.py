from io import BytesIO

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from resume_parser.custom_resume_parser import CustomResumeParser

from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ('pdf', 'doc', 'docx')


@app.route('/Backend/resume', methods=['POST'])
def parse_resume():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify(Error="File error")
        file = request.files['file']
        if file.filename == '':
            return jsonify(Error="File error")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if filename:
                resume = BytesIO(file.read())
                resume.name = filename
                return parse_resume_to_dict(resume, skills_file='resume_parser/skills_dataset.csv')
            return jsonify(Error="Filename not secure")
    return jsonify(Error="Method not allowed")


def parse_resume_to_dict(file, skills_file=None):
    resume = CustomResumeParser(file, skills_file=skills_file).get_extracted_data()
    return jsonify(Resume=resume)


if __name__ == '__main__':
    app.run()
