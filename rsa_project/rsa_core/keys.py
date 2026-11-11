"""Tạo khoá RSA từ p,q,e hoặc tự sinh p,q."""
from dataclasses import dataclass
from .arithmetic import extended_gcd, mod_inverse
from .primes import generate_prime, is_probable_prime


@dataclass(frozen=True)
class PublicKey:
    n: int
    e: int

    def __post_init__(self):
        if self.n <= 3 or not 1 < self.e < self.n:
            raise ValueError("Khoá công khai không hợp lệ.")


@dataclass(frozen=True)
class PrivateKey:
    n: int
    d: int
    p: int
    q: int
    e: int

    def __post_init__(self):
        if (self.p <= 2 or self.q <= 2 or self.p == self.q
                or self.p % 2 == 0 or self.q % 2 == 0
                or self.n != self.p*self.q):
            raise ValueError("p,q phải là hai số nguyên tố lẻ khác nhau; n=p*q.")
        phi = (self.p-1)*(self.q-1)
        if not 1 < self.e < phi or not 0 < self.d < phi or self.e*self.d % phi != 1:
            raise ValueError("e,d không thỏa điều kiện khoá RSA của dự án.")
        if not is_probable_prime(self.p) or not is_probable_prime(self.q):
            raise ValueError("p hoặc q không vượt qua Miller–Rabin.")

    @property
    def public(self):
        return PublicKey(self.n, self.e)


def key_from_primes(p, q, e=65537, trace=None):
    if p <= 2 or q <= 2 or p == q or not is_probable_prime(p) or not is_probable_prime(q):
        raise ValueError("p,q phải là hai số nguyên tố lẻ khác nhau.")
    phi = (p-1)*(q-1)
    if not 1 < e < phi:
        raise ValueError("Cần 1 < e < phi(n).")
    d = mod_inverse(e, phi, trace)
    private = PrivateKey(p*q, d, p, q, e)
    return private.public, private


def generate_keypair(bits=1024, e=65537):
    """Sinh đúng bits bit cho n. Mặc định 1024 chỉ để demo nhanh."""
    if bits < 32 or e < 3 or e % 2 == 0 or e.bit_length() >= bits-2:
        raise ValueError("Cần bits >= 32, e lẻ >= 3 và đủ nhỏ so với n.")
    while True:
        p = generate_prime(bits//2)
        q = generate_prime(bits-bits//2)
        phi = (p-1)*(q-1)
        if p == q or (p*q).bit_length() != bits or e >= phi:
            continue
        if extended_gcd(e, phi)[0] == 1:
            return key_from_primes(p, q, e)
