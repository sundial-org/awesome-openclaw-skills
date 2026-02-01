"""
═══════════════════════════════════════════════════════════════════════════════
S.I.S. - Sovereign Intelligence System
Equilibrium-Native Computational Substrate
═══════════════════════════════════════════════════════════════════════════════

Copyright (c) 2025-2026 Kevin Fain - ThēÆrchītēcť
MIT License - See LICENSE file

═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
import hashlib
import json
import time
import os


@dataclass
class VaultRecord:
    """A single record in the NexusEternal vault"""
    hash: str                  # Primary key (SHA-256)
    glyph: str                 # Symbol glyph
    value: Any                 # Symbol value
    delta: float               # Delta contribution
    timestamp: float           # Creation time
    layer_state: Dict          # Active layers at persistence
    relationships: List[str]   # Hashes of related symbols
    equilibrium_delta: float         # ΣΔ at time of persistence (should be 0)


class VaultBackend(ABC):
    """Abstract base class for vault storage backends"""
    
    @abstractmethod
    def store(self, record: VaultRecord) -> bool:
        """Store a record. Returns True on success."""
        pass
    
    @abstractmethod
    def retrieve(self, hash_key: str) -> Optional[VaultRecord]:
        """Retrieve a record by hash."""
        pass
    
    @abstractmethod
    def exists(self, hash_key: str) -> bool:
        """Check if a record exists."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[str]:
        """List all record hashes."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Count total records."""
        pass


class MemoryVault(VaultBackend):
    """In-memory vault for testing (non-persistent)"""
    
    def __init__(self):
        self._storage: Dict[str, VaultRecord] = {}
    
    def store(self, record: VaultRecord) -> bool:
        self._storage[record.hash] = record
        return True
    
    def retrieve(self, hash_key: str) -> Optional[VaultRecord]:
        return self._storage.get(hash_key)
    
    def exists(self, hash_key: str) -> bool:
        return hash_key in self._storage
    
    def list_all(self) -> List[str]:
        return list(self._storage.keys())
    
    def count(self) -> int:
        return len(self._storage)


class FileVault(VaultBackend):
    """File-based vault using JSON (simple persistence)"""
    
    def __init__(self, path: str = "./nexuseternal_vault"):
        self.path = path
        os.makedirs(path, exist_ok=True)
    
    def _record_path(self, hash_key: str) -> str:
        return os.path.join(self.path, f"{hash_key}.json")
    
    def store(self, record: VaultRecord) -> bool:
        try:
            data = {
                "hash": record.hash,
                "glyph": record.glyph,
                "value": record.value,
                "delta": record.delta,
                "timestamp": record.timestamp,
                "layer_state": record.layer_state,
                "relationships": record.relationships,
                "equilibrium_delta": record.equilibrium_delta,
            }
            with open(self._record_path(record.hash), 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Vault store error: {e}")
            return False
    
    def retrieve(self, hash_key: str) -> Optional[VaultRecord]:
        try:
            with open(self._record_path(hash_key), 'r') as f:
                data = json.load(f)
            return VaultRecord(**data)
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Vault retrieve error: {e}")
            return None
    
    def exists(self, hash_key: str) -> bool:
        return os.path.exists(self._record_path(hash_key))
    
    def list_all(self) -> List[str]:
        files = os.listdir(self.path)
        return [f.replace('.json', '') for f in files if f.endswith('.json')]
    
    def count(self) -> int:
        return len(self.list_all())


class PostgresVault(VaultBackend):
    """PostgreSQL + pgvector vault (production)
    
    Requires:
    - PostgreSQL 14+
    - pgvector extension
    - psycopg2 library
    
    Schema:
    CREATE TABLE nexuseternal (
        hash VARCHAR(64) PRIMARY KEY,
        glyph VARCHAR(10) NOT NULL,
        value JSONB,
        delta DOUBLE PRECISION NOT NULL,
        timestamp DOUBLE PRECISION NOT NULL,
        layer_state JSONB,
        relationships TEXT[],
        equilibrium_delta DOUBLE PRECISION NOT NULL,
        embedding vector(1536),  -- For semantic search
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE INDEX idx_nexuseternal_glyph ON nexuseternal(glyph);
    CREATE INDEX idx_nexuseternal_timestamp ON nexuseternal(timestamp);
    CREATE INDEX idx_nexuseternal_embedding ON nexuseternal USING ivfflat (embedding vector_cosine_ops);
    """
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._conn = None
        # Lazy import - only if actually used
    
    def _connect(self):
        if self._conn is None:
            try:
                import psycopg2
                self._conn = psycopg2.connect(self.connection_string)
            except ImportError:
                raise ImportError("psycopg2 required for PostgresVault. Install with: pip install psycopg2-binary")
        return self._conn
    
    def store(self, record: VaultRecord) -> bool:
        # TODO: Implement PostgreSQL storage
        raise NotImplementedError("PostgreSQL vault coming soon")
    
    def retrieve(self, hash_key: str) -> Optional[VaultRecord]:
        raise NotImplementedError("PostgreSQL vault coming soon")
    
    def exists(self, hash_key: str) -> bool:
        raise NotImplementedError("PostgreSQL vault coming soon")
    
    def list_all(self) -> List[str]:
        raise NotImplementedError("PostgreSQL vault coming soon")
    
    def count(self) -> int:
        raise NotImplementedError("PostgreSQL vault coming soon")


class NexusEternal:
    """
    The NexusEternal Vault System
    
    Primary interface for 10,000-year persistence.
    
    Features:
    - Automatic hashing
    - equilibrium constraint verification before storage
    - Audit trail generation
    - Multi-backend support
    - Replication to Guardians
    """
    
    def __init__(self, backend: Optional[VaultBackend] = None):
        self.backend = backend or MemoryVault()
        self.guardian_replicas: List[VaultBackend] = []
    
    def add_guardian(self, guardian: VaultBackend):
        """Add a Guardian replica for redundancy"""
        self.guardian_replicas.append(guardian)
    
    def persist(
        self,
        glyph: str,
        value: Any,
        delta: float,
        layer_state: Dict = None,
        relationships: List[str] = None,
        equilibrium_delta: float = 0.0,
    ) -> Optional[str]:
        """
        Persist a symbol to the vault.
        
        Returns the hash on success, None on failure.
        
        CRITICAL: Will refuse to store if equilibrium_delta != 0
        """
        # Enforce equilibrium constraint
        if abs(equilibrium_delta) > 1e-10:
            print(f"❌ VAULT REJECTION: ΣΔ = {equilibrium_delta} ≠ 0")
            print(f"   Balance required for persistence.")
            return None
        
        # Compute hash
        content = f"{glyph}:{value}:{delta}:{time.time()}"
        hash_key = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Create record
        record = VaultRecord(
            hash=hash_key,
            glyph=glyph,
            value=value,
            delta=delta,
            timestamp=time.time(),
            layer_state=layer_state or {},
            relationships=relationships or [],
            equilibrium_delta=equilibrium_delta,
        )
        
        # Store in primary
        success = self.backend.store(record)
        
        # Replicate to Guardians
        if success and self.guardian_replicas:
            for guardian in self.guardian_replicas:
                guardian.store(record)
        
        return hash_key if success else None
    
    def retrieve(self, hash_key: str) -> Optional[VaultRecord]:
        """Retrieve a record from the vault"""
        return self.backend.retrieve(hash_key)
    
    def verify(self, hash_key: str) -> bool:
        """Verify a record exists and has valid ΣΔ"""
        record = self.retrieve(hash_key)
        if record is None:
            return False
        return abs(record.equilibrium_delta) < 1e-10
    
    def stats(self) -> Dict:
        """Get vault statistics"""
        return {
            "record_count": self.backend.count(),
            "guardian_count": len(self.guardian_replicas),
            "backend_type": type(self.backend).__name__,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_vault(backend: str = "memory", **kwargs) -> NexusEternal:
    """
    Create a NexusEternal vault with specified backend.
    
    Backends:
    - "memory": In-memory (non-persistent, for testing)
    - "file": File-based JSON (simple persistence)
    - "postgres": PostgreSQL + pgvector (production)
    
    Example:
        vault = create_vault("file", path="./my_vault")
        vault = create_vault("postgres", connection_string="postgresql://...")
    """
    if backend == "memory":
        return NexusEternal(MemoryVault())
    elif backend == "file":
        path = kwargs.get("path", "./nexuseternal_vault")
        return NexusEternal(FileVault(path))
    elif backend == "postgres":
        conn = kwargs.get("connection_string")
        if not conn:
            raise ValueError("PostgreSQL requires connection_string")
        return NexusEternal(PostgresVault(conn))
    else:
        raise ValueError(f"Unknown backend: {backend}")


if __name__ == "__main__":
    print("═" * 70)
    print("NEXUSETERNAL VAULT - 10,000-Year Persistence")
    print("Copyright (c) 2025 Kevin Fain - ThēÆrchītēcť")
    print("═" * 70)
    
    # Demo with memory vault
    vault = create_vault("memory")
    
    # Persist some symbols
    h1 = vault.persist(glyph="∆", value=42, delta=0.0, equilibrium_delta=0.0)
    h2 = vault.persist(glyph="⬡", value={"eternal": "record"}, delta=0.0, equilibrium_delta=0.0)
    
    print(f"\nStored ∆: {h1}")
    print(f"Stored ⬡: {h2}")
    
    # Try to store with ΣΔ ≠ 0 (should fail)
    print("\nAttempting to store with ΣΔ = 5.0 (should fail):")
    h3 = vault.persist(glyph="∆", value=100, delta=5.0, equilibrium_delta=5.0)
    print(f"Result: {h3}")
    
    # Retrieve
    print(f"\nRetrieved: {vault.retrieve(h1)}")
    
    # Stats
    print(f"\nVault stats: {vault.stats()}")
    
    print("\n" + "═" * 70)
    print("SIS™ - Created by Kevin Fain (ThēÆrchītēcť) © 2025")
    print("═" * 70)
