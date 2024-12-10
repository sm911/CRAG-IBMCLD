import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from ibm_watson import DiscoveryV2, NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions
from dotenv import load_dotenv
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Set the default logging level to WARNING

# Suppress IBM Watson SDK logs
logging.getLogger("ibm-cloud-sdk-core").setLevel(logging.WARNING)

# Suppress urllib3 logs (used by IBM Watson SDKs)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Suppress Werkzeug logs
logging.getLogger("werkzeug").setLevel(logging.INFO)

# Load environment variables from the .env file
env_path = Path(__file__).parent / "ibm-credentials.env"
load_dotenv(dotenv_path=env_path)

# Fetch credentials from environment variables
discovery_api_key = os.getenv('WATSON_DISCOVERY_APIKEY')
discovery_url = os.getenv('WATSON_DISCOVERY_URL')
discovery_project_id = os.getenv('WATSON_DISCOVERY_PROJECT_ID')
discovery_collection_id = os.getenv('WATSON_DISCOVERY_COLLECTION_ID')
nlu_api_key = os.getenv('NATURAL_LANGUAGE_UNDERSTANDING_APIKEY')
nlu_url = os.getenv('NATURAL_LANGUAGE_UNDERSTANDING_URL')

# Validate environment variables
if not all([discovery_api_key, discovery_url, discovery_project_id, discovery_collection_id, nlu_api_key, nlu_url]):
    raise ValueError("One or more required environment variables are missing.")

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Configure upload directory and allowed file types
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload directory exists

# Watson Discovery Configuration
discovery_authenticator = IAMAuthenticator(discovery_api_key)
discovery = DiscoveryV2(version='2021-08-01', authenticator=discovery_authenticator)
discovery.set_service_url(discovery_url)

# Watson Natural Language Understanding Configuration
nlu_authenticator = IAMAuthenticator(nlu_api_key)
nlu = NaturalLanguageUnderstandingV1(version='2021-08-01', authenticator=nlu_authenticator)
nlu.set_service_url(nlu_url)

# Record of all search results
search_history = []


# Helper: Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Define the homepage route
@app.route('/')
def home():
    return render_template('index.html')  # Renders the homepage


# Upload Route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Ingest the file into Watson Discovery
            with open(filepath, 'rb') as file_data:
                response = discovery.add_document(
                    project_id=discovery_project_id,
                    collection_id=discovery_collection_id,  # Use collection ID from .env file
                    file=file_data,
                    filename=filename
                ).get_result()

            return jsonify({'message': 'File uploaded and added to Watson Discovery successfully', 'response': response}), 200

        except Exception as e:
            return jsonify({'error': f"Failed to add document to Watson Discovery: {str(e)}"}), 500

    return jsonify({'error': 'File type not allowed'}), 400


# Helper: Calculate Semantic Similarity using Watson NLU
def calculate_relevance(query, passage):
    try:
        response = nlu.analyze(
            text=f"{query} {passage}",
            features=Features(categories=CategoriesOptions(limit=3))
        ).get_result()
        score = response['categories'][0]['score'] if response.get('categories') else 0
        return score
    except Exception as e:
        return 0


# Query Route for Watson Discovery
@app.route('/query', methods=['POST'])
def query_discovery():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Query parameter is missing'}), 400

        query = data['query']
        start_date = data.get('start_date')  # Optional parameter
        end_date = data.get('end_date')    # Optional parameter
        confidence_threshold = float(data.get('confidence_threshold', 0))  # Default to 0 if not provided
        relevance_threshold = float(data.get('relevance_threshold', 0))    # Default to 0 if not provided

        # Build filter string
        filters = []
        if start_date:
            filters.append(f"date>={start_date}")
        if end_date:
            filters.append(f"date<={end_date}")
        filter_query = ' AND '.join(filters) if filters else None

        # Watson Discovery query
        response = discovery.query(
            project_id=discovery_project_id,
            natural_language_query=query,
            filter=filter_query,
            count=20  # Fetch more results to support pagination
        ).get_result()

        formatted_results = []
        for result in response.get("results", []):
            metadata = result.get("extracted_metadata", {})
            passages = result.get("document_passages", [])
            confidence_value = result.get('result_metadata', {}).get('confidence', 0) * 100

            # Skip results below the confidence threshold
            if confidence_value < confidence_threshold:
                continue

            scores = [
                {
                    "passage": p.get("passage_text", "No Passage Available"),
                    "relevance_score": calculate_relevance(query, p.get("passage_text", ""))
                }
                for p in passages
            ]

            # Skip results below the relevance threshold
            if relevance_threshold > 0 and not any(s['relevance_score'] >= relevance_threshold for s in scores):
                continue

            formatted_results.append({
                "document_id": result.get("document_id"),
                "author": metadata.get("author", "Unknown"),
                "title": metadata.get("title", metadata.get("filename", "No Title")),
                "confidence": f"{confidence_value:.2f}%",
                "relevance": f"{scores[0]['relevance_score']:.2f}" if scores else "0.00",
                "passages": [s['passage'] for s in scores if s['relevance_score'] >= relevance_threshold]
            })

        # Add logging for debugging
        logging.debug(f"Query results: {formatted_results}")

        # Ensure the response always contains 'results'
        return jsonify({
            "query": query,
            "results": formatted_results
        })
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500


# History Route (if applicable)
@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(search_history)


# Run the Flask App
if __name__ == '__main__':
    app.run(debug=False)