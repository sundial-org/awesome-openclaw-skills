"""
Finance Tracker — Natural Language Parser
Parses expense descriptions from natural language
"""

import re
from typing import Tuple, Optional


def parse_amount(text: str) -> Optional[int]:
    """
    Extract amount from text.
    Handles formats like: 50000, 50k, 50K, 50 000, 50,000
    
    Returns:
        Amount as integer, or None if not found
    """
    # Remove commas and spaces in numbers
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    text = text.replace(',', '')
    
    # Look for number with optional k/K suffix
    patterns = [
        r'(\d+)\s*[kK]',           # 50k, 50K, 50 k
        r'(\d+(?:\.\d+)?)\s*[kK]', # 50.5k
        r'(\d+)',                   # plain number
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            num = float(match.group(1))
            
            # Check if 'k' suffix (case insensitive)
            full_match = text[match.start():match.end()].lower()
            if 'k' in full_match:
                num *= 1000
            
            return int(num)
    
    return None


def parse_description(text: str, amount: Optional[int] = None) -> str:
    """
    Extract description from text by removing amount and common words.
    
    Returns:
        Cleaned description string
    """
    # Remove the amount part
    text = re.sub(r'\d+\s*[kK]?', '', text)
    
    # Remove common filler words
    fillers = [
        r'\bspent\b', r'\bon\b', r'\bfor\b', r'\bbought\b', 
        r'\bpaid\b', r'\bgot\b', r'\bthe\b', r'\ba\b', r'\ban\b',
        r'\bsome\b', r'\bmy\b', r'\bjust\b', r'\btoday\b'
    ]
    
    for filler in fillers:
        text = re.sub(filler, '', text, flags=re.IGNORECASE)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove leading/trailing punctuation
    text = text.strip('.,!?;:')
    
    return text if text else "expense"


def parse_expense(text: str) -> Tuple[Optional[int], str]:
    """
    Parse a natural language expense statement.
    
    Examples:
        "spent 50k on lunch" -> (50000, "lunch")
        "taxi 15000" -> (15000, "taxi")
        "bought coffee for 5k" -> (5000, "coffee")
        "haircut 30000 sum" -> (30000, "haircut")
    
    Returns:
        Tuple of (amount, description)
    """
    # Get amount first
    amount = parse_amount(text)
    
    # Get description
    description = parse_description(text, amount)
    
    return amount, description


def format_confirmation(amount: int, category: str, description: str, currency: str = "UZS") -> str:
    """Format a confirmation message for an added expense."""
    try:
        from .categories import get_emoji
    except ImportError:
        from categories import get_emoji
    
    emoji = get_emoji(category)
    return f"✅ Logged: {emoji} {amount:,} {currency} — {description} ({category})"


def format_error(error_type: str, hint: str = "") -> str:
    """Format an error message."""
    errors = {
        "no_amount": "❌ Couldn't find an amount. Try: finance add 50000 \"lunch\"",
        "invalid_amount": "❌ Invalid amount. Use a positive number.",
        "no_description": "❌ Missing description. What was this expense for?",
        "parse_failed": "❌ Couldn't parse that. Try: finance add 50000 \"description\"",
    }
    
    msg = errors.get(error_type, f"❌ Error: {error_type}")
    if hint:
        msg += f"\n💡 {hint}"
    
    return msg


# Test
if __name__ == "__main__":
    test_cases = [
        "spent 50k on lunch",
        "taxi 15000",
        "bought coffee for 5k",
        "haircut 30000",
        "50000 groceries",
        "paid 100k for new shoes",
        "netflix subscription 50000",
        "30 000 for dinner",
    ]
    
    print("Testing parser:\n")
    for text in test_cases:
        amount, desc = parse_expense(text)
        print(f"  '{text}'")
        print(f"    -> Amount: {amount:,}, Description: '{desc}'")
        print()
