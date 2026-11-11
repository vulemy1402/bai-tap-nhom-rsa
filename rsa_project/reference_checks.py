"""Đối chiếu chuẩn độc lập, tách khỏi ba ca kiểm thử chính.

pow/math.gcd chỉ là oracle. Không được import module này vào thuật toán lõi.
"""
import math
import random
from pathlib import Path
from rsa_core.arithmetic import extended_gcd, mod_inverse, mod_exp
from rsa_core.primes import is_probable_prime
from rsa_core.keys import key_from_primes, generate_keypair
from rsa_core.rsa import encrypt_int, decrypt_int
from rsa_core.blocks import encrypt_bytes, decrypt_bytes, block_sizes


def require(condition, label):
    # Không dùng assert: chạy Python -O vẫn thực hiện đối chiếu.
    if not condition:
        raise ValueError("Đối chiếu thất bại: " + label)


def run_reference_checks():
    print("\n=== ĐỐI CHIẾU THƯ VIỆN CHUẨN (tách khỏi TC01–TC03) ===")
    for a, b in ((240, 46), (7, 160), (-31, 12), (0, 0), (0, -5), (-5, 0)):
        g, x, y = extended_gcd(a, b)
        require(g == math.gcd(a, b) and a*x+b*y == g, "Euclid/Bezout")
    print("[math.gcd] 6 cặp và đồng nhất thức Bezout: PASS")
    for a, n in ((7, 160), (17, 3120), (-3, 11), (23, 101)):
        require(mod_inverse(a, n) == pow(a, -1, n), "nghịch đảo modulo")
    print("[pow(a,-1,n)] 4 nghịch đảo: PASS")
    rng = random.Random(20261111)
    for _ in range(120):
        a, e, n = rng.randrange(-10000, 10000), rng.randrange(1000), rng.randrange(1, 10000)
        require(mod_exp(a, e, n) == pow(a, e, n), "bình phương và nhân")
    print("[pow(a,e,n)] 120 bộ số xác định: PASS")
    for p, q, e, message in ((17, 11, 7, 88), (61, 53, 17, 65)):
        public, private = key_from_primes(p, q, e)
        cipher = encrypt_int(message, public)
        plain = decrypt_int(cipher, private)
        require(cipher == pow(message, e, public.n), "RSA mã hoá")
        require(plain == pow(cipher, private.d, public.n) == message, "RSA giải mã")
        print(f"[RSA với pow] M={message}, C tự viết={cipher}, C chuẩn={pow(message,e,public.n)}, M'={plain}: PASS")
    public, private = key_from_primes(17, 11, 7)
    for message in range(public.n):
        cipher = encrypt_int(message, public)
        require(cipher == pow(message, public.e, public.n), "toàn bộ đại diện RSA")
        require(decrypt_int(cipher, private) == decrypt_int(cipher, private, use_crt=True) == message,
                "RSA trực tiếp và CRT")
    print("[pow / trực tiếp / CRT] toàn bộ 187 đại diện, gồm bội của p,q: PASS")
    for n in range(2000):
        expected = n >= 2 and all(n % d for d in range(2, math.isqrt(n)+1))
        require(is_probable_prime(n, bases=[2, 3] if n >= 5 else None) == expected, "Miller–Rabin")
    print("[Chia thử độc lập] Miller–Rabin với 0..1999: PASS")
    # Các đối chiếu bổ sung cho byte/tệp và khoá sinh ngẫu nhiên.
    public, private = generate_keypair(512)
    for message in (0, 1, private.p, private.q, public.n-1, 123456789):
        cipher = encrypt_int(message, public)
        require(cipher == pow(message, public.e, public.n), "RSA 512 bit")
        require(decrypt_int(cipher, private, use_crt=True) == pow(cipher, private.d, public.n) == message,
                "giải mã RSA 512 bit")
    print("[RSA số lớn với pow] khoá sinh 512 bit, 6 bản rõ: PASS")
    b, _ = block_sizes(public.n)
    samples = [b"", b"\x00\x00A\x00\x00", "Nhóm RSA tiếng Việt 🔐".encode()]
    samples += [bytes(i % 256 for i in range(length)) for length in (1, b-1, b, b+1, 2*b)]
    samples += [(Path(__file__).parent/'examples/message_vi.txt').read_bytes()]
    for data in samples:
        require(decrypt_bytes(encrypt_bytes(data, public), private) == data, "khôi phục byte/tệp")
    print("[So sánh byte gốc] UTF-8, byte 0, ranh giới khối và tệp thật: PASS")
    print("KẾT QUẢ ĐỐI CHIẾU: TẤT CẢ KHỚP")


if __name__ == "__main__":
    run_reference_checks()
