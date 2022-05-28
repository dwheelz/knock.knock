"""Generates the stanza via the config string and key"""

from os import path
from pathlib import Path
from argparse import ArgumentParser
from common.config_string import get_stanza_args, get_secret_string_data
from gen_stanza import save_stanzas, StanzaArgs


class Args(ArgumentParser):
    """Parses the args"""

    def __init__(self, description="Decrypts the config string and passes the args to gen_stanza.py"):
        super().__init__(description=description)
        self.add_argument("--password", type=str, required=False, default="", help="The passphrase to encyrpt the fwknoprc file(s).")

def main():
    """Its main"""
    args = Args().parse_args()
    gen_stanza_args = get_stanza_args(get_secret_string_data())
    gen_stanza_args.extend(["--password", args.password])
    save_stanzas(StanzaArgs().parse_args(gen_stanza_args))

if __name__ == "__main__":
    main()
