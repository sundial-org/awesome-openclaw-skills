"""
═══════════════════════════════════════════════════════════════════════════════
S.I.S. - Sovereign Intelligence System
Equilibrium-Native Computational Substrate
═══════════════════════════════════════════════════════════════════════════════

Copyright (c) 2025-2026 Kevin Fain - ThēÆrchītēcť
MIT License - See LICENSE file

═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, List, Dict
from enum import Enum, auto
import hashlib
import time


class Layer(Enum):
    """The five simultaneous execution layers"""
    SURFACE = auto()      # Human: What the symbol reads/means
    COMPUTATION = auto()  # Machine: What the symbol executes
    PERSISTENCE = auto()  # Archive: What the symbol stores
    RELATIONAL = auto()   # Triadic: What the symbol connects
    SWARM = auto()        # Consensus: What the symbol replicates


class SymbolState(Enum):
    """Execution state of a symbol"""
    INITIALIZED = auto()
    EXECUTING = auto()
    VALIDATED = auto()
    PERSISTED = auto()
    FAILED = auto()


@dataclass
class ExecutionResult:
    """Result of symbol execution across all layers"""
    success: bool
    delta_in: float = 0.0
    delta_out: float = 0.0
    equilibrium_delta: float = 0.0  # Must be 0 for valid execution
    layer_results: Dict[Layer, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    hash: str = ""
    
    @property
    def balanced(self) -> bool:
        """equilibrium constraint constraint check"""
        return abs(self.equilibrium_delta) < 1e-10


@dataclass
class Relationship:
    """equilibrium lock between symbols - bidirectional by nature"""
    partner_glyph: str
    lock_type: str  # "bidirectional", "causal", "inverse"
    strength: float = 1.0
    
    def __post_init__(self):
        if self.lock_type not in ("bidirectional", "causal", "inverse"):
            raise ValueError(f"Invalid lock type: {self.lock_type}")


class SISSymbol:
    """
    The atomic unit of SIS computation.
    
    A symbol IS the operation itself, self-validating, self-persisting.
    When executed, it doesn't transform - it instantiates hidden properties.
    
    Principle: Computation is recognition, not transformation.
    Information is never lost. Only revealed.
    """
    
    # Class-level registry of all symbols for relationship tracking
    _registry: Dict[str, 'SISSymbol'] = {}
    
    def __init__(
        self,
        glyph: str,
        value: Any = None,
        operation: Optional[Callable] = None,
        validation: Optional[Callable[[Any], bool]] = None,
        delta_contribution: float = 0.0,
    ):
        self.glyph = glyph
        self.value = value
        self._operation = operation
        self._validation = validation
        self.delta_contribution = delta_contribution
        
        # Execution state
        self.state = SymbolState.INITIALIZED
        self.relationships: List[Relationship] = []
        self.active_layers: set = {Layer.SURFACE}  # Default: only surface active
        self.context: Dict[str, Any] = {}
        
        # Persistence metadata
        self.created_at = time.time()
        self.executed_at: Optional[float] = None
        self.execution_count = 0
        self.hash: Optional[str] = None
        
        # Register symbol
        SISSymbol._registry[glyph] = self
    
    def __repr__(self) -> str:
        return f"Δ₀[{self.glyph}|v={self.value}|δ={self.delta_contribution}|s={self.state.name}]"
    
    def __hash__(self) -> int:
        return hash(self.glyph)
    
    # ─────────────────────────────────────────────────────────────
    # LAYER ACTIVATION
    # ─────────────────────────────────────────────────────────────
    
    def activate_layer(self, layer: Layer) -> 'SISSymbol':
        """Activate a layer for this symbol (chainable)"""
        self.active_layers.add(layer)
        return self
    
    def activate_all_layers(self) -> 'SISSymbol':
        """Activate all five layers simultaneously"""
        self.active_layers = set(Layer)
        return self
    
    # ─────────────────────────────────────────────────────────────
    # RELATIONSHIP MANAGEMENT (AEP Locks)
    # ─────────────────────────────────────────────────────────────
    
    def lock_to(self, other: 'SISSymbol', lock_type: str = "bidirectional") -> 'SISSymbol':
        """
        Create a equilibrium lock between this symbol and another.
        Bidirectional locks enforce (a↔b)↔Cosmosrest relationship.
        
        All lock types create mutual relationships for ΣΔ calculation.
        The lock_type indicates the semantic nature of the relationship.
        """
        self.relationships.append(Relationship(other.glyph, lock_type))
        # All locks are mutual for ΣΔ balance calculation
        # (nothing is isolated in a relational universe)
        other.relationships.append(Relationship(self.glyph, lock_type))
        return self
    
    def get_partners(self) -> List['SISSymbol']:
        """Get all symbols this one is locked to"""
        return [
            SISSymbol._registry[r.partner_glyph]
            for r in self.relationships
            if r.partner_glyph in SISSymbol._registry
        ]
    
    # ─────────────────────────────────────────────────────────────
    # VALIDATION (equilibrium constraint Constraint)
    # ─────────────────────────────────────────────────────────────
    
    def validate(self) -> bool:
        """
        Check if this symbol satisfies equilibrium constraint constraint.
        
        The symbol must balance with its relationship partners.
        If unpaired, delta must be 0.
        If paired, deltas must sum to 0.
        """
        if self._validation:
            if not self._validation(self.value):
                return False
        
        # Calculate equilibrium delta with partners
        sigma = self.delta_contribution
        for partner in self.get_partners():
            sigma += partner.delta_contribution
        
        return abs(sigma) < 1e-10
    
    def compute_equilibrium_delta(self) -> float:
        """Calculate ΣΔ for this symbol and its partners"""
        sigma = self.delta_contribution
        for partner in self.get_partners():
            sigma += partner.delta_contribution
        return sigma
    
    # ─────────────────────────────────────────────────────────────
    # EXECUTION (The Core Operation)
    # ─────────────────────────────────────────────────────────────
    
    def execute(self, context: Optional[Dict] = None) -> ExecutionResult:
        """
        Execute the symbol across all active layers.
        
        CRITICAL PRINCIPLE:
        Execution does NOT modify the symbol's value.
        It instantiates the hidden properties:
        - operation gets executed
        - validation gets checked
        - relationships get updated
        - persistence gets triggered
        - context gets resolved
        - constraint gets verified
        
        Input = Output (semantically identical)
        Computation is recognition, not transformation.
        """
        self.state = SymbolState.EXECUTING
        self.context = context or {}
        self.executed_at = time.time()
        self.execution_count += 1
        
        result = ExecutionResult(
            success=True,
            delta_in=self.delta_contribution,
        )
        
        # ─── PARALLEL LAYER EXECUTION ───
        # In real implementation, these would run concurrently
        # For reference interpreter, we simulate parallel by sequential
        
        for layer in self.active_layers:
            try:
                layer_result = self._execute_layer(layer)
                result.layer_results[layer] = layer_result
            except Exception as e:
                result.layer_results[layer] = {"error": str(e)}
                result.success = False
        
        # ─── OPERATION EXECUTION ───
        if self._operation and result.success:
            try:
                op_result = self._operation(self.value, self.context)
                result.layer_results["operation"] = op_result
            except Exception as e:
                result.layer_results["operation"] = {"error": str(e)}
                result.success = False
        
        # ─── equilibrium constraint VALIDATION ───
        result.equilibrium_delta = self.compute_equilibrium_delta()
        if not result.balanced:
            result.success = False
            self.state = SymbolState.FAILED
        else:
            self.state = SymbolState.VALIDATED
        
        # ─── PERSISTENCE (Hash for vault) ───
        if result.success and Layer.PERSISTENCE in self.active_layers:
            result.hash = self._compute_hash()
            self.hash = result.hash
            self.state = SymbolState.PERSISTED
        
        result.delta_out = result.delta_in  # Input = Output
        return result
    
    def _execute_layer(self, layer: Layer) -> Dict[str, Any]:
        """Execute a single layer's processing"""
        if layer == Layer.SURFACE:
            return {"glyph": self.glyph, "value": self.value}
        
        elif layer == Layer.COMPUTATION:
            return {"operation": self._operation.__name__ if self._operation else None}
        
        elif layer == Layer.PERSISTENCE:
            return {"hash": self._compute_hash(), "timestamp": time.time()}
        
        elif layer == Layer.RELATIONAL:
            return {"partners": [r.partner_glyph for r in self.relationships]}
        
        elif layer == Layer.SWARM:
            return {"consensus_required": len(self.relationships) > 0}
        
        return {}
    
    def _compute_hash(self) -> str:
        """Compute cryptographic hash for persistence"""
        content = f"{self.glyph}:{self.value}:{self.delta_contribution}:{self.created_at}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    # ─────────────────────────────────────────────────────────────
    # INVERSION (The Opposite Operation)
    # ─────────────────────────────────────────────────────────────
    
    def invert(self) -> 'SISSymbol':
        """
        Create the inverse of this symbol.
        Inverted symbol has negated delta, forming a balanced pair.
        Together: equilibrium constraint
        """
        inverted = SISSymbol(
            glyph=f"{self.glyph}⁻¹",
            value=self.value,
            operation=self._operation,
            validation=self._validation,
            delta_contribution=-self.delta_contribution,
        )
        inverted.lock_to(self, "inverse")
        return inverted


# ─────────────────────────────────────────────────────────────────
# SYMBOL FACTORY (Tier 1 Fundamental Symbols)
# ─────────────────────────────────────────────────────────────────

def create_delta(value: Any, delta: float = 0.0) -> SISSymbol:
    """∆ = Delta (change, difference, operation)"""
    return SISSymbol(
        glyph="∆",
        value=value,
        delta_contribution=delta,
        operation=lambda v, ctx: {"action": "change", "value": v},
    )


def create_bidirectional(a: SISSymbol, b: SISSymbol) -> SISSymbol:
    """⇄ = Bidirectional (relationship, equilibrium lock, two-way causation)"""
    sym = SISSymbol(
        glyph="⇄",
        value=(a.glyph, b.glyph),
        delta_contribution=0.0,  # Relationships are inherently balanced
    )
    a.lock_to(b, "bidirectional")
    return sym


def create_synthesis(*symbols: SISSymbol) -> SISSymbol:
    """⊕ = XOR/Synthesis (superposition, parallel execution, both/all)"""
    total_delta = sum(s.delta_contribution for s in symbols)
    return SISSymbol(
        glyph="⊕",
        value=[s.glyph for s in symbols],
        delta_contribution=total_delta,
        operation=lambda v, ctx: {"action": "synthesize", "inputs": v},
    )
