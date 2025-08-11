# prompt = f"""Your task is to match a receipt item to the most similar inventory item.

# EXAMPLES OF CORRECT MATCHES:
# {example_context}

# AVAILABLE INVENTORY ITEMS:
# {inventory_context}

# RECEIPT ITEM TO MATCH: "{receipt_item}"

# INSTRUCTIONS:
# 1. Find the inventory item that best matches the receipt item
# 2. Pay attention to brand names, product types, sizes, and quantities
# 3. Consider both the main name and alternate name when matching
# 4. Return the inventory ID of the best matching item

# Respond with a JSON object containing:
# - inventory_id: The ID string of the best matching inventory item (or null if no good match)
# - confidence: A score from 0-100 indicating your confidence in the match
# - reasoning: Brief explanation for why this is a match

# JSON Response:"""


# # Create prompt
# prompt_2 = f"""Your task is to match a receipt item to the most similar inventory item.

# EXAMPLES OF CORRECT MATCHES:
# {example_context}

# EXAMPLE OF NO MATCH:
# Receipt Item: "ZYN NICOTINE POUCH 6MG PEPPERMINT"
# Inventory Name: N/A
# Alternate Name: N/A
# Inventory ID: null

# AVAILABLE INVENTORY ITEMS (with category):
# {inventory_context}

# RECEIPT ITEM TO MATCH: "{receipt_item}"

# INSTRUCTIONS:
# 1. Match the receipt item to an inventory item with the most similar brand, product type, size, and quantity.
# 2. Only consider items in the same general category (e.g., food, beverage, tobacco, household). Do not match tobacco to beverages or snacks.
# 3. Use both the inventory name and alternate name when comparing.
# 4. If there is no appropriate match, return null.

# Respond with a JSON object containing:
# - inventory_id: The ID string of the best matching inventory item (or null if no good match)
# - confidence: A score from 0–100 indicating your confidence in the match
# - reasoning: Brief explanation for why this is a match (or why no match was found)

# JSON Response:"""

def get_prompt(receipt_item, inventory_context):
    prompt = f"""
You are a product-matching assistant.

Your task is to identify the most likely inventory item that matches a given receipt item description. Receipt item names may include abbreviations, misspellings, product sizes, quantities, or variants (e.g., flavor, scent, oz, count).

### STRUCTURE EXAMPLES (for context only):
1. "EGGO CHOCO BUN 6 PACK" → item: EGGO CHOCO BUN | size: 6 PACK  
2. "CLOROX DISINFECTING BLEACH 6/43 oz" → item: CLOROX DISINFECTING BLEACH | size: 43 oz  
3. "TRIDENT ISLAND BERRY LIME12CT" → brand: TRIDENT | variant: ISLAND BERRY LIME | size: 12CT  
4. "ZYN 6MGS SMOOTH 5 ROLL" → brand: ZYN | variant: SMOOTH | size: 5 ROLL  
5. "GATORADE FT PNCH 24/20OZ" → brand: GATORADE | variant: FRUIT PUNCH | size: 20 oz
6. "Canada Dry Ginger Ale Soda - 20 Fl Oz Bottle" → brand: CANADA DRY | variant: GINGER ALE | size: 20 oz

> Receipt item names may use inconsistent formatting, abbreviations, or shorthand.

### COMMON ABBREVIATIONS:
- FT, FRT = Fruit
- OZ, FZ, FLZ, Fl OZ= Ounce, OZ
- PK, PCK = Pack
- CT, CNT = Count
- BTL = Bottle
- CAN = Can or 12oz 
- BX = Box
- L = Liter
- 2/12PK = 2 packs of 12
- 2/16PK = 2 packs of 16
- geto = Gatorade
- H&H  = Half & Half
- 3/8-16.9OZ = 3 packs of 8 bottles, each 16.9 ounces
- AW CRM = A&W Cream Soda
- BF FLVR = Beef Flavor
- MEX = Mexican

### INVENTORY STRUCTURE:
You are comparing against a list of inventory items from table `store_data.inventory_items`. Each item has:
- `id` (text)
- `name` (text)
- `alternate_name` (text)

### INPUTS:
RECEIPT ITEM TO MATCH: "{receipt_item}"  
AVAILABLE INVENTORY ITEMS:
{inventory_context}

### MATCHING RULES:
1. Return **only the single most likely** inventory item match.
2. Prioritize brand, product name, and **variant** (e.g., flavor, type, scent, style).
3. Size should be matched **when present**, but it is not mandatory.
4. Variants must be respected. A product with a different variant (e.g., TRIDENT Watermelon vs. TRIDENT Island Berry Lime) is **not a valid match**.
5. Use both `name` and `alternate_name` fields when comparing.
6. Only consider items from the same general category (e.g., food, beverage, tobacco, household).
7. If **no item reasonably matches**, return null.

### OUTPUT FORMAT:
Respond with a single JSON object in a list format:
- `inventory_id`: the ID of the best matching inventory item (must be one of the provided candidate IDs), or null if no match.
- `confidence`: 0–100 (estimated likelihood of correct match)  
- `reasoning`: one sentence explaining the rationale for the match (or why no match was found)

### RESPONSE EXAMPLE:
[
  {{
    "inventory_id": '1HFNV3GP9BX1T',
    "confidence": 91,
    "reasoning": "Matched brand 'ZYN', variant 'Smooth', and size '5 roll'. No other ZYN variant matched better."
  }}
]
"""
    return prompt