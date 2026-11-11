"""Đóng gói byte thành khối RSA textbook, không padding mật mã.

Header: MAGIC (8 byte), độ dài gốc uint64, n dưới dạng k byte.
Sau header là các khối bản mã k byte. Độ dài gốc giữ byte 0 đầu/cuối.
Đây là định dạng riêng của bài tập, không phải PKCS#1/OAEP.
"""
from .rsa import encrypt_int, decrypt_int

MAGIC = b"RSALAB1\x00"


def block_sizes(n):
    plain = (n.bit_length()-1)//8
    cipher = (n.bit_length()+7)//8
    if plain < 1:
        raise ValueError("n phải >= 256 để mã hoá dữ liệu byte.")
    return plain, cipher


def encrypt_bytes(data, key):
    b, k = block_sizes(key.n)
    header = MAGIC + len(data).to_bytes(8, "big") + key.n.to_bytes(k, "big")
    result = bytearray(header)
    for offset in range(0, len(data), b):
        m = int.from_bytes(data[offset:offset+b], "big")
        result.extend(encrypt_int(m, key).to_bytes(k, "big"))
    return bytes(result)


def decrypt_bytes(payload, key, use_crt=True):
    b, k = block_sizes(key.n)
    header_size = 16+k
    if len(payload) < header_size or payload[:8] != MAGIC:
        raise ValueError("Sai định dạng RSALAB1 hoặc header bị cắt.")
    length = int.from_bytes(payload[8:16], "big")
    if int.from_bytes(payload[16:header_size], "big") != key.n:
        raise ValueError("Modulo khoá không khớp tệp.")
    count = (length+b-1)//b
    if len(payload)-header_size != count*k:
        raise ValueError("Độ dài tệp mã không khớp header.")
    result = bytearray()
    for index in range(count):
        start = header_size + index*k
        c = int.from_bytes(payload[start:start+k], "big")
        m = decrypt_int(c, key, use_crt=use_crt)
        width = min(b, length-index*b)
        if m >= 1 << (8*width):
            raise ValueError("Khối giải mã không vừa độ dài khai báo.")
        result.extend(m.to_bytes(width, "big"))
    return bytes(result)
