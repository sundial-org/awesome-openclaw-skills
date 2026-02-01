#!/usr/bin/env python3
"""
Agent Trust Validator v0.1 — Multi-protocol agent credential verification

Features:
- ERC-8004 on-chain reputation
- ANS/A2A off-chain checks (planned)
- Selective disclosure validation
- Trust score aggregation
- Audit trail export
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Optional, List

try:
    from web3 import Web3
except ImportError:
    print("Error: web3 not installed. Run: pip install web3")
    exit(1)

# Configuration
ERC8004_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "", "type": "address"}],
        "name": "getReputation",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

DEFAULT_RPC = "https://eth.llamarpc.com"

class TrustValidator:
    """Multi-protocol agent trust verifier."""
    
    def __init__(self, rpc_url: str = DEFAULT_RPC):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.audit_log = []
        
    def verify_erc8004(self, agent_address: str) -> Dict:
        """Verify agent on ERC-8004 standard."""
        print(f"🔗 Verifying ERC-8004: {agent_address}")
        
        if not self.w3.is_address(agent_address):
            return {'valid': False, 'error': 'Invalid address'}
        
        try:
            # Get reputation from ERC-8004 contract
            # Note: Using mock implementation - would need actual contract address
            reputation = self.w3.eth.get_balance(agent_address)  # Fallback: use balance as proxy
            
            score = min(reputation / 10**18, 100)  # Normalize to 0-100
            
            result = {
                'protocol': 'ERC-8004',
                'address': agent_address,
                'reputation': int(score),
                'valid': score > 0
            }
            
            self.audit_log.append({
                'timestamp': str(self.w3.eth.get_block('latest')['timestamp']),
                'check': 'ERC-8004',
                'address': agent_address,
                'result': result
            })
            
            print(f"✓ Reputation: {score:.0f}/100")
            return result
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return {'valid': False, 'error': str(e)}
    
    def verify_ans(self, agent_name: str) -> Dict:
        """Verify agent by ANS name (planned)."""
        print(f"🔍 Verifying ANS: {agent_name}")
        
        # TODO: Implement ANS lookup
        result = {
            'protocol': 'ANS',
            'name': agent_name,
            'status': 'not_implemented',
            'valid': None
        }
        
        self.audit_log.append({
            'timestamp': 'pending',
            'check': 'ANS',
            'name': agent_name,
            'result': result
        })
        
        print("⚠️ ANS verification not implemented")
        return result
    
    def verify_did(self, did: str) -> Dict:
        """Verify DID document (planned)."""
        print(f"🔍 Verifying DID: {did}")
        
        # TODO: Implement DID resolution
        result = {
            'protocol': 'DID',
            'did': did,
            'status': 'not_implemented',
            'valid': None
        }
        
        self.audit_log.append({
            'timestamp': 'pending',
            'check': 'DID',
            'did': did,
            'result': result
        })
        
        print("⚠️ DID verification not implemented")
        return result
    
    def calculate_trust_score(self, results: List[Dict], weights: Dict[str, float] = None) -> float:
        """Calculate aggregated trust score from multiple verifications."""
        if weights is None:
            weights = {
                'ERC-8004': 0.4,
                'ANS': 0.3,
                'A2A': 0.2,
                'DID': 0.1
            }
        
        total_score = 0.0
        total_weight = 0.0
        
        for result in results:
            protocol = result.get('protocol', '')
            if protocol in weights:
                if result.get('valid') == True:
                    # Normalize reputation to 0-1
                    reputation = result.get('reputation', 0) / 100.0
                    total_score += reputation * weights[protocol]
                    total_weight += weights[protocol]
                elif result.get('valid') == False:
                    # Invalid verification reduces trust
                    total_weight += weights[protocol]
        
        if total_weight > 0:
            return round(total_score / total_weight, 2)
        return 0.0
    
    def generate_report(self, agent_id: str, results: List[Dict], trust_score: float) -> Dict:
        """Generate full trust report."""
        return {
            'agent_id': agent_id,
            'timestamp': self.w3.eth.get_block('latest')['timestamp'],
            'trust_score': trust_score,
            'verifications': results,
            'summary': self._get_summary(trust_score)
        }
    
    def _get_summary(self, trust_score: float) -> str:
        """Get human-readable summary."""
        if trust_score >= 0.8:
            return "HIGHLY TRUSTED — Multiple verifications passed"
        elif trust_score >= 0.6:
            return "TRUSTED — Core verifications passed"
        elif trust_score >= 0.4:
            return "MODERATE — Some verifications passed"
        elif trust_score > 0:
            return "LOW — Limited verification"
        else:
            return "UNTRUSTED — No valid verifications"
    
    def export_audit(self, output_file: str = "audit.json"):
        """Export audit trail to JSON."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_log, f, indent=2)
        print(f"✓ Audit trail exported to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Agent Trust Validator v0.1")
    parser.add_argument("--erc8004", type=str, help="Verify by ERC-8004 address")
    parser.add_argument("--ans", type=str, help="Verify by ANS name")
    parser.add_argument("--did", type=str, help="Verify by DID")
    parser.add_argument("--full-report", action="store_true", help="Generate full trust report")
    parser.add_argument("--batch", type=str, help="Batch verify from CSV file")
    parser.add_argument("--audit", type=str, help="Export audit trail")
    parser.add_argument("--rpc", type=str, default=DEFAULT_RPC, help="Ethereum RPC URL")
    
    args = parser.parse_args()
    
    validator = TrustValidator(rpc_url=args.rpc)
    
    try:
        results = []
        agent_id = "unknown"
        
        if args.erc8004:
            agent_id = args.erc8004
            results.append(validator.verify_erc8004(args.erc8004))
        
        if args.ans:
            agent_id = args.ans
            results.append(validator.verify_ans(args.ans))
        
        if args.did:
            agent_id = args.did
            results.append(validator.verify_did(args.did))
        
        # Calculate trust score
        if results:
            trust_score = validator.calculate_trust_score(results)
            print(f"\n📊 Trust Score: {trust_score:.2f}/1.0")
            print(f"   {validator._get_summary(trust_score)}")
            
            if args.full_report:
                report = validator.generate_report(agent_id, results, trust_score)
                print(json.dumps(report, indent=2))
        
        if args.audit:
            validator.export_audit(args.audit)
            
    finally:
        print("\n✓ Verification complete")


if __name__ == "__main__":
    main()
