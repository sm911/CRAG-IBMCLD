import os
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes


def list_available_models(model):
    """List all available models in the current tier."""
    try:
        available_models = model.get_details()
        print("\nAvailable Models:")
        for model_info in available_models:
            print(f"- {model_info}")
    except Exception as e:
        print(f"Error listing models: {str(e)}")


def test_model_availability(credentials, project_id, model_id):
    """Test if a specific model is available and working."""
    try:
        model = Model(
            model_id=model_id,
            credentials=credentials,
            project_id=project_id
        )

        prompt = "Say 'Hello, credentials are working!'"
        params = {
            "decoding_method": "greedy",
            "max_new_tokens": 100,
            "min_new_tokens": 0
        }
        response = model.generate_text(prompt, params)
        return True, response
    except Exception as e:
        return False, str(e)


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

    # List of models to test, in order of preference
    models_to_test = [
        "ibm/granite-3-8b-instruct",
        "ibm/granite-3-2b-instruct",
        "ibm/granite-13b-chat-v2"  # Keep as fallback
    ]

    # Test each model
    for model_id in models_to_test:
        print(f"\nTesting model: {model_id}")
        success, response = test_model_availability(credentials, project_id, model_id)

        if success:
            print(f"Successfully connected to {model_id}")
            if isinstance(response, dict) and "results" in response:
                print("Model response:", response["results"][0]["generated_text"])
            else:
                print("Raw response:", response)
            return True
        else:
            print(f"Failed to use {model_id}: {response}")

    return False


if __name__ == "__main__":
    test_credentials()