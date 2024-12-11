import os
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import DiscoveryV2, NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions
from config import (DISCOVERY_API_KEY, DISCOVERY_URL, DISCOVERY_PROJECT_ID,
                    DISCOVERY_COLLECTION_ID, NLU_API_KEY, NLU_URL, DISCOVERY_VERSION, NLU_VERSION)
from utils.logger import logger


def get_discovery_client():
    """Initialize and return the IBM Discovery client."""
    authenticator = IAMAuthenticator(DISCOVERY_API_KEY)
    discovery = DiscoveryV2(version=DISCOVERY_VERSION, authenticator=authenticator)
    discovery.set_service_url(DISCOVERY_URL)
    return discovery

def get_nlu_client():
    """Initialize and return the IBM NLU client."""
    authenticator = IAMAuthenticator(NLU_API_KEY)
    nlu = NaturalLanguageUnderstandingV1(version=NLU_VERSION, authenticator=authenticator)
    nlu.set_service_url(NLU_URL)
    return nlu

def add_document_to_discovery(file_path: str, filename: str):
    """Add a document to the Discovery collection."""
    discovery = get_discovery_client()
    with open(file_path, 'rb') as file_data:
        response = discovery.add_document(
            project_id=DISCOVERY_PROJECT_ID,
            collection_id=DISCOVERY_COLLECTION_ID,
            file=file_data,
            filename=filename
        ).get_result()
    return response

def query_discovery(query: str, start_date: str = None, end_date: str = None, count: int = 20):
    """Query the Discovery collection."""
    discovery = get_discovery_client()
    filters = []
    if start_date:
        filters.append(f"date>={start_date}")
    if end_date:
        filters.append(f"date<={end_date}")
    filter_query = ' AND '.join(filters) if filters else None

    response = discovery.query(
        project_id=DISCOVERY_PROJECT_ID,
        natural_language_query=query,
        filter=filter_query,
        count=count
    ).get_result()
    return response

def calculate_relevance(nlu_client, query: str, passage: str) -> float:
    """
    Calculate relevance of a passage to a query using NLU categories as a heuristic.
    Returns a score between 0 and 1.
    """
    if not passage:
        return 0.0
    try:
        response = nlu_client.analyze(
            text=f"{query} {passage}",
            features=Features(categories=CategoriesOptions(limit=3))
        ).get_result()

        if 'categories' in response and response['categories']:
            return response['categories'][0]['score']
        return 0.0
    except Exception as e:
        logger.warning(f"NLU relevance calculation failed: {e}")
        return 0.0
