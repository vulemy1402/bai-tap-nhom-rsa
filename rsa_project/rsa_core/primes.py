"""Miller–Rabin và sinh số nguyên tố xác suất.

secrets chỉ cung cấp ngẫu nhiên hệ điều hành, không thực hiện thuật toán RSA.
"""
import secrets
from .arithmetic import mod_exp


def is_probable_prime(n, rounds=40, trace=None, bases=None):
    """Với n lớn, mỗi vòng chọn cơ sở độc lập trong [2, n-2].

    bases chỉ phục vụ minh hoạ/kiểm thử có thể tái lập; không dùng khi sinh khoá.
    True là 'nguyên tố có xác suất cao', không phải chứng minh nguyên tố.
    """
    if rounds < 1:
        raise ValueError("Số vòng Miller–Rabin phải >= 1.")
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    if bases is not None:
        bases = tuple(bases)
        if not bases or any(not 2 <= a <= n-2 for a in bases):
            raise ValueError("Cơ sở phải thuộc [2, n-2], danh sách không rỗng.")
        witnesses = iter(bases)
    else:
        witnesses = (2 + secrets.randbelow(n-3) for _ in range(rounds))
    for a in witnesses:
        x = mod_exp(a, d, n)
        sequence = [x]
        passed = x in (1, n-1)
        if not passed:
            for _ in range(s-1):
                x = x*x % n
                sequence.append(x)
                if x == n-1:
                    passed = True
                    break
        if trace is not None:
            trace.append(dict(n=n, s=s, d=d, base=a, sequence=sequence,
                              passed=passed))
        if not passed:
            return False
    return True


def generate_prime(bits, rounds=40):
    if bits < 3:
        raise ValueError("Số nguyên tố sinh tự động cần ít nhất 3 bit.")
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits-1)) | 1
        if is_probable_prime(candidate, rounds):
            return candidate
