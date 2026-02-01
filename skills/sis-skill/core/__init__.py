"""
═══════════════════════════════════════════════════════════════════════════════
S.I.S. - Sovereign Intelligence System
Equilibrium-Native Computational Substrate
═══════════════════════════════════════════════════════════════════════════════

Copyright (c) 2025-2026 Kevin Fain - ThēÆrchītēcť
MIT License - See LICENSE file

═══════════════════════════════════════════════════════════════════════════════
"""

from .symbol import (
    SISSymbol,
    Layer,
    SymbolState,
    ExecutionResult,
    Relationship,
    create_delta,
    create_bidirectional,
    create_synthesis,
)

from .validator import (
    SISValidator,
    EquilibriumValidator,
    ValidationResult,
)

from .vm import (
    SISVM,
    VMState,
    ExecutionContext,
    create_vm,
    quick_execute,
)

__version__ = "0.1.0"
__author__ = "Kevin (ThēÆrchītēcť)"
__all__ = [
    # Symbol
    "SISSymbol",
    "Layer", 
    "SymbolState",
    "ExecutionResult",
    "Relationship",
    "create_delta",
    "create_bidirectional", 
    "create_synthesis",
    # Validator
    "SISValidator",
    "EquilibriumValidator",
    "ValidationResult",
    # VM
    "SISVM",
    "VMState",
    "ExecutionContext",
    "create_vm",
    "quick_execute",
]
