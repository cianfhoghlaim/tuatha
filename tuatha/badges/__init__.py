"""tuatha.badges — the educational-credential badge system.

The badge system is the canonical replacement for the legacy
Crypteolas financial token (per the 2026-08-29-familiar-dynamic-
nft-system-v1 change). It is educational, not financial —
students do not buy anything with real money, and the
educational credit tokens are issued by the platform itself
as quest-completion rewards.

The 3 modules:
- models.py (the Pydantic v2 models)
- mint.py (the badge minting logic)
- storage.py (the Cormorant + Merkle root anchored on Base L2)
"""
