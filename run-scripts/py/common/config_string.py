"""decrypt the initial config string

This can be used to provide the intial config as an encrypted string.
Assumptions on security are the key generated from gen_key is transported
securely, and not saved anywhere at all...

"""
from os import path
from pathlib import Path
from re import findall

from common.stanza_blob import SharedSecureString


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
    decryptor = EncryptedConfigData()
    decrypted_str = decryptor.decrypt(secret)
    found_args = findall(arg_rgx, decrypted_str)
    return_list = []
    for nested_tuple in found_args:
        for _arg in nested_tuple:
            return_list.append(_arg)
    return return_list


class EncryptedConfigData(SharedSecureString):

    def encrypt_to_file(self, priv_key: str, secret: str) -> None:
        """Encrypts data and writes to /input/secret_string.txt"""
        res = write_secret_string(self.encrypt(priv_key, secret))
        print(f"Data write returned error code: {res}")

    def decrypt_from_file(self) -> str:
        """Decrypts from secret_string.txt file"""
        return self.decrypt(get_secret_string_data())
