"""decrypt the initial config string

This can be used to provide the intial config as an encrypted string.
Assumptions on security are the key generated from gen_key is transported
securely, and not saved anywhere at all...

"""
from os import path
from pathlib import Path
from re import findall
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

def write_secret_string(encrypted_data) -> int:
    """Gets the secret string from the input DIR"""
    with open(path.join(path.abspath(Path(__file__).parents[3]), "data", "secret_string.txt"), "wb") as secret:
        return secret.write(encrypted_data)

def get_secret_string_data() -> bytes:
    """Gets the secret string from the input DIR"""
    with open(path.join(path.abspath(Path(__file__).parents[3]), "data", "secret_string.txt"), "rb") as secret:
        return secret.read().strip()

def get_stanza_args(secret: str) -> list:
    """Generates a list containing all the args for gen_stanza.py"""
    arg_rgx = r"(?P<key>[-\w]+?) = (?P<val>[\w\W]+?)(?: |\[END\])"
    decryptor = StanzaBlob()
    decrypted_str = decryptor.decrypt(secret)
    found_args = findall(arg_rgx, decrypted_str)
    return_list = []
    for nested_tuple in found_args:
        for _arg in nested_tuple:
            return_list.append(_arg)
    return return_list

class StanzaBlob:
    def __init__(self) -> None:
        self.client_priv_key = load_pem_private_key(CLIENT_PRIV_KEY, password=None)
        self.client_public_key = load_pem_public_key(CLIENT_PUB_KEY)
        self.auth_pub_key = load_pem_public_key(AUTHORITY_PUB_KEY)

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
        shared_key = priv_key.exchange(ec.ECDH(), self.client_public_key)
        init_vector = token_bytes(16)
        derived_key = self._derive_key(shared_key)
        aes = Cipher(algorithms.AES(derived_key), modes.CBC(init_vector), backend=default_backend())
        encryptor = aes.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(secret_to_encrypt.encode()) + padder.finalize()
        return encryptor.update(padded_data) + encryptor.finalize() + init_vector

    def encrypt_to_file(self, priv_key: str, secret: str) -> None:
        """Encrypts data and writes to /input/secret_string.txt"""
        res = write_secret_string(self.encrypt(priv_key, secret))
        print(f"Data write returned error code: {res}")

    def decrypt(self, secret: bytes) -> str:
        """This is locked down to only allow decyrption from authority to docker client"""
        shared_key = self.client_priv_key.exchange(ec.ECDH(), self.auth_pub_key)
        init_vector = secret[-16:]
        secret = secret[:-16]
        derived_key = self._derive_key(shared_key)
        aes = Cipher(algorithms.AES(derived_key), modes.CBC(init_vector), backend=default_backend())
        decryptor = aes.decryptor()
        decrypted_data = decryptor.update(secret) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return (unpadder.update(decrypted_data) + unpadder.finalize()).decode('utf-8')

    def decrypt_from_file(self) -> str:
        """Decrypts from secret_string.txt file"""
        return self.decrypt(get_secret_string_data())
