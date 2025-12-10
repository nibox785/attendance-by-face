# HƯỚNG DẪN SỬ DỤNG HỆ THỐNG ĐIỂM DANH

## 📚 Tổng quan

Hệ thống sử dụng **phương pháp điểm danh theo buổi học (Session-Based Attendance)** để đảm bảo:
- ✅ Không tạo bản ghi trùng lặp
- ✅ Dễ dàng chỉnh sửa và quản lý
- ✅ Có lịch sử thay đổi chi tiết
- ✅ Tính điểm tự động và chính xác

---

## 👨‍🏫 HƯỚNG DẪN CHO GIẢNG VIÊN

### Bước 1️⃣: Bắt đầu điểm danh

1. **Đăng nhập** với tài khoản giảng viên
2. Vào menu **"Quản lý điểm danh"**
3. Tìm lớp học hôm nay (chỉ hiện nút cho đúng thứ học)
4. Click nút xanh lá **"Bắt đầu điểm danh"**

**Hệ thống tự động:**
- ✓ Tạo buổi học mới (ClassSession)
- ✓ Gán tất cả sinh viên là "Vắng"
- ✓ Mở trang điểm danh chi tiết

---

### Bước 2️⃣: Chọn phương thức điểm danh

Bạn có **3 tùy chọn**:

#### 🖊️ **Phương án A: Điểm danh thủ công**

**Khi nào dùng?**
- Sinh viên ít (< 10 người)
- Không có camera
- Muốn kiểm soát chính xác từng người

**Cách thực hiện:**
1. Nhìn vào bảng danh sách sinh viên
2. Ở cột **"Trạng thái"**, mỗi sinh viên có dropdown menu:
   - 🔴 **Vắng** (Absent) - 0 điểm
   - 🟢 **Có mặt** (Present) - 1 điểm  
   - 🟡 **Muộn** (Late) - 0.5 điểm
3. Chọn trạng thái cho từng sinh viên
4. Click nút **"Lưu thay đổi"** ở cuối trang
5. Hệ thống hiển thị thông báo: "✓ Cập nhật X bản ghi điểm danh thành công!"

**Màu sắc bảng:**
- 🔴 Đỏ = Vắng
- 🟢 Xanh lá = Có mặt
- 🟡 Vàng = Muộn

---

#### 📸 **Phương án B: Điểm danh bằng khuôn mặt**

**Khi nào dùng?**
- Sinh viên nhiều (> 10 người)
- Có camera
- Muốn nhanh và chống gian lận

**Cách thực hiện:**
1. Click nút xanh dương **"Điểm danh bằng khuôn mặt"**
2. Cho phép trình duyệt truy cập camera
3. Yêu cầu sinh viên lần lượt đứng trước camera (1 người/lần)
4. Hệ thống tự động:
   - Phát hiện khuôn mặt (khung xanh)
   - Kiểm tra chống giả mạo (anti-spoofing)
   - Nhận diện người (hiển thị tên)
   - Thanh progress bar chạy đến 100%
   - Cập nhật điểm danh tự động
   - Hiển thị "✓ Điểm danh thành công: [Tên sinh viên]"

**Lưu ý:**
- ⚡ Tốc độ: ~1.5 giây/sinh viên (đã tối ưu)
- 🛡️ Chống fake: Không nhận diện ảnh in, video từ màn hình
- 🎯 Độ chính xác: 85%+ (threshold đã giảm để nhanh hơn)
- ⏱️ Tự động tính "Muộn" nếu check-in sau 15 phút
- 🔄 Nếu đã điểm danh rồi, hiển thị khung đỏ: "đã điểm danh"

**Nếu không nhận diện được:**
- Sinh viên đứng gần camera hơn
- Ánh sáng đủ sáng
- Nhìn thẳng vào camera
- Hoặc dùng điểm danh thủ công

---

#### 🔀 **Phương án C: Kết hợp cả 2**

**Quy trình đề xuất:**
1. Dùng **camera** điểm danh hàng loạt trước (90% sinh viên)
2. Quay lại **thủ công** để:
   - Sửa sai sót (nếu có)
   - Điểm danh cho SV không nhận diện được
   - Điểm danh cho SV đến muộn sau khi đóng camera

---

### Bước 3️⃣: Đóng buổi điểm danh

1. Sau khi điểm danh xong, click nút đỏ **"Đóng buổi điểm danh"**
2. Hệ thống hiển thị thống kê:
   ```
   ✓ Đã đóng buổi #3 - Lập trình Python
   Có mặt: 28/30 | Vắng: 2
   ```
3. Trạng thái chuyển từ **OPEN** → **CLOSED**

**Sau khi đóng:**
- ✅ Dữ liệu được lưu an toàn
- ✅ Không thể sửa trực tiếp (phải mở lại)
- ✅ Tính vào điểm chuyên cần

---

### Bước 4️⃣: Xem và sửa lại (nếu cần)

**Xem lịch sử:**
1. Click **"Lịch sử điểm danh"** ở góc phải trang chính
2. Xem tất cả buổi học đã diễn ra (mới nhất ở trên)
3. Mỗi buổi hiển thị:
   - Tên lớp, ngày, buổi số mấy
   - Trạng thái: OPEN (xanh) / CLOSED (xám)
   - Tỷ lệ có mặt (%)
   - Số lượng: Tổng/Có mặt/Vắng

**Mở lại để sửa:**
1. Tìm buổi cần sửa (trạng thái CLOSED)
2. Click nút vàng **"Mở lại để chỉnh sửa"**
3. Xác nhận: "Bạn có chắc muốn mở lại buổi điểm danh để chỉnh sửa?"
4. Buổi học chuyển về OPEN
5. Sửa điểm danh (thủ công hoặc camera)
6. Click **"Lưu thay đổi"**
7. Click **"Đóng buổi điểm danh"** lại

**Lưu ý:**
- 🔐 Chỉ giảng viên dạy lớp đó mới được mở lại
- 📝 Mọi thay đổi đều được ghi log (ai sửa, lúc nào)
- ⚠️ Nên sửa trong ngày để tránh quên

---

## 🎓 HƯỚNG DẪN CHO SINH VIÊN

### Xem điểm chuyên cần

1. **Đăng nhập** với tài khoản sinh viên
2. Vào menu **"Tình điểm chuyên cần"**
3. Chọn lớp học muốn xem
4. Hệ thống hiển thị:
   - Tổng số buổi học
   - Số buổi: Có mặt / Muộn / Vắng
   - Điểm chuyên cần (thang 3 điểm)
   - Cảnh báo nếu vắng quá 20%

### Công thức tính điểm

```
Điểm = ((Có mặt × 1) + (Muộn × 0.5) + (Vắng × 0)) / Tổng buổi × 3
```

**Ví dụ:**
- Tổng buổi: 10
- Có mặt: 7 buổi → 7 điểm
- Muộn: 2 buổi → 1 điểm
- Vắng: 1 buổi → 0 điểm
- **Điểm = (7 + 1 + 0) / 10 × 3 = 2.4/3**

**Quy định:**
- ⚠️ Vắng > 20% tổng buổi → **Cấm thi**
- Ví dụ: 10 buổi → vắng tối đa 2 buổi

---

## ❓ CÂU HỎI THƯỜNG GẶP

### Q1: Tại sao không thấy nút "Bắt đầu điểm danh"?
**A:** Nút chỉ hiện khi:
- ✅ Hôm nay là đúng thứ học của lớp
- ✅ Bạn là giảng viên của lớp đó
- ✅ Lớp đang trong kỳ học

### Q2: Điểm danh xong rồi nhưng muốn sửa?
**A:** Có 2 cách:
1. **Nếu chưa đóng**: Sửa trực tiếp và click "Lưu thay đổi"
2. **Nếu đã đóng**: Vào "Lịch sử điểm danh" → Click "Mở lại" → Sửa → Đóng lại

### Q3: Camera không nhận diện được sinh viên?
**A:** Thử:
- Kiểm tra ánh sáng (cần đủ sáng)
- Sinh viên đứng gần camera hơn
- Nhìn thẳng vào camera
- Nếu vẫn không được → Dùng điểm danh thủ công

### Q4: Sinh viên đã điểm danh nhưng hiện "Vắng"?
**A:** 
- Vào trang điểm danh
- Tìm sinh viên trong bảng
- Sửa từ "Vắng" → "Có mặt"
- Click "Lưu thay đổi"

### Q5: Làm sao biết ai sửa điểm danh?
**A:** Hệ thống tự động lưu:
- `modified_by`: Người sửa cuối
- `modified_at`: Thời gian sửa
- `check_in_method`: MANUAL hay FACE
→ Admin có thể truy vấn database để xem lịch sử

### Q6: Quên không đóng buổi điểm danh?
**A:** Không sao! Buổi học vẫn lưu với trạng thái OPEN. Bạn có thể:
- Vào "Lịch sử điểm danh"
- Tìm buổi đó
- Click "Đóng buổi điểm danh"

### Q7: Muốn xóa một buổi điểm danh?
**A:** Hiện tại chưa có chức năng xóa trực tiếp (để bảo vệ dữ liệu). 
Nếu cần:
- Liên hệ Admin
- Admin có thể xóa qua Django Admin Panel

---

## 🔧 XỬ LÝ SỰ CỐ

### Trường hợp 1: Mất điện giữa buổi điểm danh
- ✅ Dữ liệu đã lưu vẫn giữ nguyên
- ✅ Buổi học vẫn ở trạng thái OPEN
- ✅ Vào lại tiếp tục điểm danh bình thường

### Trường hợp 2: Camera bị lỗi
- ✅ Chuyển sang điểm danh thủ công
- ✅ Có thể kết hợp: Camera trước → Thủ công sau

### Trường hợp 3: Sinh viên khiếu nại điểm sai
- ✅ Giảng viên mở lại buổi đó
- ✅ Kiểm tra và sửa
- ✅ Lưu lại với ghi chú (nếu cần)

---

## 📊 BÁO CÁO VÀ THỐNG KÊ

### Xem điểm của cả lớp
1. Vào **"Tính điểm chuyên cần"**
2. Chọn lớp học
3. Xem bảng điểm tổng hợp:
   - Mã SV, Tên, Email
   - Số buổi: Vắng/Muộn/Có mặt
   - Điểm chuyên cần
   - Cảnh báo vượt giới hạn vắng

### Export dữ liệu (Admin)
- Vào Django Admin Panel
- Chọn bảng Attendance
- Click "Export" → CSV/Excel

---

## 🎯 TIPS & TRICKS

### Cho giảng viên:
1. **Điểm danh đầu giờ**: Mở buổi học ngay khi bắt đầu lớp
2. **Kết hợp phương pháp**: Camera cho số đông → Thủ công cho trường hợp đặc biệt
3. **Đóng buổi cuối giờ**: Đóng ngay khi kết thúc để tránh quên
4. **Kiểm tra định kỳ**: Xem "Lịch sử điểm danh" mỗi tuần để phát hiện sai sót

### Cho sinh viên:
1. **Đến đúng giờ**: Tránh bị tính "Muộn" (mất 0.5 điểm)
2. **Kiểm tra điểm thường xuyên**: Vào xem điểm sau mỗi buổi học
3. **Báo ngay nếu sai**: Giảng viên có thể sửa trong vài ngày
4. **Đăng ký khuôn mặt**: Để nhận diện nhanh và chính xác

---

## 🚀 TỐI ƯU HÓA MỚI NHẤT

### Version hiện tại đã cải thiện:
- ⚡ **Tốc độ nhận diện**: Nhanh gấp 2 lần (30 frames → 15 frames)
- 🎯 **Độ chính xác**: Cân bằng tốc độ/chất lượng (90% → 85%)
- 📹 **Xử lý video**: Tăng FPS, giảm độ trễ
- 🛡️ **Anti-spoofing**: Chỉ dùng 1 model tốt nhất (nhanh 3x)
- 💾 **Lưu dữ liệu**: Không còn tạo bản ghi trùng lặp

### So sánh trước/sau:
| Chỉ số | Trước | Sau | Cải thiện |
|--------|-------|-----|-----------|
| Thời gian nhận diện | 3 giây | 1.5 giây | **50% nhanh hơn** |
| Bản ghi trùng lặp | N×M records | 1 record/SV | **100% giảm** |
| Khả năng sửa | Không | Có (reopen) | **Linh hoạt 100%** |
| Lịch sử thay đổi | Không | Có (audit trail) | **Minh bạch 100%** |

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Đọc lại hướng dẫn này
2. Kiểm tra FAQ ở trên
3. Liên hệ Admin hệ thống
4. Báo lỗi qua GitHub Issues

---

**Cập nhật lần cuối:** 10/12/2025  
**Version:** 2.0 (Session-Based Attendance)
