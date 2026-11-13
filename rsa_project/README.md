# Bài tập nhóm: hệ mã RSA tự cài đặt

Dự án Python chạy trực tiếp trong **Visual Studio Code**, gồm một chương trình RSA với dữ liệu số nguyên, văn bản UTF-8 và tệp nhị phân. Không tách phiên bản thu nhỏ. Ví dụ trong tài liệu lớp được giữ để kiểm chứng và minh hoạ từng bước.

## Chạy giao diện web trong VS Code

1. Giải nén, mở **File > Open Folder** và chọn thư mục `rsa_project`.
2. Chọn Python 3.10 trở lên trong **Python: Select Interpreter**.
3. Mở **Terminal > New Terminal**. Chạy:

   ```bash
   python web_app.py
   ```

   Trên Windows có thể dùng `py -3 web_app.py`. Trình duyệt sẽ tự mở. Nếu chưa mở, truy cập **http://127.0.0.1:8000/**. Giữ terminal đang chạy; nhấn `Ctrl+C` tại terminal để dừng. Nếu cổng đã bận: `python web_app.py --port 8001`, sau đó mở http://127.0.0.1:8001/.

   Hoặc chọn **Run and Debug > RSA: Giao diện web**, nhấn F5.

4. **Số nguyên**: mặc định theo slide p=17, q=11, e=7, M=88. Nhấn **Mã hoá & giải mã**; mở **Xem các bước trung gian** để thuyết trình.
5. **Văn bản**: nhấn **Khoá văn bản** ở bên trái (p=61, q=53, e=17), chọn tab Văn bản, nhập nội dung, nhấn **Mã hoá văn bản** rồi **Giải mã bản mã**. Cũng có thể nhập các khoá khác hoặc nhấn **Tự sinh khoá 512 bit**.
6. **Tệp dữ liệu**: chọn khoá văn bản hoặc sinh khoá; chọn tệp gốc nhỏ tối đa 1 MB; nhấn **Mã hoá & tải xuống**. Tiếp theo chọn tệp `.rsa` vừa tải xuống, giữ nguyên p,q,e và nhấn **Giải mã & tải xuống**. Tệp khôi phục sẽ có tên gốc, có thể kiểm tra byte bằng `fc /b` trên Windows. Lưu p,q,e nếu cần giải mã về sau.
7. Tab **Kiểm thử** chạy đúng 3 ca chính và phần đối chiếu chuẩn. Thời gian tạo khoá, mã hoá, giải mã hoặc kiểm thử sẽ hiện ngay sau từng thao tác; tệp được đọc/tải qua trình duyệt nên thời gian này không tính thời gian chọn, đọc hoặc lưu tệp.

Web chỉ chạy trên máy tại địa chỉ `127.0.0.1`, không triển khai lên Internet. Chương trình dùng `http.server`, không cần `pip install`. Không chia sẻ p,q,e khi sử dụng cho dữ liệu cần bảo mật; dự án RSA textbook không có OAEP và chỉ dùng để học. Nếu nhóm đã sửa mã nguồn trên GitHub, hãy phối hợp gộp thay đổi thay vì ghi đè bản mới nhất.

## 1. Mở và chạy giao diện Terminal bằng Visual Studio Code

1. Cài **Python 3.10 trở lên**. Trên Windows, bật **Add python.exe to PATH** khi cài.
2. Giải nén bộ mã nguồn. Trong VS Code, chọn **File > Open Folder**, mở đúng thư mục `rsa_project` chứa `main.py`.
3. Cài extension **Python** của Microsoft (dự án có gợi ý extension). Nếu Run/Debug yêu cầu, cài thêm **Python Debugger** của Microsoft.
4. Nhấn `Ctrl+Shift+P`, chọn **Python: Select Interpreter**, chọn Python đã cài.
5. Mở **Run and Debug**, chọn **RSA: Menu chính**, nhấn **F5**. Nhập dữ liệu trong **Terminal**, không nhập trong Debug Console.

Không cần `pip install`, không cần OpenSSL và không cần kết nối mạng để chạy chương trình. Nếu chưa có VS Code/Python thì việc cài đặt ban đầu cần thực hiện riêng.

Cách chạy qua **Terminal > New Terminal**:

```bash
python main.py
```

Trên Windows, nếu `python` không được nhận diện nhưng đã cài Python Launcher, thay `python` bằng `py -3` trong các lệnh bên dưới. Nên kiểm tra `python --version` trước khi chạy. Nếu tiếng Việt hiển thị lỗi trong terminal cũ trên Windows, dùng terminal tích hợp mới và thử `python -X utf8 main.py`.

## 2. Các thuật toán tự viết

| Module | Chức năng |
|---|---|
| `rsa_core/arithmetic.py` | Euclid mở rộng; nghịch đảo modulo; bình phương và nhân |
| `rsa_core/primes.py` | Miller–Rabin nhiều vòng; sinh số nguyên tố |
| `rsa_core/keys.py` | Tạo, kiểm tra cặp khoá RSA từ p,q,e; tự sinh khoá |
| `rsa_core/rsa.py` | Mã hoá/giải mã số nguyên; giải mã CRT |
| `rsa_core/blocks.py` | Chia khối byte, đóng gói, khôi phục tệp |
| `rsa_core/key_io.py` | Lưu/nạp khoá JSON |
| `rsa_core/attacks.py` | Minh hoạ sửa bản mã nhờ tính nhân của RSA textbook |
| `rsa_core/cli.py` | Menu, tham số dòng lệnh, đo thời gian, đọc/ghi và hiển thị |
| `web_app.py` | Chạy web cục bộ, kết nối giao diện với lõi RSA |
| `web/index.html`, `web/style.css`, `web/app.js` | Giao diện web và xử lý tương tác |
| `tests/test_rsa.py` | Đúng 3 ca chính: slide, tự làm, lỗi |
| `reference_checks.py` | Đối chiếu Python chuẩn và kiểm tra bổ sung, tách khỏi 3 ca chính |

Lõi không dùng `pow`, `math.gcd`, `hashlib`, `Crypto`, `cryptography` hay OpenSSL. `secrets` chỉ cung cấp số ngẫu nhiên hệ điều hành; số nguyên lớn, phép nhân/chia và chuyển byte dùng Python chuẩn. `pow` và `math.gcd` chỉ xuất hiện trong bộ kiểm thử để đối chiếu.

## 3. Demo số nguyên và các bước trung gian

Chọn mục **1** trong menu, nhập `p`, `q`, `e`, `M`. Hoặc:

```bash
python main.py number --p 17 --q 11 --e 7 --message 88
```

Kết quả phải có:

```text
p=17; q=11; n=187; phi=160
KU=(e=7, n=187); KR=(d=23, p=17, q=11)
M=88 -> C=11 -> M'=88; CRT=88; KHỚP=True
```

Đây là ví dụ trang **43–44** của tài liệu lớp **Chương 3 - Mã hoá khoá công khai (1).pdf**. Chương trình còn in phép chia Euclid, hệ số Bezout, Miller–Rabin với cơ sở 2, các bit số mũ, kết quả bình phương/nhân từng bước và các giá trị CRT. Việc hiện khoá riêng ở đây phục vụ trình bày bài tập.

Đổi sang dữ liệu tự chọn:

```bash
python main.py number --p 61 --q 53 --e 17 --message 65
```

Kỳ vọng `d=2753`, `n=3233`, `65 -> 2790 -> 65`. Thêm `--quiet` để ẩn bảng trung gian. Điều kiện: p,q là hai số nguyên tố lẻ khác nhau; `1<e<phi(n)`, `gcd(e,phi(n))=1`; `0<=M<n`.

## 4. Nhập văn bản tiếng Việt và khoá

Chọn mục **2**: nhập `p=61`, `q=53`, `e=17` rồi nhập bản rõ, chẳng hạn `Nhóm RSA kiểm tra tiếng Việt 🔐`. Chương trình hiện bản mã hex và văn bản giải mã; `KHỚP=True` cho biết dữ liệu byte trùng hoàn toàn.

Hoặc sinh khoá lớn rồi dùng tệp khoá:

```bash
python main.py keygen --bits 1024 --out keys
python main.py text --public keys/public.json --private keys/private.json
```

Với văn bản/tệp cần `n>=256`, vì mỗi byte có thể đến 255. Khoá lớp `n=187` vẫn dùng được cho bản rõ số nguyên 88, nhưng không dùng cho toàn bộ byte UTF-8.

## 5. Demo một tệp thật

Có sẵn tệp tiếng Việt nhiều đoạn trong `examples/message_vi.txt`. Chạy một lệnh để tự sinh khoá, mã hoá và giải mã:

```bash
python main.py demo-file --out demo_output
```

Chương trình xuất:

- `demo_output/public.json`: khoá công khai;
- `demo_output/private.json`: khoá riêng dạng rõ để học tập;
- `demo_output/encrypted.rsa`: tệp mã;
- `demo_output/restored.bin`: đúng byte của tệp nguồn, có thể mở bằng VS Code như văn bản.

Terminal hiện kích thước, thời gian và `KHỚP TỪNG BYTE=True`. Tên `.bin` dùng chung cho mọi loại đầu vào; có thể đổi đuôi thành `.txt` hoặc đuôi gốc sau khi khôi phục.

Mã hoá/giải mã riêng từng lệnh, dùng lại khoá đã sinh:

```bash
python main.py encrypt --key keys/public.json --input examples/message_vi.txt --output message.rsa
python main.py decrypt --key keys/private.json --input message.rsa --output restored.txt
```

Lệnh cũng áp dụng cho ảnh PNG/JPG nhỏ, chỉ cần thay đường dẫn và giữ đúng đuôi tệp đầu ra. Đường dẫn chứa dấu cách cần đặt trong dấu ngoặc kép. Chương trình đọc tệp vào bộ nhớ; thiết kế cho tệp nhỏ phục vụ demo.

**Không ghi đè tệp đã có**: chạy lại `keygen`/`demo-file` cần thư mục mới hoặc tự dọn kết quả cũ. Ví dụ lần hai dùng `--out demo_output_2`.

## 6. Kiểm thử và đối chiếu

```bash
python main.py test
```

Hoặc chọn cấu hình **RSA: Toàn bộ kiểm thử và đối chiếu** rồi F5; hoặc mở biểu tượng **Testing** trong VS Code. Có thể chạy trực tiếp:

```bash
python -m unittest discover -s tests -v
```

Bộ kiểm thử chính có **đúng 3 ca** theo yêu cầu:

| Ca | Đầu vào | Kết quả mong đợi |
|---|---|---|
| TC01 – Ví dụ slide thầy | p=17, q=11, e=7, M=88 | n=187, d=23, C=11, giải mã lại 88 |
| TC02 – Tự làm ngoài ví dụ slide | p=61, q=53, e=17, M=65 | n=3233, d=2753, C=2790, giải mã lại 65 |
| TC03 – Lỗi | p=17, q=11, e=2 | ValueError: không tồn tại nghịch đảo vì gcd(2,160)=2 |

Mỗi ca in đầu vào, kỳ vọng, thực tế và PASS. TC03 được tính là PASS khi chương trình **bắt đúng lỗi mong đợi**, không phải khi tạo được khoá sai. Xem thêm `docs/KIEM_THU.md`.

Sau 3 ca chính, `main.py test` tự chạy phần **đối chiếu chuẩn riêng** trong `reference_checks.py`: gồm phép toán, toàn bộ 187 đại diện bản rõ của khoá lớp, khoá sinh 512 bit, UTF-8, byte 0, ranh giới khối và tệp thật. Có thể chạy riêng bằng `python reference_checks.py`. Chạy qua biểu tượng Testing hoặc lệnh unittest chỉ chạy 3 ca chính.

Các dòng `[math.gcd]`, `[pow(...)]`, `[RSA với pow]` và các dòng `PASS` in rõ kết quả so với `pow(a,e,n)`, `pow(a,-1,n)`, `math.gcd`; Miller–Rabin được đối chiếu với phép chia thử độc lập trên 0..1999. Cơ sở Miller–Rabin cố định chỉ nằm trong kiểm thử/minh hoạ; sinh khoá dùng 40 cơ sở ngẫu nhiên mỗi lần kiểm tra.

**Phạm vi đối chiếu:** đáp ứng nhánh “đối chiếu với thư viện chuẩn” của đề bài bằng Python built-ins/math cho phép toán và RSA primitive. Không tuyên bố đây là bộ test vector NIST/RFC, cũng không đối chiếu định dạng tệp riêng với PKCS#1. Tài liệu RFC 8017 mục 5.1.1–5.1.2 được dùng làm tham chiếu công thức primitive.

`evidence/` chứa log chạy thực tế tại lúc đóng gói. Thời gian phụ thuộc máy; hãy chạy lại trên máy trình bày.

## Đo thời gian ngay khi chạy

**Không cần chọn benchmark mới thấy thời gian.** Chạy menu mục 1, 2 hoặc 3, hay các lệnh `number`, `text`, `demo-file`, `keygen`, `encrypt`, `decrypt` sẽ tự in bảng **THỜI GIAN THỰC HIỆN** sau kết quả.

Bảng hiển thị giây và mili giây với độ chính xác đủ để quan sát các phép tính RSA nhỏ. Mục 1 có thời gian tạo/kiểm tra khoá, mã hoá, giải mã trực tiếp, giải mã CRT và tổng của bốn công đoạn. Tổng này bao gồm cả hai cách giải mã đã chạy; không phải thời gian của một luồng chỉ dùng một cách giải mã. Mục 2 tính tổng mã hoá và giải mã; mục 3 có thêm sinh khoá. Dùng `time.perf_counter()` để đo thời gian thực trôi qua của các lời gọi xử lý, không tính chờ nhập, in bảng hoặc đọc/ghi tệp. Việc thu thập bước trung gian trong lời gọi thuật toán vẫn nằm trong phép đo. Đây là thời gian xử lý từng lượt, không phải thời gian toàn bộ tiến trình từ mở đến đóng menu.

Muốn đo trên nhiều kích thước dữ liệu thì dùng benchmark bên dưới.

## 7. Phần khuyến khích

```bash
python main.py benchmark --bits 512
python main.py attack
```

Benchmark đo mã hoá/giải mã cho 1 KiB, 4 KiB, 16 KiB, so sánh dữ liệu sau từng lượt. Thời gian không bao gồm sinh khoá và I/O. Đây là một lần đo mỗi cỡ dữ liệu, chưa phải thí nghiệm thống kê.

Demo tấn công sửa `C` thành `C'=C*r^e mod n`; người nhận thu được `M*r mod n`. Với ví dụ lớp, chọn r=2 làm 88 bị biến thành 176 mà không cần khoá riêng để sửa bản mã. Xem giải thích ở `docs/THUYET_TRINH.md`.

## 8. Giới hạn cần trình bày trung thực

Đây là **RSA textbook cho bài tập**, chưa có OAEP, xác thực, chống timing/side channel hay quản lý khoá sản phẩm. Độ dài header giữ byte gốc, không phải padding mật mã. Khối trùng nhau tạo bản mã trùng nhau; sửa nội dung có thể không bị phát hiện. Kiểm tra định dạng và so sánh byte trong demo không thay thế cơ chế bảo đảm toàn vẹn.

Mặc định 1024 bit nhằm demo nhanh; có thể sinh 2048 bit bằng `--bits 2048`, nhưng tăng độ dài khoá không khắc phục việc thiếu padding/xác thực. RSA thực tế thường dùng cơ chế chuẩn để bảo vệ khoá phiên thay vì trực tiếp mã hoá cả tệp. Không dùng dự án này bảo vệ dữ liệu thật nhạy cảm.

## 9. Phân công và GitHub

Nhóm tự điền tên và nhiệm vụ vào `docs/PHAN_CONG.md`. Tạo repository GitHub và commit phần công việc thật của từng thành viên; không tạo lịch sử đóng góp giả. Mã nguồn đã có `.gitignore` để tránh đưa khoá demo và tệp đầu ra vào Git.

## Nguồn

- Tài liệu lớp: **Chương 3 - Mã hoá khoá công khai (1).pdf**, trang 43–44 (RSA và CRT), phần lý thuyết số (Euclid, nghịch đảo, Miller–Rabin).
- RFC 8017, PKCS #1 v2.2, mục 5.1: https://www.rfc-editor.org/rfc/rfc8017.html#section-5.1
- Python built-in `pow`: https://docs.python.org/3/library/functions.html#pow
- Python `math.gcd`: https://docs.python.org/3/library/math.html#math.gcd
