import os
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes

# Load environment variables
load_dotenv('ibm-credentials.env')

# Initialize credentials
credentials = {
    "url": os.getenv('WATSONX_URL'),
    "apikey": os.getenv('WATSONX_API_KEY')
}


def generate_answer(query: str, formatted_results: list) -> str:
    """
    Generate a comprehensive answer to the user's query with consistent,
    clean formatting optimized for web display. The response will use
    proper spacing, indentation, and structure without any markdown or
    special formatting characters.
    """
    try:
        # Construct context from relevant documents
        context = "Relevant Documents and Passages:\n"
        for result in formatted_results:
            title = result.get('title', 'No Title')
            author = result.get('author', 'Unknown')
            context += f"Document: {title} (Author: {author})\n"
            for passage in result.get("passages", []):
                context += f"Content: {passage}\n"

        # Detailed system instructions for consistent formatting
        system_instructions = """You are an AI assistant that MUST format responses EXACTLY like this:

                OVERVIEW

                    Provide a 2-3 sentence high-level summary of the answer.

                KEY POINTS

                    First major point with specific details from the documents.
                    Each point should be properly indented with 4 spaces.

                    Second major point with supporting information from the sources.
                    Include specific details and maintain the indentation.

                CONCLUSION

                    Wrap up the main ideas in 1-2 clear sentences.

                IMPORTANT: 
                - Every section MUST be in CAPITAL LETTERS
                - Every paragraph MUST be indented with exactly 4 spaces
                - Always include all three sections: OVERVIEW, KEY POINTS, and CONCLUSION
                - Use clear transitions between ideas
                - Be direct and specific in answering the query"""

        # Make the prompt more directive and include the Response label
        prompt = f"""System: {system_instructions}

        Query: {query}

        Response:
        {context}

        You MUST:
        1. Start with the word "Response:" followed by a newline
        2. Answer the query directly and comprehensively
        3. Use specific information from the provided documents
        4. Maintain proper paragraph structure and punctuation"""

        # Initialize model
        model = Model(
            model_id="ibm/granite-13b-chat-v2",
            credentials=credentials,
            project_id=os.getenv('WATSONX_PROJECT_ID')
        )

        # Generate response with parameters
        params = {
            "decoding_method": "greedy",
            "max_new_tokens": 1500,
            "min_new_tokens": 0,
            "temperature": 0.7,
            "repetition_penalty": 1.1
        }

        response = model.generate_text(prompt, params)

        # Clean and format the response
        if isinstance(response, dict) and "results" in response:
            result = response["results"][0]["generated_text"].strip()
        else:
            result = str(response).strip()

        # Clean up spacing and formatting
        result = result.replace('**AI Assistant Summary**', '')
        result = result.replace('**', '')
        result = result.replace('*', '')
        result = result.replace('\n\n\n', '\n\n')

        # Ensure proper spacing for sections
        result = result.replace('OVERVIEW\n', 'OVERVIEW\n\n')
        result = result.replace('KEY POINTS\n', 'KEY POINTS\n\n')
        result = result.replace('CONCLUSION\n', 'CONCLUSION\n\n')

        return result

    except Exception as e:
        return f"I apologize, but an error occurred while generating the response: {str(e)}"