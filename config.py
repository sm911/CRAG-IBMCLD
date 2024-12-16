import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / "ibm-credentials.env")

# Validate environment variables
def get_env_var(var_name: str) -> str:
    val = os.getenv(var_name)
    if not val:
        raise ValueError(f"Missing required environment variable: {var_name}")
    return val

# IBM Credentials
DISCOVERY_API_KEY = get_env_var('WATSON_DISCOVERY_APIKEY')
DISCOVERY_URL = get_env_var('WATSON_DISCOVERY_URL')
DISCOVERY_PROJECT_ID = get_env_var('WATSON_DISCOVERY_PROJECT_ID')
DISCOVERY_COLLECTION_ID = get_env_var('WATSON_DISCOVERY_COLLECTION_ID')

NLU_API_KEY = get_env_var('NATURAL_LANGUAGE_UNDERSTANDING_APIKEY')
NLU_URL = get_env_var('NATURAL_LANGUAGE_UNDERSTANDING_URL')

# WatsonX.ai Credentials
WATSONX_API_KEY = get_env_var('WATSONX_API_KEY')
WATSONX_PROJECT_ID = get_env_var('WATSONX_PROJECT_ID')
WATSONX_URL = get_env_var('WATSONX_URL')

# Application settings
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

# Service versions
DISCOVERY_VERSION = '2021-08-01'
NLU_VERSION = '2021-08-01'

# Add this with your other env var validations
APP_PASSPHRASE = get_env_var('DronesOverUSA')  # Store actual passphrase server-side