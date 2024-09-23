import time
import json
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from jinja2 import Environment, FileSystemLoader

from pathlib import Path
from jobs.job_logger import logger
from jobs.models import Job, ContextGroup
from jobs.datastore import db

MIN_KEYWORDS_THRESHOLD = 2
nltk.download('punkt_tab')
nltk.download('stopwords')

def get_context_keywords(context="IT"):
    context_keywords = []
    if context:
        context_group = ContextGroup.by_name(context)
        if context_group:
            context_keywords = context_group.keyword_list()

    return context_keywords

def generate_file_scores(source_file, context="IT"):
    target_path = Path(source_file).resolve().absolute()

    if target_path.suffix != '.txt':
        logger.error(f'Only text files are supported at this time.  File must have the ".txt" extension.')
        quit()

    with open(source_file, 'r') as fh:
        content = fh.read()

    return generate_keyword_scores(content=content, context=context)
    

def generate_keyword_scores(content, context="IT"):
    context_keywords = get_context_keywords(context)
    content_data = get_content_data(content, context_keywords=context_keywords)
    
    job_scores = []
    jobs = Job.all()
    logger.info(f'Comparing keywords for {len(jobs)} job entries')
    for job in jobs:
        job_keywords = []
        score = {}

        # job_keywords = extract_keywords_guided(job.description.lower(), context_keywords=context_keywords)
        # weighted_keywords = get_weighted_keywords(job.description.lower(), context_keywords=context_keywords)
        weighted_keywords = job.keywords
        posting = {
            "content": job.description,
            "keywords": job_keywords,
            "weighted_keywords": weighted_keywords
        }
       
        score = get_score(posting, content_data)

        detail = {
            "site": job.source,
            "url": job.url,
            "title": job.title,
            "score": score
        }
        job_scores.append(detail)
        # logger.info(f'[{job.source}][{score["total"]}][{job.title}]')

    job_scores.sort(key=lambda x: x['score']['total'], reverse=True)
    return job_scores

def get_content_data(source_content, context_keywords=[]):
    keywords = extract_keywords_guided(source_content.lower(), context_keywords)
    weighted_keywords = calculate_weights(source_content.lower(), keywords)

    return {
        "content": source_content,
        "keywords": keywords,
        "weighted_keywords": weighted_keywords
    }

def get_weighted_keywords(content, context_keywords=[]):
    if not context_keywords:
        context_keywords = get_context_keywords()

    keywords = extract_keywords_guided(content, context_keywords)
    weighted_keywords = calculate_weights(content, keywords)   
    return weighted_keywords

def extract_keywords_guided(text, context_keywords=[]):
    """
    Extract skill-related keywords from the given text and calculate their frequencies.

    This function tokenizes and stems the provided text, removes common stop words, and then 
    counts the occurrences of each remaining word. It returns a dictionary where each skill 
    keyword found in the text is mapped to its frequency.

    Parameters:
    - text (str): The text from which keywords are extracted.

    Returns:
    - dict: A dictionary where each key is a skill-related keyword found in the text, and the 
            value is its frequency (number of occurrences) in the text.
    """
    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [w for w in tokens if not w in stop_words]
    
    # Stem the words
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(w) for w in filtered_tokens]

    # Count the frequency of each token
    token_frequencies = Counter(stemmed_tokens)
   
    # Extract skills and calculate their weights based on frequency
    extracted_skills_with_weights = {}
    if context_keywords:
        # restrict to only the context_keyword entries
        # This is the "guided" part
        for word, freq in token_frequencies.items():
            if word in context_keywords:
                extracted_skills_with_weights[word] = freq
   

    return extracted_skills_with_weights


def calculate_weights(text, skill_keywords):
    """
    Calculate the frequency and relative weight of skill-related keywords in a given text.

    This function tokenizes and stems the provided text, then counts the occurrences of each 
    keyword from the provided list of skill keywords. It returns a dictionary where each skill 
    keyword is mapped to its relative weight, which is the frequency of the keyword divided by 
    the total number of skill-related keywords found in the text.

    Parameters:
    - text (str): The text from which keywords are extracted.
    - skill_keywords (list): A list of skill-related keywords to look for in the text.

    Returns:
    - dict: A dictionary with skill keywords as keys and their normalized weights as values. 
            The weight is the frequency of the keyword in the text, normalized by the total 
            number of skill-related keywords found in the text.
    """
    # Tokenize and stem the text as before
    tokens = nltk.word_tokenize(text)
    stemmed_tokens = [PorterStemmer().stem(w) for w in tokens]

    # filter out single character tokens
    filtered_tokens = [word for word in stemmed_tokens if len(word) > 1]
    
    # Initialize weights dictionary with the skill keywords
    weighted_skills = {skill: 0 for skill in skill_keywords}
    
    # Calculate frequency of each skill keyword in the text
    for word in filtered_tokens:
        if word in weighted_skills:
            weighted_skills[word] += 1  # Increment the weight for each occurrence
    
    # Normalize the weights if needed (e.g., divide by the total count)
    total_occurrences = sum(weighted_skills.values())
    if total_occurrences > 0:
        for skill in weighted_skills:
            weighted_skills[skill] /= total_occurrences
    
    return weighted_skills

def get_score(posting, resume):
    coverage = {}
    density = {}
    common_kw = set(posting["keywords"]).intersection(set(resume["keywords"]))
    
    # Calculate weighted coverage
    coverage = calculate_weighted_coverage(posting["weighted_keywords"], resume["weighted_keywords"])
    
    # Calculate frequency score
    frequency_score = calculate_frequency_score(posting["weighted_keywords"], resume["weighted_keywords"])
    
    # Calculate density score
    density_score = calculate_density_score(posting["weighted_keywords"], resume["weighted_keywords"])
    
    # Calculate overall score
    overall_density_score = round((frequency_score + density_score) / 2, 3)
    
    total_score = (coverage["overall"] + overall_density_score) / 2

    return {
        "total": round(total_score, 2),
        "keywords": {
            "job": posting["keywords"],
            "resume": resume["keywords"],
            "common": list(common_kw)
        },
        "coverage": coverage,
        "density": {
            "frequency_score": frequency_score,
            "density_score": density_score,
            "overall_density_score": overall_density_score
        }
    }


def calculate_weighted_coverage(job_kw_weights, resume_kw_weights):
    """
    Calculate keyword coverage between a job description and a resume.

    - Computes the weight of matching keywords in the job and resume.
    - Calculates the percentage of job and resume keywords that match predefined skill keywords.
    - Measures how many keywords are common to both job and resume.
    - Returns an overall score based on the job and resume keyword coverage and common keyword match.

    Returns:
        A dictionary with:
        - 'overall': The combined score for job and resume keyword coverage.
        - 'coverage': Detailed coverage percentages for job, resume, and common keywords.
        - 'keywords': The job, resume, and common keywords with their weights.
    """

    # Calculate total weights for job and resume keywords
    total_job_weight = sum(job_kw_weights.values())
    total_resume_weight = sum(resume_kw_weights.values())

    # Calculate common keyword weights
    common_weight_sum = sum(resume_kw_weights.get(word, 0) for word in job_kw_weights)

    # Calculate coverage percentages
    job_coverage = (common_weight_sum / max(total_job_weight, 1)) * 100
    resume_coverage = (common_weight_sum / max(total_resume_weight, 1)) * 100
    common_coverage = (common_weight_sum / max(total_job_weight, 1)) * 100

    # Implement minimum threshold for meaningful coverage
    if len(job_kw_weights) < MIN_KEYWORDS_THRESHOLD:
        job_coverage = 0

    if len(resume_kw_weights) < MIN_KEYWORDS_THRESHOLD:
        resume_coverage = 0

    if len(resume_kw_weights) < MIN_KEYWORDS_THRESHOLD:
        resume_coverage = 0

    
    coverage = {
        "job": round(job_coverage, 3),
        "resume": round(resume_coverage, 3),
        # "common": round(common_coverage, 3)
    }
    
    # Calculate overall score
    overall_score = round(((coverage["job"] + coverage["resume"]) / 2), 3)

    return {
        "overall": overall_score,
        "coverage": coverage,
    }

def calculate_frequency_score(job_kw_weights, resume_kw_weights):
    """
    Calculate the frequency score representing how well the resume's keywords match the job's keywords.

    This function computes how much the keywords in the resume overlap with those in the job posting based on their frequencies. 
    It measures the percentage of the job's keyword weight that is also present in the resume's keywords.

    Parameters:
    - job_kw_weights (dict): A dictionary with job keywords as keys and their frequencies as values.
    - resume_kw_weights (dict): A dictionary with resume keywords as keys and their frequencies as values.

    Returns:
    - float: The frequency score as a percentage, indicating how well the resume matches the job description based on keyword frequencies.
    """
    # Calculate total weights for job and resume keywords
    total_job_weight = sum(job_kw_weights.values())
    total_resume_weight = sum(resume_kw_weights.values())
    
    # Calculate common keyword weights
    common_weight_sum = sum(resume_kw_weights.get(word, 0) for word in job_kw_weights)
    
    # Ensure no division by zero
    total_job_weight = max(total_job_weight, 1)
    total_resume_weight = max(total_resume_weight, 1)
    
    # Frequency score as a percentage
    frequency_score = round((common_weight_sum / total_job_weight) * 100, 3)
    
    return frequency_score

def calculate_density_score(job_kw_weights, resume_kw_weights):
    """
    Calculate the density score representing the proportion of keywords from the job description that are also found in the resume.

    This function measures the density of matching keywords between the job description and the resume. Unlike frequency, which counts occurrences, density focuses on how many of the job’s keywords appear in the resume and vice versa. 
    It provides an indication of the extent to which the resume's keyword set overlaps with the job’s keyword set.

    Parameters:
    - job_kw_weights (dict): A dictionary with job keywords as keys and their frequencies as values.
    - resume_kw_weights (dict): A dictionary with resume keywords as keys and their frequencies as values.

    Returns:
    - float: The average density score as a percentage, representing the proportion of job keywords that are present in the resume's keyword set, and vice versa.
    
    """
    # Calculate total number of keywords in job and resume
    total_job_count = sum(1 for word in job_kw_weights if word in resume_kw_weights)
    total_resume_count = sum(1 for word in resume_kw_weights if word in job_kw_weights)
    
    # Calculate density scores
    job_density_score = 0
    resume_density_score = 0
    if len(job_kw_weights):
        job_density_score = round((total_job_count / len(job_kw_weights)) * 100, 3)

    if len(resume_kw_weights):
        resume_density_score = round((total_resume_count / len(resume_kw_weights)) * 100, 3)
    
    return (job_density_score + resume_density_score) / 2


def create_report_html(scores):
    template_dir = Path(__file__).joinpath('../../templates').resolve().absolute()
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('main.html')

    # adjust scores to only those that have a score greater than zero
    filtered_scores = [item for item in scores if item["score"]["total"] > 0]
    
    context = {
        "generated_at": time.strftime("%a, %d %b %Y %H:%M:%S"),
        "result_count": len(filtered_scores),
        "scores": filtered_scores
    }

    output = template.render(context)
    report_file = Path(__file__).parent.joinpath('../report.html').resolve().absolute()
    
    with open(report_file, 'w') as fh:
        fh.write(output)

    logger.info(f'generated {report_file}')
    logger.info(f'  Click to file://{report_file} to open in browser')

