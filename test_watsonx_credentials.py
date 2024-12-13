import os
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes


def test_credentials():
    # Load environment variables
    load_dotenv('ibm-credentials.env')

    # Get credentials from env file
    api_key = os.getenv('WATSONX_API_KEY')
    project_id = os.getenv('WATSONX_PROJECT_ID')
    url = os.getenv('WATSONX_URL')

    # Set up credentials dictionary
    credentials = {
        "url": url,
        "apikey": api_key
    }

    try:
        # Initialize model
        model = Model(
            model_id="ibm/granite-13b-chat-v2",  # Updated to v2
            credentials=credentials,
            project_id=project_id
        )

        # Test simple prompt
        prompt = "Say 'Hello, credentials are working!'"
        params = {
            "decoding_method": "greedy",
            "max_new_tokens": 100,
            "min_new_tokens": 0
        }
        response = model.generate_text(prompt, params)

        print("Connection successful!")
        if isinstance(response, dict) and "results" in response:
            print("Model response:", response["results"][0]["generated_text"])
        else:
            print("Raw response:", response)
        return True

    except Exception as e:
        print("Error connecting to watsonx.ai:")
        print(str(e))
        return False

if __name__ == "__main__":
        test_credentials()