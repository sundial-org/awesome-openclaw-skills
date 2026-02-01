"""
═══════════════════════════════════════════════════════════════════════════════
S.I.S. - Sovereign Intelligence System
Equilibrium-Native Computational Substrate
═══════════════════════════════════════════════════════════════════════════════

Copyright (c) 2025-2026 Kevin Fain - ThēÆrchītēcť
MIT License - See LICENSE file

═══════════════════════════════════════════════════════════════════════════════
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
from .symbol import SISSymbol, ExecutionResult


@dataclass
class ValidationResult:
    """Result of equilibrium constraint validation"""
    valid: bool
    equilibrium_delta: float
    symbols_checked: int
    violations: List[str]
    correction_needed: float  # What delta would balance the system
    
    @property
    def balanced(self) -> bool:
        return abs(self.equilibrium_delta) < 1e-10


class SISValidator:
    """
    Enforces the equilibrium constraint constraint across symbol sequences.
    
    The equilibrium principle: Every change must be balanced.
    For any symbol S executing: ΣΔ_in = ΣΔ_out
    
    This validator can:
    1. Check if a symbol sequence is balanced
    2. Find the minimal correction to achieve balance
    3. Detect where imbalance originates
    4. Suggest balancing symbols
    """
    
    EPSILON = 1e-10  # Tolerance for floating point comparison
    
    def __init__(self):
        self.history: List[ValidationResult] = []
    
    def validate_symbol(self, symbol: SISSymbol) -> ValidationResult:
        """
        Validate a single symbol and its relationship partners.
        
        The symbol must satisfy equilibrium constraint with its partners.
        """
        sigma = symbol.delta_contribution
        partners = symbol.get_partners()
        
        for partner in partners:
            sigma += partner.delta_contribution
        
        violations = []
        if abs(sigma) >= self.EPSILON:
            violations.append(
                f"Symbol {symbol.glyph} has ΣΔ = {sigma:.6f} (expected 0)"
            )
        
        result = ValidationResult(
            valid=len(violations) == 0,
            equilibrium_delta=sigma,
            symbols_checked=1 + len(partners),
            violations=violations,
            correction_needed=-sigma if abs(sigma) >= self.EPSILON else 0.0,
        )
        
        self.history.append(result)
        return result
    
    def validate_sequence(self, symbols: List[SISSymbol]) -> ValidationResult:
        """
        Validate a sequence of symbols for global balance.
        
        All symbols in the sequence must collectively satisfy equilibrium constraint.
        """
        sigma = 0.0
        violations = []
        
        for symbol in symbols:
            sigma += symbol.delta_contribution
            
            # Also check individual symbol validity
            if symbol._validation:
                if not symbol._validation(symbol.value):
                    violations.append(
                        f"Symbol {symbol.glyph} failed custom validation"
                    )
        
        if abs(sigma) >= self.EPSILON:
            violations.append(
                f"Sequence has ΣΔ = {sigma:.6f} (expected 0)"
            )
        
        result = ValidationResult(
            valid=len(violations) == 0,
            equilibrium_delta=sigma,
            symbols_checked=len(symbols),
            violations=violations,
            correction_needed=-sigma if abs(sigma) >= self.EPSILON else 0.0,
        )
        
        self.history.append(result)
        return result
    
    def find_balancing_delta(self, symbols: List[SISSymbol]) -> float:
        """
        Calculate what delta contribution would balance the sequence.
        
        If you add a symbol with this delta, equilibrium constraint will hold.
        """
        sigma = sum(s.delta_contribution for s in symbols)
        return -sigma
    
    def suggest_correction(
        self, 
        symbols: List[SISSymbol]
    ) -> Optional[SISSymbol]:
        """
        Suggest a balancing symbol to achieve equilibrium constraint.
        
        Returns a new symbol that, when added to the sequence,
        makes the entire system balanced.
        """
        correction = self.find_balancing_delta(symbols)
        
        if abs(correction) < self.EPSILON:
            return None  # Already balanced
        
        # Create a correction symbol
        return SISSymbol(
            glyph="◯",  # Align symbol
            value=correction,
            delta_contribution=correction,
        )
    
    def validate_equilibrium_loop(
        self,
        perceive: SISSymbol,
        measure: SISSymbol,
        correct: SISSymbol,
    ) -> Tuple[ValidationResult, bool]:
        """
        Validate a complete equilibrium control loop: sense → quantify → compensate → iterate
        
        A valid equilibrium control loop must:
        1. Perceive creates a delta (identifies imbalance)
        2. Measure quantifies the delta
        3. Correct negates the delta (restores balance)
        4. Result: equilibrium constraint
        
        Returns validation result and whether the loop is complete.
        """
        loop_symbols = [perceive, measure, correct]
        result = self.validate_sequence(loop_symbols)
        
        # A complete equilibrium control loop should achieve balance
        loop_complete = result.valid and result.balanced
        
        return result, loop_complete
    
    def get_imbalance_trace(
        self, 
        symbols: List[SISSymbol]
    ) -> List[Tuple[str, float, float]]:
        """
        Trace the delta accumulation through a symbol sequence.
        
        Returns list of (glyph, delta_contribution, running_sigma) tuples.
        Useful for debugging where imbalance originates.
        """
        trace = []
        running_sigma = 0.0
        
        for symbol in symbols:
            running_sigma += symbol.delta_contribution
            trace.append((symbol.glyph, symbol.delta_contribution, running_sigma))
        
        return trace


class EquilibriumValidator(SISValidator):
    """
    Extended validator specifically for AEP (Adaptive Equilibrium Protocol)
    
    AEP Principle: sense → quantify → compensate → iterate
    Attractor: equilibrium convergence (asymptotic, never fully reached)
    Context: (a↔b) ↔ Cosmosrest (nothing isolated)
    """
    
    def __init__(self):
        super().__init__()
        self.iteration_count = 0
        self.sigma_history: List[float] = []
    
    def iterate(
        self,
        current_state: List[SISSymbol],
        correction: SISSymbol,
    ) -> Tuple[ValidationResult, float]:
        """
        Perform one AEP iteration:
        1. Measure current ΣΔ
        2. Apply correction
        3. Measure new ΣΔ
        4. Track convergence toward 0
        
        Returns validation result and improvement (old_sigma - new_sigma).
        """
        self.iteration_count += 1
        
        # Measure before correction
        old_sigma = sum(s.delta_contribution for s in current_state)
        self.sigma_history.append(old_sigma)
        
        # Apply correction (add to state)
        new_state = current_state + [correction]
        
        # Measure after correction
        result = self.validate_sequence(new_state)
        new_sigma = result.equilibrium_delta
        
        improvement = abs(old_sigma) - abs(new_sigma)
        
        return result, improvement
    
    def is_converging(self, window: int = 5) -> bool:
        """
        Check if the system is converging toward equilibrium constraint.
        
        Looks at recent history to determine if corrections
        are successfully reducing imbalance.
        """
        if len(self.sigma_history) < window:
            return True  # Not enough data
        
        recent = self.sigma_history[-window:]
        
        # Check if absolute sigma is decreasing
        for i in range(1, len(recent)):
            if abs(recent[i]) > abs(recent[i-1]):
                return False
        
        return True
    
    def sigma_approaching_zero(self, threshold: float = 0.01) -> bool:
        """
        Check if ΣΔ is approaching 0 within threshold.
        
        The attractor state equilibrium constraint is never fully reached,
        but we can detect when we're asymptotically close.
        """
        if not self.sigma_history:
            return False
        
        current_sigma = abs(self.sigma_history[-1])
        return current_sigma < threshold
