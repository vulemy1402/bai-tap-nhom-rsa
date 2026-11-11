"""Đúng ba ca chính theo yêu cầu: slide, tự làm, lỗi."""
import unittest
from rsa_core.keys import key_from_primes
from rsa_core.rsa import encrypt_int, decrypt_int


class RSATests(unittest.TestCase):
    def test_01_vi_du_slide(self):
        """TC01: trang 43–44, p=17,q=11,e=7,M=88."""
        public, private = key_from_primes(17, 11, 7)
        cipher = encrypt_int(88, public)
        plain = decrypt_int(cipher, private)
        self.assertEqual((public.n, private.d), (187, 23))
        self.assertEqual(cipher, 11)
        self.assertEqual(plain, 88)
        self.assertEqual(decrypt_int(cipher, private, use_crt=True), 88)
        print("\n[TC01 — SLIDE] p=17, q=11, e=7, M=88")
        print(f"  Kỳ vọng: n=187, d=23, C=11, M'=88")
        print(f"  Thực tế: n={public.n}, d={private.d}, C={cipher}, M'={plain} => PASS")

    def test_02_ca_tu_lam(self):
        """TC02: bộ số ngoài ví dụ lớp, p=61,q=53,e=17,M=65."""
        public, private = key_from_primes(61, 53, 17)
        cipher = encrypt_int(65, public)
        plain = decrypt_int(cipher, private)
        self.assertEqual((public.n, private.d), (3233, 2753))
        self.assertEqual(cipher, 2790)
        self.assertEqual(plain, 65)
        self.assertEqual(decrypt_int(cipher, private, use_crt=True), 65)
        print("\n[TC02 — TỰ LÀM] p=61, q=53, e=17, M=65")
        print("  Kỳ vọng: n=3233, d=2753, C=2790, M'=65")
        print(f"  Thực tế: n={public.n}, d={private.d}, C={cipher}, M'={plain} => PASS")

    def test_03_khoa_loi(self):
        """TC03: e=2 không nguyên tố cùng nhau với phi=160."""
        expected = "Không tồn tại nghịch đảo: gcd(a, modulo) != 1."
        with self.assertRaises(ValueError) as captured:
            key_from_primes(17, 11, 2)
        self.assertEqual(str(captured.exception), expected)
        print("\n[TC03 — LỖI] p=17, q=11, e=2; phi=160; gcd(2,160)=2")
        print("  Kỳ vọng: từ chối tạo khoá, báo ValueError không tồn tại nghịch đảo")
        print(f"  Thực tế: {captured.exception} => PASS (bắt đúng lỗi mong đợi)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
