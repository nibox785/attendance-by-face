# ⚠️ LƯU Ý QUAN TRỌNG - ĐỌC TRƯỚC KHI SỬ DỤNG

## 🚨 VẤN ĐỀ VỪA PHÁT HIỆN

Hệ thống đã nhận diện ra MSSV `2011060842` nhưng **MSSV này KHÔNG TỒN TẠI trong database**!

### Nguyên nhân:

Model cũ đã được train với folder chứa ảnh của người không phải sinh viên trong hệ thống:
- Folder `2011060842` (hoặc `1949982759`) tồn tại trong FaceData
- Nhưng MSSV này không có trong database StudentInfo
- Khi nhận diện được → hệ thống không tìm thấy sinh viên → LỖI

### Database hiện tại chỉ có 5 sinh viên:

1. `2011003929` - Nguyễn Văn Anh
2. `2011010091` - Trần Thị Bảo
3. `2011010708` - Lê Minh Chiến
4. `2011020456` - Phạm Thị Diệu
5. `2011030789` - Huỳnh Văn Em

## ✅ ĐÃ SỬA

- ✅ Xóa folder `1949982759` (không hợp lệ)
- ✅ Xóa folder `processed` (rác)
- ✅ Xóa model cũ `facemodel.pkl` (chứa data không hợp lệ)

## 🔄 CẦN LÀM TIẾP

### Bước 1: Thêm ảnh cho 5 sinh viên

Mỗi sinh viên cần **20-30 ảnh** trong folder của họ:

```
main/Dataset/FaceData/
├── 2011003929/  ← Thêm 20-30 ảnh vào đây
├── 2011010091/  ← Thêm 20-30 ảnh vào đây
├── 2011010708/  ← Thêm 20-30 ảnh vào đây
├── 2011020456/  ← Thêm 20-30 ảnh vào đây
└── 2011030789/  ← Thêm 20-30 ảnh vào đây
```

**Yêu cầu ảnh:**
- Rõ nét, khuôn mặt chiếm 60-70% khung hình
- Nhiều góc độ: thẳng, nghiêng trái/phải 15-30°
- Nhiều biểu cảm khác nhau
- Đủ ánh sáng
- Format: JPG, JPEG, PNG

### Bước 2: Kiểm tra folder

```bash
python check_face_folders.py
```

Đảm bảo output hiển thị:
```
✅ FOLDER HỢP LỆ (5)
   ✓ 2011003929 → 2011003929 (25 ảnh)
   ✓ 2011010091 → 2011010091 (30 ảnh)
   ...
```

### Bước 3: Train model mới

```bash
python train_face_model.py
```

**Lưu ý:** Model sẽ CHÍNH XÁC hơn nếu:
- Mỗi sinh viên có đủ 20-30 ảnh
- Ảnh chất lượng cao
- KHÔNG có folder của người ngoài

### Bước 4: Test lại

1. Chạy server:
   ```bash
   python manage.py runserver
   ```

2. Đăng nhập giảng viên

3. Tạo buổi điểm danh mới

4. Test với **5 sinh viên thật** trong database

5. Kiểm tra log trong terminal:
   ```
   ➡️ insert_attendance called: session_id=X, student_id='2011003929'
   🔍 Normalized: '2011003929' → '2011003929'
   ✅ Exact match: 2011003929 - Nguyễn Văn Anh
   ✓ Attendance marked: Present
   ```

## 🚫 TUYỆT ĐỐI TRÁNH

### ❌ KHÔNG được:

1. **Train với ảnh của người không có trong database**
   - Chỉ train với 5 MSSV trong danh sách trên
   - Nếu muốn thêm sinh viên mới → thêm vào DB trước

2. **Đặt tên folder sai**
   - Tên folder PHẢI giống CHÍNH XÁC với MSSV
   - VD: `2011003929` ✅
   - VD: `2011003929 ` ❌ (có khoảng trắng)
   - VD: `Nguyen Van Anh` ❌ (dùng tên thay vì MSSV)

3. **Folder rỗng hoặc ít ảnh**
   - Tối thiểu 10 ảnh/người (khuyến nghị 20-30)
   - Nếu ít hơn → nhận diện kém

4. **Ảnh chất lượng thấp**
   - Ảnh mờ, tối, bị che khuôn mặt
   - Khuôn mặt quá nhỏ trong khung hình

## 📊 QUY TRÌNH ĐÚNG KHI THÊM SINH VIÊN MỚI

Nếu muốn thêm sinh viên `2011060842` vào hệ thống:

### 1. Thêm vào Database trước:

Chỉnh sửa `Database/StudentInfo.json`:

```json
{
  "id_student": "2011060842",
  "student_name": "Tên Sinh Viên",
  "email": "email@student.uth.edu.vn",
  "phone": "0901234567",
  "address": "Địa chỉ",
  "birthday": "2003-01-01",
  "PathImageFolder": "./main/Dataset/FaceData/2011060842",
  "password": "pbkdf2_sha256$600000$Nta2N5O5ePVWG2UByOAB0m$Dkfmk1IzFFcAl3FxVY1wON6zM/52xMk/VMocovIZmkQ="
}
```

### 2. Load vào database:

```bash
python manage.py loaddata Database/StudentInfo.json
```

### 3. Tạo folder ảnh:

```bash
mkdir "main\Dataset\FaceData\2011060842"
```

### 4. Thêm 20-30 ảnh vào folder

### 5. Train lại model:

```bash
python train_face_model.py
```

### 6. Test nhận diện

## 🔍 KIỂM TRA NHANH

**Trước khi train:**

```bash
# Kiểm tra folder
python check_face_folders.py

# Kết quả mong đợi:
✅ Folder khớp với DB: 5
❌ Folder KHÔNG có trong DB: 0
📸 Sinh viên chưa có ảnh: 0
```

**Sau khi train:**

```bash
# Chạy server
python manage.py runserver

# Test với 5 sinh viên
# Tất cả phải nhận diện ĐÚNG tên và MSSV
```

## 📞 KHI GẶP LỖI

### Lỗi: "Không tìm thấy sinh viên 'XXXXXX'"

**Nguyên nhân:**
- Model nhận diện ra MSSV không có trong DB

**Giải pháp:**
1. Kiểm tra folder: `python check_face_folders.py`
2. Xóa folder không hợp lệ
3. Xóa model cũ: `del main\Models\facemodel.pkl`
4. Train lại: `python train_face_model.py`

### Lỗi: "Fuzzy match: X → Y"

**Nguyên nhân:**
- Tên folder không khớp chính xác với MSSV

**Giải pháp:**
1. Đổi tên folder cho đúng
2. Train lại model

### Lỗi: "UNKNOWN"

**Nguyên nhân:**
- Chưa train model
- Ảnh training kém chất lượng
- Điều kiện nhận diện không tốt

**Giải pháp:**
1. Train model: `python train_face_model.py`
2. Thêm ảnh chất lượng cao
3. Cải thiện ánh sáng, khoảng cách

## 📚 TÀI LIỆU THAM KHẢO

- **`SETUP_FACE_RECOGNITION.md`** - Hướng dẫn setup đầy đủ
- **`HUONG_DAN_TRAINING_FACE.md`** - Chi tiết về training
- **`CAI_TIEN_NHAN_DIEN_V2.md`** - Tính năng v2.0

---

**📌 NHẮC LẠI:**
1. Chỉ train với sinh viên CÓ TRONG DATABASE
2. Tên folder = MSSV chính xác
3. 20-30 ảnh/người
4. Xóa model cũ trước khi train lại
5. Kiểm tra log khi gặp lỗi

**Chúc bạn setup thành công! 🎉**
