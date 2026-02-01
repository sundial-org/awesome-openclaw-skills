"""
Finance Tracker — Category Definitions
Professional expense categorization with smart keyword detection
"""

CATEGORIES = {
    # Food & Dining
    "food": {
        "emoji": "🍔",
        "name": "Food & Dining",
        "keywords": [
            "food", "lunch", "dinner", "breakfast", "meal", "restaurant", 
            "cafe", "coffee", "snack", "grocery", "groceries", "supermarket",
            "eat", "eating", "pizza", "burger", "sushi", "takeout", "delivery",
            "ovqat", "tushlik", "nonushta", "kechki", "choy", "restoran"
        ]
    },
    
    # Transportation
    "transport": {
        "emoji": "🚗",
        "name": "Transportation",
        "keywords": [
            "taxi", "uber", "yandex", "bus", "metro", "subway", "train",
            "transport", "fuel", "gas", "petrol", "benzin", "parking",
            "fare", "ride", "driving", "car", "avtobuz", "taksi", "marshrutka"
        ]
    },
    
    # Shopping & Clothes
    "shopping": {
        "emoji": "🛍️",
        "name": "Shopping",
        "keywords": [
            "clothes", "clothing", "shirt", "pants", "jeans", "shoes", 
            "jacket", "coat", "dress", "shopping", "mall", "store",
            "kiyim", "oyoq kiyim", "ko'ylak", "shim", "kurtka"
        ]
    },
    
    # Technology
    "tech": {
        "emoji": "📱",
        "name": "Technology",
        "keywords": [
            "phone", "laptop", "computer", "headphones", "earbuds", "cable",
            "charger", "tech", "electronics", "gadget", "software", "app",
            "subscription", "iphone", "android", "macbook", "tablet", "ipad"
        ]
    },
    
    # Entertainment
    "entertainment": {
        "emoji": "🎮",
        "name": "Entertainment",
        "keywords": [
            "movie", "movies", "cinema", "game", "games", "gaming", "concert",
            "netflix", "spotify", "youtube", "premium", "fun", "party",
            "club", "bar", "entertainment", "stream", "kino", "o'yin"
        ]
    },
    
    # Education
    "education": {
        "emoji": "📚",
        "name": "Education",
        "keywords": [
            "book", "books", "course", "courses", "school", "university",
            "education", "learning", "class", "tutor", "tutoring", "lesson",
            "study", "studying", "exam", "test", "kitob", "darslik", "kurs",
            "o'qish", "ta'lim", "maktab", "universitet"
        ]
    },
    
    # Health & Medical
    "health": {
        "emoji": "💊",
        "name": "Health & Medical",
        "keywords": [
            "medicine", "pharmacy", "doctor", "hospital", "clinic", "health",
            "medical", "prescription", "pills", "vitamins", "gym", "fitness",
            "workout", "dori", "apteka", "shifoxona", "doktor", "vrach"
        ]
    },
    
    # Home & Utilities
    "home": {
        "emoji": "🏠",
        "name": "Home & Utilities",
        "keywords": [
            "rent", "utility", "utilities", "electricity", "water", "gas",
            "internet", "wifi", "furniture", "home", "house", "apartment",
            "cleaning", "repair", "maintenance", "uy", "kvartira", "ijara",
            "kommunal", "elektr", "suv"
        ]
    },
    
    # Personal Care
    "personal": {
        "emoji": "💇",
        "name": "Personal Care",
        "keywords": [
            "haircut", "barber", "salon", "spa", "massage", "grooming",
            "cosmetics", "makeup", "skincare", "personal", "beauty",
            "sartarosh", "soch", "salon"
        ]
    },
    
    # Gifts & Donations
    "gifts": {
        "emoji": "🎁",
        "name": "Gifts & Donations",
        "keywords": [
            "gift", "gifts", "present", "birthday", "wedding", "donation",
            "charity", "tip", "tips", "sovg'a", "tug'ilgan kun", "to'y"
        ]
    },
    
    # Subscriptions
    "subscriptions": {
        "emoji": "🔄",
        "name": "Subscriptions",
        "keywords": [
            "subscription", "monthly", "annual", "yearly", "membership",
            "premium", "pro", "plus", "obuna"
        ]
    },
    
    # Communication
    "communication": {
        "emoji": "📞",
        "name": "Communication",
        "keywords": [
            "phone bill", "mobile", "sim", "data", "minutes", "sms",
            "call", "calling", "telefon", "aloqa", "mobil"
        ]
    },
    
    # Travel
    "travel": {
        "emoji": "✈️",
        "name": "Travel",
        "keywords": [
            "travel", "trip", "flight", "hotel", "hostel", "airbnb",
            "vacation", "holiday", "tourism", "tourist", "sayohat",
            "mehmonxona", "parvoz", "samolyot"
        ]
    },
    
    # Finance & Banking
    "finance": {
        "emoji": "🏦",
        "name": "Finance & Banking",
        "keywords": [
            "bank", "fee", "fees", "transfer", "atm", "commission",
            "interest", "loan", "credit", "debit", "bank xizmati"
        ]
    },
    
    # Other
    "other": {
        "emoji": "❓",
        "name": "Other",
        "keywords": []  # Default category
    }
}


def detect_category(text: str) -> str:
    """
    Detect category from description text.
    Returns category key (e.g., 'food', 'transport').
    Falls back to 'other' if no match.
    """
    text_lower = text.lower()
    
    # Check each category's keywords
    for category, data in CATEGORIES.items():
        if category == "other":
            continue
        for keyword in data["keywords"]:
            if keyword in text_lower:
                return category
    
    return "other"


def get_emoji(category: str) -> str:
    """Get emoji for a category."""
    return CATEGORIES.get(category, CATEGORIES["other"])["emoji"]


def get_name(category: str) -> str:
    """Get display name for a category."""
    return CATEGORIES.get(category, CATEGORIES["other"])["name"]


def list_categories() -> str:
    """Return formatted list of all categories."""
    lines = ["📋 Available Categories:", ""]
    for key, data in CATEGORIES.items():
        lines.append(f"  {data['emoji']} {data['name']} ({key})")
    return "\n".join(lines)


if __name__ == "__main__":
    # Test
    print(list_categories())
    print()
    print(f"'lunch at cafe' -> {detect_category('lunch at cafe')}")
    print(f"'taxi home' -> {detect_category('taxi home')}")
    print(f"'haircut' -> {detect_category('haircut')}")
    print(f"'random stuff' -> {detect_category('random stuff')}")
