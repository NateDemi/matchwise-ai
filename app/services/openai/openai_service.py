# app/services/openai_service.py
import json
import logging
from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.services.openai.prompts import get_prompt

# Initialize OpenAI client and logger
client = OpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)


def match_with_openai(receipt_item, candidates, model="gpt-3.5-turbo"):
    """
    Match a receipt item to the best inventory candidate using OpenAI.
    
    Args:
        receipt_item (str): Receipt item to match
        candidates (list): Inventory candidates
        model (str): OpenAI model to use
        
    Returns:
        dict: Matching result
    """
    logger.info(f"🔍 Searching for: '{receipt_item}'")
    logger.info(f"📦 Found {len(candidates)} candidates: {[c['name'] for c in candidates]}")
    
    # Validate inputs
    if not candidates:
        logger.warning(f"❌ No candidates found for '{receipt_item}'")
        return {
            "error": "No candidates found",
            "receipt_item": receipt_item,
            "inventory_id": None,
            "inventory_name": None,
            "confidence": 0,
            "reasoning": "No similar inventory items found",
            "success": False
        }
    
    inventory_context = ""
    for i, item in enumerate(candidates, 1):
        inventory_context += f"ID: {item['id']}, Name: \"{item['name']}\"\n"
    
    prompt = get_prompt(
        receipt_item=receipt_item,
        inventory_context=inventory_context
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        response_content = json.loads(response.choices[0].message.content)
        
        # Handle both list and single object responses
        if isinstance(response_content, list) and len(response_content) > 0:
            result = response_content[0]
        else:
            result = response_content
        
        matching_item = next((item for item in candidates if str(item["id"]) == str(result.get("inventory_id"))), None)
        
        if matching_item:
            inventory_id = str(matching_item["id"])
            result["inventory_id"] = inventory_id
            result["inventory_name"] = matching_item["name"]
            
            # Log successful match
            confidence = result.get("confidence", 0)
            logger.info(f"✅ MATCH FOUND: '{receipt_item}' → '{matching_item['name']}' (Confidence: {confidence}%)")
        else:
            result["inventory_id"] = None
            result["inventory_name"] = None
            
            logger.warning(f"❌ NO MATCH: '{receipt_item}' - OpenAI returned invalid ID or low confidence")
        
        result["receipt_item"] = receipt_item
        result["success"] = True
        
    except json.JSONDecodeError as e:
        error_message = f"JSON parsing error: {str(e)}"
        logger.error(f"❌ PARSE ERROR for '{receipt_item}': {error_message}")
        
        result = {
            "error": error_message,
            "receipt_item": receipt_item,
            "inventory_id": None,
            "inventory_name": None,
            "confidence": 0,
            "reasoning": f"Failed to parse OpenAI response: {error_message}",
            "success": False
        }
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"❌ API ERROR for '{receipt_item}': {error_message}")
        
        result = {
            "error": error_message,
            "receipt_item": receipt_item,
            "inventory_id": None,
            "inventory_name": None,
            "confidence": 0,
            "reasoning": f"Error: {error_message}",
            "success": False
        }
    
    return result


if __name__ == "__main__":
    from app.database.queries import get_candidates_by_similarity
    
    receipt_item = "TIDE 2X DOWNY APRL FRESH LIQ 6/42 OZ"
    candidates = get_candidates_by_similarity(receipt_item)
    
    if candidates:
        result = match_with_openai(receipt_item, candidates, model=OPENAI_MODEL)
        print(f"Match: {result.get('inventory_name', 'None')}")
        print(f"Confidence: {result.get('confidence', 0)}%")
    else:
        print("No candidates found")