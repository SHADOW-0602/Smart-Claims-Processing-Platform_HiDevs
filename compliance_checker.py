import logging
import json
import re

# Load configuration
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    POLICY_DB = config['policy_db']
except FileNotFoundError:
    logging.error("config.json not found.")
    raise FileNotFoundError("config.json not found.")
except json.JSONDecodeError:
    logging.error("Invalid config.json format.")
    raise ValueError("Invalid config.json format.")

def check_policy_compliance(policy_number: str, claim_type: str, claim_details: str):
    """
    Verifies if the claim adheres to the policy rules.
    
    Args:
        policy_number (str): The policy number from the claim.
        claim_type (str): The classified claim type.
        claim_details (str): The extracted text from the claim.
        
    Returns:
        tuple: (is_compliant, reason)
    """
    logging.info(f"Checking policy compliance for Policy No: {policy_number}")
    
    try:
        # Validate inputs
        if not policy_number or not claim_type or not claim_details:
            return False, "Invalid Data (Missing Policy No., Claim Type, or Claim Details)"
        
        # Validate policy number format (e.g., PN-XXXX-12345)
        if not re.match(r"PN-[A-Z]+-\d+", policy_number):
            return False, f"Invalid Policy Number format: {policy_number}"

        policy = POLICY_DB.get(policy_number)
        if not policy:
            return False, f"Policy {policy_number} not found"
        
        if claim_type not in policy["coverage"]:
            return False, f"Claim type '{claim_type}' is not covered."
        
        for exclusion in policy["exclusions"]:
            if exclusion in claim_details.lower():
                return False, f"Claim rejected due to exclusion clause: '{exclusion}'."
        
        logging.info("Policy is compliant.")
        return True, "Compliant"
    except Exception as e:
        logging.error(f"Compliance check error: {e}")
        return False, f"Compliance check failed: {e}"