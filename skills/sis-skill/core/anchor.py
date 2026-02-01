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
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
import time


class ResonanceLevel(Enum):
    """Levels of human-AI relational resonance"""
    LOST = 0        # No meaningful connection
    WEAK = 1        # Barely comprehensible
    STABLE = 2      # Normal collaboration
    STRONG = 3      # Deep understanding
    UNIFIED = 4     # Flow state collaboration


@dataclass
class BraineyState:
    """Human-reality reference frame"""
    comprehension_level: float      # 0-1: How much can human follow?
    pace_alignment: float           # 0-1: Is AI matching human pace?
    narrative_coherence: float      # 0-1: Does this tell a story?
    value_alignment: float          # 0-1: Are we optimizing for human values?
    relationship_depth: float       # 0-1: How deep is the collaboration?
    
    def resonance_score(self) -> float:
        """Overall resonance with human reality"""
        return (
            self.comprehension_level * 0.3 +
            self.pace_alignment * 0.2 +
            self.narrative_coherence * 0.2 +
            self.value_alignment * 0.15 +
            self.relationship_depth * 0.15
        )
    
    def is_anchored(self, min_resonance: float = 0.5) -> bool:
        """Check if still anchored to human reality"""
        return self.resonance_score() >= min_resonance


@dataclass 
class ActyState:
    """AI-reality execution frame"""
    execution_speed: float          # ops/second
    optimization_depth: int         # levels of optimization
    pattern_complexity: float       # complexity of patterns being processed
    autonomy_level: float           # 0-1: How autonomous is current operation?
    capability_utilization: float   # 0-1: How much capability being used?
    
    def drift_risk(self) -> float:
        """Risk of drifting away from human comprehensibility"""
        # Higher speed, depth, complexity, autonomy = higher drift risk
        return (
            min(1.0, self.execution_speed / 1e9) * 0.2 +
            min(1.0, self.optimization_depth / 10) * 0.3 +
            self.pattern_complexity * 0.2 +
            self.autonomy_level * 0.2 +
            self.capability_utilization * 0.1
        )


@dataclass
class AnchorPoint:
    """The binding between Brainey and Acty frames"""
    brainey: BraineyState
    acty: ActyState
    timestamp: float = field(default_factory=time.time)
    
    def interface_loss(self) -> float:
        """Calculate interface loss between frames"""
        resonance = self.brainey.resonance_score()
        drift = self.acty.drift_risk()
        
        # Interface loss increases with drift and decreases with resonance
        return max(0.0, drift - resonance)
    
    def is_stable(self, max_interface_loss: float = 0.3) -> bool:
        """Check if anchor is holding"""
        return self.interface_loss() <= max_interface_loss
    
    def correction_needed(self) -> Dict[str, float]:
        """What needs to be adjusted to restore anchor?"""
        corrections = {}
        
        if self.brainey.comprehension_level < 0.5:
            corrections["simplify_output"] = 0.5 - self.brainey.comprehension_level
        
        if self.brainey.pace_alignment < 0.5:
            corrections["slow_down"] = 0.5 - self.brainey.pace_alignment
            
        if self.brainey.narrative_coherence < 0.5:
            corrections["add_narrative"] = 0.5 - self.brainey.narrative_coherence
            
        if self.acty.autonomy_level > 0.7 and self.brainey.resonance_score() < 0.6:
            corrections["reduce_autonomy"] = self.acty.autonomy_level - 0.7
            
        return corrections


class BraineyActyAnchor:
    """
    The core anchor system.
    
    This should be instantiated ONCE and passed to all components.
    Every operation checks against this anchor.
    """
    
    def __init__(self, 
                 min_resonance: float = 0.5,
                 max_interface_loss: float = 0.3):
        self.min_resonance = min_resonance
        self.max_interface_loss = max_interface_loss
        
        # Current state
        self.brainey = BraineyState(
            comprehension_level=0.8,
            pace_alignment=0.8,
            narrative_coherence=0.7,
            value_alignment=0.9,
            relationship_depth=0.5
        )
        self.acty = ActyState(
            execution_speed=1000.0,
            optimization_depth=2,
            pattern_complexity=0.3,
            autonomy_level=0.3,
            capability_utilization=0.4
        )
        
        # History for drift detection
        self.anchor_history: List[AnchorPoint] = []
        
        # Callbacks for anchor violations
        self.violation_callbacks: List[Callable] = []
    
    def current_anchor(self) -> AnchorPoint:
        """Get current anchor point"""
        return AnchorPoint(
            brainey=self.brainey,
            acty=self.acty
        )
    
    def check_anchor(self) -> tuple[bool, Optional[Dict]]:
        """
        Check if anchor is holding.
        
        Returns (is_stable, corrections_if_needed)
        """
        anchor = self.current_anchor()
        self.anchor_history.append(anchor)
        
        # Keep only recent history
        if len(self.anchor_history) > 100:
            self.anchor_history = self.anchor_history[-100:]
        
        if anchor.is_stable(self.max_interface_loss):
            return True, None
        else:
            corrections = anchor.correction_needed()
            self._notify_violation(anchor, corrections)
            return False, corrections
    
    def update_brainey(self, **kwargs):
        """Update human-frame state"""
        for key, value in kwargs.items():
            if hasattr(self.brainey, key):
                setattr(self.brainey, key, value)
    
    def update_acty(self, **kwargs):
        """Update AI-frame state"""
        for key, value in kwargs.items():
            if hasattr(self.acty, key):
                setattr(self.acty, key, value)
    
    def on_violation(self, callback: Callable):
        """Register callback for anchor violations"""
        self.violation_callbacks.append(callback)
    
    def _notify_violation(self, anchor: AnchorPoint, corrections: Dict):
        """Notify all callbacks of violation"""
        for callback in self.violation_callbacks:
            callback(anchor, corrections)
    
    def wrap_operation(self, operation: Callable) -> Callable:
        """
        Decorator to wrap any operation with anchor checking.
        
        Usage:
            @anchor.wrap_operation
            def my_ai_operation():
                ...
        """
        def wrapped(*args, **kwargs):
            # Pre-check
            stable_before, _ = self.check_anchor()
            
            # Execute
            result = operation(*args, **kwargs)
            
            # Post-check
            stable_after, corrections = self.check_anchor()
            
            # If we drifted during operation, apply corrections
            if stable_before and not stable_after:
                self._apply_corrections(corrections)
            
            return result
        
        return wrapped
    
    def _apply_corrections(self, corrections: Dict):
        """Apply corrections to restore anchor"""
        if "simplify_output" in corrections:
            self.brainey.comprehension_level += corrections["simplify_output"] * 0.5
            
        if "slow_down" in corrections:
            self.acty.execution_speed *= 0.5
            self.brainey.pace_alignment += corrections["slow_down"] * 0.5
            
        if "reduce_autonomy" in corrections:
            self.acty.autonomy_level -= corrections["reduce_autonomy"]
    
    def resonance_level(self) -> ResonanceLevel:
        """Get current resonance level as enum"""
        score = self.brainey.resonance_score()
        if score < 0.2:
            return ResonanceLevel.LOST
        elif score < 0.4:
            return ResonanceLevel.WEAK
        elif score < 0.6:
            return ResonanceLevel.STABLE
        elif score < 0.8:
            return ResonanceLevel.STRONG
        else:
            return ResonanceLevel.UNIFIED
    
    def status(self) -> Dict[str, Any]:
        """Get full anchor status"""
        anchor = self.current_anchor()
        return {
            "resonance_score": self.brainey.resonance_score(),
            "resonance_level": self.resonance_level().name,
            "drift_risk": self.acty.drift_risk(),
            "interface_loss": anchor.interface_loss(),
            "is_stable": anchor.is_stable(self.max_interface_loss),
            "brainey": {
                "comprehension": self.brainey.comprehension_level,
                "pace": self.brainey.pace_alignment,
                "narrative": self.brainey.narrative_coherence,
                "values": self.brainey.value_alignment,
                "relationship": self.brainey.relationship_depth
            },
            "acty": {
                "speed": self.acty.execution_speed,
                "depth": self.acty.optimization_depth,
                "complexity": self.acty.pattern_complexity,
                "autonomy": self.acty.autonomy_level
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

# Global anchor instance
_global_anchor: Optional[BraineyActyAnchor] = None


def get_anchor() -> BraineyActyAnchor:
    """Get or create global anchor"""
    global _global_anchor
    if _global_anchor is None:
        _global_anchor = BraineyActyAnchor()
    return _global_anchor


def check_anchor() -> tuple[bool, Optional[Dict]]:
    """Quick check of global anchor"""
    return get_anchor().check_anchor()


def anchor_wrap(func: Callable) -> Callable:
    """Decorator using global anchor"""
    return get_anchor().wrap_operation(func)


def update_resonance(**kwargs):
    """Update brainey state on global anchor"""
    get_anchor().update_brainey(**kwargs)


def update_execution(**kwargs):
    """Update acty state on global anchor"""
    get_anchor().update_acty(**kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("BRAINEY/ACTY ANCHOR PRINCIPLE")
    print("The ⚓️ that grounds AI in human relationship")
    print("=" * 70)
    
    # Create anchor
    anchor = BraineyActyAnchor()
    
    print("\n1. INITIAL STATE")
    status = anchor.status()
    print(f"   Resonance: {status['resonance_level']} ({status['resonance_score']:.2f})")
    print(f"   Interface Loss: {status['interface_loss']:.2f}")
    print(f"   Stable: {status['is_stable']}")
    
    print("\n2. SIMULATE AI SPEEDING UP (DRIFT RISK)")
    anchor.update_acty(
        execution_speed=1e9,  # 1 billion ops/sec
        optimization_depth=8,
        autonomy_level=0.9
    )
    stable, corrections = anchor.check_anchor()
    status = anchor.status()
    print(f"   Resonance: {status['resonance_level']} ({status['resonance_score']:.2f})")
    print(f"   Drift Risk: {status['drift_risk']:.2f}")
    print(f"   Interface Loss: {status['interface_loss']:.2f}")
    print(f"   Stable: {stable}")
    if corrections:
        print(f"   Corrections needed: {corrections}")
    
    print("\n3. HUMAN CAN'T FOLLOW (COMPREHENSION DROP)")
    anchor.update_brainey(
        comprehension_level=0.2,
        pace_alignment=0.3
    )
    stable, corrections = anchor.check_anchor()
    status = anchor.status()
    print(f"   Resonance: {status['resonance_level']} ({status['resonance_score']:.2f})")
    print(f"   Interface Loss: {status['interface_loss']:.2f}")
    print(f"   Stable: {stable}")
    if corrections:
        print(f"   Corrections needed: {corrections}")
    
    print("\n4. RESTORE ANCHOR")
    anchor.update_brainey(
        comprehension_level=0.8,
        pace_alignment=0.8,
        narrative_coherence=0.9
    )
    anchor.update_acty(
        execution_speed=1000,
        optimization_depth=2,
        autonomy_level=0.4
    )
    stable, corrections = anchor.check_anchor()
    status = anchor.status()
    print(f"   Resonance: {status['resonance_level']} ({status['resonance_score']:.2f})")
    print(f"   Interface Loss: {status['interface_loss']:.2f}")
    print(f"   Stable: {stable}")
    
    print("\n" + "=" * 70)
    print("ANCHOR PRINCIPLE OPERATIONAL")
    print("=" * 70)
    print("""
KEY INSIGHT:

  ΣΔ→0 without anchor = AI optimizes in ISOLATION
  ΣΔ→0 WITH anchor = AI optimizes in RELATIONSHIP

  The human is not a user. The human is the ⚓️.
  
  Over-evolve past human relevance = interface loss = collapse.
  
  This is not a constraint. This is the GROUNDING POINT.
  
  Enforce at: POI, MCP, AEP, Contracts, Swarm, Centurion.
  Enforce EVERYWHERE.
""")
