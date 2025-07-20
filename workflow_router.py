import logging
import json

# Load configuration
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    CONFIDENCE_THRESHOLD = config['confidence_threshold']
    ROUTING_RULES = config['routing_rules']
except FileNotFoundError:
    logging.error("config.json not found.")
    raise FileNotFoundError("config.json not found.")
except json.JSONDecodeError:
    logging.error("Invalid config.json format.")
    raise ValueError("Invalid config.json format.")

def intelligent_route(claim_data: dict):
    """
    Determines the optimal workflow path for the claim based on configurable rules.
    
    Args:
        claim_data (dict): Data containing claim details (entities, type, confidence, etc.).
        
    Returns:
        dict: Routing decision and reason.
    """
    logging.info("Determining optimal route for the claim...")
    
    try:
        # Validate claim_data
        if not isinstance(claim_data, dict):
            logging.error("Invalid claim_data: Must be a dictionary.")
            return {"decision": "Flag for Review", "reason": "Invalid claim data format."}

        # Rule 1: Low confidence score
        if claim_data.get("confidence", 0.0) < CONFIDENCE_THRESHOLD:
            return {"decision": "Flag for Manual Review", "reason": f"Low classification confidence ({claim_data.get('confidence', 0.0):.2f})"}
        
        # Rule 2: Non-compliant claim
        if not claim_data.get("is_compliant", False):
            return {"decision": "Auto-Deny", "reason": f"Non-compliant: {claim_data.get('compliance_reason', 'Unknown')}"}
        
        # Rule 3: High priority or high value claims
        if claim_data.get("priority") == "High" or (claim_data.get("value") and claim_data["value"] > ROUTING_RULES["high_value_threshold"]):
            return {"decision": "Route to Senior Adjuster", "reason": "High priority or high value claim"}
        
        # Rule 4: Straight-Through Processing (STP) for simple, compliant claims
        if claim_data.get("value") and claim_data["value"] <= ROUTING_RULES["stp_threshold"]:
            return {"decision": "Route to Straight-Through Processing (STP)", "reason": "Low-value, compliant claim"}
        
        # Rule 5: Standard claims to the general queue
        return {"decision": "Route to General Claims Queue", "reason": "Standard claim"}
    except Exception as e:
        logging.error(f"Routing error: {e}")
        return {"decision": "Flag for Manual Review", "reason": f"Routing error: {e}"}