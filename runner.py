import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo



# From NLTK, provides common stopwords like 'An, The, Who ..'
stop_words = set(stopwords.words('english'))

# Function to calculate the similarity between two files
def calculate_tfidf_similarity(file1_path, file2_path):
    # Try to open with utf-8 encoding
    try:
        with open(file1_path, 'r', encoding='utf-8') as file1, open(file2_path, 'r', encoding='utf-8') as file2:
            file1_contents = file1.read()
            file2_contents = file2.read()
    except UnicodeDecodeError:
        # If utf-8 doesn't work, try iso-8859-1
        with open(file1_path, 'r', encoding='iso-8859-1') as file1, open(file2_path, 'r', encoding='iso-8859-1') as file2:
            file1_contents = file1.read()
            file2_contents = file2.read()

    file1_preprocessed = preprocess_text(file1_contents)
    file2_preprocessed = preprocess_text(file2_contents)

    # TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([file1_preprocessed, file2_preprocessed])

    # Get the TF-IDF vectors for file1 and file2
    file1_tfidf = tfidf_matrix[0]
    file2_tfidf = tfidf_matrix[1]

    # Calculate cosine similarity
    similarity = (file1_tfidf * file2_tfidf.T).toarray()[0, 0]

    return similarity

# Function to preprocess text (tokenize, remove stopwords, etc.)
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    preprocessed_text = " ".join(tokens)
    return preprocessed_text

# Function to process a single job description against the resume
def process_single_job(resume_path, job_desc_path):
    return calculate_tfidf_similarity(resume_path, job_desc_path)
