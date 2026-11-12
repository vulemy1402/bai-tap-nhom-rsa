# Chạy giao diện web RSA

1. Mở đúng thư mục `rsa_project` trong VS Code (có `main.py` và `rsa_core`).
2. Mở **Terminal → New Terminal**, chạy:

   ```bash
   python web_app.py
   ```

   Nếu Windows không nhận `python`, thử `py -3 web_app.py`. Cần Python 3.10 trở lên, không cần cài thêm thư viện.
3. Trình duyệt sẽ mở trang http://127.0.0.1:8000/. Nếu không tự mở, sao chép địa chỉ này vào trình duyệt. Giữ Terminal mở khi dùng. Nhấn Ctrl+C trong Terminal để dừng.
4. Ví dụ slide: ở tab **Số nguyên**, dùng sẵn p=17, q=11, e=7, M=88 và nhấn **Mã hoá & giải mã**. Mở **Xem các bước trung gian** nếu cần.
5. Văn bản: chọn **Khoá văn bản**, mở tab **Văn bản**, nhập nội dung, nhấn **Mã hoá văn bản** rồi **Giải mã bản mã**.
6. Tệp: chọn **Khoá văn bản** hoặc **Tự sinh khoá 512 bit**; chọn tệp gốc tối đa 1 MB, nhấn **Mã hoá & tải xuống**. Để giải mã, chọn tệp `.rsa` đã tải xuống và giữ nguyên p,q,e, rồi nhấn **Giải mã & tải xuống**. Lưu p,q,e khi cần giải mã về sau.
7. Tab **Kiểm thử** chạy 3 ca chính và phần đối chiếu chuẩn. Thời gian được hiện sau từng thao tác.

Nếu báo cổng đang được sử dụng, chạy `python web_app.py --port 8001` và mở http://127.0.0.1:8001/.

Web chạy cục bộ trên máy, dùng lại `rsa_core` của dự án, không tự cập nhật GitHub và không đưa lên Internet. Đây là RSA textbook cho bài tập, chưa có OAEP và xác thực; không dùng với dữ liệu nhạy cảm.

## Giao diện v2

Bản mới dùng thanh chức năng bên trái, các ô kết quả lớn và ô thời gian riêng cho từng công đoạn. Khi đổi khoá hoặc bản rõ số nguyên, kết quả cũ được ẩn để tránh nhầm. Ở mục Văn bản/Tệp có nút Áp dụng để chọn nhanh bộ khoá phù hợp.

Nếu đã cài phần web trước đó, ba file giao diện cần cập nhật là `web/index.html`, `web/style.css`, `web/app.js`. Sau khi thay file, tải lại trình duyệt bằng **Ctrl+F5**. Không tự đưa code lên GitHub; bước này cần đăng nhập tài khoản có quyền ghi.

## Nếu đang dùng repository nhóm

Bản `RSA_Web_BoSung.zip` chỉ chứa `web_app.py`, thư mục `web/` và hướng dẫn. Mở repository mới nhất của nhóm, chép 3 mục này vào thư mục `rsa_project`, nằm cùng cấp với `main.py` và `rsa_core`. Các file web dùng API của bản dự án đã cung cấp; nếu nhóm đã đổi `rsa_core` thì cần kiểm tra tương thích. Không ghi đè những thay đổi của thành viên khác. Chạy và kiểm tra trước khi commit/push.
