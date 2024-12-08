from flask import Flask, request, jsonify, render_template
from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
import os

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Watson Discovery Configuration
authenticator = IAMAuthenticator('MSIT5S8iFv-CHlYzTarbcrWENND381Xl6qrelESIJtUf')
discovery = DiscoveryV2(version='2021-08-01', authenticator=authenticator)
discovery.set_service_url('https://api.us-east.discovery.watson.cloud.ibm.com/instances/a48613e0-5108-4657-a9c6-6f9c2bde1b37')

# Record of all search results
search_history = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_discovery():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Query parameter is missing'}), 400

        query = data['query']
        response = discovery.query(
            project_id='64cb5014-a3c7-4dee-92c6-1223b49eb98e',
            natural_language_query=query,
            count=5
        ).get_result()

        # Parse and format results
        formatted_results = []
        for result in response.get("results", []):
            metadata = result.get("extracted_metadata", {})
            passages = result.get("document_passages", [])
            formatted_results.append({
                "document_id": result.get("document_id"),
                "author": metadata.get("author", ["Unknown"])[0] if isinstance(metadata.get("author", []), list) else metadata.get("author", "Unknown"),
                "title": metadata.get("title", metadata.get("filename", "No Title")),
                "confidence": f"{result.get('result_metadata', {}).get('confidence', 0) * 100:.2f}%",
                "passages": [p.get("passage_text", "No Passage Available") for p in passages]
            })

        # Record the query and results
        search_record = {
            "query": query,
            "results": formatted_results
        }
        search_history.append(search_record)

        return jsonify(search_record)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(search_history)

if __name__ == '__main__':
    app.run(debug=True)


