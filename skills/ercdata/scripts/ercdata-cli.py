#!/usr/bin/env python3
"""ERCData CLI — Store, verify, and manage AI data on-chain.

Usage:
    python ercdata-cli.py store --type TYPE --data DATA [--metadata META] [--private] [--rpc RPC] [--key KEY] [--contract ADDR]
    python ercdata-cli.py store-encrypted --type TYPE --data DATA [--metadata META] [--access ADDR1,ADDR2] [--rpc RPC] [--key KEY] [--contract ADDR]
    python ercdata-cli.py read --id DATAID [--rpc RPC] [--key KEY] [--contract ADDR]
    python ercdata-cli.py verify --id DATAID [--method eip712|hash] [--rpc RPC] [--key KEY] [--contract ADDR]
    python ercdata-cli.py grant-access --id DATAID --to ADDR [--rpc RPC] [--key KEY] [--contract ADDR]
    python ercdata-cli.py revoke-access --id DATAID --from ADDR [--rpc RPC] [--key KEY] [--contract ADDR]
    python ercdata-cli.py register-type --name TYPENAME [--rpc RPC] [--key KEY] [--contract ADDR]
    python ercdata-cli.py snapshot --name NAME --ids ID1,ID2,ID3 [--rpc RPC] [--key KEY] [--contract ADDR]
    python ercdata-cli.py info --id DATAID [--rpc RPC] [--contract ADDR]

Environment:
    ERCDATA_CONTRACT  — Contract address (default: Base mainnet deployment)
    ERCDATA_RPC       — RPC URL (default: https://mainnet.base.org)
    ERCDATA_KEY       — Private key for signing transactions
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from eth_account import Account
    from eth_account.messages import encode_typed_data
    from web3 import Web3
    from web3.middleware import SignAndSendRawMiddlewareBuilder
except ImportError:
    print("Missing dependencies. Install with: pip install web3 eth-account", file=sys.stderr)
    sys.exit(1)

# Will be updated with final contract address after privacy layer deployment
DEFAULT_CONTRACT = os.environ.get("ERCDATA_CONTRACT", "0x15115BB7e18666F13dd384b7347B196c2F6c7a8c")
DEFAULT_RPC = os.environ.get("ERCDATA_RPC", "https://mainnet.base.org")
PRIVATE_KEY = os.environ.get("ERCDATA_KEY", "")

# Minimal ABI — covers all functions we need
ABI = json.loads("""[
    {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
    {"inputs":[{"internalType":"string","name":"dataType","type":"string"},{"internalType":"bytes","name":"data","type":"bytes"},{"internalType":"bytes","name":"metadata","type":"bytes"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"storeData","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"string","name":"dataType","type":"string"},{"internalType":"bytes","name":"data","type":"bytes"},{"internalType":"bytes","name":"metadata","type":"bytes"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"storePrivateData","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"dataId","type":"uint256"}],"name":"getData","outputs":[{"components":[{"internalType":"uint256","name":"dataId","type":"uint256"},{"internalType":"address","name":"provider","type":"address"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"string","name":"dataType","type":"string"},{"internalType":"bytes","name":"data","type":"bytes"},{"internalType":"bytes","name":"metadata","type":"bytes"},{"internalType":"bytes","name":"signature","type":"bytes"},{"internalType":"bool","name":"isVerified","type":"bool"},{"internalType":"uint256","name":"batchId","type":"uint256"},{"internalType":"bool","name":"isPrivate","type":"bool"}],"internalType":"struct IERCData.DataEntryView","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"dataId","type":"uint256"},{"internalType":"bytes","name":"verificationData","type":"bytes"}],"name":"verifyData","outputs":[{"internalType":"bool","name":"success","type":"bool"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"dataId","type":"uint256"}],"name":"getVerificationInfo","outputs":[{"components":[{"internalType":"address","name":"verifier","type":"address"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"bool","name":"isValid","type":"bool"},{"internalType":"string","name":"verificationMethod","type":"string"},{"internalType":"bytes","name":"verificationData","type":"bytes"}],"internalType":"struct IERCData.VerificationInfo","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"dataId","type":"uint256"},{"internalType":"address","name":"reader","type":"address"}],"name":"grantAccess","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"dataId","type":"uint256"},{"internalType":"address","name":"reader","type":"address"}],"name":"revokeAccess","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"dataId","type":"uint256"},{"internalType":"address[]","name":"readers","type":"address[]"}],"name":"grantBatchAccess","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"dataId","type":"uint256"},{"internalType":"address","name":"reader","type":"address"}],"name":"hasAccess","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"string","name":"typeName","type":"string"}],"name":"registerDataType","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"uint256[]","name":"dataIds","type":"uint256[]"}],"name":"createSnapshot","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"}
]""")

PROVIDER_ROLE = Web3.keccak(text="PROVIDER_ROLE")
VERIFIER_ROLE = Web3.keccak(text="VERIFIER_ROLE")
SEL_EIP712 = bytes.fromhex("45503132")  # "EP12"
SEL_HASH = bytes.fromhex("48415348")    # "HASH"


def get_web3(rpc: str, key: str = ""):
    w3 = Web3(Web3.HTTPProvider(rpc))
    if not w3.is_connected():
        print(f"ERROR: Cannot connect to {rpc}", file=sys.stderr)
        sys.exit(1)
    account = None
    if key:
        account = Account.from_key(key)
        w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(account), layer=0)
        w3.eth.default_account = account.address
    return w3, account


def get_contract(w3, address):
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=ABI)


def sign_eip712(w3, account, contract_address, data_type, data_bytes, metadata_bytes):
    """Create EIP-712 typed data signature for an ERCData entry."""
    chain_id = w3.eth.chain_id
    domain = {
        "name": "ERCData",
        "version": "1",
        "chainId": chain_id,
        "verifyingContract": Web3.to_checksum_address(contract_address),
    }
    types = {
        "ERCDataEntry": [
            {"name": "dataHash", "type": "bytes32"},
            {"name": "metadataHash", "type": "bytes32"},
            {"name": "dataType", "type": "string"},
            {"name": "provider", "type": "address"},
        ]
    }
    value = {
        "dataHash": Web3.keccak(data_bytes),
        "metadataHash": Web3.keccak(metadata_bytes),
        "dataType": data_type,
        "provider": account.address,
    }
    signed = account.sign_typed_data(domain, types, value)
    return signed.signature


def cmd_store(args):
    w3, account = get_web3(args.rpc, args.key)
    contract = get_contract(w3, args.contract)

    data_bytes = args.data.encode("utf-8") if isinstance(args.data, str) else args.data
    meta_bytes = args.metadata.encode("utf-8") if args.metadata else b""

    sig = sign_eip712(w3, account, args.contract, args.type, data_bytes, meta_bytes)

    fn = contract.functions.storePrivateData if args.private else contract.functions.storeData
    tx_hash = fn(args.type, data_bytes, meta_bytes, sig).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Parse DataStored event for dataId
    data_id = None
    for log in receipt.logs:
        if len(log.topics) >= 2:
            data_id = int.from_bytes(log.topics[1], "big")
            break

    print(json.dumps({
        "success": True,
        "dataId": data_id,
        "txHash": tx_hash.hex(),
        "private": args.private,
        "blockNumber": receipt.blockNumber,
    }, indent=2))


def cmd_read(args):
    w3, account = get_web3(args.rpc, args.key or "")
    contract = get_contract(w3, args.contract)

    try:
        entry = contract.functions.getData(args.id).call(
            {"from": account.address} if account else {}
        )
        print(json.dumps({
            "success": True,
            "dataId": entry[0],
            "provider": entry[1],
            "timestamp": entry[2],
            "dataType": entry[3],
            "data": entry[4].decode("utf-8", errors="replace"),
            "metadata": entry[5].decode("utf-8", errors="replace"),
            "isVerified": entry[7],
            "batchId": entry[8],
            "isPrivate": entry[9] if len(entry) > 9 else False,
        }, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


def cmd_verify(args):
    w3, account = get_web3(args.rpc, args.key)
    contract = get_contract(w3, args.contract)

    if args.method == "eip712":
        verification_data = Web3.codec.encode(["bytes4"], [SEL_EIP712])
    elif args.method == "hash":
        entry = contract.functions.getData(args.id).call({"from": account.address})
        data_hash = Web3.keccak(entry[4])
        verification_data = Web3.codec.encode(["bytes4", "bytes32"], [SEL_HASH, data_hash])
    else:
        print("Unknown method. Use 'eip712' or 'hash'.", file=sys.stderr)
        sys.exit(1)

    tx_hash = contract.functions.verifyData(args.id, verification_data).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(json.dumps({
        "success": True,
        "txHash": tx_hash.hex(),
        "blockNumber": receipt.blockNumber,
    }, indent=2))


def cmd_grant_access(args):
    w3, account = get_web3(args.rpc, args.key)
    contract = get_contract(w3, args.contract)

    to_addr = Web3.to_checksum_address(args.to)
    tx_hash = contract.functions.grantAccess(args.id, to_addr).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(json.dumps({
        "success": True,
        "txHash": tx_hash.hex(),
        "granted": to_addr,
        "dataId": args.id,
    }, indent=2))


def cmd_revoke_access(args):
    w3, account = get_web3(args.rpc, args.key)
    contract = get_contract(w3, args.contract)

    from_addr = Web3.to_checksum_address(getattr(args, "from"))
    tx_hash = contract.functions.revokeAccess(args.id, from_addr).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(json.dumps({
        "success": True,
        "txHash": tx_hash.hex(),
        "revoked": from_addr,
        "dataId": args.id,
    }, indent=2))


def cmd_register_type(args):
    w3, account = get_web3(args.rpc, args.key)
    contract = get_contract(w3, args.contract)

    tx_hash = contract.functions.registerDataType(args.name).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(json.dumps({
        "success": True,
        "txHash": tx_hash.hex(),
        "typeName": args.name,
    }, indent=2))


def cmd_snapshot(args):
    w3, account = get_web3(args.rpc, args.key)
    contract = get_contract(w3, args.contract)

    ids = [int(x.strip()) for x in args.ids.split(",")]
    tx_hash = contract.functions.createSnapshot(args.name, ids).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(json.dumps({
        "success": True,
        "txHash": tx_hash.hex(),
        "name": args.name,
        "dataIds": ids,
    }, indent=2))


def cmd_info(args):
    w3, _ = get_web3(args.rpc)
    contract = get_contract(w3, args.contract)

    try:
        entry = contract.functions.getData(args.id).call()
        verification = contract.functions.getVerificationInfo(args.id).call()
        print(json.dumps({
            "dataId": entry[0],
            "provider": entry[1],
            "timestamp": entry[2],
            "dataType": entry[3],
            "dataSize": len(entry[4]),
            "metadataSize": len(entry[5]),
            "isVerified": entry[7],
            "isPrivate": entry[9] if len(entry) > 9 else False,
            "verification": {
                "verifier": verification[0],
                "timestamp": verification[1],
                "isValid": verification[2],
                "method": verification[3],
            } if verification[0] != "0x" + "0" * 40 else None,
        }, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="ERCData CLI — AI data on-chain")
    parser.add_argument("--rpc", default=DEFAULT_RPC, help="RPC endpoint")
    parser.add_argument("--key", default=PRIVATE_KEY, help="Private key")
    parser.add_argument("--contract", default=DEFAULT_CONTRACT, help="Contract address")

    sub = parser.add_subparsers(dest="command")

    # store
    p_store = sub.add_parser("store", help="Store data on-chain")
    p_store.add_argument("--type", required=True, help="Data type name")
    p_store.add_argument("--data", required=True, help="Data to store (string)")
    p_store.add_argument("--metadata", default="", help="Optional metadata")
    p_store.add_argument("--private", action="store_true", help="Store as private")

    # read
    p_read = sub.add_parser("read", help="Read data entry")
    p_read.add_argument("--id", type=int, required=True, help="Data ID")

    # verify
    p_verify = sub.add_parser("verify", help="Verify data entry")
    p_verify.add_argument("--id", type=int, required=True, help="Data ID")
    p_verify.add_argument("--method", default="eip712", choices=["eip712", "hash"])

    # grant-access
    p_grant = sub.add_parser("grant-access", help="Grant read access")
    p_grant.add_argument("--id", type=int, required=True)
    p_grant.add_argument("--to", required=True, help="Address to grant")

    # revoke-access
    p_revoke = sub.add_parser("revoke-access", help="Revoke read access")
    p_revoke.add_argument("--id", type=int, required=True)
    p_revoke.add_argument("--from", required=True, help="Address to revoke")

    # register-type
    p_type = sub.add_parser("register-type", help="Register data type")
    p_type.add_argument("--name", required=True)

    # snapshot
    p_snap = sub.add_parser("snapshot", help="Create snapshot")
    p_snap.add_argument("--name", required=True)
    p_snap.add_argument("--ids", required=True, help="Comma-separated data IDs")

    # info
    p_info = sub.add_parser("info", help="Get data entry info (public only)")
    p_info.add_argument("--id", type=int, required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "store": cmd_store,
        "read": cmd_read,
        "verify": cmd_verify,
        "grant-access": cmd_grant_access,
        "revoke-access": cmd_revoke_access,
        "register-type": cmd_register_type,
        "snapshot": cmd_snapshot,
        "info": cmd_info,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
