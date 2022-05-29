"""Knocks on the SPA servers door"""

from glob import glob
from pathlib import Path
from os import path, remove
from subprocess import check_output
from tempfile import NamedTemporaryFile

from common.fwknoprc import ReadStanza


def knock():
    """Knocks on the SPA servers door"""
    fwknoprc_dir = path.join(path.abspath(Path(__file__).parents[2]), "config")
    fwknoprc_stanzas = glob(f"{fwknoprc_dir}/*.fwknoprc")
    stanza_decryptor = ReadStanza()
    for stanza in fwknoprc_stanzas:
        stanza_data = stanza_decryptor.read_encrypted_file(stanza)
        with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=Path(fwknoprc_dir)) as temp_f:
            temp_f.write(stanza_data)
            f_name = temp_f.name
        check_output([f"/usr/bin/fwknop --rc-file {f_name} --verbose"], shell=True)  # fwknop requires shell

    remove(f_name)

if __name__ == "__main__":
    knock()
