"""Euclid mở rộng, nghịch đảo modulo, bình phương và nhân.

trace là danh sách tuỳ chọn để ghi trạng thái; thuật toán không in giao diện.
"""


def extended_gcd(a, b, trace=None):
    """Trả (g, x, y) sao cho ax + by = g = gcd(a, b) >= 0."""
    r0, r1 = abs(a), abs(b)
    x0, x1, y0, y1 = 1, 0, 0, 1
    while r1:
        q = r0 // r1
        if trace is not None:
            trace.append(dict(r0=r0, r1=r1, q=q, remainder=r0-q*r1,
                              x0=x0, x1=x1, y0=y0, y1=y1))
        r0, r1 = r1, r0-q*r1
        x0, x1 = x1, x0-q*x1
        y0, y1 = y1, y0-q*y1
    return r0, x0 if a >= 0 else -x0, y0 if b >= 0 else -y0


def mod_inverse(a, modulus, trace=None):
    """Tìm a^(-1) mod modulus bằng Euclid mở rộng."""
    if modulus <= 1:
        raise ValueError("Modulo phải lớn hơn 1.")
    g, x, _ = extended_gcd(a, modulus, trace)
    if g != 1:
        raise ValueError("Không tồn tại nghịch đảo: gcd(a, modulo) != 1.")
    return x % modulus


def mod_exp(base, exponent, modulus, trace=None):
    """Bình phương và nhân từ trái sang phải; không gọi pow()."""
    if modulus <= 0 or exponent < 0:
        raise ValueError("Modulo phải dương và số mũ không âm.")
    result = 1 % modulus
    base %= modulus
    for i, bit in enumerate(bin(exponent)[2:], 1):
        before = result
        squared = result * result % modulus
        result = squared * base % modulus if bit == "1" else squared
        if trace is not None:
            trace.append(dict(step=i, bit=int(bit), before=before,
                              squared=squared, result=result))
    return result
