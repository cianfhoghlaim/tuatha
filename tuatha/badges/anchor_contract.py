"""badges.anchor_contract — CredAnchor.sol ABI + helper.

The CredAnchor smart contract is a minimal Solidity contract deployed
to Base L2. It stores `(timestamp, merkleRoot, batchId)` for each
daily anchor batch.

Solidity source (for reference; the actual contract is at
`infrastructure/contracts/CredAnchor.sol`):

    // SPDX-License-Identifier: BUSL-1.1
    pragma solidity ^0.8.20;

    contract CredAnchor {
        struct Anchor {
            bytes32 merkleRoot;
            uint256 timestamp;
            string batchId;
            uint256 leafCount;
        }

        mapping(string => Anchor) public anchors;
        address public owner;

        event AnchorPublished(string indexed batchId, bytes32 merkleRoot, uint256 leafCount, uint256 timestamp);

        constructor() {
            owner = msg.sender;
        }

        modifier onlyOwner() {
            require(msg.sender == owner, "CredAnchor: not owner");
            _;
        }

        function publish(string calldata batchId, bytes32 merkleRoot, uint256 leafCount) external onlyOwner {
            anchors[batchId] = Anchor(merkleRoot, block.timestamp, batchId, leafCount);
            emit AnchorPublished(batchId, merkleRoot, leafCount, block.timestamp);
        }

        function getAnchor(string calldata batchId) external view returns (bytes32 merkleRoot, uint256 timestamp, uint256 leafCount) {
            Anchor storage a = anchors[batchId];
            return (a.merkleRoot, a.timestamp, a.leafCount);
        }
    }
"""
from __future__ import annotations

CREEDANCHOR_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "batchId", "type": "string"}],
        "name": "getAnchor",
        "outputs": [
            {
                "components": [
                    {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "string", "name": "batchId", "type": "string"},
                    {"internalType": "uint256", "name": "leafCount", "type": "uint256"},
                ],
                "internalType": "struct CredAnchor.Anchor",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "string", "name": "batchId", "type": "string"},
            {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
            {"internalType": "uint256", "name": "leafCount", "type": "uint256"},
        ],
        "name": "publish",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "batchId", "type": "string"},
            {"indexed": False, "internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
            {"indexed": False, "internalType": "uint256", "name": "leafCount", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
        ],
        "name": "AnchorPublished",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"},
        ],
        "name": "OwnerRotated",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def publish(
    w3: object,
    contract_address: str,
    root: str,
    batch_id: str,
    leaf_count: int,
    sender_address: str | None = None,
) -> str:
    """Publish a daily Merkle root anchor to the deployed CredAnchor.

    Thin convenience wrapper around the `publish` ABI entry. The
    on-chain signature is `publish(batchId, merkleRoot, leafCount)`
    (mirroring CredAnchor.sol), but the spec
    (`2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`,
    Layer 4 + the spec language "calls
    ``CredAnchor.publish(root, batchId)`` on Base L2") adopts the
    ``publish(root, batchId)`` argument order at the Python call site
    so the daily_credential_anchor Dagster asset reads in the
    natural "compute the root, then publish" flow.

    Args:
        w3: A connected web3.Web3 instance (must already point at
            Base L2; the caller is responsible for RPC selection +
            signing-account configuration).
        contract_address: The 0x-prefixed deployed CredAnchor address.
        root: The 32-byte Merkle root, either as a 0x-prefixed hex
            string (``0xabc...``) or as a 64-char hex string without
            the prefix.
        batch_id: The canonical batch ID, e.g. ``"2026-08-26"``.
        leaf_count: The number of badge evidence_hashes included in
            the Merkle tree (>= 1).
        sender_address: Optional 0x-prefixed address to send the tx
            from. Defaults to ``w3.eth.accounts[0]`` (the same default
            the previous `_call_credanchor_publish` used).

    Returns:
        The 0x-prefixed transaction hash as a string.
    """
    root_bytes = bytes.fromhex(root[2:] if root.startswith("0x") else root)
    if len(root_bytes) != 32:
        raise ValueError(
            f"Merkle root must be 32 bytes, got {len(root_bytes)} "
            f"(root={root!r})"
        )
    if leaf_count <= 0:
        raise ValueError(f"leaf_count must be > 0, got {leaf_count}")
    if not batch_id:
        raise ValueError("batch_id must be a non-empty string")

    contract = w3.eth.contract(  # type: ignore[attr-defined]
        address=contract_address, abi=CREEDANCHOR_ABI
    )
    from_addr = sender_address or w3.eth.accounts[0]  # type: ignore[attr-defined]
    tx = contract.functions.publish(batch_id, root_bytes, leaf_count).transact(
        {"from": from_addr}
    )
    receipt = w3.eth.wait_for_transaction_receipt(tx)  # type: ignore[attr-defined]
    return receipt.transactionHash.hex()
