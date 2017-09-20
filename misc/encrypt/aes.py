#!/usr/bin/env python3

import sys
import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):
    """
    A classical AES Cipher. Can use any size of data and any size of password thanks to padding.
    Also ensure the coherence and the type of the data with a unicode to byte converter.
    """
    def __init__(self, key, iv):
        self.bs = 32
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()
        self.iv = iv

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b''.decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * AESCipher.str_to_bytes(chr(self.bs - len(s) % self.bs))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        raw = self._pad(AESCipher.str_to_bytes(raw))
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self._unpad(cipher.decrypt(enc))


if __name__ == "__main__":
    for i in range(1024*100):
        key = 'd4f7d2adf42c34a3'
        # iv = Random.new().read(AES.block_size)
        iv = "5c6ca7c26b1b068d"
        message = Random.new().read(1) * i
        cipher = AESCipher(key=key, iv=iv)
        encrypted = cipher.encrypt(message)
        new_cipher = AESCipher(key=key, iv=iv)
        decrypted = new_cipher.decrypt(encrypted)
        try:
            assert decrypted == message
        except:
            print(decrypted)
            print(message)
            sys.exit(1)
