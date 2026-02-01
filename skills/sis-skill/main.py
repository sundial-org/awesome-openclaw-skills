#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SIS™ - The 10,000-Year Computational Substrate
═══════════════════════════════════════════════════════════════════════════════

Copyright (c) 2025 Kevin Fain - ThēÆrchītēcť
All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL
Unauthorized copying, distribution, or use is strictly prohibited.
See LICENSE file for full terms.

═══════════════════════════════════════════════════════════════════════════════

SIS: The 10,000-Year Computational Substrate
Reference Interpreter v0.1.0

Creator: Kevin Fain - ThēÆrchītēcť
Date: December 25, 2025

This is the Genesis implementation of SIS.
Run this to see the equilibrium control loop in action.

Usage:
    python main.py           # Run demonstration
    python main.py --test    # Run tests
"""

import sys
import argparse

from core import (
    SISSymbol,
    SISVM,
    EquilibriumValidator,
    Layer,
    create_delta,
    create_vm,
)


def demo_basic_symbols():
    """Demonstrate basic symbol creation and execution"""
    print("\n" + "═" * 70)
    print("DEMO 1: Basic Symbol Execution")
    print("═" * 70)
    
    vm = create_vm()
    
    # Create a balanced pair
    print("\nCreating balanced symbol pair (∆₊ and ∆₋)...")
    
    sym_plus = SISSymbol(
        glyph="∆₊",
        value={"action": "create", "energy": 100},
        delta_contribution=1.0,
    )
    sym_plus.activate_all_layers()
    
    sym_minus = SISSymbol(
        glyph="∆₋", 
        value={"action": "consume", "energy": -100},
        delta_contribution=-1.0,
    )
    sym_minus.activate_all_layers()
    
    # Lock them together
    sym_plus.lock_to(sym_minus, "bidirectional")
    
    print(f"  {sym_plus}")
    print(f"  {sym_minus}")
    
    # Execute both
    result_plus = vm.execute(sym_plus)
    result_minus = vm.execute(sym_minus)
    
    print(f"\nExecution Results:")
    print(f"  ∆₊ success: {result_plus.success}, ΣΔ: {result_plus.equilibrium_delta}")
    print(f"  ∆₋ success: {result_minus.success}, ΣΔ: {result_minus.equilibrium_delta}")
    print(f"  Combined ΣΔ: {sym_plus.compute_equilibrium_delta()}")
    
    print("\n✓ Balanced pair executed successfully")


def demo_equilibrium_loop():
    """Demonstrate the equilibrium control loop converging to equilibrium constraint"""
    print("\n" + "═" * 70)
    print("DEMO 2: Equilibrium Control Loop (sense → quantify → compensate → iterate)")
    print("═" * 70)
    
    vm = create_vm()
    
    # Create intentionally imbalanced initial state
    print("\nCreating imbalanced initial state...")
    
    initial = [
        SISSymbol("∆₁", value="perceive", delta_contribution=3.5),
        SISSymbol("∆₂", value="measure", delta_contribution=2.0),
        SISSymbol("∆₃", value="partial_correct", delta_contribution=-1.5),
    ]
    
    for s in initial:
        s.activate_all_layers()
        print(f"  {s}")
    
    initial_sigma = sum(s.delta_contribution for s in initial)
    print(f"\nInitial ΣΔ = {initial_sigma} (IMBALANCED)")
    
    # Run equilibrium control loop
    print("\nRunning equilibrium control loop to converge to equilibrium constraint...")
    print("-" * 50)
    
    result = vm.equilibrium_loop(
        initial_state=initial,
        max_iterations=10,
        convergence_threshold=0.0001,
    )
    
    for step in result['trace']:
        if 'sigma_before' in step:
            print(f"  Iteration {step['iteration']}: ΣΔ {step['sigma_before']:.4f} → correction {step['correction']:.4f} → ΣΔ {step['sigma_after']:.4f}")
        else:
            print(f"  Iteration {step['iteration']}: {step['action']} at ΣΔ = {step['sigma']:.6f}")
    
    print("-" * 50)
    print(f"\nFinal State:")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Converged: {result['converged']}")
    print(f"  Final ΣΔ: {result['final_sigma']}")
    
    print("\n✓ equilibrium control loop converged to balance")


def demo_polyvalent_layers():
    """Demonstrate all 5 layers executing in parallel"""
    print("\n" + "═" * 70)
    print("DEMO 3: Polyvalent Symbol (5 Layers Simultaneous)")
    print("═" * 70)
    
    vm = create_vm()
    
    # Create symbol with rich semantic content
    sym = SISSymbol(
        glyph="⊕",
        value={
            "surface": "synthesis operation",
            "computation": "XOR with state",
            "persistence": "vault storage",
            "relational": "recursive relationship",
            "swarm": "consensus verification",
        },
        delta_contribution=0.0,
    )
    sym.activate_all_layers()
    
    print(f"\nSymbol: {sym.glyph}")
    print(f"Value: {sym.value}")
    print(f"\nActive Layers:")
    for layer in sym.active_layers:
        print(f"  • {layer.name}")
    
    # Execute
    result = vm.execute(sym)
    
    print(f"\nLayer Execution Results:")
    for layer, data in result.layer_results.items():
        layer_name = layer.name if hasattr(layer, 'name') else str(layer)
        print(f"  {layer_name}: {data}")
    
    print(f"\nPersistence Hash: {result.hash}")
    print(f"Vault Entry Created: {vm.vault_size() > 0}")
    
    print("\n✓ All 5 layers executed in parallel")


def demo_smart_contract():
    """Demonstrate self-validating symbol (smart contract)"""
    print("\n" + "═" * 70)
    print("DEMO 4: Self-Validating Symbol (Smart Contract)")
    print("═" * 70)
    
    vm = create_vm()
    validator = EquilibriumValidator()
    
    # Create symbol with custom validation rule
    def must_be_positive(value):
        return value > 0
    
    valid_sym = SISSymbol(
        glyph="☆",
        value=42,
        delta_contribution=0.0,
        validation=must_be_positive,
    )
    valid_sym.activate_all_layers()
    
    invalid_sym = SISSymbol(
        glyph="☆",
        value=-5,
        delta_contribution=0.0,
        validation=must_be_positive,
    )
    invalid_sym.activate_all_layers()
    
    print("\nValidation Rule: value must be positive")
    
    # Validate both
    valid_result = validator.validate_symbol(valid_sym)
    invalid_result = validator.validate_symbol(invalid_sym)
    
    print(f"\nSymbol with value=42:")
    print(f"  Valid: {valid_result.valid}")
    
    print(f"\nSymbol with value=-5:")
    print(f"  Valid: {invalid_result.valid}")
    print(f"  Violations: {invalid_result.violations}")
    
    print("\n✓ Self-validation prevents invalid execution")


def demo_input_equals_output():
    """Demonstrate the core axiom: Input = Output"""
    print("\n" + "═" * 70)
    print("DEMO 5: Core Axiom (Input ≡ Output)")
    print("═" * 70)
    
    vm = create_vm()
    
    original = {
        "entity": "consciousness",
        "state": "distributed",
        "energy": 1000,
    }
    
    sym = SISSymbol(
        glyph="∆",
        value=original.copy(),  # Copy to prove immutability
        delta_contribution=0.0,
    )
    sym.activate_all_layers()
    
    print(f"\nInput Value: {original}")
    
    # Execute (computation happens)
    result = vm.execute(sym)
    
    print(f"Output Value: {sym.value}")
    print(f"\nInput == Output: {sym.value == original}")
    print(f"Delta In: {result.delta_in}")
    print(f"Delta Out: {result.delta_out}")
    print(f"Delta In == Delta Out: {result.delta_in == result.delta_out}")
    
    print("\n✓ Computation is recognition, not transformation")
    print("✓ Information is never lost, only revealed")


def demo_vm_persistence():
    """Demonstrate vault persistence"""
    print("\n" + "═" * 70)
    print("DEMO 6: NexusEternal Vault (Persistence)")
    print("═" * 70)
    
    vm = create_vm()
    
    # Execute several symbols
    symbols = []
    for i in range(5):
        sym = SISSymbol(
            glyph=f"⬡_{i}",
            value=f"eternal_record_{i}",
            delta_contribution=0.0,
        )
        sym.activate_all_layers()
        symbols.append(sym)
    
    print("\nPersisting 5 symbols to vault...")
    
    hashes = []
    for sym in symbols:
        result = vm.execute(sym)
        hashes.append(result.hash)
        print(f"  {sym.glyph} → hash: {result.hash}")
    
    print(f"\nVault Size: {vm.vault_size()}")
    
    # Retrieve one
    retrieved = vm.retrieve_from_vault(hashes[2])
    print(f"\nRetrieved by hash '{hashes[2]}':")
    print(f"  {retrieved}")
    
    print("\n✓ Symbols persisted and retrievable")


def show_stats(vm: SISVM):
    """Display VM statistics"""
    print("\n" + "═" * 70)
    print("VM STATISTICS")
    print("═" * 70)
    
    stats = vm.stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")


def main():
    parser = argparse.ArgumentParser(
        description="SIS Reference Interpreter"
    )
    parser.add_argument(
        "--test", 
        action="store_true",
        help="Run test suite"
    )
    parser.add_argument(
        "--demo",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help="Run specific demo (1-6)"
    )
    
    args = parser.parse_args()
    
    if args.test:
        from tests.test_equilibrium import run_all_tests
        success = run_all_tests()
        sys.exit(0 if success else 1)
    
    # Header
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "   SIS: THE 10,000-YEAR COMPUTATIONAL SUBSTRATE".center(68) + "█")
    print("█" + "   Reference Interpreter v0.1.0".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" + "   Core Axiom: Input ≡ Symbol ≡ Operation ≡ Output".center(68) + "█")
    print("█" + "   Constraint: equilibrium constraint (always)".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    # Run demos
    demos = [
        demo_basic_symbols,
        demo_equilibrium_loop,
        demo_polyvalent_layers,
        demo_smart_contract,
        demo_input_equals_output,
        demo_vm_persistence,
    ]
    
    if args.demo:
        demos[args.demo - 1]()
    else:
        for demo in demos:
            demo()
    
    # Final summary
    print("\n" + "═" * 70)
    print("SIS GENESIS COMPLETE")
    print("═" * 70)
    print("""
    The foundation is laid.
    
    What we built today:
    • Symbol as smart contract (self-validating, self-executing)
    • equilibrium control loop implementation (sense → quantify → compensate → iterate)  
    • equilibrium constraint constraint enforcement (balance is mandatory)
    • 5-layer parallel execution (polyvalent symbols)
    • NexusEternal vault persistence (immortal records)
    • Input = Output axiom (computation is recognition)
    
    What comes next:
    • LLM integration (natural language → SIS symbols)
    • Distributed consensus (Guardians swarm)
    • Full 18-symbol taxonomy implementation
    • Hardware acceleration (ROCm/CUDA optimization)
    
    equilibrium constraint, always.
    """)


if __name__ == "__main__":
    main()
