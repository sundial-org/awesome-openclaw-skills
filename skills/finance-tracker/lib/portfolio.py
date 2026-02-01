"""
Finance Tracker — Portfolio & Net Worth
Track assets, income, and overall financial position
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class Portfolio:
    """Track assets, income, and net worth."""
    
    ASSET_TYPES = {
        "cash": {"emoji": "💵", "name": "Cash & Bank"},
        "stocks": {"emoji": "📈", "name": "Stocks"},
        "crypto": {"emoji": "🪙", "name": "Cryptocurrency"},
        "realestate": {"emoji": "🏠", "name": "Real Estate"},
        "savings": {"emoji": "🏦", "name": "Savings"},
        "investments": {"emoji": "💼", "name": "Investments"},
        "other": {"emoji": "📦", "name": "Other Assets"}
    }
    
    INCOME_TYPES = {
        "salary": {"emoji": "💼", "name": "Salary"},
        "freelance": {"emoji": "💻", "name": "Freelance"},
        "business": {"emoji": "🏪", "name": "Business"},
        "investment": {"emoji": "📈", "name": "Investment Returns"},
        "gift": {"emoji": "🎁", "name": "Gifts"},
        "other": {"emoji": "💰", "name": "Other Income"}
    }
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / ".finance-tracker"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.portfolio_file = self.data_dir / "portfolio.json"
        self.income_file = self.data_dir / "income.json"
        
        self._init_files()
    
    def _init_files(self):
        if not self.portfolio_file.exists():
            self._save_portfolio({
                "currency": "UZS",
                "assets": [],
                "updated_at": datetime.now().isoformat()
            })
        
        if not self.income_file.exists():
            self._save_income({
                "currency": "UZS",
                "income": [],
                "created_at": datetime.now().isoformat()
            })
    
    def _load_portfolio(self) -> Dict[str, Any]:
        try:
            with open(self.portfolio_file) as f:
                return json.load(f)
        except:
            return {"currency": "UZS", "assets": []}
    
    def _save_portfolio(self, data: Dict[str, Any]):
        data["updated_at"] = datetime.now().isoformat()
        with open(self.portfolio_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_income(self) -> Dict[str, Any]:
        try:
            with open(self.income_file) as f:
                return json.load(f)
        except:
            return {"currency": "UZS", "income": []}
    
    def _save_income(self, data: Dict[str, Any]):
        with open(self.income_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ===== ASSETS =====
    
    def add_asset(self, name: str, value: int, asset_type: str = "other") -> Dict[str, Any]:
        """Add or update an asset."""
        data = self._load_portfolio()
        
        # Check if asset exists
        existing = next((a for a in data["assets"] if a["name"].lower() == name.lower()), None)
        
        if existing:
            existing["value"] = value
            existing["updated_at"] = datetime.now().isoformat()
            asset = existing
        else:
            asset = {
                "id": len(data["assets"]) + 1,
                "name": name,
                "value": value,
                "type": asset_type,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            data["assets"].append(asset)
        
        self._save_portfolio(data)
        return asset
    
    def remove_asset(self, name: str) -> bool:
        """Remove an asset."""
        data = self._load_portfolio()
        original_len = len(data["assets"])
        data["assets"] = [a for a in data["assets"] if a["name"].lower() != name.lower()]
        
        if len(data["assets"]) < original_len:
            self._save_portfolio(data)
            return True
        return False
    
    def get_assets(self) -> List[Dict[str, Any]]:
        """Get all assets."""
        data = self._load_portfolio()
        return data["assets"]
    
    def get_net_worth(self) -> int:
        """Calculate total net worth."""
        assets = self.get_assets()
        return sum(a["value"] for a in assets)
    
    def get_portfolio_report(self) -> str:
        """Generate portfolio report."""
        assets = self.get_assets()
        data = self._load_portfolio()
        currency = data.get("currency", "UZS")
        
        if not assets:
            return "📊 Portfolio\n━━━━━━━━━━━━━━━━━━━━━\n\n📭 No assets tracked yet.\n\nAdd one: finance asset add \"Bank Account\" 5000000 cash"
        
        total = self.get_net_worth()
        
        lines = [
            "📊 Portfolio & Net Worth",
            "━━━━━━━━━━━━━━━━━━━━━",
            f"💎 Net Worth: {total:,} {currency}",
            ""
        ]
        
        # Group by type
        by_type = {}
        for asset in assets:
            t = asset.get("type", "other")
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(asset)
        
        for asset_type, items in by_type.items():
            type_info = self.ASSET_TYPES.get(asset_type, self.ASSET_TYPES["other"])
            type_total = sum(a["value"] for a in items)
            pct = (type_total / total * 100) if total > 0 else 0
            
            lines.append(f"{type_info['emoji']} {type_info['name']}: {type_total:,} {currency} ({pct:.1f}%)")
            for item in items:
                lines.append(f"   • {item['name']}: {item['value']:,}")
        
        return "\n".join(lines)
    
    # ===== INCOME =====
    
    def add_income(self, amount: int, description: str, income_type: str = "other") -> Dict[str, Any]:
        """Log income."""
        data = self._load_income()
        
        income = {
            "id": len(data["income"]) + 1,
            "amount": amount,
            "description": description,
            "type": income_type,
            "date": datetime.now().isoformat(),
            "timestamp": int(datetime.now().timestamp())
        }
        
        data["income"].append(income)
        self._save_income(data)
        return income
    
    def get_income(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get income entries."""
        data = self._load_income()
        income = data["income"]
        
        if days is not None:
            cutoff = datetime.now().timestamp() - (days * 86400)
            income = [i for i in income if i["timestamp"] >= cutoff]
        
        return sorted(income, key=lambda x: x["timestamp"], reverse=True)
    
    def get_income_report(self, days: int = 30) -> str:
        """Generate income report."""
        income = self.get_income(days=days)
        data = self._load_income()
        currency = data.get("currency", "UZS")
        
        if not income:
            return f"📈 Income (last {days} days)\n━━━━━━━━━━━━━━━━━━━━━\n\n📭 No income recorded.\n\nAdd: finance income 5000000 \"salary\""
        
        total = sum(i["amount"] for i in income)
        
        lines = [
            f"📈 Income (last {days} days)",
            "━━━━━━━━━━━━━━━━━━━━━",
            f"💵 Total: {total:,} {currency}",
            ""
        ]
        
        # Group by type
        by_type = {}
        for entry in income:
            t = entry.get("type", "other")
            if t not in by_type:
                by_type[t] = {"amount": 0, "count": 0}
            by_type[t]["amount"] += entry["amount"]
            by_type[t]["count"] += 1
        
        for income_type, data in sorted(by_type.items(), key=lambda x: x[1]["amount"], reverse=True):
            type_info = self.INCOME_TYPES.get(income_type, self.INCOME_TYPES["other"])
            pct = (data["amount"] / total * 100) if total > 0 else 0
            lines.append(f"{type_info['emoji']} {type_info['name']}: {data['amount']:,} {currency} ({pct:.1f}%)")
        
        lines.append(f"\n📝 {len(income)} entries")
        
        return "\n".join(lines)


# Global instance
_portfolio: Optional[Portfolio] = None

def get_portfolio(data_dir: Optional[Path] = None) -> Portfolio:
    global _portfolio
    if _portfolio is None:
        _portfolio = Portfolio(data_dir)
    return _portfolio
