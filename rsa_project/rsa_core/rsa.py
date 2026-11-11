"""RSA trên số nguyên; hỗ trợ giải mã trực tiếp và CRT."""
from .arithmetic import mod_exp, mod_inverse


def _check(value, n):
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < n:
        raise ValueError("Đại diện khối phải là số nguyên trong [0, n-1].")


def encrypt_int(message, key, trace=None):
    _check(message, key.n)
    return mod_exp(message, key.e, key.n, trace)


def decrypt_int(ciphertext, key, trace=None, use_crt=False):
    _check(ciphertext, key.n)
    if not use_crt:
        return mod_exp(ciphertext, key.d, key.n, trace)
    # p,q lẻ nên dP,dQ khác 0: đúng cả khi ciphertext chia hết p hoặc q.
    dp, dq = key.d % (key.p-1), key.d % (key.q-1)
    mp = mod_exp(ciphertext, dp, key.p)
    mq = mod_exp(ciphertext, dq, key.q)
    q_inv = mod_inverse(key.q, key.p)
    h = q_inv * (mp-mq) % key.p
    message = mq + h*key.q
    if trace is not None:
        trace.append(dict(dp=dp, dq=dq, mp=mp, mq=mq,
                          q_inverse=q_inv, h=h, result=message))
    return message
