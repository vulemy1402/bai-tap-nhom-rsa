"""Lưu/nạp JSON; số lớn dùng chuỗi thập phân tránh mất độ chính xác."""
import json
from pathlib import Path
from .keys import PublicKey, PrivateKey


def save_key(path, key):
    fields = ("n", "e", "d", "p", "q") if isinstance(key, PrivateKey) else ("n", "e")
    payload = {name: str(getattr(key, name)) for name in fields}
    payload["type"] = "private" if isinstance(key, PrivateKey) else "public"
    # Không ghi đè khoá đã có; khoá riêng chỉ cấp quyền đọc/ghi cho chủ trên POSIX.
    import os
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                 0o600 if isinstance(key, PrivateKey) else 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2)


def load_key(path, private=False):
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("Khoá JSON phải là object.")
    if private:
        if obj.get("type") != "private":
            raise ValueError("Cần tệp khoá riêng.")
        return PrivateKey(**{name: int(obj[name]) for name in ("n", "d", "p", "q", "e")})
    if obj.get("type") not in ("public", "private"):
        raise ValueError("Loại khoá không hợp lệ.")
    return PublicKey(int(obj["n"]), int(obj["e"]))
