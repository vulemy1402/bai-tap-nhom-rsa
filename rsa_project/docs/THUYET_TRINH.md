# Ghi chú báo cáo và kịch bản thuyết trình

## 1. Ý tưởng RSA

Chọn hai số nguyên tố lẻ phân biệt p,q; n=pq; phi(n)=(p-1)(q-1). Chọn e nguyên tố cùng nhau với phi(n), tính d=e^(-1) mod phi(n). Khoá công khai là (e,n); khoá riêng chứa d,p,q (dự án lưu thêm e,n để kiểm tra và tiện nạp).

Mã hoá C=M^e mod n; giải mã M=C^d mod n, với 0<=M<n. Vì ed=1+k*phi(n), ta xét riêng theo p và q: nếu M chia hết p, cả hai vế đều bằng 0 modulo p; nếu không, dùng định lý Fermat và (p-1)|phi(n) để có M^(ed)=M mod p. Tương tự với q; CRT suy ra M^(ed)=M mod n. Lập luận này bao phủ cả trường hợp gcd(M,n)!=1, ví dụ M=88,n=187 của lớp.

## 2. Thuật toán nền và độ phức tạp

- **Euclid mở rộng:** cập nhật hai số dư và hai cặp hệ số Bezout qua mỗi phép chia. Khi số dư bằng 0, thu được g=ax+by. Số phép chia O(log min(|a|,|b|)) khi cả hai khác 0.
- **Nghịch đảo modulo:** nếu gcd(a,n)=1 thì hệ số x ở ax+ny=1 cho nghịch đảo x mod n. Nếu gcd khác 1 thì báo lỗi.
- **Bình phương và nhân:** quét bit số mũ từ trái sang phải, bình phương bộ tích luỹ rồi nhân cơ sở khi bit bằng 1. O(log e) phép nhân modulo; không phải O(log e) thời gian bit khi n lớn.
- **Miller–Rabin:** phân tích n-1=2^s*d, d lẻ. Một cơ sở a vượt kiểm tra nếu a^d bằng 1 hoặc -1, hoặc dãy bình phương tiếp chạm -1 modulo n. Nếu mọi điều kiện đều sai, n chắc chắn hợp số. Nếu vượt mọi vòng, chỉ kết luận nguyên tố có xác suất cao. Với hợp số lẻ cố định và t cơ sở độc lập chọn đều, xác suất vượt tất cả không quá 4^(-t); t=40 cho cận 2^(-80) trên từng hợp số đem kiểm tra, không phải xác suất lỗi tổng thể của mọi phiên chạy.
- **CRT:** dp=d mod(p-1), dq=d mod(q-1); mp=C^dp mod p; mq=C^dq mod q; h=q^(-1)*(mp-mq) mod p; M=mq+h*q. Hai luỹ thừa trên modulo nhỏ hơn thường nhanh hơn một luỹ thừa modulo n.

## 3. Ví dụ đúng tài liệu lớp

p=17, q=11; n=187; phi=160; e=7. Euclid: 160=22*7+6; 7=1*6+1; suy ra 1=23*7-160, nên d=23.

M=88; số mũ 7 có bit 111. Bộ tích luỹ sau các bit: 88,44,11; C=11. Số mũ 23 có bit 10111, giải mã cho 88. Theo CRT: dp=7, dq=3; mp=3, mq=0; q^(-1) mod p=14; h=8; M=0+8*11=88.

Chạy `python main.py number` để hiện các bảng đầy đủ. Đây là một đầu vào kiểm chứng của chương trình chung, không phải một phiên bản RSA riêng.

## 4. Chia khối và giữ nguyên byte

Với b=floor((bit_length(n)-1)/8), mọi khối b byte có giá trị <2^(8b)<=2^(bit_length(n)-1)<=n. Khối cuối có thể ngắn hơn. Mã hoá mỗi khối thành k=ceil(bit_length(n)/8) byte.

Định dạng riêng: magic `RSALAB1` + byte 0 (8 byte tổng), độ dài gốc uint64 big-endian (8 byte), n (k byte), rồi các khối mã (k byte mỗi khối). Khi giải mã, biết chính xác độ dài khối cuối và dùng `to_bytes(width,'big')` để phục hồi cả byte 0 đầu. File rỗng có header và 0 khối. Bộ đọc dùng khoá để xác định k; đây không phải định dạng trao đổi chuẩn.

Header có n giúp từ chối khoá sai modulo, độ dài giúp phát hiện cắt/nối đơn giản. Không có MAC/chữ ký nên không bảo đảm phát hiện sửa bản mã hoặc header có chủ đích. Hàm demo chỉ khẳng định bản gốc và bản giải mã của chính lượt chạy trùng byte.

## 5. Kịch bản demo 7–10 phút

1. Mở thư mục trong VS Code; giới thiệu tách module thuật toán và giao diện.
2. F5 cấu hình menu. Mục 1: nhập 17,11,7,88; giải thích Euclid và các bit bình phương/nhân.
3. Mục 2: nhập 61,53,17; nhập một câu tiếng Việt; chỉ ra bản mã hex và dòng KHỚP.
4. Terminal: `python main.py demo-file --out demo_output`. Mở tệp nguồn và restored.bin; chỉ ra dòng KHỚP TỪNG BYTE và kích thước tệp.
5. `python main.py test`: giới thiệu ca tự viết, số ca đối chiếu và kết quả cuối cùng. Ba ca chính là ví dụ slide, bộ số tự làm và khoá lỗi; phần đối chiếu riêng dùng Python chuẩn làm oracle toán học, không tự nhận có NIST vector.
6. `python main.py benchmark --bits 512`: chỉ ra chi phí tăng theo số khối.
7. `python main.py attack`: giải thích kẻ sửa bản mã không cần d; chốt giới hạn của textbook RSA và nhu cầu dùng lược đồ chuẩn có padding/xác thực.

Nếu thư mục demo đã chứa kết quả, dùng tên mới trước buổi trình bày. Sinh khoá số lớn có thời gian ngẫu nhiên; có thể sinh sẵn khoá demo trước giờ trình bày rồi chạy encrypt/decrypt riêng.

## 6. Minh hoạ tấn công tính nhân

Do (M*r)^e mod n = (M^e)*(r^e) mod n, từ bản mã C và khoá công khai, kẻ tấn công tạo được C'=C*r^e mod n. Người nhận giải mã C' thành M*r mod n. Với p=17,q=11,e=7,M=88,r=2: C=11; r^e mod n=128; C'=99; kết quả giải mã là 176.

Đây là minh hoạ tính dễ sửa của textbook RSA. Không cần giả định giải được bài toán phân tích n. Ví dụ không chứng minh phá được OAEP hay một hệ thống RSA đã triển khai đầy đủ. Chạy trong môi trường bài tập với khoá do chương trình tạo.

## 7. Liên hệ tiêu chí chấm

| Yêu cầu | Minh chứng |
|---|---|
| Tự cài RSA và bốn thuật toán nền | arithmetic.py, primes.py, keys.py, rsa.py |
| Mã hoá và giải mã khôi phục bản gốc | Menu 1–3, encrypt/decrypt, kiểm thử round-trip |
| Ví dụ học trên lớp | number và test_classroom_exact |
| 3 ca theo yêu cầu: slide, tự làm, lỗi + đối chiếu chuẩn | tests/test_rsa.py; reference_checks.py đối chiếu pow và math.gcd |
| In kết quả đối chiếu | main.py test, phần ĐỐI CHIẾU THƯ VIỆN CHUẨN |
| Chia module và tách giao diện | rsa_core/cli.py riêng, main.py chỉ gọi entry point |
| Dữ liệu thật | examples/message_vi.txt và demo-file |
| Hướng dẫn chạy | README.md, .vscode/launch.json |
| Giao diện, thời gian, tấn công (khuyến khích) | Menu, benchmark, attack |
| Lịch sử đóng góp nhóm (khuyến khích) | Nhóm cần tự thực hiện commit thật trên GitHub |

## 8. Nguồn tham khảo

Tài liệu lớp đính kèm: phần RSA, trang 41–44 và lý thuyết số. RFC 8017 mục 5.1: https://www.rfc-editor.org/rfc/rfc8017.html#section-5.1 . Các chi tiết đóng gói file, giao diện và ca kiểm thử do dự án thiết kế, không phải trích từ RFC.
