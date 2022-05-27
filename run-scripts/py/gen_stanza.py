"""Generates fwknoprc file(s)"""

from argparse import ArgumentParser, Namespace
from re import search
from urllib.request import urlopen
from common.fwknoprc import WriteStanza
from common.docker_secret_reader import read_secret, SecretNotFound

DEFAULT_SECRET_FILE_NAME = "knock.password"

class StanzaArgs(ArgumentParser):
    """Arg parser"""

    _description = (
        "Create your fwknoprc file(s) here. To create stanzas with the same credentials but for different ports, simply provide the arg "
        "multiple times, like this: --port tcp/9090 --port tcp/8080"
    )

    def __init__(self, description=_description):
        super().__init__(description=description)
        self.add_argument("--user", dest="spoof_user", type=str, help="The username provided")
        self.add_argument("--port", dest="access", type=str, action='append', help="Provide me multiple times for multiple ports")
        self.add_argument("--host", dest="spa_server", type=str, help="The Hostname/IP you want to connect to")
        self.add_argument("--key", dest="key_base64", type=str, help="Your base64 encoded key")
        self.add_argument("--hmac", dest="hmac_key_base64", type=str, help="Your base64 encoded HMAC key")
        self.add_argument("--your_ip", dest="allow_ip", type=str, required=False, default=None, help="Your external IP. This is not required")
        self.add_argument("--password", type=str, required=False, default="", help="The passphrase to encyrpt the fwknoprc file(s).")


def get_external_ip() -> str:
    """The domain used when ALLOW_IP is set to 'resolve' is very slow to respond. This hack should get around that."""
    resp = urlopen("https://www.wikipedia.org")
    ext_ip = resp.headers.get('x-client-ip', False)
    if not ext_ip:
        raise Exception("'x-client-ip' header missing in response. No external IP could be found.")

    print(f"External IP Address: {ext_ip}")
    return ext_ip

def save_stanzas(args: Namespace):
    """Creates the stanza files"""
    for port in args.access:
        stanza_kwargs = {
            "spoof_user": args.spoof_user,
            "access": port,
            "spa_server": args.spa_server,
            "key_base64": args.key_base64,
            "hmac_base64": args.hmac_key_base64
        }
        stanza_kwargs["allow_ip"] = args.allow_ip if args.allow_ip else get_external_ip()
        stanza = WriteStanza(**stanza_kwargs)
        pw_file = None
        if not args.password:
            pw_file = DEFAULT_SECRET_FILE_NAME
        elif args.password.startswith("secret:"):
            pw_file = search(r"secret:(?P<pass_file>[\w\W]+?)")

        if pw_file is not None:
            try:
                password = read_secret(pw_file)
            except Exception as exc:
                raise SecretNotFound("Password secret cannot be found. Did you create it before running this?") from exc
        else:
            password = args.password

        stanza.save(password=password)

def main():
    """Its main baby"""
    save_stanzas(StanzaArgs().parse_args())

if __name__ == "__main__":
    main()
