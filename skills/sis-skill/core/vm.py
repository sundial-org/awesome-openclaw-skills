"""
═══════════════════════════════════════════════════════════════════════════════
S.I.S. - Sovereign Intelligence System
Equilibrium-Native Computational Substrate
═══════════════════════════════════════════════════════════════════════════════

Copyright (c) 2025-2026 Kevin Fain - ThēÆrchītēcť
MIT License - See LICENSE file

═══════════════════════════════════════════════════════════════════════════════
"""

import time
import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import threading

from .symbol import SISSymbol, Layer, ExecutionResult, SymbolState
from .validator import SISValidator, EquilibriumValidator, ValidationResult


@dataclass
class VMState:
    """Current state of the SIS Virtual Machine"""
    symbols_executed: int = 0
    symbols_failed: int = 0
    total_equilibrium_delta: float = 0.0
    execution_times: List[float] = field(default_factory=list)
    vault: Dict[str, Dict] = field(default_factory=dict)  # hash -> symbol data
    
    @property
    def average_execution_time_ns(self) -> float:
        if not self.execution_times:
            return 0.0
        return sum(self.execution_times) / len(self.execution_times) * 1e9


@dataclass 
class ExecutionContext:
    """Context passed through symbol execution"""
    vm_state: VMState
    global_sigma: float = 0.0
    parent_symbols: List[str] = field(default_factory=list)
    consensus_required: bool = False
    persist: bool = True


class SISVM:
    """
    The SIS Virtual Machine.
    
    Executes symbols with parallel layer processing and
    enforces equilibrium constraint at the atomic level.
    
    Principle: Symbols execute in parallel, not sequentially.
    All operations understand each other through equilibrium locks.
    No intermediate states. Single convergence point.
    """
    
    def __init__(self, max_workers: int = 5):
        self.state = VMState()
        self.validator = EquilibriumValidator()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.lock = threading.Lock()
        
        # Event hooks for extensibility
        self.on_execute: List[Callable] = []
        self.on_validate: List[Callable] = []
        self.on_persist: List[Callable] = []
    
    # ─────────────────────────────────────────────────────────────
    # CORE EXECUTION
    # ─────────────────────────────────────────────────────────────
    
    def execute(self, symbol: SISSymbol) -> ExecutionResult:
        """
        Execute a single symbol through the VM pipeline.
        
        Pipeline:
        1. Decode symbol
        2. Dispatch to parallel layers
        3. Validate equilibrium constraint
        4. Persist to vault
        5. Return result (Input = Output)
        """
        start_time = time.perf_counter()
        
        context = ExecutionContext(
            vm_state=self.state,
            global_sigma=self.state.total_equilibrium_delta,
        )
        
        # Execute symbol (triggers all layers)
        result = symbol.execute(context.__dict__)
        
        # Update VM state
        with self.lock:
            self.state.symbols_executed += 1
            self.state.total_equilibrium_delta += symbol.delta_contribution
            
            if not result.success:
                self.state.symbols_failed += 1
            elif result.hash and symbol.state == SymbolState.PERSISTED:
                # Store in vault
                self.state.vault[result.hash] = {
                    "glyph": symbol.glyph,
                    "value": symbol.value,
                    "delta": symbol.delta_contribution,
                    "timestamp": result.timestamp,
                }
        
        # Track execution time
        elapsed = time.perf_counter() - start_time
        self.state.execution_times.append(elapsed)
        
        # Fire hooks
        for hook in self.on_execute:
            hook(symbol, result)
        
        return result
    
    def execute_sequence(
        self, 
        symbols: List[SISSymbol],
        require_balance: bool = True,
    ) -> List[ExecutionResult]:
        """
        Execute a sequence of symbols.
        
        If require_balance=True, the sequence must satisfy equilibrium constraint
        or no symbols will execute.
        """
        # Pre-validate if balance required
        if require_balance:
            validation = self.validator.validate_sequence(symbols)
            if not validation.valid:
                # Return failed results for all
                return [
                    ExecutionResult(
                        success=False, 
                        equilibrium_delta=validation.equilibrium_delta
                    ) for _ in symbols
                ]
        
        # Execute all symbols
        results = []
        for symbol in symbols:
            result = self.execute(symbol)
            results.append(result)
            
            # Early exit on failure if balance required
            if require_balance and not result.success:
                break
        
        return results
    
    def execute_parallel(
        self, 
        symbols: List[SISSymbol]
    ) -> List[ExecutionResult]:
        """
        Execute symbols in parallel (true to SIS philosophy).
        
        All symbols execute simultaneously, coordinated by shared state.
        """
        futures = []
        for symbol in symbols:
            future = self.executor.submit(self.execute, symbol)
            futures.append(future)
        
        results = [f.result() for f in futures]
        return results
    
    # ─────────────────────────────────────────────────────────────
    # AEP LOOP EXECUTION
    # ─────────────────────────────────────────────────────────────
    
    def equilibrium_loop(
        self,
        initial_state: List[SISSymbol],
        max_iterations: int = 100,
        convergence_threshold: float = 0.001,
    ) -> Dict[str, Any]:
        """
        Execute the equilibrium control loop: sense → quantify → compensate → iterate
        
        Continues until ΣΔ approaches 0 within threshold or max iterations.
        
        Returns execution trace and final state.
        """
        trace = []
        current_symbols = list(initial_state)
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # PERCEIVE: Calculate current state
            current_sigma = sum(s.delta_contribution for s in current_symbols)
            
            # Check convergence
            if abs(current_sigma) < convergence_threshold:
                trace.append({
                    "iteration": iteration,
                    "sigma": current_sigma,
                    "action": "converged",
                })
                break
            
            # MEASURE Δ: Quantify the imbalance
            delta_needed = -current_sigma
            
            # CORRECT: Create balancing symbol
            correction = self.validator.suggest_correction(current_symbols)
            
            if correction is None:
                trace.append({
                    "iteration": iteration,
                    "sigma": current_sigma,
                    "action": "already_balanced",
                })
                break
            
            # Execute correction
            result = self.execute(correction)
            current_symbols.append(correction)
            
            trace.append({
                "iteration": iteration,
                "sigma_before": current_sigma,
                "correction": correction.delta_contribution,
                "sigma_after": sum(s.delta_contribution for s in current_symbols),
                "success": result.success,
            })
            
            # REPEAT: Continue loop
        
        return {
            "iterations": iteration,
            "converged": abs(sum(s.delta_contribution for s in current_symbols)) < convergence_threshold,
            "final_sigma": sum(s.delta_contribution for s in current_symbols),
            "trace": trace,
            "symbols": current_symbols,
        }
    
    # ─────────────────────────────────────────────────────────────
    # VAULT OPERATIONS
    # ─────────────────────────────────────────────────────────────
    
    def persist_to_vault(self, symbol: SISSymbol) -> str:
        """
        Explicitly persist a symbol to the vault.
        
        Returns the hash (vault key).
        """
        symbol.activate_layer(Layer.PERSISTENCE)
        result = self.execute(symbol)
        return result.hash if result.success else ""
    
    def retrieve_from_vault(self, hash_key: str) -> Optional[Dict]:
        """
        Retrieve symbol data from vault by hash.
        """
        return self.state.vault.get(hash_key)
    
    def vault_size(self) -> int:
        """Number of symbols in vault"""
        return len(self.state.vault)
    
    # ─────────────────────────────────────────────────────────────
    # INTROSPECTION
    # ─────────────────────────────────────────────────────────────
    
    def stats(self) -> Dict[str, Any]:
        """Get VM execution statistics"""
        return {
            "symbols_executed": self.state.symbols_executed,
            "symbols_failed": self.state.symbols_failed,
            "success_rate": (
                (self.state.symbols_executed - self.state.symbols_failed) 
                / max(1, self.state.symbols_executed)
            ),
            "total_equilibrium_delta": self.state.total_equilibrium_delta,
            "vault_size": self.vault_size(),
            "avg_execution_time_ns": self.state.average_execution_time_ns,
        }
    
    def reset(self):
        """Reset VM state"""
        self.state = VMState()
        self.validator = EquilibriumValidator()


# ─────────────────────────────────────────────────────────────────
# CONVENIENCE FUNCTIONS
# ─────────────────────────────────────────────────────────────────

def create_vm() -> SISVM:
    """Create a new SIS VM instance"""
    return SISVM()


def quick_execute(glyph: str, value: Any, delta: float = 0.0) -> ExecutionResult:
    """Quick one-off symbol execution"""
    vm = SISVM()
    symbol = SISSymbol(glyph, value, delta_contribution=delta)
    symbol.activate_all_layers()
    return vm.execute(symbol)
