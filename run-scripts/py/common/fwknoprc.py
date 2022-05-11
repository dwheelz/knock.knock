
import os
from pathlib import Path
from re import search

DEFAULT_SAVE_DIR = os.path.join(Path(__file__).parents[3], "config")

class Stanza:
    """Creates a Stanza"""

    def __init__(self, spoof_user, allow_ip, access, spa_server, key_base64, hmac_base64):
        """init baby"""
        self.spoof_user = spoof_user
        self.allow_ip = allow_ip
        self.access = access
        self.spa_server = spa_server
        self.key_base64 = key_base64
        self.hmac_key_base64 = hmac_base64
        self.use_hmac = "Y"

    def _formater(self) -> str:
        """Format the stanza, lets make it look pretty"""
        stanza = "[default]\n"
        stanza += "".join(
            f"{x.upper()}{' ' * (20 - len(x))}{self.__getattribute__(x)}\n" for x in dir(self) if not x.startswith("__") and not callable(getattr(self, x))
        )
        return stanza

    def save_to_file(self, _dir : str = DEFAULT_SAVE_DIR, file_name : str = None):
        """
        Saves a the stanza to a .fwknoprc file (Yes, this is a file format I've made up, but it makes the files easily recognisable)

        : param _dir: The dir to save the stanza to
        : param file_name: The filename
        """
        if file_name is None:
            rgx = r"[a-z]+\/+(?P<port>[\d]+)"
            file_name = f"{search(rgx, self.allow_ip).group('port')}"

        file_name = f"{file_name}.fwknoprc"
        with open(Path(_dir, file_name), "w", encoding="utf-8") as file:
            file.write(self._formater())
