"""Test cases for the stanza blob"""

from unittest import TestCase
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../")))

from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

from common import stanza_blob, fwknoprc
from test_data.test_keys import TEST_AUTH_PRIV_KEY, TEST_AUTH_PUB_KEY, \
    TEST_CLIENT_PRIV_KEY, TEST_CLIENT_PUB_KEY
from test_data.test_stanza_data import TEST_FORMATED_STANZA_DATA, TEST_FORMATED_STANZA_DATA_RESOLVE


def _patched_read_key(file_data: bytes) -> bytes:
    """I just return what I've been given"""
    return file_data


# monkey patch _read_key so it just returns the value its passed
stanza_blob._read_key = _patched_read_key


class TestSharedSecureString(TestCase):
    """Test cases for SharedSecureString"""

    data_to_encrypt = "hello there world"

    def _encryptor(self) -> bytes:
        """Returns the encrypted data"""
        encryptor = stanza_blob.SharedSecureString(
            TEST_CLIENT_PRIV_KEY, TEST_CLIENT_PUB_KEY, TEST_AUTH_PUB_KEY
        )
        return encryptor.encrypt(TEST_AUTH_PRIV_KEY, self.data_to_encrypt)

    def test_encrypt(self):
        """Tests encrypting a data actually encrypts it"""
        encrypted_data = self._encryptor()
        self.assertIsInstance(encrypted_data, bytes)
        self.assertNotEqual(self.data_to_encrypt.encode(), encrypted_data)

    def test_decrypt(self):
        """Tests that data can be encrypted and decrypted as expected"""
        encrypted_data = self._encryptor()
        assert encrypted_data != self.data_to_encrypt
        decryptor = stanza_blob.SharedSecureString(
            TEST_CLIENT_PRIV_KEY, TEST_CLIENT_PUB_KEY, TEST_AUTH_PUB_KEY
        )
        decrypted_data = decryptor.decrypt(encrypted_data)
        self.assertIsInstance(decrypted_data, str)
        self.assertEqual(self.data_to_encrypt, decrypted_data)


class TestWriteStanza(TestCase):
    """Test cases for WriteStanza"""

    access = "udp/209040"  # mildly sensible with a value here as this is parsed with a regex
    spoof_user = "Test user"
    spa_server = "a.spa-server.com"
    key_base64 = "KEYBASE64fdgfdgdfgfdgfdg"
    hmac_key_base64 = "HMACKEYBASE64jhghgfhgfhgfh"
    allow_ip = "10.10.10.10"
    use_hmac = "Y"

    def _init_write_stanza(self):
        """Creates an instance of WriteStanza and returns it"""
        return fwknoprc.WriteStanza(
            access=self.access,
            spoof_user=self.spoof_user,
            spa_server=self.spa_server,
            key_base64=self.key_base64,
            hmac_base64=self.hmac_key_base64,
            allow_ip=self.allow_ip
        )

    def test_fname_regex_udp(self):
        """Tests that the fname regex can parse the self.access value correctly"""
        stanza = self._init_write_stanza()
        self.assertEqual(stanza._fname(None), "209040.fwknoprc")

    def test_fname_regex_tcp(self):
        """Tests that the fname regex can parse the self.access value correctly"""
        stanza = self._init_write_stanza()
        stanza.access = "tcp/209040"  # monkey patch access
        self.assertEqual(stanza._fname(None), "209040.fwknoprc")

    def test_formater(self):
        """test _formatter method"""
        stanza = self._init_write_stanza()
        self.assertEqual(stanza._formater(), TEST_FORMATED_STANZA_DATA)

    def test_formater_resolve(self):
        """test _formatter method (defaulting allow_ip to resolve)"""
        # omitting resolve, so lets just make our own instance (rather than mess around with optional args)
        stanza = fwknoprc.WriteStanza(
            access=self.access,
            spoof_user=self.spoof_user,
            spa_server=self.spa_server,
            key_base64=self.key_base64,
            hmac_base64=self.hmac_key_base64
        )
        self.assertEqual(stanza._formater(), TEST_FORMATED_STANZA_DATA_RESOLVE)

    def test_write_secure(self):
        """Test _write method (secure)"""
        pass

    def test_write_unsecure(self):
        """Test _write method (unsecure)"""
        pass
