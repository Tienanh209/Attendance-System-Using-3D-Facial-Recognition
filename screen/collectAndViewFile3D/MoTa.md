# Mô tả

1.  **`collectData3d` (Thu thập dữ liệu khuôn mặt 3D):**
    * Sử dụng camera Intel RealSense để thu thập hình ảnh màu và độ sâu.
    * Dùng thư viện Dlib để phát hiện khuôn mặt và xác định các điểm đặc trưng (landmark) trên khuôn mặt.
    * Tính toán tọa độ 3D của các điểm đặc trưng.
    * Lưu trữ dữ liệu 3D và thông tin liên quan vào các tệp `.obj` và `.json`.
    * Cung cấp giao diện người dùng để điều khiển quá trình thu thập (nhập ID người, chọn chế độ chụp đơn/liên tục, hiển thị video và trạng thái).
    * Tùy chọn sử dụng InsightFace để trích xuất đặc trưng khuôn mặt (nếu thư viện này được cài đặt).

2.  **`viewFile3d` (Xem dữ liệu khuôn mặt 3D):**
    * Đọc dữ liệu tọa độ 3D từ các tệp `.obj`.
    * Hiển thị các điểm đặc trưng 3D trên biểu đồ.
    * Cho phép người dùng tải và so sánh dữ liệu từ nhiều tệp.
    * Cung cấp các tùy chọn hiển thị (ẩn/hiện các nhóm điểm đặc trưng).
    * Tính toán và hiển thị các thống kê so sánh (ví dụ: độ khác biệt trung bình giữa hai bộ dữ liệu).
    * Cho phép tương tác với biểu đồ 3D (xoay, thu phóng) và lưu biểu đồ thành hình ảnh.

**Tóm lại:** Ứng dụng đầu tiên dùng để thu thập dữ liệu khuôn mặt 3D từ camera RealSense, còn ứng dụng thứ hai dùng để xem và phân tích dữ liệu 3D đã thu thập.
**Lưu ý**: Cần thu thập nhiều dữ liệu ở collect chọn lọc ra file đủ dữ liệu 3d để sử dụng bên viewFile3d 