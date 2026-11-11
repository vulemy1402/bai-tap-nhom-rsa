# Bộ kiểm thử chính: 3 ca

Chạy `python main.py test` hoặc F5 cấu hình kiểm thử trong VS Code. Cả ba đều phải PASS. Sau đó chương trình mới chạy phần đối chiếu Python chuẩn riêng.

## TC01 – Ví dụ trong slides thầy

- Nguồn: tài liệu lớp đính kèm, trang 43–44.
- Đầu vào: p=17, q=11, e=7, M=88.
- Tính khoá: n=187; phi(n)=160; d=23 vì 7*23=161=1 mod 160.
- Mã hoá: C=88^7 mod 187=11.
- Giải mã: M'=11^23 mod 187=88.
- Mong đợi: đúng n,d,C,M'; giải mã trực tiếp và CRT đều ra 88.
- Đạt khi tất cả giá trị thực tế bằng giá trị đã biết từ slide.

## TC02 – Ca tự làm, ngoài ví dụ slide

- Đầu vào tự chọn cho bài: p=61, q=53, e=17, M=65.
- Tính khoá: n=3233; phi(n)=60*52=3120; gcd(17,3120)=1.
- Tính d=2753 vì 17*2753=46801=15*3120+1.
- Mã hoá: C=65^17 mod 3233=2790.
- Giải mã: M'=2790^2753 mod 3233=65.
- Mong đợi: n=3233,d=2753,C=2790,M'=65; kết quả CRT cũng bằng 65.
- Đạt khi chương trình khớp các giá trị đã tính trên, không chỉ kiểm tra round-trip.

Ca này do dự án viết riêng ngoài ví dụ slide; bộ số 61,53 thường được dùng để minh hoạ RSA, không tuyên bố là một test vector mới hoặc chuẩn NIST.

## TC03 – Ca lỗi

- Đầu vào: p=17, q=11, e=2.
- phi(n)=160; gcd(2,160)=2 khác 1.
- Không có số nguyên d thoả 2*d=1 mod 160 vì vế trái chẵn, không thể đồng dư số lẻ theo modulo chẵn.
- Mong đợi: từ chối tạo khoá, ném `ValueError` với thông báo `Không tồn tại nghịch đảo: gcd(a, modulo) != 1.`
- Đạt khi kiểm thử bắt đúng loại lỗi và thông báo. Nếu chương trình vẫn tạo khoá hoặc báo một lỗi khác, ca này thất bại.

Có thể demo lỗi trực tiếp:

```bash
python main.py number --p 17 --q 11 --e 2 --message 88
```

Lệnh báo lỗi và trả mã thoát 1. Ngược lại, bộ kiểm thử trả mã thoát 0 khi đã bắt đúng lỗi dự kiến.

## Phần đối chiếu chuẩn riêng

Đề bài còn yêu cầu đối chiếu test vector chuẩn **hoặc thư viện chuẩn**. Dự án chọn thư viện chuẩn Python: `pow(a,e,n)`, `pow(a,-1,n)` và `math.gcd`, đặt trong `reference_checks.py`, tách khỏi ba ca trên. Mã RSA và thuật toán nền trong `rsa_core/` không gọi các oracle này.

Kết quả mã hoá của cả TC01 và TC02 được in cạnh kết quả `pow` để dễ trình bày. Ngoài ra đối chiếu toàn bộ 187 đại diện của modulo lớp, một khoá sinh 512 bit, nhiều bộ số phép toán và kiểm tra Miller–Rabin bằng chia thử độc lập. Các kiểm tra byte/tệp bổ sung chứng minh khả năng khôi phục UTF-8 và byte 0; chúng không thay đổi số lượng **ba ca chính** trong unittest.

Log chạy thực tế được lưu ở `evidence/tests.txt`.
