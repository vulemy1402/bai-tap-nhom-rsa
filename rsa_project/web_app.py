"""Máy chủ web cục bộ cho bài tập RSA, chỉ dùng thư viện chuẩn Python."""
import base64
import binascii
import json
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Timer
from time import perf_counter

from rsa_core.arithmetic import extended_gcd
from rsa_core.blocks import decrypt_bytes, encrypt_bytes
from rsa_core.keys import generate_keypair, key_from_primes
from rsa_core.rsa import decrypt_int, encrypt_int

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
MAX_DATA = 1024 * 1024
MAX_REQUEST = 4 * 1024 * 1024


def integer(data, name):
    value = str(data.get(name, "")).strip()
    if not value or not value.isascii() or not value.isdecimal() or len(value) > 1000:
        raise ValueError(f"{name} phải là số nguyên không âm (tối đa 1000 chữ số).")
    return int(value)


def keys(data):
    p, q, e = (integer(data, item) for item in ("p", "q", "e"))
    return key_from_primes(p, q, e)


def elapsed(start):
    return (perf_counter() - start) * 1000


def blob(data):
    try:
        raw = base64.b64decode(str(data.get("data", "")), validate=True)
    except (ValueError, binascii.Error):
        raise ValueError("Dữ liệu mã hoá không đúng định dạng Base64.")
    if len(raw) > 2 * MAX_DATA + 2048:
        raise ValueError("Tệp quá lớn. Hãy chọn tệp nhỏ tối đa 1 MB.")
    return raw


def handle_api(path, data):
    if path == "/api/generate":
        bits = integer(data, "bits")
        if bits not in (512, 1024):
            raise ValueError("Chọn khoá 512 hoặc 1024 bit.")
        start = perf_counter()
        public, private = generate_keypair(bits)
        return {"p": str(private.p), "q": str(private.q), "e": str(public.e),
                "n": str(public.n), "time_ms": elapsed(start)}

    if path == "/api/tests":
        start = perf_counter()
        run = subprocess.run([sys.executable, "-u", "main.py", "test"], cwd=ROOT,
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=90)
        return {"ok": run.returncode == 0, "output": run.stdout + run.stderr,
                "time_ms": elapsed(start)}

    start = perf_counter()
    public, private = keys(data)
    key_ms = elapsed(start)
    if path == "/api/number":
        message = integer(data, "message")
        enc_trace, dec_trace, euclid = [], [], []
        extended_gcd(public.e, (private.p - 1) * (private.q - 1), euclid)
        start = perf_counter()
        cipher = encrypt_int(message, public, enc_trace)
        enc_ms = elapsed(start)
        start = perf_counter()
        recovered = decrypt_int(cipher, private, dec_trace)
        dec_ms = elapsed(start)
        # Dùng chuỗi cho số lớn để JavaScript không làm tròn.
        return {"m": str(message), "c": str(cipher), "recovered": str(recovered),
                "n": str(public.n), "e": str(public.e), "d": str(private.d),
                "phi": str((private.p - 1) * (private.q - 1)),
                "valid": message == recovered, "key_ms": key_ms,
                "enc_ms": enc_ms, "dec_ms": dec_ms,
                "enc_trace": [{k: str(v) for k, v in row.items()} for row in enc_trace],
                "dec_trace": [{k: str(v) for k, v in row.items()} for row in dec_trace],
                "euclid": [{k: str(v) for k, v in row.items()} for row in euclid]}
    if path in ("/api/text/encrypt", "/api/text/decrypt", "/api/file/encrypt", "/api/file/decrypt"):
        is_text = "/text/" in path
        encrypt = path.endswith("/encrypt")
        if is_text and encrypt:
            raw = str(data.get("text", "")).encode("utf-8")
        else:
            raw = blob(data)
        if encrypt and len(raw) > MAX_DATA:
            raise ValueError("Dữ liệu vượt quá 1 MB.")
        start = perf_counter()
        output = encrypt_bytes(raw, public) if encrypt else decrypt_bytes(raw, private)
        time_ms = elapsed(start)
        result = {"data": base64.b64encode(output).decode("ascii"),
                  "input_bytes": len(raw), "output_bytes": len(output),
                  "time_ms": time_ms, "key_ms": key_ms}
        if is_text and not encrypt:
            try:
                result["text"] = output.decode("utf-8")
            except UnicodeDecodeError:
                raise ValueError("Dữ liệu giải mã không phải văn bản UTF-8.")
        return result
    raise ValueError("Chức năng không tồn tại.")


class Handler(BaseHTTPRequestHandler):
    def send_content(self, status, content, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        routes = {"/": ("index.html", "text/html; charset=utf-8"),
                  "/style.css": ("style.css", "text/css; charset=utf-8"),
                  "/app.js": ("app.js", "application/javascript; charset=utf-8")}
        if self.path not in routes:
            self.send_error(404)
            return
        name, content_type = routes[self.path]
        self.send_content(200, (WEB / name).read_bytes(), content_type)

    def do_POST(self):
        try:
            if self.headers.get_content_type() != "application/json":
                raise ValueError("Yêu cầu phải dùng JSON.")
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_REQUEST:
                raise ValueError("Dữ liệu gửi lên quá lớn hoặc rỗng.")
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Dữ liệu yêu cầu không hợp lệ.")
            result = handle_api(self.path, data)
            self.send_content(200, json.dumps(result, ensure_ascii=False).encode("utf-8"),
                              "application/json; charset=utf-8")
        except (ValueError, KeyError, UnicodeDecodeError, subprocess.TimeoutExpired) as error:
            self.send_content(400, json.dumps({"error": str(error)}, ensure_ascii=False).encode("utf-8"),
                              "application/json; charset=utf-8")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Giao diện web RSA cục bộ")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as error:
        print(f"Không mở được cổng {args.port}: {error}. Thử python web_app.py --port 8001")
        return 1
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Giao diện RSA đang chạy tại: {url}", flush=True)
    print("Giữ cửa sổ Terminal mở; nhấn Ctrl+C để dừng.", flush=True)
    if not args.no_browser:
        Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng máy chủ.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
