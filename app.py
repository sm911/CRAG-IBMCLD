import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from services.ibm_services import add_document_to_discovery, query_discovery, get_nlu_client, calculate_relevance
# from services.openai_service import generate_answer  # Original OpenAI implementation
from services.watsonxai_service import generate_answer  # New watsonx.ai implementation
from utils.validators import allowed_file, validate_thresholds, validate_dates
from utils.logger import logger
from config import UPLOAD_FOLDER, APP_PASSPHRASE_HASH
from functools import wraps

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

search_history = []

def requires_passphrase(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('X-App-Passphrase')
        if not auth_header or auth_header != APP_PASSPHRASE_HASH:
            return jsonify({'error': 'Access denied. Valid passphrase required.'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    """Render the home page template."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@requires_passphrase
def upload_file():
    """Upload and add a document to IBM Discovery."""
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
            response = add_document_to_discovery(filepath, filename)
            return jsonify({'message': 'File uploaded successfully', 'response': response}), 200
        except Exception as e:
            logger.error(f"Failed to add document: {str(e)}")
            return jsonify({'error': f"Failed to add document: {str(e)}"}), 500

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/query', methods=['POST'])
@requires_passphrase
def query_endpoint():
    """
    Query IBM Discovery for documents relevant to the user's query,
    filter them by confidence and relevance thresholds, and generate a summary using IBM watsonx.ai.
    Return all documents that meet minimum requirements for display in a table.

    The process:
    1. Query IBM Discovery for relevant documents
    2. Use NLU to calculate relevance scores
    3. Filter results based on confidence and relevance thresholds
    4. Generate comprehensive answer using watsonx.ai foundation model
    5. Return query results and generated answer
    """
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query parameter is missing'}), 400

        query = data['query']
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        confidence_threshold = float(data.get('confidence_threshold', 0))
        relevance_threshold = float(data.get('relevance_threshold', 0))

        # Validate input
        validate_thresholds(confidence_threshold, relevance_threshold)
        validate_dates(start_date, end_date)

        logger.info(f"Received query: {query}")

        discovery_response = query_discovery(query, start_date, end_date)
        results = discovery_response.get("results", [])

        nlu_client = get_nlu_client()
        formatted_results = []
        for result in results:
            metadata = result.get("extracted_metadata", {})
            passages = result.get("document_passages", [])
            confidence_value = result.get('result_metadata', {}).get('confidence', 0) * 100

            if confidence_value < confidence_threshold:
                continue

            # Calculate relevance for each passage
            scores = [
                {
                    "passage": p.get("passage_text", "No Passage Available"),
                    "relevance_score": calculate_relevance(nlu_client, query, p.get("passage_text", ""))
                }
                for p in passages
            ]

            # If a relevance threshold is set, skip documents that don't meet it
            if relevance_threshold > 0 and not any(s['relevance_score'] >= relevance_threshold for s in scores):
                continue

            # Include all passages that meet or exceed relevance threshold
            relevant_passages = [s['passage'] for s in scores if s['relevance_score'] >= relevance_threshold]

            # If no relevant passages after filtering, skip the doc
            if not relevant_passages:
                continue

            # Document passes the filters, so add it
            top_relevance = max(s['relevance_score'] for s in scores if s['relevance_score'] >= relevance_threshold)
            formatted_results.append({
                "document_id": result.get("document_id"),
                "author": metadata.get("author", "Unknown"),
                "title": metadata.get("title", metadata.get("filename", "No Title")),
                "confidence": f"{confidence_value:.2f}%",
                "relevance": f"{top_relevance:.2f}",
                "passages": relevant_passages
            })

        answer = ""
        if formatted_results:
            # Generate answer using watsonx.ai foundation model
            answer = generate_answer(query, formatted_results)

        # Log the query and answer
        search_history.append({
            "query": query,
            "answer": answer
        })

        return jsonify({
            "query": query,
            "answer": answer,
            "relevant_documents": formatted_results,
            "search_history": search_history
        }), 200

    except ValueError as ve:
        logger.error(str(ve))
        return jsonify({'error': str(ve)}), 422
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info("Starting Flask Application")
    # Get port from environment variable or default to 8080
    port = int(os.environ.get('PORT', 8080))
    # If running locally (not in Code Engine)
    if os.environ.get('K_SERVICE') is None:
        app.run(host='127.0.0.1', port=port, debug=True)
    else:
        # In Code Engine, let gunicorn handle it
        app.run(host='0.0.0.0', port=port, debug=False)