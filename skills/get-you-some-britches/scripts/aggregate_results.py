#!/usr/bin/env python3
"""
Aggregate and rank pants search results from multiple retailers.

This script compiles product data from multiple retailers and ranks them
according to value optimization algorithms considering budget, size availability,
discount percentage, and quality indicators.
"""

import json
import sys
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class PantsProduct:
    """Standardized pants product data structure."""
    store_name: str
    product_name: str
    price_current: float
    url: str
    sizes_available: List[str]
    in_stock: bool
    price_original: float = None
    discount_percent: int = None
    fabric_composition: str = None
    fit_type: str = None
    color: str = None
    image_url: str = None

    def calculate_discount(self) -> int:
        """Calculate discount percentage if not already set."""
        if self.discount_percent is None and self.price_original:
            discount = ((self.price_original - self.price_current) / self.price_original) * 100
            self.discount_percent = round(discount)
        return self.discount_percent or 0

    def get_value_score(self, user_budget: float, premium_brands: List[str]) -> float:
        """
        Calculate value score for ranking.

        Higher score = better value proposition.

        Factors:
        - Budget compliance (critical)
        - Size availability (critical)
        - Discount percentage (higher is better)
        - Price competitiveness (lower price = higher score within budget)
        - Premium brand bonus
        """
        # Must be in budget and in stock
        if self.price_current > user_budget or not self.in_stock:
            return 0.0

        score = 100.0  # Base score

        # Discount bonus (up to 30 points for 50%+ discount)
        discount = self.calculate_discount()
        score += min(discount * 0.6, 30)

        # Price competitiveness (up to 30 points for being under budget)
        budget_utilization = self.price_current / user_budget
        if budget_utilization <= 0.5:  # 50% under budget
            score += 30
        elif budget_utilization <= 0.75:  # 25% under budget
            score += 20
        elif budget_utilization <= 0.9:  # 10% under budget
            score += 10

        # Premium brand bonus (up to 20 points)
        is_premium = any(brand.lower() in self.product_name.lower() or
                        brand.lower() in self.store_name.lower()
                        for brand in premium_brands)
        if is_premium:
            score += 20

        # Store credibility bonus
        store_bonus = {
            "Levi's": 15,
            "Nordstrom Rack": 12,
            "Bonobos": 12,
            "Old Navy": 8,
            "H&M": 5,
            "Marshall's": 10
        }
        score += store_bonus.get(self.store_name, 5)

        return score


def load_results(filepath: str = None) -> List[PantsProduct]:
    """Load product results from JSON file or stdin."""
    if filepath:
        with open(filepath, 'r') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    products = []
    for item in data.get('products', []):
        try:
            products.append(PantsProduct(**item))
        except TypeError as e:
            print(f"Warning: Skipping malformed product: {e}", file=sys.stderr)
            continue

    return products


def filter_and_rank(
    products: List[PantsProduct],
    user_budget: float,
    user_size: str = None,
    max_results: int = 15
) -> List[PantsProduct]:
    """
    Filter products by budget and size, then rank by value score.

    Args:
        products: List of product objects
        user_budget: Maximum budget in USD
        user_size: Required size (e.g., "32x30"). If None, include all.
        max_results: Maximum number of results to return

    Returns:
        Ranked list of products (best value first)
    """
    # Premium brands for scoring bonus
    premium_brands = [
        "Bonobos", "Levi's", "Calvin Klein", "DKNY", "Theory",
        "Hugo Boss", "J.Crew", "Brooks Brothers", "Banana Republic"
    ]

    # Filter by budget
    filtered = [p for p in products if p.price_current <= user_budget]

    # Filter by size if specified
    if user_size:
        filtered = [p for p in filtered if p.in_stock and user_size in p.sizes_available]

    # Calculate value scores
    for product in filtered:
        product.value_score = product.get_value_score(user_budget, premium_brands)

    # Sort by value score (descending)
    ranked = sorted(filtered, key=lambda p: p.value_score, reverse=True)

    return ranked[:max_results]


def format_output(products: List[PantsProduct], include_reasoning: bool = True) -> str:
    """
    Format ranked products for display.

    Args:
        products: Ranked list of products
        include_reasoning: Include "Why" recommendations

    Returns:
        Formatted string ready for display
    """
    if not products:
        return "No pants found matching your criteria.\n\nSuggestions:\n- Increase your budget\n- Try a different size\n- Check back later for new inventory"

    output = ["TOP PANTS ACQUISITION OPPORTUNITIES\n"]

    for i, product in enumerate(products, 1):
        # Header: Rank and product name
        output.append(f"{i}. {product.store_name} - {product.product_name}")

        # Price info with discount if applicable
        if product.price_original and product.calculate_discount() > 0:
            output.append(
                f"   ${product.price_current:.2f} "
                f"(Originally ${product.price_original:.2f}, "
                f"{product.calculate_discount()}% off)"
            )
        else:
            output.append(f"   ${product.price_current:.2f}")

        # Stock status
        if product.in_stock:
            output.append(f"   ✓ IN STOCK")
        else:
            output.append(f"   ✗ OUT OF STOCK")

        # Fabric info if available
        if product.fabric_composition:
            output.append(f"   Fabric: {product.fabric_composition}")

        # Fit info if available
        if product.fit_type:
            output.append(f"   Fit: {product.fit_type}")

        # URL
        output.append(f"   → {product.url}")

        # Reasoning (why this product)
        if include_reasoning:
            reason = generate_recommendation_reason(product, i)
            output.append(f"   Why: {reason}")

        output.append("")  # Blank line between products

    return "\n".join(output)


def generate_recommendation_reason(product: PantsProduct, rank: int) -> str:
    """Generate contextual recommendation reason for a product."""
    reasons = []

    discount = product.calculate_discount()

    if rank == 1:
        if discount >= 30:
            reasons.append(f"Outstanding {discount}% discount")
        if product.price_current < 40:
            reasons.append("Exceptional value")
        if any(brand in product.product_name.lower() for brand in ["bonobos", "levi's"]):
            reasons.append("Premium brand at competitive price")
        if not reasons:
            reasons.append("Best overall value in search results")

    elif rank <= 3:
        if discount >= 25:
            reasons.append(f"Strong {discount}% discount")
        if "stretch" in product.product_name.lower() or "flex" in product.product_name.lower():
            reasons.append("Comfort features")
        if product.store_name == "Nordstrom Rack":
            reasons.append("Designer quality at outlet pricing")

    else:
        if discount > 0:
            reasons.append(f"{discount}% off")
        if product.store_name == "Levi's":
            reasons.append("Premium denim quality")
        if product.price_current < 35:
            reasons.append("Budget-friendly option")

    return "; ".join(reasons) if reasons else "Solid option meeting your criteria"


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Aggregate and rank pants search results"
    )
    parser.add_argument(
        '--input', '-i',
        help='Input JSON file (default: stdin)',
        default=None
    )
    parser.add_argument(
        '--budget', '-b',
        type=float,
        required=True,
        help='Maximum budget in USD'
    )
    parser.add_argument(
        '--size', '-s',
        help='Required size (e.g., 32x30)',
        default=None
    )
    parser.add_argument(
        '--max-results', '-m',
        type=int,
        default=15,
        help='Maximum results to return (default: 15)'
    )
    parser.add_argument(
        '--json-output', '-j',
        action='store_true',
        help='Output as JSON instead of formatted text'
    )

    args = parser.parse_args()

    # Load products
    try:
        products = load_results(args.input)
    except Exception as e:
        print(f"Error loading results: {e}", file=sys.stderr)
        sys.exit(1)

    # Filter and rank
    ranked = filter_and_rank(
        products,
        args.budget,
        args.size,
        args.max_results
    )

    # Output
    if args.json_output:
        # JSON output for programmatic use
        output = [asdict(p) for p in ranked]
        print(json.dumps(output, indent=2))
    else:
        # Formatted text output for user display
        print(format_output(ranked, include_reasoning=True))


if __name__ == '__main__':
    main()
