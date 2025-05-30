from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# 鍵ペアの生成
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# 公開鍵をPEM形式で保存（オプション）
pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
print(pem.decode())

print(private_key.private_numbers().d)
print(private_key.private_bytes(encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
).decode())

# 秘密鍵をPEM形式で保存（オプション）
with open("private_key.pem", "wb") as key_file:
    key_file.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# 秘密鍵をファイルから読み込む例
with open("private_key.pem", "rb") as key_file:
    loaded_private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,  # パスワード付きの場合はここにバイト列で指定
    )

# 暗号化する文字列
message = "これは秘密のメッセージです".encode('utf-8')

# 公開鍵で暗号化
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print("暗号文（バイナリ）:", ciphertext)
