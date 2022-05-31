"""Test cases for the stanza blob"""

from unittest import TestCase

import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../")))

from common import stanza_blob
from test_data.test_keys import TEST_AUTH_PRIV_KEY, TEST_AUTH_PUB_KEY, \
    TEST_CLIENT_PRIV_KEY, TEST_CLIENT_PUB_KEY


def _patched_read_key(file_data: bytes) -> bytes:
    """I just return what I've been given"""
    return file_data


# monkey patch _read_key so it just returns the value its passed
stanza_blob._read_key = _patched_read_key


class TestSharedSecureString(TestCase):
    """Test cases for SharedSecureString"""

    data_to_encrypt = "hello there world"

    def test_encrypt(self):
        """Tests encrypting a data actually encrypts it"""
        encryptor = stanza_blob.SharedSecureString(
            TEST_CLIENT_PRIV_KEY, TEST_CLIENT_PUB_KEY, TEST_AUTH_PUB_KEY
        )
        encrypted_data = encryptor.encrypt(TEST_AUTH_PRIV_KEY, self.data_to_encrypt)
        self.assertTrue(isinstance(encrypted_data, bytes))
        self.assertNotEqual(self.data_to_encrypt.encode(), encrypted_data)

    def test_decrypt(self):
        pass

    def test_derive_key(self):
        pass

    def test_init_vector(self):
        pass
