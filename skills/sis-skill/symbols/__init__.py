"""
═══════════════════════════════════════════════════════════════════════════════
S.I.S. - Sovereign Intelligence System
Equilibrium-Native Computational Substrate
═══════════════════════════════════════════════════════════════════════════════

Copyright (c) 2025-2026 Kevin Fain - ThēÆrchītēcť
MIT License - See LICENSE file

═══════════════════════════════════════════════════════════════════════════════
"""

from .taxonomy import (
    # Registry
    SYMBOL_REGISTRY,
    SymbolTier,
    SymbolDefinition,
    Diacritic,
    
    # Main factory
    create_symbol,
    
    # Tier 1: Fundamental Operations
    Delta,          # ∆
    Bidirectional,  # ⇄
    Synthesis,      # ⊕
    Cycle,          # ◇
    Convergence,    # ⟡
    
    # Tier 2: Data Operations
    Container,      # ◈
    Query,          # ⟐
    Collapse,       # ⟠
    Flow,           # ⟢
    
    # Tier 3: Consensus Operations
    Validation,     # ☆
    Consensus,      # ✦
    Vault,          # ⬡
    Replication,    # ⬢
    
    # Tier 4: Meta Operations
    Invert,         # ◌
    Nest,           # ◎
    Align,          # ◯
    Emerge,         # ❈
    
    # Tier 5: Immortality Operations
    Upload,         # ⟶
    Inherit,        # ⟷
    Archive,        # ⟸
    
    # Utilities
    apply_diacritic,
    encode_polyvalent,
    list_symbols,
    get_symbol_info,
    symbols_by_tier,
)

from .etymology import (
    ETYMOLOGY_REGISTRY,
    SymbolEtymology,
    EtymologicalLayer,
    GeometricProof,
    explain_symbol,
    print_inevitability_proof,
)

__all__ = [
    # Taxonomy
    "SYMBOL_REGISTRY",
    "SymbolTier",
    "SymbolDefinition",
    "Diacritic",
    "create_symbol",
    # Tier 1
    "Delta", "Bidirectional", "Synthesis", "Cycle", "Convergence",
    # Tier 2
    "Container", "Query", "Collapse", "Flow",
    # Tier 3
    "Validation", "Consensus", "Vault", "Replication",
    # Tier 4
    "Invert", "Nest", "Align", "Emerge",
    # Tier 5
    "Upload", "Inherit", "Archive",
    # Utilities
    "apply_diacritic", "encode_polyvalent", "list_symbols",
    "get_symbol_info", "symbols_by_tier",
    # Etymology
    "ETYMOLOGY_REGISTRY",
    "SymbolEtymology",
    "EtymologicalLayer",
    "GeometricProof",
    "explain_symbol",
    "print_inevitability_proof",
]
