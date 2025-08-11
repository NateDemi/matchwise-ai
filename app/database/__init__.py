"""
Database package for Receipt Inventory Matcher.
"""

from app.database.connection import get_connection, execute_query
from app.database.queries import (
    fetch_training_examples,
    get_receipt_items_to_match,
    get_full_inventory_items,
    get_embedded_inventory_ids,
    store_embeddings,
    get_upc_for_item,
    get_vendor_name_for_item
)

__all__ = [
    'get_connection',
    'execute_query',
    'fetch_training_examples',
    'get_receipt_items_to_match',
    'get_full_inventory_items',
    'get_embedded_inventory_ids',
    'store_embeddings',
    'get_upc_for_item',
    'get_vendor_name_for_item'
] 