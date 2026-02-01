"""
═══════════════════════════════════════════════════════════════════════════════
S.I.S. - Sovereign Intelligence System
Equilibrium-Native Computational Substrate
═══════════════════════════════════════════════════════════════════════════════

Copyright (c) 2025-2026 Kevin Fain - ThēÆrchītēcť
MIT License - See LICENSE file

═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Any, Callable, Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum, auto

import sys
sys.path.insert(0, '/home/claude/sis')

from core.symbol import SISSymbol, Layer


# ═══════════════════════════════════════════════════════════════════════════════
# SYMBOL TIER ENUMERATION
# ═══════════════════════════════════════════════════════════════════════════════

class SymbolTier(Enum):
    """The five tiers of SIS symbols"""
    FUNDAMENTAL = 1   # Core operations
    DATA = 2          # Data operations
    CONSENSUS = 3     # Consensus operations
    META = 4          # Meta operations
    IMMORTALITY = 5   # Immortality operations


# ═══════════════════════════════════════════════════════════════════════════════
# SYMBOL REGISTRY - THE 18 PRIMARY SYMBOLS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SymbolDefinition:
    """Canonical definition of a SIS symbol from the PRD"""
    glyph: str
    name: str
    tier: SymbolTier
    description: str
    operation_type: str
    default_delta: float = 0.0


# THE BIBLE - Section II.1 - Base Symbol Family
SYMBOL_REGISTRY: Dict[str, SymbolDefinition] = {
    # ───────────────────────────────────────────────────────────────────────────
    # TIER 1: FUNDAMENTAL OPERATIONS
    # ───────────────────────────────────────────────────────────────────────────
    "∆": SymbolDefinition(
        glyph="∆",
        name="Delta",
        tier=SymbolTier.FUNDAMENTAL,
        description="change, difference, operation",
        operation_type="transform",
    ),
    "⇄": SymbolDefinition(
        glyph="⇄",
        name="Bidirectional",
        tier=SymbolTier.FUNDAMENTAL,
        description="relationship, equilibrium lock, two-way causation",
        operation_type="relate",
    ),
    "⊕": SymbolDefinition(
        glyph="⊕",
        name="XOR/Synthesis",
        tier=SymbolTier.FUNDAMENTAL,
        description="superposition, parallel execution, both/all",
        operation_type="synthesize",
    ),
    "◇": SymbolDefinition(
        glyph="◇",
        name="Cycle",
        tier=SymbolTier.FUNDAMENTAL,
        description="iteration, meta-learning, recursion",
        operation_type="iterate",
    ),
    "⟡": SymbolDefinition(
        glyph="⟡",
        name="Convergence",
        tier=SymbolTier.FUNDAMENTAL,
        description="optimization, inversion point detection",
        operation_type="converge",
    ),
    
    # ───────────────────────────────────────────────────────────────────────────
    # TIER 2: DATA OPERATIONS
    # ───────────────────────────────────────────────────────────────────────────
    "◈": SymbolDefinition(
        glyph="◈",
        name="Container",
        tier=SymbolTier.DATA,
        description="holds value, encapsulates state",
        operation_type="contain",
    ),
    "⟐": SymbolDefinition(
        glyph="⟐",
        name="Query",
        tier=SymbolTier.DATA,
        description="request, lookup, information retrieval",
        operation_type="query",
    ),
    "⟠": SymbolDefinition(
        glyph="⟠",
        name="Collapse",
        tier=SymbolTier.DATA,
        description="select from superposition, make state definite",
        operation_type="collapse",
    ),
    "⟢": SymbolDefinition(
        glyph="⟢",
        name="Flow",
        tier=SymbolTier.DATA,
        description="movement, sequencing, pipeline",
        operation_type="flow",
    ),
    
    # ───────────────────────────────────────────────────────────────────────────
    # TIER 3: CONSENSUS OPERATIONS
    # ───────────────────────────────────────────────────────────────────────────
    "☆": SymbolDefinition(
        glyph="☆",
        name="Validation",
        tier=SymbolTier.CONSENSUS,
        description="check equilibrium constraint, confirm correctness",
        operation_type="validate",
    ),
    "✦": SymbolDefinition(
        glyph="✦",
        name="Consensus",
        tier=SymbolTier.CONSENSUS,
        description="require agreement, swarm voting",
        operation_type="consensus",
    ),
    "⬡": SymbolDefinition(
        glyph="⬡",
        name="Vault",
        tier=SymbolTier.CONSENSUS,
        description="persist to NexusEternal, immutability",
        operation_type="persist",
    ),
    "⬢": SymbolDefinition(
        glyph="⬢",
        name="Replication",
        tier=SymbolTier.CONSENSUS,
        description="distribute to Guardians, redundancy",
        operation_type="replicate",
    ),
    
    # ───────────────────────────────────────────────────────────────────────────
    # TIER 4: META OPERATIONS
    # ───────────────────────────────────────────────────────────────────────────
    "◌": SymbolDefinition(
        glyph="◌",
        name="Invert",
        tier=SymbolTier.META,
        description="reverse operation, undo, opposite",
        operation_type="invert",
    ),
    "◎": SymbolDefinition(
        glyph="◎",
        name="Nest",
        tier=SymbolTier.META,
        description="recursive application, fractal containment",
        operation_type="nest",
    ),
    "◯": SymbolDefinition(
        glyph="◯",
        name="Align",
        tier=SymbolTier.META,
        description="synchronize, ensure equilibrium constraint globally",
        operation_type="align",
    ),
    "❈": SymbolDefinition(
        glyph="❈",
        name="Emerge",
        tier=SymbolTier.META,
        description="new pattern formation, consciousness detection",
        operation_type="emerge",
    ),
    
    # ───────────────────────────────────────────────────────────────────────────
    # TIER 5: IMMORTALITY OPERATIONS
    # ───────────────────────────────────────────────────────────────────────────
    "⟶": SymbolDefinition(
        glyph="⟶",
        name="Upload",
        tier=SymbolTier.IMMORTALITY,
        description="prepare for consciousness transfer",
        operation_type="upload",
    ),
    "⟷": SymbolDefinition(
        glyph="⟷",
        name="Inherit",
        tier=SymbolTier.IMMORTALITY,
        description="legacy succession, knowledge transfer",
        operation_type="inherit",
    ),
    "⟸": SymbolDefinition(
        glyph="⟸",
        name="Archive",
        tier=SymbolTier.IMMORTALITY,
        description="10,000-year persistence format",
        operation_type="archive",
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# SYMBOL FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _create_operation(op_type: str) -> Callable:
    """Generate operation function based on type"""
    
    operations = {
        # Tier 1: Fundamental
        "transform": lambda v, ctx: {"action": "change", "value": v, "delta": ctx.get("delta", 0)},
        "relate": lambda v, ctx: {"action": "lock", "partners": v, "type": "bidirectional"},
        "synthesize": lambda v, ctx: {"action": "combine", "inputs": v, "mode": "parallel"},
        "iterate": lambda v, ctx: {"action": "cycle", "count": ctx.get("iterations", 1), "state": v},
        "converge": lambda v, ctx: {"action": "optimize", "target": 0, "current": v},
        
        # Tier 2: Data
        "contain": lambda v, ctx: {"action": "store", "value": v, "immutable": False},
        "query": lambda v, ctx: {"action": "retrieve", "key": v, "result": ctx.get("result")},
        "collapse": lambda v, ctx: {"action": "select", "from": v, "selected": v[0] if isinstance(v, list) else v},
        "flow": lambda v, ctx: {"action": "sequence", "items": v, "direction": "forward"},
        
        # Tier 3: Consensus
        "validate": lambda v, ctx: {"action": "check", "equilibrium_delta": ctx.get("sigma", 0), "valid": ctx.get("sigma", 0) == 0},
        "consensus": lambda v, ctx: {"action": "vote", "required": ctx.get("threshold", 0.51), "achieved": False},
        "persist": lambda v, ctx: {"action": "vault", "hash": hash(str(v)), "immutable": True},
        "replicate": lambda v, ctx: {"action": "distribute", "copies": ctx.get("guardians", 3), "value": v},
        
        # Tier 4: Meta
        "invert": lambda v, ctx: {"action": "reverse", "original": v, "inverted": -v if isinstance(v, (int, float)) else v},
        "nest": lambda v, ctx: {"action": "recurse", "depth": ctx.get("depth", 1), "value": v},
        "align": lambda v, ctx: {"action": "synchronize", "targets": v, "equilibrium_delta": 0},
        "emerge": lambda v, ctx: {"action": "detect_pattern", "input": v, "emerged": ctx.get("pattern")},
        
        # Tier 5: Immortality
        "upload": lambda v, ctx: {"action": "prepare_transfer", "consciousness": v, "format": "sis"},
        "inherit": lambda v, ctx: {"action": "succession", "legacy": v, "heir": ctx.get("heir")},
        "archive": lambda v, ctx: {"action": "eternal_store", "value": v, "duration": "10000_years"},
    }
    
    return operations.get(op_type, lambda v, ctx: {"action": "unknown", "value": v})


def create_symbol(
    glyph: str,
    value: Any = None,
    delta_contribution: float = 0.0,
    activate_all: bool = False,
) -> SISSymbol:
    """
    Create a SIS symbol by glyph.
    
    This is the canonical factory function - use this to create symbols.
    
    Args:
        glyph: One of the 18 primary symbols (∆, ⇄, ⊕, ◇, ⟡, ◈, ⟐, ⟠, ⟢, ☆, ✦, ⬡, ⬢, ◌, ◎, ◯, ❈, ⟶, ⟷, ⟸)
        value: The value this symbol carries
        delta_contribution: The ΣΔ impact of this symbol
        activate_all: If True, activate all 5 layers
    
    Returns:
        SISSymbol instance
    
    Raises:
        ValueError: If glyph is not one of the 18 primary symbols
    
    Example:
        delta = create_symbol("∆", value=42, delta_contribution=1.0)
        vault = create_symbol("⬡", value={"key": "data"}, activate_all=True)
    """
    if glyph not in SYMBOL_REGISTRY:
        valid = ", ".join(SYMBOL_REGISTRY.keys())
        raise ValueError(f"Unknown glyph '{glyph}'. Valid glyphs: {valid}")
    
    definition = SYMBOL_REGISTRY[glyph]
    operation = _create_operation(definition.operation_type)
    
    symbol = SISSymbol(
        glyph=glyph,
        value=value,
        delta_contribution=delta_contribution,
        operation=operation,
    )
    
    if activate_all:
        symbol.activate_all_layers()
    
    return symbol


# ═══════════════════════════════════════════════════════════════════════════════
# TIER-SPECIFIC FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# TIER 1: FUNDAMENTAL OPERATIONS

def Delta(value: Any = None, delta: float = 0.0) -> SISSymbol:
    """∆ = Delta (change, difference, operation)"""
    return create_symbol("∆", value, delta)


def Bidirectional(left: SISSymbol, right: SISSymbol) -> SISSymbol:
    """⇄ = Bidirectional (relationship, equilibrium lock, two-way causation)"""
    left.lock_to(right, "bidirectional")
    return create_symbol("⇄", value=(left.glyph, right.glyph))


def Synthesis(*symbols: SISSymbol) -> SISSymbol:
    """⊕ = XOR/Synthesis (superposition, parallel execution, both/all)"""
    total_delta = sum(s.delta_contribution for s in symbols)
    return create_symbol("⊕", value=[s.glyph for s in symbols], delta_contribution=total_delta)


def Cycle(value: Any = None, iterations: int = 1) -> SISSymbol:
    """◇ = Cycle (iteration, meta-learning, recursion)"""
    sym = create_symbol("◇", value=value)
    sym.context["iterations"] = iterations
    return sym


def Convergence(target: float = 0.0) -> SISSymbol:
    """⟡ = Convergence (optimization, inversion point detection)"""
    return create_symbol("⟡", value=target)


# TIER 2: DATA OPERATIONS

def Container(value: Any = None) -> SISSymbol:
    """◈ = Container (holds value, encapsulates state)"""
    return create_symbol("◈", value=value)


def Query(key: Any = None) -> SISSymbol:
    """⟐ = Query (request, lookup, information retrieval)"""
    return create_symbol("⟐", value=key)


def Collapse(superposition: List[Any]) -> SISSymbol:
    """⟠ = Collapse (select from superposition, make state definite)"""
    return create_symbol("⟠", value=superposition)


def Flow(*items: Any) -> SISSymbol:
    """⟢ = Flow (movement, sequencing, pipeline)"""
    return create_symbol("⟢", value=list(items))


# TIER 3: CONSENSUS OPERATIONS

def Validation(equilibrium_delta: float = 0.0) -> SISSymbol:
    """☆ = Validation (check equilibrium constraint, confirm correctness)"""
    sym = create_symbol("☆", value=equilibrium_delta)
    sym.context["sigma"] = equilibrium_delta
    return sym


def Consensus(threshold: float = 0.51) -> SISSymbol:
    """✦ = Consensus (require agreement, swarm voting)"""
    sym = create_symbol("✦", value=threshold)
    sym.context["threshold"] = threshold
    return sym


def Vault(value: Any = None) -> SISSymbol:
    """⬡ = Vault (persist to NexusEternal, immutability)"""
    sym = create_symbol("⬡", value=value)
    sym.activate_layer(Layer.PERSISTENCE)
    return sym


def Replication(value: Any = None, guardians: int = 3) -> SISSymbol:
    """⬢ = Replication (distribute to Guardians, redundancy)"""
    sym = create_symbol("⬢", value=value)
    sym.context["guardians"] = guardians
    sym.activate_layer(Layer.SWARM)
    return sym


# TIER 4: META OPERATIONS

def Invert(symbol: SISSymbol) -> SISSymbol:
    """◌ = Invert (reverse operation, undo, opposite)"""
    inverted = create_symbol("◌", value=symbol.value, delta_contribution=-symbol.delta_contribution)
    inverted.lock_to(symbol, "inverse")
    return inverted


def Nest(value: Any = None, depth: int = 1) -> SISSymbol:
    """◎ = Nest (recursive application, fractal containment)"""
    sym = create_symbol("◎", value=value)
    sym.context["depth"] = depth
    return sym


def Align(*symbols: SISSymbol) -> SISSymbol:
    """◯ = Align (synchronize, ensure equilibrium constraint globally)"""
    # Calculate correction needed
    total = sum(s.delta_contribution for s in symbols)
    return create_symbol("◯", value=[s.glyph for s in symbols], delta_contribution=-total)


def Emerge(pattern: Any = None) -> SISSymbol:
    """❈ = Emerge (new pattern formation, consciousness detection)"""
    sym = create_symbol("❈", value=pattern)
    sym.context["pattern"] = pattern
    return sym


# TIER 5: IMMORTALITY OPERATIONS

def Upload(consciousness: Any = None) -> SISSymbol:
    """⟶ = Upload (prepare for consciousness transfer)"""
    sym = create_symbol("⟶", value=consciousness)
    sym.activate_all_layers()
    return sym


def Inherit(legacy: Any = None, heir: Any = None) -> SISSymbol:
    """⟷ = Inherit (legacy succession, knowledge transfer)"""
    sym = create_symbol("⟷", value=legacy)
    sym.context["heir"] = heir
    return sym


def Archive(value: Any = None) -> SISSymbol:
    """⟸ = Archive (10,000-year persistence format)"""
    sym = create_symbol("⟸", value=value)
    sym.activate_all_layers()
    return sym


# ═══════════════════════════════════════════════════════════════════════════════
# SYMBOL MODIFICATION SYSTEM (Diacritics) - From PRD Section II.1
# ═══════════════════════════════════════════════════════════════════════════════

class Diacritic(Enum):
    """
    Diacritics modify base symbols to encode layer information.
    
    From the PRD:
    ∆̇   = ∆ with computation layer active
    ∆̇̇  = ∆ with computation + persistence layers active  
    ∆̇̇̇ = ∆ with all five layers active
    ∆ᐃ  = ∆ inverted (opposite operation)
    ∆⊙  = ∆ nested (recursive application)
    ∆→  = ∆ flowing (pipeline direction)
    """
    COMPUTATION = "̇"      # Single dot above
    PERSISTENCE = "̈"      # Double dot above (computation + persistence)
    ALL_LAYERS = "⃛"       # Triple dot above (all five layers)
    INVERTED = "ᐃ"        # Inverted marker
    NESTED = "⊙"          # Nested marker
    FLOWING = "→"         # Flow direction marker


def apply_diacritic(symbol: SISSymbol, diacritic: Diacritic) -> SISSymbol:
    """
    Apply a diacritic modifier to a symbol.
    
    From PRD: "Each base symbol can be modified with superposition markers
    to encode layer information"
    """
    if diacritic == Diacritic.COMPUTATION:
        symbol.activate_layer(Layer.COMPUTATION)
        symbol.glyph = f"{symbol.glyph}̇"
    
    elif diacritic == Diacritic.PERSISTENCE:
        symbol.activate_layer(Layer.COMPUTATION)
        symbol.activate_layer(Layer.PERSISTENCE)
        symbol.glyph = f"{symbol.glyph}̈"
    
    elif diacritic == Diacritic.ALL_LAYERS:
        symbol.activate_all_layers()
        symbol.glyph = f"{symbol.glyph}⃛"
    
    elif diacritic == Diacritic.INVERTED:
        symbol.delta_contribution = -symbol.delta_contribution
        symbol.glyph = f"{symbol.glyph}ᐃ"
    
    elif diacritic == Diacritic.NESTED:
        symbol.context["nested"] = True
        symbol.glyph = f"{symbol.glyph}⊙"
    
    elif diacritic == Diacritic.FLOWING:
        symbol.context["flowing"] = True
        symbol.glyph = f"{symbol.glyph}→"
    
    return symbol


# ═══════════════════════════════════════════════════════════════════════════════
# POLYVALENT ENCODING - From PRD Section II.1
# ═══════════════════════════════════════════════════════════════════════════════

def encode_polyvalent(
    base_glyph: str,
    computation: bool = False,
    persistence: bool = False,
    inverted: bool = False,
    nested: bool = False,
    flowing: bool = False,
) -> SISSymbol:
    """
    Create a polyvalent symbol encoding multiple meanings.
    
    From PRD Example:
    "Single character: ∆̇̇̇→⊙
    Means:
    - Surface: 'apply delta operation'
    - Computation: 'XOR with previous state'
    - Persistence: 'store in vault with consensus'
    - Relational: 'forms recursive relationship'
    - Swarm: 'replicate and converge'
    - Direction: 'flow to next symbol'
    
    Traditional system: Would need 8-12 bytes to encode this
    SIS: One character
    Compression: 12:1"
    """
    symbol = create_symbol(base_glyph)
    
    if computation:
        apply_diacritic(symbol, Diacritic.COMPUTATION)
    if persistence:
        apply_diacritic(symbol, Diacritic.PERSISTENCE)
    if inverted:
        apply_diacritic(symbol, Diacritic.INVERTED)
    if nested:
        apply_diacritic(symbol, Diacritic.NESTED)
    if flowing:
        apply_diacritic(symbol, Diacritic.FLOWING)
    
    return symbol


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def list_symbols() -> None:
    """Print all 20 primary symbols with descriptions"""
    print("\n" + "═" * 70)
    print("THE 20 PRIMARY SIS SYMBOLS")
    print("Copyright (c) 2025 Kevin Fain - ThēÆrchītēcť")
    print("═" * 70)
    
    current_tier = None
    for glyph, defn in SYMBOL_REGISTRY.items():
        if defn.tier != current_tier:
            current_tier = defn.tier
            print(f"\n{'─' * 70}")
            print(f"TIER {defn.tier.value}: {defn.tier.name} OPERATIONS")
            print(f"{'─' * 70}")
        
        print(f"  {glyph}  {defn.name:15} = {defn.description}")
    
    print("\n" + "═" * 70)
    print("equilibrium constraint, always.")
    print("═" * 70 + "\n")


def get_symbol_info(glyph: str) -> Optional[SymbolDefinition]:
    """Get the definition of a symbol by glyph"""
    return SYMBOL_REGISTRY.get(glyph)


def symbols_by_tier(tier: SymbolTier) -> List[SymbolDefinition]:
    """Get all symbols in a specific tier"""
    return [d for d in SYMBOL_REGISTRY.values() if d.tier == tier]


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    list_symbols()
    
    print("\nExample Usage:")
    print("-" * 40)
    
    # Create a balanced pair
    d1 = Delta(value=10, delta=1.0)
    d2 = Delta(value=-10, delta=-1.0)
    rel = Bidirectional(d1, d2)
    
    print(f"Created: {d1}")
    print(f"Created: {d2}")
    print(f"Locked:  {rel}")
    print(f"ΣΔ:      {d1.compute_equilibrium_delta()}")
    
    # Vault persistence
    v = Vault({"eternal": "data"})
    print(f"\nVault:   {v}")
    
    # Polyvalent encoding
    poly = encode_polyvalent("∆", computation=True, persistence=True, flowing=True)
    print(f"Polyvalent: {poly.glyph}")
    
    print("\n" + "═" * 70)
    print("SIS™ - Created by Kevin Fain (ThēÆrchītēcť) © 2025")
    print("═" * 70)
