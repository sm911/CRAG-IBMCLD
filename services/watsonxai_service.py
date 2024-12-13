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
        system_instructions = """You are an AI assistant that MUST format responses EXACTLY as follows:

OVERVIEW

   [Write a clear 2-3 sentence overview here, with 4 spaces indentation]

KEY POINTS

   [Component Name] ([ABBREVIATION]):
       • List key capabilities with bullet points
       • Each bullet should be indented with 8 spaces
       • Include specific details from the documents

   [Next Component] ([ABBREVIATION]):
       • Continue with similar bullet point structure
       • Maintain consistent formatting
       • Focus on key features and benefits

CONCLUSION

   [Write a clear 1-2 sentence conclusion here, with 4 spaces indentation]"""

        prompt = f"""System: {system_instructions}

Provide a response to this query using ONLY the information from the context. Format your response exactly as shown above.

Query: {query}

Context:
{context}

Begin with "Response:" and maintain consistent formatting throughout. DO NOT include any instruction text in your response."""

        # Initialize model
        model = Model(
            model_id="ibm/granite-3-8b-instruct",  # Updated to non-deprecated model
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