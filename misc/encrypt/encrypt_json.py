#!/usr/bin/env python3

from aes import AESCipher
import json


def encrypt_result(key, iv, s):
    obj = json.loads(s)
    if "result" not in obj.keys():
        return s
    result = json.dumps(obj["result"])
    cipher = AESCipher(key=key, iv=iv)
    encrypted = cipher.encrypt(result)
    obj["result"] = encrypted.decode("utf-8")
    return json.dumps(obj)


def decrypt_result(key, iv, s):
    obj = json.loads(s)
    if "result" not in obj.keys():
        return s
    cipher = AESCipher(key=key, iv=iv)
    decrypted = cipher.decrypt(bytes(obj["result"], encoding='utf-8'))
    obj["result"] = json.loads(decrypted)
    return json.dumps(obj)


if __name__ == "__main__":
    key = 'd4f7d2adf42c34a3'
    iv = "5c6ca7c26b1b068d"

    body_plaintext_1 = '{"status": 200, "message": "ok", "result": {"id": 4, "version": "1.1.2", "rsa": "1234567890", "patch": {"released": [], "deleted": [{"id": 40}, {"id": 42}, {"id": 43}, {"id": 48}, {"id": 67}, {"id": 68}, {"id": 69}, {"id": 72}, {"id": 73}, {"id": 74}, {"id": 75}]}}}'
    body_plaintext_2 = '{"status": 200, "message": "ok"}' 
    body_ciphertext_1 = '{"status": 200, "message": "ok", "result": "QsTubOGmgNQrq3XMy9ALHV9umA2l8ZwKNb0HpRyzxHSZSPckMKsqcA9UeUs6P+6uQtcqZSY/Ci9ub9q0X5K6xAEb49fUIyexdbbAFkqovjn803VGL2fsreB8A4uGgrGlHcd5uooKQO1pqHh1I0xOOyhrObD80l9ixOIp84K2YJWlbu2XfyxzT5dLP9JpkgoqklLhsTEvb2vIgJoIxWs7QbVzh+frxPd/M03uhgiZtRUdrQ//Wb/H2v6q5H0df9qtwUizmF82tIjhNYRYpxMybcqHMRlxvVxVc4bcT5dHVMw="}'
    body_ciphertext_2 = '{"status": 200, "message": "ok"}' 
    body_plaintext_3 = '{"status": 200, "result": {"id": "79"}, "message": "ok"}'
    
    ret = encrypt_result(key, iv, body_plaintext_1)
    print(ret)
    encrypt_result(key, iv, body_plaintext_2)
    ret = decrypt_result(key, iv, body_ciphertext_1)
    decrypt_result(key, iv, body_ciphertext_2)

    print(ret)
    assert body_plaintext_1 == ret

    print("$%s$" % (body_plaintext_3))
    print(encrypt_result(key, iv, body_plaintext_3))
