import base64
import secrets
from typing import Any, Optional


class Coder:
    def __init__(self, secret_key: Optional[str] = None):
        if secret_key is None:
            self.secret_key = self.get_secret_key()
        else:
            self.secret_key = secret_key

    def get_secret_key(nbytes: Optional[int] = 16) -> str:
        return secrets.token_hex(nbytes)

    def encrypt(self, string: str) -> str:
        string_bytes = string.encode("utf-8")
        key_bytes = self._extend_key(len(string_bytes))

        encrypted_bytes = bytes(p ^ k for p, k in zip(string_bytes, key_bytes))
        encrypted_b64 = base64.b64encode(encrypted_bytes)

        return encrypted_b64.decode("utf-8")

    def decrypt(self, encrypted_string: str, default: Any) -> str:
        try:
            encrypted_bytes = base64.b64decode(encrypted_string)

            key_bytes = self._extend_key(len(encrypted_bytes))
            decrypted_bytes = bytes(e ^ k for e, k in zip(encrypted_bytes, key_bytes))

            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            return default

    def _extend_key(self, length: int) -> bytes:
        key_bytes = self.secret_key.encode("utf-8")
        return bytes(key_bytes[i % len(key_bytes)] for i in range(length))
