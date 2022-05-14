
import os
from base64 import urlsafe_b64encode as b64e
from base64 import urlsafe_b64decode as b64d
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from pathlib import Path
from re import search, match
import secrets

DEFAULT_SAVE_DIR = os.path.join(Path(__file__).parents[3], "config")


class PasswordSucksError(Exception):
    """Raised when a password really sucks"""
    pass


class StanzaBase:
    """Stanza base class"""

    _byte_order = "big"
    _iter_len = 4
    _salt_nbytes = 16
    _encoding = "utf-8"

    def __init__(self, access):
        """init baby"""
        self.access = access

    def _fname(self, file_name: str) -> str:
        """Returns the full filename"""
        if file_name is None:
            rgx = r"[a-z]+\/+(?P<port>[\d]+)"
            file_name = f"{search(rgx, self.access).group('port')}"

        return f"{file_name}.fwknoprc"

    def _derive_key(self, password: str, salt: bytes, iterations: int) -> bytes:
        backend = default_backend()
        key = PBKDF2HMAC(hashes.SHA512(), length=32, salt=salt, iterations=iterations, backend=backend)
        return b64e(key.derive(password.encode(self._encoding)))


class WriteStanza(StanzaBase):
    """WriteStanza"""

    use_hmac = "Y"

    def __init__(self, spoof_user, allow_ip, access, spa_server, key_base64, hmac_base64):
        """init baby"""
        super().__init__(access)
        self.spoof_user = spoof_user
        self.allow_ip = allow_ip
        self.spa_server = spa_server
        self.key_base64 = key_base64
        self.hmac_key_base64 = hmac_base64

    def _formater(self) -> str:
        """Format the stanza, lets make it look pretty"""
        stanza = "[default]\n"
        stanza += "".join(
            f"{x.upper()}{' ' * (20 - len(x))}{self.__getattribute__(x)}\n" for x in dir(self) if not x.startswith("_") and not callable(getattr(self, x))
        )
        return stanza

    def _password_checker(self, password: str) -> None:
        """Validates that the password isn't totally awful, but I'll allow stuff I'd consider bad..
        Enforces a password that is 8 characters long, must contain: Caps [A-Z], lowercase [a-z], digit and a non-word (special). Apologies people of the world...
        """
        password_rgx = r"^(?=.{8,})(?=.*[a-z])(?=.*[A-Z])(?=.*[\d])(?=.*[\W]).*$"
        if not match(password_rgx, password):
            raise PasswordSucksError(
                "Your password must be 8 characters long and contain: An upper and lower case letter, a digit and a speical char. Som3Th1ngL!ke_this"
            )

    def _write(self, data: str | bytes, _dir : str = DEFAULT_SAVE_DIR, file_name : str = None) -> str:
        """Creates and saves the data to the file. The data can be plain text, or an encrypted bytestring.

        : param data: the stanza data
        : param _dir: The dir to save the stanza to
        : param file_name: The filename
        """
        file_name = self._fname(file_name)
        if isinstance(data, bytes):
            write_type = "wb"
            encoding = None
        else:
            write_type = "w"
            encoding = self._encoding

        with open(Path(_dir, file_name), write_type, encoding=encoding) as file:
            file.write(data)

        print(f"file '{file_name}' has been created")
        return file_name

    def _encrypt(self, password: str, data: str) -> bytes:
        """Encrypts the Stanza, uses a password (not great I know, but I don't want people saving keys to text files...)

        : param password: a password
        : param data: the stanza data
        """
        self._password_checker(password)
        iterations = 100_000
        salt = secrets.token_bytes(self._salt_nbytes)
        key = self._derive_key(password, salt, iterations)
        return b64e(b"%b%b%b" % (salt, iterations.to_bytes(self._iter_len, self._byte_order), b64d(Fernet(key).encrypt(data.encode(self._encoding)))))

    def save_unsecure(self, _dir : str = DEFAULT_SAVE_DIR, file_name : str = None):
        """Saves a the stanza to a .fwknoprc file (Yes, this is a file format I've made up, but it makes the files easily recognisable).
        This just spits out a plain text file in the DIR of your choice. Only use if you know you this file will be kept safe (I bet you don't know...).

        : param _dir: The dir to save the stanza to
        : param file_name: The filename
        """
        return self._write(self._formater(), _dir, file_name)

    def save(self, password: str, _dir : str = DEFAULT_SAVE_DIR, file_name : str = None) -> str:
        """Saves the stanza to a file, encrypts the data.

        : param password: a password
        : param _dir: The dir to save the stanza to
        : param file_name: The filename
        """
        data = self._encrypt(password, self._formater())
        return self._write(data, _dir, file_name)


class ReadStanza(StanzaBase):
    """Read Stanza"""

    def __init__(self, access=None):
        """init baby"""
        super().__init__(access)

    def _decrypt(self, password: str, token: bytes) -> str | None:
        """Decrypts the Stanza (assuming it was encrypted).

        : param password: a password
        : param token: the token data
        """
        decoded_token = b64d(token)
        iter_bytes_end = self._iter_len + self._salt_nbytes
        salt, _iter, token = decoded_token[:self._salt_nbytes], decoded_token[self._salt_nbytes:iter_bytes_end], b64e(decoded_token[iter_bytes_end:])
        iterations = int.from_bytes(_iter, self._byte_order)
        key = self._derive_key(password, salt, iterations)
        try:
            return Fernet(key).decrypt(token).decode(self._encoding)
        except InvalidToken:
            print("-------------- Invalid password for .fwknoprc file! --------------")
            return None

    def read_encrypted_file(self, password: str, _dir : str = DEFAULT_SAVE_DIR, file_name : str = None) -> str | None:
        """Reads the encrypted stanza. Requires the stanza name via: file_name param or self.access.

        : param password: a password
        : param _dir: The dir to save the stanza to
        : param file_name: The filename
        """
        assert any([file_name, self.access]), "either file_name or allow_ip must contain a value"
        file_name = self._fname(file_name)
        with open(Path(_dir, file_name), "rb") as file:
            token = file.read()

        return self._decrypt(password, token)
