from config import ALLOWED_EXTENSIONS

def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_thresholds(confidence_threshold: float, relevance_threshold: float):
    if not (0 <= confidence_threshold <= 100):
        raise ValueError("Confidence threshold must be between 0 and 100.")
    if not (0 <= relevance_threshold <= 1):
        raise ValueError("Relevance threshold must be between 0 and 1.")

def validate_dates(start_date: str, end_date: str):
    # Basic validation: if both provided, ensure start_date <= end_date
    if start_date and end_date and start_date > end_date:
        raise ValueError("Start date cannot be after end date.")
