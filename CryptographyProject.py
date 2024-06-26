import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from PIL import Image
from Crypto.Cipher import AES, DES
from Crypto.Util.Padding import pad

print("* Welcome to MMG encryption system *")

def generate_aes_key(key_size):
    return os.urandom(key_size)

def generate_des_key():
    return os.urandom(8)

def generate_iv_des():
    return os.urandom(8)

def encrypt_text_ecb_aes(text, key):
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_text = cipher.encrypt(pad(text.encode(), AES.block_size))
    return encrypted_text

def encrypt_text_ecb_des(text, key):
    cipher = DES.new(key, DES.MODE_ECB)
    encrypted_text = cipher.encrypt(pad(text.encode(), DES.block_size))
    return encrypted_text

def encrypt_text_cbc_aes(text, key):
    iv = os.urandom(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_text = cipher.encrypt(pad(text.encode(), AES.block_size))
    return encrypted_text, iv

def encrypt_text_cbc_des(text, key):
    iv = os.urandom(DES.block_size)
    cipher = DES.new(key, DES.MODE_CBC, iv)
    encrypted_text = cipher.encrypt(pad(text.encode(), DES.block_size))
    return encrypted_text, iv

def encrypt_text_cfb_aes(text, key):
    iv = os.urandom(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    encrypted_text = cipher.encrypt(text.encode())
    return encrypted_text, iv

def encrypt_text_cfb_des(text, key):
    iv = generate_iv_des()  # Ensure IV length for DES CFB
    cipher = DES.new(key, DES.MODE_CFB, iv, segment_size=64)
    encrypted_text = cipher.encrypt(text.encode())
    return encrypted_text, iv

def encrypt_text_ofb_aes(text, key):
    iv = os.urandom(AES.block_size)
    cipher = AES.new(key, AES.MODE_OFB, iv)
    encrypted_text = cipher.encrypt(text.encode())
    return encrypted_text, iv

def encrypt_text_ofb_des(text, key):
    iv = os.urandom(DES.block_size)
    cipher = DES.new(key, DES.MODE_OFB, iv)
    encrypted_text = cipher.encrypt(text.encode())
    return encrypted_text, iv

def encrypt_text_ctr_aes(text, key):
    nonce = os.urandom(8)
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    encrypted_text = cipher.encrypt(text.encode())
    return encrypted_text, nonce.hex()

def encrypt_image(image_path, mode, encryption_method, key):
    # Print the generated key
    print("Key:", key.hex())

    # Generate a random IV
    iv = None
    if mode in ["CBC", "CFB", "OFB"]:
        if encryption_method == "AES":
            iv = os.urandom(16)
        elif encryption_method == "DES":
            iv = generate_iv_des()
        print("IV:", iv.hex())

    message = Image.open(image_path)
    message_bytes = message.tobytes()

    block_size = 16
    remainder = len(message_bytes) % block_size
    if remainder:
        padding_size = block_size - remainder
        message_bytes += bytes([padding_size]) * padding_size

    if encryption_method == "AES":
        if mode == "ECB":
            cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend()).encryptor()
        elif mode == "CBC":
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()).encryptor()
        elif mode == "CFB":
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend()).encryptor()
        elif mode == "OFB":
            cipher = Cipher(algorithms.AES(key), modes.OFB(iv), backend=default_backend()).encryptor()
        elif mode == "CTR":
            nonce = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend()).encryptor()
    elif encryption_method == "DES":
        if mode == "ECB":
            cipher = DES.new(key, DES.MODE_ECB)
        elif mode == "CBC":
            cipher = DES.new(key, DES.MODE_CBC, iv)
        elif mode == "CFB":
            cipher = DES.new(key, DES.MODE_CFB, iv, segment_size=64)  # Use segment_size=64 for DES CFB
        elif mode == "OFB":
            cipher = DES.new(key, DES.MODE_OFB, iv)
        else:
            print("DES Doesn't Support CTR Mode!")
            return

    if encryption_method != "AES":
        encrypted_text = cipher.encrypt(message_bytes)
    else:
        encrypted_text = cipher.update(message_bytes) + cipher.finalize()

    width, height = message.size
    E_size = width * height * 3
    if len(encrypted_text) < E_size:
        encrypted_text += b'\x00' * (E_size - len(encrypted_text))
    else:
        encrypted_text = encrypted_text[:E_size]
    output = Image.frombytes("RGB", (width, height), encrypted_text)
    output_path = image_path[:-4] + f"ENCRYPTION{mode}_{encryption_method}.jpg"
    output.save(output_path)
    print("Your image has been encrypted successfully.")
    return output_path

while True:
    choose = input("Please input if you want to encrypt an image or text: ").lower()

    if choose == "image":
        print("You choose to encrypt an image.")
        
        # Prompt the user to choose the encryption mode
        mode = input("Please choose an encryption mode for the image (ECB, CBC, CFB, OFB, or CTR): ").upper()

        if mode not in ["ECB", "CBC", "CFB", "OFB", "CTR"]:
            print("Invalid encryption mode. Please choose one of ECB, CBC, CFB, OFB, or CTR.")
            continue

        encryption_method = input("Please choose the encryption method for the image (AES, DES): ").upper()

        if encryption_method not in ["AES", "DES"]:
            print("Invalid encryption method. Please choose either AES or DES.")
            continue

        image_path = input("Enter the path of the image to encrypt: ")
        if not os.path.exists(image_path):
            print("Error: The provided image path does not exist.")
            continue

        key = None
        if encryption_method == "AES":
            key = generate_aes_key(16)
        elif encryption_method == "DES":
            key = generate_des_key()

        encrypted_image_path = encrypt_image(image_path, mode, encryption_method, key)
        print("Encrypted image saved at:", encrypted_image_path)
        break

    elif choose == "text":
        print("You choose to encrypt text.")
        text_mode = input("Please choose an encryption mode for the text (ECB, CBC, CFB, OFB, or CTR): ").upper()
        encryption_method = input("Please choose the encryption method for the text (AES, DES): ").upper()

        if encryption_method not in ["AES", "DES"]:
            print("Invalid encryption method. Please choose either AES or DES.")
            continue

        text = input("Enter the Plaintext: ")

        key = None
        if encryption_method == "AES":
            key = generate_aes_key(16)
            print("Key:", key.hex())
        elif encryption_method == "DES":
            key = generate_des_key()
            print("Key:", key.hex())

        if text_mode == "ECB":
            if encryption_method == "AES":
                encrypted_text = encrypt_text_ecb_aes(text, key)
            elif encryption_method == "DES":
                encrypted_text = encrypt_text_ecb_des(text, key)
        elif text_mode == "CBC":
            if encryption_method == "AES":
                encrypted_text, iv = encrypt_text_cbc_aes(text, key)
            elif encryption_method == "DES":
                encrypted_text, iv = encrypt_text_cbc_des(text, key)
            print("IV:", iv.hex())
        elif text_mode == "CFB":
            if encryption_method == "AES":
                encrypted_text, iv = encrypt_text_cfb_aes(text, key)
            elif encryption_method == "DES":
                encrypted_text, iv = encrypt_text_cfb_des(text, key)
            print("IV:", iv.hex())
        elif text_mode == "OFB":
            if encryption_method == "AES":
                encrypted_text, iv = encrypt_text_ofb_aes(text, key)
            elif encryption_method == "DES":
                encrypted_text, iv = encrypt_text_ofb_des(text, key)
            print("IV:", iv.hex())
        elif text_mode == "CTR":
            if encryption_method == "AES":
                encrypted_text, nonce = encrypt_text_ctr_aes(text, key)
                print("Nonce:", nonce)
            elif encryption_method == "DES":
                print("DES Doesn't Support CTR Mode!")
            break
        print("Encrypted text:", encrypted_text.hex())
        print(f"The text encrypted using {text_mode} mode and {encryption_method} method.")
        break

    else:
        print("Wrong input. Please choose again.")
