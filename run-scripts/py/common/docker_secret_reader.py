"""Reads values from the docker secret files"""

from pathlib import Path

class SecretNotFound(Exception):
    """Raised when a secret cannot be found"""
    pass

def read_secret(file_name: str) -> str:
    """Reads the docker secret from /run/secrets/file_name"""
    with open(Path("/run/secrets", file_name), "r", encoding="utf-8") as secret:
        return secret.read().strip("\n")
