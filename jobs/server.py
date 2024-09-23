import os
import time
from pathlib import Path
from flask import Flask, render_template, request
from flask_caching import Cache
from jobs.analysis import get_weighted_keywords, generate_keyword_scores
from jobs.models import Job

TEMPLATE_DIR = Path(__file__).parent.joinpath('../templates').resolve().absolute()
STATIC_DIR = Path(__file__).parent.joinpath('../static').resolve().absolute()
DB_FILE = Path(__file__).parent.joinpath('../data.db').resolve().absolute()



def create_app():

    config = {
        "DEBUG": False,
        "CACHE_TYPE": "SimpleCache",  # Choose your desired cache backend
        "CACHE_DEFAULT_TIMEOUT": 300  # Cache results for 5 minutes (300 seconds)
    }

    app = Flask(__name__)
    app.config.from_mapping(config)

    cache = Cache(app)  # Create a cache instance

    app.template_folder = TEMPLATE_DIR
    app.static_folder = STATIC_DIR

    @app.get('/')
    def home():
        return render_template('home.html')

    @app.post('/resume')
    def post_resume():
        # Check if a file was uploaded
        if 'file' not in request.files:
            return {"error": "No file uploaded"}, 400  # Bad request

        # Get the uploaded file
        uploaded_file = request.files['file']

        # Check if filename is empty (user didn't select a file)
        if uploaded_file.filename == '':
            return {"error": "No file selected"}, 400  # Bad request

        # Read the file content (assuming it's text-based)
        try:
            file_text = uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError:
            return {"error": "Invalid file format. Please upload a text file."}, 400  # Bad request

        # Return the structure with the extracted content
        return {
            "resume_content": file_text.strip(),
            "resume_keywords": get_weighted_keywords(file_text.lower())
        }

    @app.post('/report')
    @cache.cached(timeout=900)
    def report():
        content = request.get_json()['resume']
        scores = generate_keyword_scores(content)
        jobcount = Job.size()

        # adjust scores to only those that have a score greater than zero
        filtered_scores = [item for item in scores if item["score"]["total"] > 0]
    
        stat = os.stat(DB_FILE)

        context = {
            "generated_at": time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(stat.st_mtime)),
            "total_jobs": jobcount,
            "result_count": len(filtered_scores),
            "scores": filtered_scores
        }

        return render_template("report.html", **context)

    return app

def run():
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=9876)
    

WEB_APP = create_app()