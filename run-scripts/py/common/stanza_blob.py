"""Encrypts and Decrypts the Stanzas"""

from os import path
from pathlib import Path
from secrets import token_bytes

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key


def _read_key(file) -> bytes:
    """Reads the data from the .pem key files"""
    with open(path.join(path.abspath(Path(__file__).parent), "keys", file), "r") as fi:
        return fi.read().encode()

CLIENT_PRIV_KEY = _read_key("client_priv.pem")
CLIENT_PUB_KEY = _read_key("client_pub.pem")
AUTHORITY_PUB_KEY = _read_key("server_pub.pem")


class SharedSecureString:
    """Shared key between authoritive issuer and client"""
    def __init__(self, _client_priv: bytes = CLIENT_PRIV_KEY, _client_pub: bytes = CLIENT_PUB_KEY,
        _auth_pub: bytes = AUTHORITY_PUB_KEY) -> None:
        self._client_priv_key = load_pem_private_key(_client_priv, password=None)
        self._client_public_key = load_pem_public_key(_client_pub)
        self._auth_pub_key = load_pem_public_key(_auth_pub)

    @staticmethod
    def _derive_key(shared_key: bytes) -> bytes:
        """Dervives a key"""
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=None,
            backend=default_backend()
        ).derive(shared_key)
        return derived_key

    def encrypt(self, priv_key: str, secret_to_encrypt: str) -> bytes:
        """Private key must be provided, key exchange with docker clients pub key"""
        priv_key = load_pem_private_key(_read_key(priv_key), password=None)
        shared_key = priv_key.exchange(ec.ECDH(), self._client_public_key)
        init_vector = token_bytes(16)
        derived_key = self._derive_key(shared_key)
        aes = Cipher(algorithms.AES(derived_key), modes.CBC(init_vector), backend=default_backend())
        encryptor = aes.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(secret_to_encrypt.encode()) + padder.finalize()
        return encryptor.update(padded_data) + encryptor.finalize() + init_vector

    def decrypt(self, secret: bytes, pub_key: str | None = None) -> str:
        """Decrypt the secured string"""
        if pub_key is None:
            pub_key = self._auth_pub_key
        else:
            pub_key = load_pem_public_key(_read_key(pub_key))
        shared_key = self._client_priv_key.exchange(ec.ECDH(), pub_key)
        init_vector = secret[-16:]
        secret = secret[:-16]
        derived_key = self._derive_key(shared_key)
        aes = Cipher(algorithms.AES(derived_key), modes.CBC(init_vector), backend=default_backend())
        decryptor = aes.decryptor()
        decrypted_data = decryptor.update(secret) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return (unpadder.update(decrypted_data) + unpadder.finalize()).decode('utf-8')
