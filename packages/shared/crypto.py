"""
QUANTARA Shared Cryptography & Security Utilities
Symmetric encryption for sensitive broker credentials and API keys.
"""

from __future__ import annotations
import base64
import hashlib
import os
from typing import Optional


class SecretVault:
    """Provides secure encryption and decryption for sensitive user credentials."""

    def __init__(self, master_key: Optional[str] = None):
        key = master_key or os.getenv("ENCRYPTION_KEY", "quantara-default-secure-32-byte-key-2026")
        self._key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, plain_text: str) -> str:
        """Simple XOR-based stream cipher with base64 encoding for clean dependency-free storage."""
        if not plain_text:
            return ""
        data = plain_text.encode()
        encrypted = bytes([b ^ self._key[i % len(self._key)] for i, b in enumerate(data)])
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt(self, cipher_text: str) -> str:
        """Decrypts base64 encoded ciphertext."""
        if not cipher_text:
            return ""
        try:
            raw = base64.b64decode(cipher_text.encode("utf-8"))
            decrypted = bytes([b ^ self._key[i % len(self._key)] for i, b in enumerate(raw)])
            return decrypted.decode("utf-8")
        except Exception:
            return ""


# Singleton instance
default_vault = SecretVault()
