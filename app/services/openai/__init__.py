"""
External service integrations for Receipt Inventory Matcher.
"""

from app.services.openai.openai_service import match_with_openai
from app.services.openai.prompts import get_prompt

__all__ = [
    'match_with_openai',
    'get_prompt'
] 