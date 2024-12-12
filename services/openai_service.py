import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def generate_answer(query: str, formatted_results: list) -> str:
    """
    Generate a comprehensive answer to the user's query with consistent,
    clean formatting optimized for web display. The response will use
    proper spacing, indentation, and structure without any markdown or
    special formatting characters.
    """
    # Construct context from relevant documents
    context = "Relevant Documents and Passages:\n"
    for result in formatted_results:
        title = result.get('title', 'No Title')
        author = result.get('author', 'Unknown')
        context += f"Document: {title} (Author: {author})\n"
        for passage in result.get("passages", []):
            context += f"Content: {passage}\n"

        # Detailed system instructions for consistent formatting
        system_instructions = """You are an AI assistant that provides clear, human-readable responses with excellent sentence and paragraph punctuation.

	Follow these formatting rules exactly:

	* **No Markdown or Special Characters:**  Do NOT use any markdown symbols (**, -, *) or HTML tags. Use only plain text.
	* **Spacing:**  
	   * Add a blank line (empty newline) after each heading.
	   * Add a blank line (empty newline) between paragraphs.
	   * Indent each paragraph with four spaces. 

	* **Structure:**
	   * Start with the OVERVIEW heading.
	   * Include main sections in CAPITALS followed by a new line.
	   * End with a CONCLUSION heading.

	* **Example:**

	  OVERVIEW

		  This is an overview paragraph with an empty newline above and below.

	  COMPONENTS

		  This is a section with an empty newline above and below. 

	  CONCLUSION

		  This is the conclusion with an empty newline above.


		OVERVIEW

		<blank line here> 
			Indented overview paragraph.
		<blank line here> 
		COMPONENTS

		<blank line here> 
			RESPONSE SEPARATED BY NEWLINE 
		<blank line here>
		CONCLUSION

		<blank line here> 
			RESPONSE 
		<blank line here> 
	"""

    user_content = f"""Based on the following context, please answer this query: {query}

    {context}

    Remember:
    1. DO NOT use any markdown symbols (**, -, *)
    2. DO NOT include "AI Assistant Summary" or similar headers
    3. Follow the formatting rules exactly"""

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
            max_tokens=1500,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )

        # Get the response and clean it
        response = completion.choices[0].message.content.strip()

        # Remove any remaining markdown or unwanted headers
        response = response.replace('**AI Assistant Summary**', '')
        response = response.replace('**', '')
        response = response.replace('*', '')

        # Clean up spacing
        response = response.replace('\n\n\n', '\n\n')

        return response

    except Exception as e:
        return f"I apologize, but an error occurred while generating the response: {str(e)}"