from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

class Encryptor:
    private_key: rsa.RSAPrivateKey
    public_key: rsa.RSAPublicKey

    def __init__(self, private_key_path: str | None = None, public_key_path: str | None = None):
        if private_key_path:
            with open(private_key_path, "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                )
        else:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            with open("private_key.pem", "wb") as key_file:
                key_file.write(
                    self.private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                )

        if private_key_path and public_key_path:
            with open(public_key_path, "rb") as key_file:
                self.public_key = serialization.load_pem_public_key(
                    key_file.read(),
                )
        else:
            self.public_key = self.private_key.public_key()
            with open("public_key.pem", "wb") as key_file:
                key_file.write(
                    self.public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                )

    def encrypt_file(self, target_file_path: str, output_file_path: str):
        # Generate a random AES key and IV
        aes_key = os.urandom(32)  # AES-256
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
        encryptor = cipher.encryptor()

        # Encrypt the AES key with RSA public key
        encrypted_key = self.public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )

        with open(target_file_path, "rb") as infile, open(output_file_path, "wb") as outfile:
            # Write encrypted AES key and IV at the beginning
            outfile.write(len(encrypted_key).to_bytes(2, "big"))
            outfile.write(encrypted_key)
            outfile.write(iv)
            # Encrypt file in chunks
            while True:
                chunk = infile.read(4096)
                if not chunk:
                    break
                outfile.write(encryptor.update(chunk))
            outfile.write(encryptor.finalize())

    def decrypt_file(self, encrypted_file_path: str, output_file_path: str):
        with open(encrypted_file_path, "rb") as infile, open(output_file_path, "wb") as outfile:
            # Read encrypted AES key length, encrypted key, and IV
            key_len = int.from_bytes(infile.read(2), "big")
            encrypted_key = infile.read(key_len)
            iv = infile.read(16)
            # Decrypt AES key with RSA private key
            aes_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            )
            cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
            decryptor = cipher.decryptor()
            # Decrypt file in chunks
            while True:
                chunk = infile.read(4096)
                if not chunk:
                    break
                outfile.write(decryptor.update(chunk))
            outfile.write(decryptor.finalize())

# Example usage
encryptor = Encryptor(private_key_path="private_key.pem", public_key_path="public_key.pem")

encryptor.encrypt_file("./sample/share_github.py", "./sample_encrypted.txt")
encryptor.decrypt_file("./sample_encrypted.txt", "./sample_decrypted.py")
