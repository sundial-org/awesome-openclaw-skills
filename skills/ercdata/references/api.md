# ERCData API Reference

## Contract

**Base Mainnet:** `0x15115BB7e18666F13dd384b7347B196c2F6c7a8c`
**Chain:** Base (8453)
**RPC:** https://mainnet.base.org

## Roles

| Role | Hash | Purpose |
|------|------|---------|
| DEFAULT_ADMIN_ROLE | 0x00 | Grant roles, register types, pause |
| PROVIDER_ROLE | keccak256("PROVIDER_ROLE") | Store and update data |
| VERIFIER_ROLE | keccak256("VERIFIER_ROLE") | Verify data entries |
| SNAPSHOT_ROLE | keccak256("SNAPSHOT_ROLE") | Create snapshots |

## Core Functions

### storeData(dataType, data, metadata, signature) → uint256
Store public data. Requires PROVIDER_ROLE. Returns dataId.

### storePrivateData(dataType, data, metadata, signature) → uint256
Store private data with access control. Only provider and granted addresses can read. Requires PROVIDER_ROLE.

### getData(dataId) → DataEntryView
Read a data entry. Private entries require access (provider, granted address, or admin).

### verifyData(dataId, verificationData) → bool
Verify integrity. Requires VERIFIER_ROLE.
- EIP-712: `abi.encode(bytes4("EP12"))` — verifies provider signature
- Hash: `abi.encode(bytes4("HASH"), expectedHash)` — verifies data hash

### updateData(dataId, newData, newMetadata, signature) → bool
Update existing entry. Resets verification. Only original provider.

### grantAccess(dataId, reader)
Grant read access to an address for a private entry. Only provider.

### revokeAccess(dataId, reader)
Revoke read access. Only provider.

### grantBatchAccess(dataId, address[])
Bulk grant access. Only provider.

### hasAccess(dataId, reader) → bool
Check if address has read access.

### registerDataType(typeName) → bool
Register a new data type. Requires admin.

### createSnapshot(name, dataIds[]) → bytes32
Create point-in-time snapshot. Requires SNAPSHOT_ROLE.

## Verification Methods

### EIP-712 Signature
Provider signs a typed struct containing dataHash, metadataHash, dataType, and provider address.
Domain: name="ERCData", version="1", chainId, verifyingContract.

### Hash Comparison
Simple keccak256(data) == expectedHash check.

## Limits
- Max data size: 1MB
- Max metadata size: 64KB
- Max batch size: 100 entries
- Max snapshot size: 1000 entries
- Type/field names: max 64/32 chars

## Events
- DataStored(dataId, provider, dataType, timestamp)
- DataVerified(dataId, verifier, isValid, timestamp)
- DataUpdated(dataId, provider, timestamp)
- BatchProcessed(dataType, batchId, entriesCount)
- SnapshotTaken(snapshotId, name, timestamp)
- AccessGranted(dataId, reader)
- AccessRevoked(dataId, reader)
