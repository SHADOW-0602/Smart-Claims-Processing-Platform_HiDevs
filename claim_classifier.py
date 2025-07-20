import logging
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import json

# Load configuration
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    TRAINING_DATA = config['training_data']
except FileNotFoundError:
    logging.error("config.json not found.")
    raise FileNotFoundError("config.json not found.")
except json.JSONDecodeError:
    logging.error("Invalid config.json format.")
    raise ValueError("Invalid config.json format.")

def train_model():
    """Trains a Naive Bayes classifier for claim types."""
    try:
        df = pd.DataFrame(TRAINING_DATA)
        if 'description' not in df.columns or 'claim_type' not in df.columns:
            raise KeyError("TRAINING_DATA must contain 'description' and 'claim_type' fields.")
        if len(df) < 2:
            raise ValueError("TRAINING_DATA must contain at least 2 samples for training.")
        
        model = make_pipeline(TfidfVectorizer(), MultinomialNB(), memory=None)
        model.fit(df['description'], df['claim_type'])
        logging.info("Claim classification model trained successfully.")
        return model
    except Exception as e:
        logging.error(f"Failed to train classification model: {e}")
        return None

def classify_claim(model, claim_text: str):
    """
    Classifies the claim by type and priority.
    
    Args:
        model: Trained classifier model.
        claim_text (str): Extracted text from the claim.
        
    Returns:
        tuple: (claim_type, confidence, priority)
    """
    if not model or not claim_text or not isinstance(claim_text, str):
        logging.warning("Invalid model or claim text for classification.")
        return None, 0.0, None
    
    try:
        prediction = model.predict([claim_text])
        probabilities = model.predict_proba([claim_text])
        confidence = probabilities.max()
        claim_type = prediction[0]

        # Rule-based logic for priority
        high_priority_keywords = ["major", "fire", "totaled", "emergency", "collision"]
        priority = "High" if any(kw in claim_text.lower() for kw in high_priority_keywords) else "Medium"
        
        logging.info(f"Claim classified as Type: {claim_type}, Priority: {priority}, Confidence: {confidence:.2f}")
        return claim_type, confidence, priority
    except Exception as e:
        logging.error(f"Failed to classify claim: {e}")
        return None, 0.0, None