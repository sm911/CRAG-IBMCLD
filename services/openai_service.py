from openai import OpenAI
from config import OPENAI_API_KEY

def get_openai_client():
    return OpenAI(api_key=OPENAI_API_KEY)

def generate_answer(query: str, formatted_results: list) -> str:
    """
    Generate a comprehensive answer to the user's query using OpenAI.
    """
    prompt = f"User Query: {query}\n\nRelevant Documents and Passages:\n"
    for result in formatted_results:
        prompt += f"- Title: {result['title']}\n  Author: {result['author']}\n  Passages:\n"
        for passage in result["passages"]:
            prompt += f"    - {passage}\n"
    prompt += "\nBased on the above information, please provide a comprehensive answer to the user's query."

    client = get_openai_client()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides comprehensive answers based on the provided documents."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    return completion.choices[0].message.content.strip()
