"""Generates the stanza via the config string and key"""

from common.config_string import get_stanza_args, get_secret_string_data
from gen_stanza import save_stanzas, StanzaArgs


def main():
    """Its main"""
    gen_stanza_args = get_stanza_args(get_secret_string_data())
    save_stanzas(StanzaArgs().parse_args(gen_stanza_args))

if __name__ == "__main__":
    main()
