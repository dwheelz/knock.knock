
import os
from pathlib import Path
from re import search

from common.stanza_blob import SharedSecureString

DEFAULT_SAVE_DIR = os.path.join(Path(__file__).parents[3], "config")


class StanzaBase(SharedSecureString):
    """Stanza base class"""

    def __init__(self, access):
        """init baby"""
        super().__init__()
        self.access = access

    def _fname(self, file_name: str) -> str:
        """Returns the full filename"""
        if file_name is None:
            rgx = r"[a-z]+\/+(?P<port>[\d]+)"
            file_name = f"{search(rgx, self.access).group('port')}"

        return f"{file_name}.fwknoprc"

class WriteStanza(StanzaBase):
    """WriteStanza"""

    use_hmac = "Y"

    def __init__(self, spoof_user, access, spa_server, key_base64, hmac_base64, allow_ip="resolve"):
        """init baby"""
        super().__init__(access)
        self.spoof_user = spoof_user
        self.spa_server = spa_server
        self.key_base64 = key_base64
        self.hmac_key_base64 = hmac_base64
        self.allow_ip = allow_ip

    def _formater(self) -> str:
        """Format the stanza, lets make it look pretty"""
        stanza = "[default]\n"
        stanza += "".join(
            f"{x.upper()}{' ' * (20 - len(x))}{self.__getattribute__(x)}\n" for x in dir(self) if not x.startswith("_") and not callable(getattr(self, x))
        )
        return stanza

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
            encoding = "utf-8"

        with open(Path(_dir, file_name), write_type, encoding=encoding) as file:
            file.write(data)

        print(f"file '{file_name}' has been created")
        return file_name

    def save_unsecure(self, _dir : str = DEFAULT_SAVE_DIR, file_name : str = None):
        """Saves a the stanza to a .fwknoprc file (Yes, this is a file format I've made up, but it makes the files easily recognisable).
        This just spits out a plain text file in the DIR of your choice. Only use if you know you this file will be kept safe (I bet you don't know...).

        : param _dir: The dir to save the stanza to
        : param file_name: The filename
        """
        return self._write(self._formater(), _dir, file_name)

    def save(self, _dir : str = DEFAULT_SAVE_DIR, file_name : str = None) -> str:
        """Saves the stanza to a file, encrypts the data.

        : param _dir: The dir to save the stanza to
        : param file_name: The filename
        """
        data = self.encrypt("client_priv.pem", self._formater())
        return self._write(data, _dir, file_name)


class ReadStanza(StanzaBase):
    """Read Stanza"""

    def __init__(self, access=None):
        """init baby"""
        super().__init__(access)

    def read_encrypted_file(self, _dir : str = DEFAULT_SAVE_DIR, file_name : str = None) -> str | None:
        """Reads the encrypted stanza. Requires the stanza name via: file_name param or self.access.

        : param _dir: The dir to save the stanza to
        : param file_name: The filename
        """
        assert any([file_name, self.access]), "either file_name or allow_ip must contain a value"
        file_name = self._fname(file_name)
        with open(Path(_dir, file_name), "rb") as file:
            data = file.read().strip()

        return self.decrypt(data, "client_pub.pem")
