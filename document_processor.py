import re
import logging
import pytesseract
import spacy
from PIL import Image, ImageEnhance
import config
import subprocess

# Check for Tesseract binary
try:
    subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
except subprocess.CalledProcessError:
    logging.error("Tesseract OCR not found. Install it with 'sudo apt install tesseract-ocr' in Codespaces.")
    raise RuntimeError("Tesseract OCR not found.")

# Singleton for caching spaCy model
class SpacyModel:
    _instance = None
    _nlp = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpacyModel, cls).__new__(cls)
            try:
                cls._nlp = spacy.load(config.SPACY_MODEL)
            except OSError:
                logging.error(f"SpaCy model '{config.SPACY_MODEL}' not found. Run 'python -m spacy download {config.SPACY_MODEL}'")
                raise RuntimeError(f"SpaCy model '{config.SPACY_MODEL}' not found.")
        return cls._instance

    @property
    def nlp(self):
        return self._nlp

def process_document(image_path: str):
    """
    Extracts text and structured entities from a claim document image.
    
    Args:
        image_path (str): Path to the claim document image.
        
    Returns:
        tuple: (extracted_entities, raw_text)
    """
    logging.info(f"Starting document processing for: {image_path}")
    
    try:
        # Preprocess image for better OCR
        image = Image.open(image_path).convert('L')  # Convert to grayscale
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)  # Increase contrast
        
        extracted_text = pytesseract.image_to_string(image)
        
        if not extracted_text.strip() or len(extracted_text) < 50:
            logging.warning("OCR returned insufficient text. The document might be blank or unreadable.")
            return None, None

        nlp = SpacyModel().nlp
        entities = {"PERSON": [], "DATE": [], "POLICY_NO": None, "CLAIM_VALUE": None}

        # Use regex and NLP for entity extraction
        policy_match = re.search(r"Policy No[:\s]+([A-Z0-9\-]+)", extracted_text, re.IGNORECASE)
        if policy_match:
            entities["POLICY_NO"] = policy_match.group(1).strip()
        
        value_match = re.search(r"Claim Amount[:\s]+\$?([\d,]+\.?\d*)", extracted_text, re.IGNORECASE)
        if value_match:
            entities["CLAIM_VALUE"] = float(value_match.group(1).replace(",", ""))

        # Extract PERSON and DATE entities using SpaCy
        doc = nlp(extracted_text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["PERSON"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["DATE"].append(ent.text)

        logging.info(f"Successfully extracted entities: {entities}")
        return entities, extracted_text
        
    except FileNotFoundError:
        logging.error(f"File not found at path: {image_path}")
        return None, None
    except Exception as e:
        logging.error(f"An unexpected error occurred during document processing: {e}")
        return None, None