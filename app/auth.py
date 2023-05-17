import json
from base64 import b64decode

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from app.exceptions import InvalidToken
from app.globals import CIPHER_KEY


def decrypt_aes_256_cbc(token: str):
    """
    Decrypts the given ciphertext using AES-256-CBC with the given key and IV.
    The ciphertext must be padded using PKCS7.
    """
    try:
        decoded_token = json.loads(b64decode(token).decode("utf-8"))
        key = b64decode(CIPHER_KEY)
        iv = b64decode(decoded_token["iv"])
        value = b64decode(decoded_token["value"])

        # Create a new AES-256-CBC Cipher using the given key and IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

        # Create a decryption context
        decryptor = cipher.decryptor()

        # Decrypt the ciphertext
        plaintext_padded = decryptor.update(value) + decryptor.finalize()

        # Remove padding from the plaintextpoetry
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = (unpadder.update(plaintext_padded) + unpadder.finalize()).decode(
            "utf-8"
        )

        # decode jwt token
        decoded_token = jwt.decode(plaintext, options={"verify_signature": False})

        # return user_id
        user_id = decoded_token["sub"]
        return user_id
    except Exception:
        raise InvalidToken()
