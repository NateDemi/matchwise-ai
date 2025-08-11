"""
Core matching functionality for Receipt Inventory Matcher.
"""

from .matcher import (
    match_receipt_item_with_inventory,
    process_item,
    process_receipt_items
)

__all__ = [
    'match_receipt_item_with_inventory',
    'process_item',
    'process_receipt_items'
] 