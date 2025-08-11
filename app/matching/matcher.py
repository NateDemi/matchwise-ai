# app/matching/matcher.py
import logging
import os
import pandas as pd
from datetime import datetime
from app.config import RESULTS_DIR, OPENAI_MODEL
from app.database.queries import (
    get_receipt_items_to_match, 
    get_receipt_items_by_docupanda_id,
    save_ai_match_results, 
    get_candidates_by_similarity,
    check_inventory_id
)
from app.services.openai.openai_service import match_with_openai

logger = logging.getLogger(__name__)


def match_receipt_item_with_inventory(receipt_item, receipt_upc=None):
    """
    Match a receipt item with inventory using AI
    
    Args:
        receipt_item (str): Receipt item to match
        receipt_upc (str, optional): Receipt item UPC
        
    Returns:
        dict: Match result
    """
    try:
        candidates = get_candidates_by_similarity(receipt_item, limit=10)

        if not candidates:
            return {
                "success": False,
                "error": f"No candidates found for receipt item: {receipt_item}",
                "receipt_item": receipt_item,
                "receipt_upc": receipt_upc
            }
            
        # Match with AI
        result = match_with_openai(receipt_item, candidates, model=OPENAI_MODEL)
        
        # Add receipt information
        result["receipt_item"] = receipt_item
        if receipt_upc:
            result["receipt_upc"] = receipt_upc
        
        # Validate inventory ID exists
        if result.get("inventory_id") and not check_inventory_id(result["inventory_id"]):
            logger.warning(f"Invalid inventory_id returned by AI: {result['inventory_id']}")
            return {
                "success": False,
                "error": f"Invalid inventory ID returned by AI: {result['inventory_id']}",
                "receipt_item": receipt_item,
                "receipt_upc": receipt_upc,
                "inventory_id": None,
                "inventory_name": None,
                "confidence": 0,
                "reasoning": "Invalid inventory ID returned by AI"
            }
        
        # Format inventory item for database
        if result.get("inventory_id"):
            result["inventory_item"] = {
                "id": result["inventory_id"],
                "name": result.get("inventory_name", "")
            }
        
        result["success"] = True
        return result
        
    except Exception as e:
        logger.error(f"Error matching receipt item '{receipt_item}': {e}")
        return {
            "success": False,
            "error": str(e),
            "receipt_item": receipt_item,
            "receipt_upc": receipt_upc,
            "inventory_id": None,
            "inventory_name": None,
            "confidence": 0,
            "reasoning": f"Processing error: {str(e)}"
        }


def process_item(item):
    """
    Process a receipt item and return result.
    
    Args:
        item (dict): Receipt item with keys: vendor_item_id, vendor_name, receipt_item_name, receipt_upc
        
    Returns:
        dict: Result dictionary
    """
    receipt_item_name = item.get('receipt_item_name', '')
    receipt_upc = item.get('receipt_upc', '')
    vendor_item_id = item.get('vendor_item_id')
    vendor_name = item.get('vendor_name', '')
    
    logger.info(f"Processing: {receipt_item_name} (UPC: {receipt_upc})")
    
    # Match the item
    result = match_receipt_item_with_inventory(receipt_item_name, receipt_upc)
    
    # Add vendor information
    result["vendor_item_id"] = vendor_item_id
    result["vendor_name"] = vendor_name
    
    return result


def process_receipt_items(docupanda_id: str, save_to_db: bool = True):
    """
    Process all receipt items for a single docupanda_id without batching.
    
    Args:
        docupanda_id (str): Document ID to process
        save_to_db (bool): Whether to save results to database
        
    Returns:
        list: List of result dictionaries
    """
    logger.info(f"🚀 Starting processing for docupanda_id: {docupanda_id}")
    
    # Get receipt items for this document
    receipt_items = get_receipt_items_by_docupanda_id(docupanda_id)
    
    if not receipt_items:
        logger.info(f"✅ No unmatched receipt items found for docupanda_id: {docupanda_id}")
        return []
    
    logger.info(f"📋 Found {len(receipt_items)} items to process")
    
    results = []
    for i, item in enumerate(receipt_items, 1):
        result = process_item(item)
        results.append(result)
        
        # Simple progress logging every 10 items
        if i % 10 == 0 or i == len(receipt_items):
            success_count = sum(1 for r in results if r.get("success", False))
            logger.info(f"📈 Progress: {i}/{len(receipt_items)} | ✅ {success_count} successful | ❌ {i - success_count} failed")
    
    # Save results to database if requested
    if save_to_db and results:
        try:
            saved_count = save_ai_match_results(results)
            logger.info(f"💾 Saved {saved_count} matches to database")
        except Exception as e:
            logger.error(f"❌ Failed to save results to database: {str(e)}")
    
    # Final summary
    successful = sum(1 for r in results if r.get("success", False))
    total = len(results)
    success_rate = (successful / total * 100) if total > 0 else 0
    
    logger.info(f"🏁 FINAL RESULTS: {total} total | ✅ {successful} successful | ❌ {total - successful} failed | Success rate: {success_rate:.1f}%")
    
    return results








if __name__ == "__main__":
    receipt_item = 'CORONA 4/6 /12 OZ BTL'
    
    candidates = get_candidates_by_similarity(receipt_item, limit=10)
    if candidates:
        result = match_with_openai(receipt_item, candidates, model=OPENAI_MODEL)
        print(f"OpenAI Result: {result}")
        
        match = match_receipt_item_with_inventory(receipt_item)
        print(f"Full Match: {match}")
    else:
        print("No candidates found")