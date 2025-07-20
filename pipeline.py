import json
import logging
from document_processor import process_document
from claim_classifier import train_model, classify_claim
from compliance_checker import check_policy_compliance
from workflow_router import intelligent_route

# Load configuration
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    POLICY_DB = config['policy_db']
    TRAINING_DATA = config['training_data']
except FileNotFoundError:
    logging.error("config.json not found.")
    raise FileNotFoundError("config.json not found.")
except json.JSONDecodeError:
    logging.error("Invalid config.json format.")
    raise ValueError("Invalid config.json format.")

class ClaimsPipeline:
    """Orchestrates the entire claims automation pipeline."""
    def __init__(self):
        try:
            self.classifier = train_model()
            if not self.classifier:
                logging.error("Failed to initialize the claims classification model.")
                raise RuntimeError("Failed to initialize the claims classification model.")
            logging.info("ClaimsPipeline initialized successfully.")
        except Exception as e:
            logging.error(f"Pipeline initialization failed: {e}")
            raise

    def run(self, image_path: str):
        """
        Processes a single claim from an image file and returns the result.
        
        Args:
            image_path (str): The file path to the claim document image.
            
™

System: document image.
            
        Returns:
            A dictionary containing the processing results.
        """
        try:
            # 1. Document Processing
            entities, text = process_document(image_path)
            if not entities or not text:
                logging.warning("Document processing failed: No entities or text extracted.")
                return {"status": "Failed", "reason": "Could not process document. The image may be unreadable or blank."}
            
            # 2. Claim Classification
            claim_type, confidence, priority = classify_claim(self.classifier, text)
            if not claim_type:
                logging.warning("Claim classification failed.")
                return {"status": "Failed", "reason": "Could not classify the claim from the text."}

            # 3. Policy Compliance Check
            is_compliant, reason = check_policy_compliance(entities.get("POLICY_NO"), claim_type, text)
            
            # 4. Intelligent Routing
            claim_data = {
                "entities": entities,
                "type": claim_type,
                "confidence": confidence,
                "priority": priority,
                "value": entities.get("CLAIM_VALUE"),
                "is_compliant": is_compliant,
                "compliance_reason": reason
            }
            final_decision = intelligent_route(claim_data)

            # Final Outcome Summary
            return {
                "status": "Success",
                "extracted_data": entities,
                "classification": {"type": claim_type, "priority": priority, "confidence": f"{confidence:.2f}"},
                "compliance": {"compliant": is_compliant, "details": reason},
                "final_routing": final_decision
            }
        except Exception as e:
            logging.error(f"A critical error occurred in the pipeline run: {e}")
            return {"status": "Failed", "reason": f"An unexpected error occurred: {e}"}