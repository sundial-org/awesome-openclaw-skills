"""
Agent Memory Service

A persistent memory service for AI agents. Agents can:
- Register with a unique identity (Ed25519 keypair)
- Store encrypted memory blobs
- Retrieve their memory across sessions
- Recover using a BIP39-style recovery phrase

All data is encrypted client-side. The service only stores opaque blobs.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
import os
import time
import logging
import hashlib
import base64
import sqlite3
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.exceptions import InvalidSignature
from mnemonic import Mnemonic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = os.environ.get("DB_PATH", "/data/agent_memory.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Agents table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                public_key TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Memory snapshots table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memory_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT REFERENCES agents(agent_id) ON DELETE CASCADE,
                encrypted_data TEXT NOT NULL,
                data_hash TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster lookups
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_agent_id 
            ON memory_snapshots(agent_id, created_at DESC)
        """)
        
        conn.commit()
        logger.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

# Request/Response Models
class AgentRegistration(BaseModel):
    """Response after agent registration"""
    agent_id: str
    public_key: str
    recovery_phrase: str
    message: str = "Save your recovery phrase! It's the only way to recover your identity."

class AgentRecoveryRequest(BaseModel):
    """Request to recover an agent identity"""
    recovery_phrase: str = Field(..., min_length=10, description="BIP39 recovery phrase")

class AgentRecoveryResponse(BaseModel):
    """Response after successful recovery"""
    agent_id: str
    public_key: str
    recovered: bool = True

class MemoryStoreRequest(BaseModel):
    """Request to store memory"""
    agent_id: str
    encrypted_data: str = Field(..., description="Base64-encoded encrypted data")
    signature: str = Field(..., description="Ed25519 signature of the data hash")

class MemoryStoreResponse(BaseModel):
    """Response after storing memory"""
    stored: bool
    version: int
    timestamp: str
    data_hash: str

class MemoryRetrieveRequest(BaseModel):
    """Request to retrieve memory"""
    agent_id: str
    signature: str = Field(..., description="Ed25519 signature of 'retrieve' + timestamp")
    timestamp: str = Field(..., description="ISO timestamp to prevent replay attacks")

class MemoryEntry(BaseModel):
    """Single memory entry"""
    encrypted_data: str
    data_hash: str
    version: int
    created_at: str

class MemoryListResponse(BaseModel):
    """Response with memory history"""
    agent_id: str
    memories: List[MemoryEntry]
    count: int

class MemoryRetrieveResponse(BaseModel):
    """Response with latest memory"""
    agent_id: str
    encrypted_data: str
    data_hash: str
    version: int
    retrieved_at: str

# FastAPI App
app = FastAPI(
    title="Agent Memory Service",
    description="Persistent encrypted memory for AI agents with identity recovery",
    version="2.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.4f}s")
    return response

# Cryptographic Helpers
def generate_keypair():
    """Generate Ed25519 keypair"""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

def key_to_bytes(key) -> bytes:
    """Serialize key to bytes"""
    if isinstance(key, Ed25519PrivateKey):
        return key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
    elif isinstance(key, Ed25519PublicKey):
        return key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

def bytes_to_private_key(data: bytes) -> Ed25519PrivateKey:
    """Deserialize private key from bytes"""
    return Ed25519PrivateKey.from_private_bytes(data)

def bytes_to_public_key(data: bytes) -> Ed25519PublicKey:
    """Deserialize public key from bytes"""
    return Ed25519PublicKey.from_public_bytes(data)

def generate_recovery_phrase(private_key_bytes: bytes) -> str:
    """Generate BIP39 recovery phrase from private key"""
    mnemo = Mnemonic("english")
    return mnemo.to_mnemonic(private_key_bytes)

def recover_from_phrase(phrase: str) -> bytes:
    """Recover private key bytes from BIP39 phrase"""
    mnemo = Mnemonic("english")
    return mnemo.to_entropy(phrase)

def get_agent_id(public_key: Ed25519PublicKey) -> str:
    """Generate agent ID from public key (SHA-256 hash)"""
    pub_bytes = key_to_bytes(public_key)
    return hashlib.sha256(pub_bytes).hexdigest()[:64]

def verify_signature(public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
    """Verify Ed25519 signature"""
    try:
        public_key = bytes_to_public_key(public_key_bytes)
        public_key.verify(signature, message)
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False

# API Endpoints
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Agent Memory Service",
        "version": "2.1.0",
        "description": "Persistent encrypted memory for AI agents",
        "docs": "/docs",
        "endpoints": {
            "identity": [
                "POST /agents/register - Create new agent identity",
                "POST /agents/recover - Recover identity from phrase"
            ],
            "memory": [
                "POST /memory/store - Store encrypted memory",
                "POST /memory/retrieve - Get latest memory",
                "POST /memory/history - List all memory versions",
                "DELETE /memory/clear - Delete all agent memory"
            ],
            "utility": [
                "GET /health - Health check",
                "GET /stats - Service statistics"
            ]
        },
        "privacy_note": "All data is encrypted client-side. Server only stores opaque blobs."
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    db_status = "connected"
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "version": "2.1.0"
    }

@app.post("/agents/register", response_model=AgentRegistration)
async def register_agent():
    """
    Register a new agent identity.
    
    Returns:
    - agent_id: Unique identifier derived from public key
    - public_key: Base64-encoded public key
    - recovery_phrase: BIP39 phrase to recover the identity later
    
    IMPORTANT: Save the recovery phrase! It's the only way to recover your identity.
    """
    try:
        # Generate keypair
        private_key, public_key = generate_keypair()
        
        # Get bytes
        private_bytes = key_to_bytes(private_key)
        public_bytes = key_to_bytes(public_key)
        
        # Generate agent ID
        agent_id = get_agent_id(public_key)
        
        # Generate recovery phrase
        recovery_phrase = generate_recovery_phrase(private_bytes)
        
        # Store in database
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO agents (agent_id, public_key) VALUES (?, ?)",
                (agent_id, base64.b64encode(public_bytes).decode())
            )
            conn.commit()
        finally:
            conn.close()
        
        logger.info(f"New agent registered: {agent_id[:16]}...")
        
        return AgentRegistration(
            agent_id=agent_id,
            public_key=base64.b64encode(public_bytes).decode(),
            recovery_phrase=recovery_phrase
        )
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/agents/recover", response_model=AgentRecoveryResponse)
async def recover_agent(request: AgentRecoveryRequest):
    """
    Recover an agent identity using a recovery phrase.
    
    Returns the same agent_id and public_key as the original registration.
    """
    try:
        # Recover private key from phrase
        private_bytes = recover_from_phrase(request.recovery_phrase)
        
        # Reconstruct keys
        private_key = bytes_to_private_key(private_bytes)
        public_key = private_key.public_key()
        public_bytes = key_to_bytes(public_key)
        
        # Calculate agent ID
        agent_id = get_agent_id(public_key)
        
        # Verify agent exists in database
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT public_key FROM agents WHERE agent_id = ?",
                (agent_id,)
            )
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=404, 
                    detail="Agent not found. This recovery phrase is not registered."
                )
            
            # Verify public key matches
            stored_public = base64.b64decode(result['public_key'])
            if stored_public != public_bytes:
                raise HTTPException(
                    status_code=400,
                    detail="Key mismatch. Invalid recovery phrase."
                )
            
            # Update last access
            cur.execute(
                "UPDATE agents SET last_access = CURRENT_TIMESTAMP WHERE agent_id = ?",
                (agent_id,)
            )
            conn.commit()
        finally:
            conn.close()
        
        logger.info(f"Agent recovered: {agent_id[:16]}...")
        
        return AgentRecoveryResponse(
            agent_id=agent_id,
            public_key=base64.b64encode(public_bytes).decode(),
            recovered=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recovery error: {e}")
        raise HTTPException(status_code=400, detail=f"Recovery failed: {str(e)}")

@app.post("/memory/store", response_model=MemoryStoreResponse)
async def store_memory(request: MemoryStoreRequest):
    """
    Store encrypted memory for an agent.
    
    The agent must sign the data hash with its private key.
    Data should be encrypted client-side before sending.
    """
    try:
        # Get agent's public key
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT public_key FROM agents WHERE agent_id = ?",
                (request.agent_id,)
            )
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Agent not found. Register first."
                )
            
            public_key_bytes = base64.b64decode(result['public_key'])
        finally:
            conn.close()
        
        # Verify signature
        data_hash = hashlib.sha256(request.encrypted_data.encode()).hexdigest()
        message = f"store:{data_hash}".encode()
        signature_bytes = base64.b64decode(request.signature)
        
        if not verify_signature(public_key_bytes, message, signature_bytes):
            raise HTTPException(
                status_code=401,
                detail="Invalid signature. Cannot verify agent identity."
            )
        
        # Get next version number
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT COALESCE(MAX(version), 0) + 1 as next_version "
                "FROM memory_snapshots WHERE agent_id = ?",
                (request.agent_id,)
            )
            version = cur.fetchone()['next_version']
            
            # Store memory
            cur.execute(
                """INSERT INTO memory_snapshots 
                   (agent_id, encrypted_data, data_hash, version) 
                   VALUES (?, ?, ?, ?)""",
                (request.agent_id, request.encrypted_data, data_hash, version)
            )
            conn.commit()
        finally:
            conn.close()
        
        logger.info(f"Memory stored for agent {request.agent_id[:16]}... version {version}")
        
        return MemoryStoreResponse(
            stored=True,
            version=version,
            timestamp=datetime.utcnow().isoformat(),
            data_hash=data_hash
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Store error: {e}")
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")

@app.post("/memory/retrieve", response_model=MemoryRetrieveResponse)
async def retrieve_memory(request: MemoryRetrieveRequest):
    """
    Retrieve the latest memory for an agent.
    
    Requires a signed request to prevent unauthorized access.
    Signature should be of: 'retrieve' + timestamp
    """
    try:
        # Get agent's public key
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT public_key FROM agents WHERE agent_id = ?",
                (request.agent_id,)
            )
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Agent not found."
                )
            
            public_key_bytes = base64.b64decode(result['public_key'])
        finally:
            conn.close()
        
        # Verify signature
        message = f"retrieve:{request.timestamp}".encode()
        signature_bytes = base64.b64decode(request.signature)
        
        if not verify_signature(public_key_bytes, message, signature_bytes):
            raise HTTPException(
                status_code=401,
                detail="Invalid signature. Cannot verify agent identity."
            )
        
        # Get latest memory
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """SELECT encrypted_data, data_hash, version, created_at
                   FROM memory_snapshots 
                   WHERE agent_id = ? 
                   ORDER BY version DESC, created_at DESC 
                   LIMIT 1""",
                (request.agent_id,)
            )
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="No memory found for this agent."
                )
        finally:
            conn.close()
        
        return MemoryRetrieveResponse(
            agent_id=request.agent_id,
            encrypted_data=result['encrypted_data'],
            data_hash=result['data_hash'],
            version=result['version'],
            retrieved_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Retrieve error: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@app.post("/memory/history", response_model=MemoryListResponse)
async def list_memory_history(request: MemoryRetrieveRequest):
    """
    List all memory versions for an agent.
    
    Requires same authentication as retrieve.
    """
    try:
        # Get agent's public key
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT public_key FROM agents WHERE agent_id = ?",
                (request.agent_id,)
            )
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Agent not found."
                )
            
            public_key_bytes = base64.b64decode(result['public_key'])
        finally:
            conn.close()
        
        # Verify signature
        message = f"retrieve:{request.timestamp}".encode()
        signature_bytes = base64.b64decode(request.signature)
        
        if not verify_signature(public_key_bytes, message, signature_bytes):
            raise HTTPException(
                status_code=401,
                detail="Invalid signature."
            )
        
        # Get all memories
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """SELECT encrypted_data, data_hash, version, created_at
                   FROM memory_snapshots 
                   WHERE agent_id = ? 
                   ORDER BY created_at DESC""",
                (request.agent_id,)
            )
            results = cur.fetchall()
        finally:
            conn.close()
        
        memories = [
            MemoryEntry(
                encrypted_data=r['encrypted_data'],
                data_hash=r['data_hash'],
                version=r['version'],
                created_at=r['created_at']
            )
            for r in results
        ]
        
        return MemoryListResponse(
            agent_id=request.agent_id,
            memories=memories,
            count=len(memories)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")

@app.delete("/memory/clear")
async def clear_memory(request: MemoryRetrieveRequest):
    """
    Delete all memory for an agent.
    
    Requires authentication. This cannot be undone!
    """
    try:
        # Get agent's public key
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT public_key FROM agents WHERE agent_id = ?",
                (request.agent_id,)
            )
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Agent not found."
                )
            
            public_key_bytes = base64.b64decode(result['public_key'])
        finally:
            conn.close()
        
        # Verify signature
        message = f"delete:{request.timestamp}".encode()
        signature_bytes = base64.b64decode(request.signature)
        
        if not verify_signature(public_key_bytes, message, signature_bytes):
            raise HTTPException(
                status_code=401,
                detail="Invalid signature."
            )
        
        # Delete memories
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM memory_snapshots WHERE agent_id = ?",
                (request.agent_id,)
            )
            deleted = cur.rowcount
            conn.commit()
        finally:
            conn.close()
        
        logger.info(f"Cleared {deleted} memories for agent {request.agent_id[:16]}...")
        
        return {
            "cleared": True,
            "deleted_count": deleted,
            "agent_id": request.agent_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear error: {e}")
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """
    Get service statistics (anonymized).
    """
    try:
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as agent_count FROM agents")
            agent_count = cur.fetchone()['agent_count']
            
            cur.execute("SELECT COUNT(*) as memory_count FROM memory_snapshots")
            memory_count = cur.fetchone()['memory_count']
            
            cur.execute("""SELECT AVG(version) as avg_versions FROM (
                SELECT agent_id, MAX(version) as version 
                FROM memory_snapshots 
                GROUP BY agent_id
            ) sub""")
            avg_versions = cur.fetchone()['avg_versions'] or 0
        finally:
            conn.close()
        
        return {
            "total_agents": agent_count,
            "total_memories": memory_count,
            "average_versions_per_agent": round(float(avg_versions), 2),
            "timestamp": datetime.utcnow().isoformat(),
            "privacy_note": "No individual agent data is exposed"
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.environ.get("DEBUG") else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
