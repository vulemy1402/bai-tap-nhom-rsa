"""Giao diện dòng lệnh; việc đọc/ghi tệp và in được tách khỏi lõi."""
import argparse
import json
import sys
from pathlib import Path
from time import perf_counter
from .keys import key_from_primes, generate_keypair
from .key_io import save_key, load_key
from .rsa import encrypt_int, decrypt_int
from .blocks import encrypt_bytes, decrypt_bytes
from .primes import is_probable_prime
from .attacks import multiplicative_demo

ROOT = Path(__file__).resolve().parent.parent


def print_trace(label, rows):
    print(label)
    for row in rows:
        print("  " + " | ".join(f"{k}={v}" for k, v in row.items()))


def print_timings(items):
    """In thời gian ngay sau mỗi lượt demo, không tính nhập liệu/in bảng."""
    print("\nTHỜI GIAN THỰC HIỆN")
    for label, seconds in items:
        print(f"  {label}: {seconds:.9f} giây ({seconds*1000:.6f} ms)")
    total = sum(seconds for _, seconds in items)
    print(f"  Tổng thời gian xử lý: {total:.9f} giây ({total*1000:.6f} ms)")
    print("  Đo bằng perf_counter; không tính chờ nhập, đọc/ghi tệp và in kết quả.")


def number_demo(p=17, q=11, e=7, message=88, verbose=True):
    euclid = []
    start = perf_counter()
    public, private = key_from_primes(p, q, e, euclid)
    key_time = perf_counter()-start
    print(f"p={p}; q={q}; n={public.n}; phi={(p-1)*(q-1)}")
    print(f"KU=(e={e}, n={public.n}); KR=(d={private.d}, p={p}, q={q})")
    if verbose:
        # Cơ sở cố định ở đây chỉ để tái hiện bảng minh hoạ.
        for prime in (p, q):
            rows = []
            is_probable_prime(prime, trace=rows, bases=[2])
            print_trace(f"Miller–Rabin: n={prime}, n-1=2^s*d", rows)
        print_trace("Euclid: r0=q*r1+remainder; theo dõi hệ số Bezout", euclid)
    enc, dec, crt = [], [], []
    start = perf_counter()
    c = encrypt_int(message, public, enc)
    enc_time = perf_counter()-start
    start = perf_counter()
    m = decrypt_int(c, private, dec)
    dec_time = perf_counter()-start
    start = perf_counter()
    fast = decrypt_int(c, private, crt, use_crt=True)
    crt_time = perf_counter()-start
    if verbose:
        print_trace("Mã hoá: bit từ trái sang phải; squared=before² mod n", enc)
        print_trace("Giải mã: nhân base nếu bit=1", dec)
        print_trace("Giải mã CRT", crt)
    print(f"M={message} -> C={c} -> M'={m}; CRT={fast}; KHỚP={m == fast == message}")
    print_timings([("Tạo và kiểm tra khoá", key_time), ("Mã hoá", enc_time),
                   ("Giải mã trực tiếp", dec_time), ("Giải mã CRT", crt_time)])


def text_demo(text, public, private):
    data = text.encode("utf-8")
    start = perf_counter()
    payload = encrypt_bytes(data, public)
    encrypted = perf_counter()-start
    start = perf_counter()
    restored = decrypt_bytes(payload, private)
    decrypted = perf_counter()-start
    print("Bản mã (hex, gồm header):", payload.hex())
    print("Giải mã:", restored.decode("utf-8"))
    print(f"KHỚP={restored == data}; mã hoá={encrypted:.6f}s; giải mã={decrypted:.6f}s")
    print_timings([("Mã hoá", encrypted), ("Giải mã CRT", decrypted)])


def write_new(path, data):
    """Từ chối ghi đè cả đầu vào lẫn kết quả cũ."""
    with Path(path).open("xb") as stream:
        stream.write(data)


def file_demo(source, outdir, bits):
    directory = Path(outdir)
    directory.mkdir(parents=True, exist_ok=True)
    start = perf_counter()
    public, private = generate_keypair(bits)
    key_time = perf_counter()-start
    data = Path(source).read_bytes()
    start = perf_counter()
    ciphertext = encrypt_bytes(data, public)
    enc_time = perf_counter()-start
    start = perf_counter()
    restored = decrypt_bytes(ciphertext, private)
    dec_time = perf_counter()-start
    if restored != data:
        raise ValueError("Dữ liệu sau giải mã không khớp.")
    # Tên cố định giúp dễ tìm khi thuyết trình; chạy lại cần thư mục mới.
    save_key(directory/"public.json", public)
    save_key(directory/"private.json", private)
    write_new(directory/"encrypted.rsa", ciphertext)
    write_new(directory/"restored.bin", restored)
    print(f"n={bits} bit; gốc={len(data)} byte; bản mã={len(ciphertext)} byte")
    print(f"Mã hoá={enc_time:.6f}s; giải mã CRT={dec_time:.6f}s; KHỚP TỪNG BYTE=True")
    print(f"Đã xuất khoá, encrypted.rsa và restored.bin vào {directory.resolve()}")
    print_timings([("Sinh và kiểm tra khoá", key_time), ("Mã hoá", enc_time),
                   ("Giải mã CRT", dec_time)])


def benchmark(bits=512):
    public, private = generate_keypair(bits)
    print("bytes,encrypt_seconds,decrypt_seconds,match")
    for size in (1024, 4096, 16384):
        data = (bytes(range(256))*((size+255)//256))[:size]
        start = perf_counter()
        payload = encrypt_bytes(data, public)
        enc = perf_counter()-start
        start = perf_counter()
        restored = decrypt_bytes(payload, private)
        dec = perf_counter()-start
        if restored != data:
            raise ValueError("Benchmark: dữ liệu không khớp.")
        print(f"{size},{enc:.6f},{dec:.6f},{restored == data}")


def run_tests():
    import unittest
    from reference_checks import run_reference_checks
    suite = unittest.defaultTestLoader.discover(str(ROOT/"tests"))
    passed = unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    if passed:
        run_reference_checks()
    return passed


def attack_demo():
    public, private = key_from_primes(17, 11, 7)
    result = multiplicative_demo(public, private)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("C' = C × r^e mod n -> giải mã thành M×r mod n.")
    print("Bản mã bị sửa vẫn giải mã được: RSA textbook không xác thực thông điệp.")


def menu():
    while True:
        print("\nRSA — TỰ CÀI ĐẶT | Chỉ dùng học tập (textbook, không OAEP)")
        print("1. Nhập p,q,e và bản rõ số nguyên (in từng bước)")
        print("2. Nhập văn bản UTF-8 và khoá p,q,e")
        print("3. Demo tệp thật (tự sinh khoá)")
        print("4. Chạy kiểm thử và đối chiếu thư viện chuẩn")
        print("5. Minh hoạ sửa bản mã RSA textbook")
        print("6. Đo thời gian theo kích thước dữ liệu\n0. Thoát")
        try:
            choice = input("Chọn: ").strip()
            if choice == "0":
                return True
            if choice in ("1", "2"):
                print("Ví dụ số nguyên trên lớp: p=17, q=11, e=7, M=88.")
                if choice == "2":
                    print("Văn bản cần n>=256, ví dụ p=61, q=53, e=17.")
                p, q, e = (int(input(label)) for label in ("p: ", "q: ", "e: "))
                if choice == "1":
                    number_demo(p, q, e, int(input("Bản rõ M (0<=M<n): ")))
                else:
                    public, private = key_from_primes(p, q, e)
                    text_demo(input("Bản rõ: "), public, private)
            elif choice == "3":
                source = input("Tệp nguồn (Enter dùng examples/message_vi.txt): ").strip()
                output = input("Thư mục kết quả (chưa có các tệp kết quả): ").strip()
                file_demo(source or ROOT/"examples/message_vi.txt", output or "demo_output", 1024)
            elif choice == "4":
                run_tests()
            elif choice == "5":
                attack_demo()
            elif choice == "6":
                benchmark()
            else:
                print("Lựa chọn không hợp lệ.")
        except (ValueError, OSError, KeyError, TypeError) as error:
            print(f"Lỗi: {error}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="RSA tự cài đặt — Python / Visual Studio Code")
    subs = parser.add_subparsers(dest="command")
    number = subs.add_parser("number", help="RSA số nguyên, nhập khoá và in từng bước")
    for name, default in (("p", 17), ("q", 11), ("e", 7), ("message", 88)):
        number.add_argument("--"+name, type=int, default=default)
    number.add_argument("--quiet", action="store_true")
    keygen = subs.add_parser("keygen", help="Sinh public.json và private.json")
    keygen.add_argument("--bits", type=int, default=1024)
    keygen.add_argument("--out", required=True)
    text = subs.add_parser("text", help="Nhập văn bản, mã hoá và giải mã ngay")
    text.add_argument("--public", required=True)
    text.add_argument("--private", required=True)
    for command in ("encrypt", "decrypt"):
        item = subs.add_parser(command, help=command+" một tệp")
        item.add_argument("--key", required=True)
        item.add_argument("--input", required=True)
        item.add_argument("--output", required=True)
    demo = subs.add_parser("demo-file", help="Sinh khoá, mã hoá/giải mã tệp và so sánh byte")
    demo.add_argument("--input", default=str(ROOT/"examples/message_vi.txt"))
    demo.add_argument("--out", default="demo_output")
    demo.add_argument("--bits", type=int, default=1024)
    bench = subs.add_parser("benchmark")
    bench.add_argument("--bits", type=int, default=512)
    subs.add_parser("test")
    subs.add_parser("attack")
    args = parser.parse_args(argv)
    try:
        if args.command is None:
            return 0 if menu() else 1
        if args.command == "number":
            number_demo(args.p, args.q, args.e, args.message, not args.quiet)
        elif args.command == "keygen":
            directory = Path(args.out)
            directory.mkdir(parents=True, exist_ok=True)
            start = perf_counter()
            public, private = generate_keypair(args.bits)
            key_time = perf_counter()-start
            save_key(directory/"public.json", public)
            save_key(directory/"private.json", private)
            print(f"Đã sinh khoá {public.n.bit_length()} bit vào {directory.resolve()}")
            print_timings([("Sinh và kiểm tra khoá", key_time)])
        elif args.command == "text":
            public, private = load_key(args.public), load_key(args.private, private=True)
            if public != private.public:
                raise ValueError("Hai khoá không cùng cặp.")
            text_demo(input("Nhập bản rõ UTF-8: "), public, private)
        elif args.command in ("encrypt", "decrypt"):
            private = args.command == "decrypt"
            key = load_key(args.key, private=private)
            source = Path(args.input).read_bytes()
            start = perf_counter()
            result = decrypt_bytes(source, key) if private else encrypt_bytes(source, key)
            elapsed = perf_counter()-start
            write_new(args.output, result)
            print(f"{args.command}: {len(source)} -> {len(result)} byte, {elapsed:.6f}s")
            print_timings([("Giải mã CRT" if private else "Mã hoá", elapsed)])
        elif args.command == "demo-file":
            file_demo(args.input, args.out, args.bits)
        elif args.command == "benchmark":
            benchmark(args.bits)
        elif args.command == "attack":
            attack_demo()
        elif args.command == "test":
            return 0 if run_tests() else 1
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Lỗi: {error}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nĐã kết thúc.")
        return 0
