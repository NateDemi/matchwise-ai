# app/database/queries.py
from app.database.connection import execute_query
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def get_candidates_by_similarity(receipt_item, limit=4):
    escaped_item = receipt_item.replace("'", "''")
    
    query = f"""
            SELECT 
            id,
            name
            FROM (
            SELECT 
                ii.id,
                ii.name,
                'name' AS field_matched,
                (store_data.get_similarity_scores('{escaped_item}', ii.name)).trigram_score AS trigram_score
            FROM store_data.inventory_items ii
            WHERE ii.name IS NOT NULL AND TRIM(ii.name) != ''
            
            UNION ALL
            
            SELECT 
                ii.id,
                ii.alternate_name AS name,
                'alternate_name' AS field_matched,
                (store_data.get_similarity_scores('{escaped_item}', ii.alternate_name)).trigram_score AS trigram_score
            FROM store_data.inventory_items ii
            WHERE ii.alternate_name IS NOT NULL AND TRIM(ii.alternate_name) != ''
            ) AS similarity_scores
            ORDER BY trigram_score DESC
            LIMIT {limit};
    """
    
    print(f"Searching for: '{receipt_item}' with limit: {limit}")
    result = execute_query(query)
    print(f"Result: {result}")
    return result

def fetch_training_examples(limit=50):
    """
    Fetch good examples for training
    
    Args:
        limit (int): Maximum number of examples to fetch
        
    Returns:
        list: Training examples
    """
    query = """
    SELECT 
        vi.receipt_item_name as receipt_item, 
        it.id as inventory_id,
        it.name as inventory_name, 
        it.alternate_name
    FROM store_data.vendor_items vi
    INNER JOIN store_data.item_mapping im ON im.receipt_upc = vi.receipt_upc
    INNER JOIN store_data.inventory_items it ON it.id = im.inventory_item_id
    ORDER BY RANDOM()
    LIMIT %s
    """
    
    return execute_query(query, (limit,))


def get_receipt_items_to_match():
    """
    Get receipt items that need to be matched
    
    Returns:
        list: Receipt items to match that don't have an existing mapping
    """
    query = """
    SELECT 
        vi.id as vendor_item_id,
        vd.vendor_name,
        vi.receipt_item_name,
        vi.receipt_upc
    FROM 
        store_data.vendor_items vi
    LEFT JOIN 
        store_data.vendor_details vd ON vi.vendor_id = vd.id
    LEFT JOIN 
        store_data.item_mapping im ON vi.id = im.vendor_item_id
    WHERE
        im.vendor_item_id IS NULL
    """
    
    return execute_query(query)


def get_receipt_items_by_docupanda_id(docupanda_id: str):
    """
    Get receipt items that need to be matched for a specific docupanda_id
    
    Args:
        docupanda_id (str): The docupanda_id from the webhook payload
        
    Returns:
        list: Receipt items to match for the specific docupanda_id
    """
    query = """
    SELECT 
        vi.id as vendor_item_id,
        vd.vendor_name,
        vi.receipt_item_name,
        vi.receipt_upc
    FROM 
        store_data.vendor_items vi
    LEFT JOIN 
        store_data.vendor_details vd ON vi.vendor_id = vd.id
    LEFT JOIN 
        store_data.item_mapping im ON vi.id = im.vendor_item_id
    LEFT JOIN 
        store_data.vendor_purchases_line_items vpli ON vpli.upc = vi.receipt_upc
    WHERE
        im.vendor_item_id IS NULL
        AND vpli.docupanda_id = %s
    """
    
    return execute_query(query, (docupanda_id,))

# EMBEDDING FUNCTIONS
def get_full_inventory_items():
    """
    Get all inventory items 
    """
    query = """
    SELECT id, name, alternate_name
    FROM store_data.inventory_items
    """
    return execute_query(query)

def get_embedded_inventory_ids():
    query = "SELECT inventory_item_id FROM store_data.inventory_item_embeddings"
    rows = execute_query(query)
    return {row["inventory_item_id"] for row in rows}

def store_embeddings(rows):
    insert_query = """
        INSERT INTO store_data.inventory_item_embeddings (
            inventory_item_id,
            item_name,
            item_description,
            embedding_vector,
            embedded_at,
            last_updated,
            model_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    for idx, row in enumerate(rows):
        if len(row) != 7:
            logger.error(f"❌ Row {idx} has wrong number of elements: {row}")
            raise ValueError("Each row must have 7 values for the insert")

    try:
        execute_query(insert_query, rows)
        logger.info(f"📦 Inserted {len(rows)} new embeddings into DB.")
    except Exception as e:
        logger.error(f"Failed to insert into DB: {e}")

def get_upc_for_item(item: str) -> str:
    """Get UPC for a receipt item"""
    try:
        # Query the database to find UPC
        sql_query = f"""
        SELECT receipt_upc
        FROM store_data.vendor_items
        WHERE receipt_item_name ILIKE '%{item}%' 
        LIMIT 1
        """
        result = execute_query(sql_query, fetch_all=False)
        return result.get('receipt_upc', '') if result else ''
    except Exception as e:
        logger.warning(f"Could not get UPC for '{item}': {e}")
        return ""
        
def get_vendor_name_for_item(receipt_item):
    """Helper: Extract vendor name from database using receipt item """
    sql_query = f"""
    SELECT vendor_name
    FROM store_data.vendor_items
    WHERE receipt_item_name ILIKE '%{receipt_item}%' 
    LIMIT 1
    """
    vendor_name = execute_query(sql_query)[0]['vendor_name']

    return vendor_name or ""

def get_inventory_item_embeddings(query_embedding, limit=10, similarity_threshold=0.7):
    """
    Search inventory items based on embedding vector similarity
    
    Args:
        query_embedding (list): The embedding vector to search with
        limit (int): Maximum number of results to return
        similarity_threshold (float): Minimum similarity score (0-1) for results
        
    Returns:
        list: Matching inventory items with similarity scores
    """
    try:
        query = """
        SELECT 
            i.id,
            i.name,
            i.alternate_name,
            i.sku,
            i.code,
            i.price,
            i.price_type,
            i.price_without_vat,
            i.cost,
            i.stock_count,
            i.unit_name,
            i.available,
            i.auto_manage,
            i.default_tax_rates,
            i.is_revenue,
            i.hidden,
            i.deleted,
            i.category,
            i.modified_time,
            e.item_name,
            e.item_description,
            1 - (e.embedding_vector <=> CAST(%s AS vector)) AS similarity_score
        FROM 
            store_data.inventory_item_embeddings e
        JOIN 
            store_data.inventory_items i ON e.inventory_item_id = i.id
        WHERE 
            1 - (e.embedding_vector <=> CAST(%s AS vector)) >= %s
        ORDER BY 
            similarity_score DESC
        LIMIT %s
        """
        
        results = execute_query(query, (query_embedding, query_embedding, similarity_threshold, limit))
        return results or []  # Return empty list instead of None
    except Exception as e:
        logger.error(f"Failed to search inventory: {e}")
        return []  # Return empty list on error


def save_ai_match_results(match_results: List[Dict]) -> int:
    """Save AI match results to the database and return count of saved items."""
    saved_count = 0
    
    try:
        for result in match_results:
            if not result.get('inventory_item') or result.get('confidence', 0) < 70:
                logger.debug(f"Skipping result: confidence {result.get('confidence', 0)} < 70 or no inventory_item")
                continue

            receipt_item_name = result.get('receipt_item', '')
            receipt_upc = result.get('receipt_upc', '')
            inventory_item_id = result.get('inventory_id', '')
            vendor_item_id = result.get('vendor_item_id')

            if not vendor_item_id:
                logger.warning(f"No vendor_item_id for {receipt_item_name} - skipping database save")
                continue

            # Check if mapping already exists
            check_query = """
                SELECT * 
                FROM store_data.item_mapping 
                WHERE vendor_item_id = %s AND inventory_item_id = %s
            """
            existing = execute_query(check_query, (vendor_item_id, inventory_item_id), fetch_all=False)

            if existing:
                # Update existing mapping
                update_query = """
                    UPDATE store_data.item_mapping 
                    SET match_type = 'AI_MATCH', mapped_at = NOW()
                    WHERE vendor_item_id = %s AND inventory_item_id = %s
                """
                execute_query(update_query, (vendor_item_id, inventory_item_id))
                logger.debug(f"Updated existing mapping for {receipt_item_name}")
            else:
                # Insert new mapping
                insert_query = """
                    INSERT INTO store_data.item_mapping 
                    (vendor_item_id, receipt_upc, inventory_item_id, match_type, mapped_at)
                    VALUES (%s, %s, %s, 'AI_MATCH', NOW())
                """
                execute_query(insert_query, (vendor_item_id, receipt_upc, inventory_item_id))
                logger.debug(f"Inserted new mapping for {receipt_item_name}")
            
            saved_count += 1

    except Exception as e:
        logger.error(f"Error saving AI match results: {str(e)}")
        raise
    
    return saved_count

def check_inventory_id(inventory_id: str) -> bool:
    """
    Check if an inventory ID exists in the inventory_items table.
    
    Args:
        inventory_id (str): The inventory ID to check
        
    Returns:
        bool: True if the ID exists, False otherwise
    """
    query = """
        SELECT EXISTS(
            SELECT 1 
            FROM store_data.inventory_items 
            WHERE id = %s
        ) as exists
    """
    result = execute_query(query, (inventory_id,), fetch_all=False)
    return result.get('exists', False) if result else False

if __name__ == "__main__":
  

    # inventory_items = get_full_inventory_items()
    # print(inventory_items)

    candidates = get_candidates_by_similarity("TWIZZLERS STRAWBERRY TWISTS 18/2.5OZ", limit=10)
    print(candidates)


