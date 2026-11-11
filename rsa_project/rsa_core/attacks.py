"""Minh hoạ RSA textbook có tính nhân, không cần biết khoá riêng."""
from .rsa import encrypt_int, decrypt_int


def multiplicative_demo(public, private, message=88, factor=2):
    ciphertext = encrypt_int(message, public)
    # Kẻ sửa bản mã chỉ cần e,n và hệ số factor.
    changed = ciphertext * encrypt_int(factor, public) % public.n
    recovered = decrypt_int(changed, private)
    return dict(message=message, ciphertext=ciphertext, factor=factor,
                changed_ciphertext=changed, recovered=recovered,
                expected=message*factor % public.n)
