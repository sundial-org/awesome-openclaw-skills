#!/usr/bin/env python3
"""skillsign — Sign and verify skill folders with ed25519 keys.

Usage:
  skillsign keygen [--name NAME]              Generate a new ed25519 keypair
  skillsign sign <folder> [--key KEYFILE]      Sign a skill folder
  skillsign verify <folder>                    Verify a skill folder's signature
  skillsign inspect <folder>                   Inspect signature metadata
  skillsign trust <pubkey-file>                Add a public key to trusted authors
  skillsign trusted                            List trusted public keys
  skillsign chain <folder>                     Show the full isnad (provenance chain)
  skillsign revoke [--key KEYFILE] [--reason]  Revoke a signing key
  skillsign revoked                            List all revoked keys

The signature covers every file in the folder (excluding .skillsig/).
A .skillsig/ directory is created inside the skill folder containing:
  - manifest.json   (sorted file hashes)
  - signature.bin   (ed25519 signature of the manifest)
  - signer.json     (author metadata + public key)
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
except ImportError:
    print("Error: 'cryptography' package required. Run: pip install cryptography")
    sys.exit(1)

SKILLSIG_DIR = ".skillsig"
TRUST_DIR = Path.home() / ".skillsign" / "trusted"
KEYS_DIR = Path.home() / ".skillsign" / "keys"
REVOKED_DIR = Path.home() / ".skillsign" / "revoked"


# ─── Helpers ───────────────────────────────────────────────────────────────

def hash_file(path: Path) -> str:
    """SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(folder: Path) -> dict:
    """Build a sorted dict of relative_path -> sha256 for all files in folder."""
    manifest = {}
    for root, dirs, files in os.walk(folder):
        # Skip the signature directory itself
        dirs[:] = [d for d in dirs if d != SKILLSIG_DIR]
        for fname in sorted(files):
            fpath = Path(root) / fname
            rel = fpath.relative_to(folder)
            manifest[str(rel)] = hash_file(fpath)
    return dict(sorted(manifest.items()))


def manifest_bytes(manifest: dict) -> bytes:
    """Canonical JSON bytes of the manifest for signing."""
    return json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load_private_key(keyfile: Path) -> Ed25519PrivateKey:
    with open(keyfile, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key_bytes(data: bytes) -> Ed25519PublicKey:
    return serialization.load_pem_public_key(data)


def pubkey_fingerprint(pub: Ed25519PublicKey) -> str:
    """Short fingerprint of a public key."""
    raw = pub.public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    return hashlib.sha256(raw).hexdigest()[:16]


def get_default_key() -> Path:
    """Return the default private key path, or None."""
    if not KEYS_DIR.exists():
        return None
    keys = list(KEYS_DIR.glob("*.pem"))
    if not keys:
        return None
    # Prefer one named 'default.pem'
    default = KEYS_DIR / "default.pem"
    return default if default.exists() else keys[0]


# ─── Commands ──────────────────────────────────────────────────────────────

def cmd_keygen(args):
    """Generate a new ed25519 keypair."""
    name = args.name or "default"
    KEYS_DIR.mkdir(parents=True, exist_ok=True)

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Save private key
    priv_path = KEYS_DIR / f"{name}.pem"
    with open(priv_path, "wb") as f:
        f.write(private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ))
    os.chmod(priv_path, 0o600)

    # Save public key
    pub_path = KEYS_DIR / f"{name}.pub"
    with open(pub_path, "wb") as f:
        f.write(public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ))

    fp = pubkey_fingerprint(public_key)
    print(f"Keypair generated:")
    print(f"  Private: {priv_path}")
    print(f"  Public:  {pub_path}")
    print(f"  Fingerprint: {fp}")
    print(f"\nShare {pub_path} with others so they can verify your signatures.")
    print(f"Keep {priv_path} secret.")


def cmd_sign(args):
    """Sign a skill folder."""
    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        print(f"Error: {folder} is not a directory.")
        sys.exit(1)

    # Find key
    if args.key:
        keyfile = Path(args.key)
    else:
        keyfile = get_default_key()
    if not keyfile or not keyfile.exists():
        print("Error: No private key found. Run 'skillsign keygen' first.")
        sys.exit(1)

    private_key = load_private_key(keyfile)
    public_key = private_key.public_key()

    # Build manifest
    manifest = build_manifest(folder)
    if not manifest:
        print("Error: Folder is empty.")
        sys.exit(1)

    # Sign
    data = manifest_bytes(manifest)
    signature = private_key.sign(data)

    # Write .skillsig/
    sig_dir = folder / SKILLSIG_DIR
    sig_dir.mkdir(exist_ok=True)

    # manifest.json
    with open(sig_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    # signature.bin
    with open(sig_dir / "signature.bin", "wb") as f:
        f.write(signature)

    # signer.json (metadata)
    pub_pem = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    fp = pubkey_fingerprint(public_key)

    signer_info = {
        "fingerprint": fp,
        "public_key": pub_pem,
        "signed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files_signed": len(manifest),
        "tool": "skillsign v1.0.0",
    }

    # Preserve chain if previous signature exists
    chain_path = sig_dir / "chain.json"
    chain = []
    if chain_path.exists():
        with open(chain_path) as f:
            chain = json.load(f)

    chain.append({
        "fingerprint": fp,
        "action": "sign",
        "timestamp": signer_info["signed_at"],
        "files": len(manifest),
    })

    with open(sig_dir / "signer.json", "w") as f:
        json.dump(signer_info, f, indent=2)

    with open(chain_path, "w") as f:
        json.dump(chain, f, indent=2)

    print(f"✅ Signed {len(manifest)} files in {folder.name}/")
    print(f"   Signer: {fp}")
    print(f"   Signature: {sig_dir / 'signature.bin'}")


def cmd_verify(args):
    """Verify a skill folder's signature."""
    folder = Path(args.folder).resolve()
    sig_dir = folder / SKILLSIG_DIR

    if not sig_dir.exists():
        print(f"❌ No signature found in {folder.name}/")
        sys.exit(1)

    # Load signer info
    with open(sig_dir / "signer.json") as f:
        signer = json.load(f)

    # Load stored manifest
    with open(sig_dir / "manifest.json") as f:
        stored_manifest = json.load(f)

    # Load signature
    with open(sig_dir / "signature.bin", "rb") as f:
        signature = f.read()

    # Rebuild manifest from current files
    current_manifest = build_manifest(folder)

    # Check for tampering
    added = set(current_manifest.keys()) - set(stored_manifest.keys())
    removed = set(stored_manifest.keys()) - set(current_manifest.keys())
    modified = {
        k for k in set(current_manifest.keys()) & set(stored_manifest.keys())
        if current_manifest[k] != stored_manifest[k]
    }

    if added or removed or modified:
        print(f"❌ TAMPERED — Files changed since signing:")
        for f in sorted(added):
            print(f"   + {f} (added)")
        for f in sorted(removed):
            print(f"   - {f} (removed)")
        for f in sorted(modified):
            print(f"   ~ {f} (modified)")
        sys.exit(1)

    # Verify cryptographic signature
    pub_key = load_public_key_bytes(signer["public_key"].encode("utf-8"))
    data = manifest_bytes(stored_manifest)

    try:
        pub_key.verify(signature, data)
    except InvalidSignature:
        print(f"❌ INVALID SIGNATURE — manifest matches but signature is forged.")
        sys.exit(1)

    # Check revocation
    fp = signer["fingerprint"]
    revoked, rev_info = is_revoked_at(fp, signer.get("signed_at", ""))
    if revoked:
        print(f"🔴 REVOKED — Signer {fp} was revoked.")
        print(f"   Revoked at: {rev_info['revoked_at']}")
        print(f"   Reason: {rev_info['reason']}")
        print(f"   Signed at: {signer.get('signed_at', 'unknown')}")
        print(f"   Signatures after revocation are not trustworthy.")
        sys.exit(1)

    # Check trust
    trusted = is_trusted(fp)
    trust_label = "TRUSTED" if trusted else "UNTRUSTED"

    print(f"✅ Verified — {len(stored_manifest)} files intact.")
    print(f"   Signer: {fp} [{trust_label}]")
    print(f"   Signed at: {signer['signed_at']}")

    if rev_info and not revoked:
        print(f"   ⚠️  Signer was later revoked ({rev_info['revoked_at']}), but this signature predates revocation.")

    if not trusted:
        print(f"\n   ⚠️  Signer is not in your trusted authors list.")
        print(f"   Run: skillsign trust <pubkey-file> to add them.")


def cmd_inspect(args):
    """Inspect signature metadata without full verification."""
    folder = Path(args.folder).resolve()
    sig_dir = folder / SKILLSIG_DIR

    if not sig_dir.exists():
        print(f"No signature found in {folder.name}/")
        sys.exit(1)

    with open(sig_dir / "signer.json") as f:
        signer = json.load(f)

    with open(sig_dir / "manifest.json") as f:
        manifest = json.load(f)

    fp = signer["fingerprint"]
    trusted = is_trusted(fp)

    print(f"=== Signature: {folder.name}/ ===")
    print(f"  Signer:     {fp} [{'TRUSTED' if trusted else 'UNTRUSTED'}]")
    print(f"  Signed at:  {signer.get('signed_at', 'unknown')}")
    print(f"  Files:      {len(manifest)}")
    print(f"  Tool:       {signer.get('tool', 'unknown')}")
    print()
    print("  Files covered:")
    for path, h in manifest.items():
        print(f"    {path}: {h[:12]}...")


def cmd_trust(args):
    """Add a public key to the trusted authors list."""
    pub_path = Path(args.pubkey_file)
    if not pub_path.exists():
        print(f"Error: {pub_path} not found.")
        sys.exit(1)

    with open(pub_path, "rb") as f:
        pub_data = f.read()

    pub_key = load_public_key_bytes(pub_data)
    fp = pubkey_fingerprint(pub_key)

    TRUST_DIR.mkdir(parents=True, exist_ok=True)
    dest = TRUST_DIR / f"{fp}.pub"
    with open(dest, "wb") as f:
        f.write(pub_data)

    print(f"✅ Trusted: {fp}")
    print(f"   Stored: {dest}")


def cmd_trusted(args):
    """List trusted public keys."""
    if not TRUST_DIR.exists():
        print("No trusted keys. Run: skillsign trust <pubkey-file>")
        return

    keys = list(TRUST_DIR.glob("*.pub"))
    if not keys:
        print("No trusted keys.")
        return

    print(f"=== Trusted Authors ({len(keys)}) ===")
    for k in sorted(keys):
        print(f"  {k.stem}")


def cmd_chain(args):
    """Show the full isnad (provenance chain)."""
    folder = Path(args.folder).resolve()
    chain_path = folder / SKILLSIG_DIR / "chain.json"

    if not chain_path.exists():
        print(f"No provenance chain found in {folder.name}/")
        sys.exit(1)

    with open(chain_path) as f:
        chain = json.load(f)

    print(f"=== Isnād: {folder.name}/ ({len(chain)} links) ===")
    for i, link in enumerate(chain):
        trusted = is_trusted(link["fingerprint"])
        trust = "TRUSTED" if trusted else "UNTRUSTED"
        print(f"  [{i+1}] {link['fingerprint']} [{trust}]")
        print(f"      Action: {link['action']}")
        print(f"      Time:   {link['timestamp']}")
        print(f"      Files:  {link['files']}")
        if i < len(chain) - 1:
            print(f"      ↓")


def is_trusted(fingerprint: str) -> bool:
    """Check if a fingerprint is in the trusted authors list."""
    if not TRUST_DIR.exists():
        return False
    return (TRUST_DIR / f"{fingerprint}.pub").exists()


def get_revocation(fingerprint: str) -> dict | None:
    """Return revocation info for a fingerprint, or None if not revoked."""
    revoke_path = REVOKED_DIR / f"{fingerprint}.json"
    if not revoke_path.exists():
        return None
    with open(revoke_path) as f:
        return json.load(f)


def is_revoked_at(fingerprint: str, signed_at: str) -> tuple[bool, dict | None]:
    """Check if a key was revoked at the time of signing.
    Returns (is_revoked, revocation_info)."""
    rev = get_revocation(fingerprint)
    if rev is None:
        return False, None
    # If signed_at is after revocation timestamp, the signature is invalid
    return signed_at >= rev["revoked_at"], rev


def cmd_revoke(args):
    """Revoke a signing key."""
    # Find the private key to create a self-signed revocation
    if args.key:
        keyfile = Path(args.key)
    else:
        keyfile = get_default_key()
    if not keyfile or not keyfile.exists():
        print("Error: No private key found. Provide --key or run 'skillsign keygen' first.")
        sys.exit(1)

    private_key = load_private_key(keyfile)
    public_key = private_key.public_key()
    fp = pubkey_fingerprint(public_key)

    # Check if already revoked
    if get_revocation(fp) is not None:
        print(f"Key {fp} is already revoked.")
        sys.exit(1)

    reason = args.reason or "Key compromised"
    revoked_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Create revocation statement
    revocation = {
        "fingerprint": fp,
        "revoked_at": revoked_at,
        "reason": reason,
        "tool": "skillsign v1.1.0",
    }

    # Sign the revocation statement with the key being revoked (proof of ownership)
    rev_bytes = json.dumps(revocation, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = private_key.sign(rev_bytes)

    revocation["signature"] = signature.hex()
    revocation["public_key"] = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    # Store revocation
    REVOKED_DIR.mkdir(parents=True, exist_ok=True)
    with open(REVOKED_DIR / f"{fp}.json", "w") as f:
        json.dump(revocation, f, indent=2)

    # Remove from trusted if present
    trusted_path = TRUST_DIR / f"{fp}.pub"
    if trusted_path.exists():
        trusted_path.unlink()
        print(f"   Removed from trusted authors.")

    print(f"🔴 Revoked: {fp}")
    print(f"   Reason: {reason}")
    print(f"   Time: {revoked_at}")
    print(f"   Signatures made after this timestamp will fail verification.")


def cmd_revoked(args):
    """List all revoked keys."""
    if not REVOKED_DIR.exists():
        print("No revoked keys.")
        return

    revs = list(REVOKED_DIR.glob("*.json"))
    if not revs:
        print("No revoked keys.")
        return

    print(f"=== Revoked Keys ({len(revs)}) ===")
    for r in sorted(revs):
        with open(r) as f:
            rev = json.load(f)
        print(f"  {rev['fingerprint']}")
        print(f"    Revoked: {rev['revoked_at']}")
        print(f"    Reason:  {rev['reason']}")


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="skillsign",
        description="Sign and verify skill folders with ed25519 keys.",
    )
    sub = parser.add_subparsers(dest="command")

    # keygen
    p_kg = sub.add_parser("keygen", help="Generate a new ed25519 keypair")
    p_kg.add_argument("--name", default="default", help="Key name (default: 'default')")

    # sign
    p_sign = sub.add_parser("sign", help="Sign a skill folder")
    p_sign.add_argument("folder", help="Path to the skill folder")
    p_sign.add_argument("--key", help="Path to private key (default: auto-detect)")

    # verify
    p_ver = sub.add_parser("verify", help="Verify a skill folder's signature")
    p_ver.add_argument("folder", help="Path to the skill folder")

    # inspect
    p_ins = sub.add_parser("inspect", help="Inspect signature metadata")
    p_ins.add_argument("folder", help="Path to the skill folder")

    # trust
    p_trust = sub.add_parser("trust", help="Add a public key to trusted authors")
    p_trust.add_argument("pubkey_file", help="Path to .pub file")

    # trusted
    sub.add_parser("trusted", help="List trusted public keys")

    # chain
    p_chain = sub.add_parser("chain", help="Show the full isnād (provenance chain)")
    p_chain.add_argument("folder", help="Path to the skill folder")

    # revoke
    p_revoke = sub.add_parser("revoke", help="Revoke a signing key")
    p_revoke.add_argument("--key", help="Path to private key to revoke")
    p_revoke.add_argument("--reason", default="Key compromised", help="Reason for revocation")

    # revoked
    sub.add_parser("revoked", help="List all revoked keys")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "keygen": cmd_keygen,
        "sign": cmd_sign,
        "verify": cmd_verify,
        "inspect": cmd_inspect,
        "trust": cmd_trust,
        "trusted": cmd_trusted,
        "chain": cmd_chain,
        "revoke": cmd_revoke,
        "revoked": cmd_revoked,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
