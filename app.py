from flask import Flask, request, jsonify, render_template
from ibm_watson import DiscoveryV2, NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from the .env file
env_path = Path(__file__).parent / "ibm-credentials.env"
load_dotenv(dotenv_path=env_path)

# Fetch credentials from environment variables
discovery_api_key = os.getenv('WATSON_DISCOVERY_APIKEY')
discovery_url = os.getenv('WATSON_DISCOVERY_URL')
discovery_project_id = os.getenv('WATSON_DISCOVERY_PROJECT_ID')
nlu_api_key = os.getenv('NATURAL_LANGUAGE_UNDERSTANDING_APIKEY')
nlu_url = os.getenv('NATURAL_LANGUAGE_UNDERSTANDING_URL')

# Validate environment variables
if not all([discovery_api_key, discovery_url, discovery_project_id, nlu_api_key, nlu_url]):
    raise ValueError("One or more required environment variables are missing.")

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

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

# Home Page Route
@app.route('/')
def home():
    return render_template('index.html')

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
        response = discovery.query(
            project_id=discovery_project_id,
            natural_language_query=query,
            count=5
        ).get_result()

        formatted_results = []
        for result in response.get("results", []):
            metadata = result.get("extracted_metadata", {})
            passages = result.get("document_passages", [])

            scores = [
                {
                    "passage": p.get("passage_text", "No Passage Available"),
                    "relevance_score": calculate_relevance(query, p.get("passage_text", ""))
                }
                for p in passages
            ]

            formatted_results.append({
                "document_id": result.get("document_id"),
                "author": metadata.get("author", "Unknown"),
                "title": metadata.get("title", metadata.get("filename", "No Title")),
                "confidence": f"{result.get('result_metadata', {}).get('confidence', 0) * 100:.2f}%",
                "scores": sorted(scores, key=lambda x: x['relevance_score'], reverse=True)
            })

        search_record = {"query": query, "results": formatted_results}
        search_history.append(search_record)

        return jsonify(search_record)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# History Route
@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(search_history)

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)