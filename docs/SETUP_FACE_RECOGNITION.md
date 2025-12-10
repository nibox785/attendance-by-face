# 🚀 HƯỚNG DẪN SETUP NHẬN DIỆN KHUÔN MẶT

## 📋 TỔNG QUAN

Hệ thống đã phát hiện **5 sinh viên** trong database nhưng **chưa có ảnh**:

1. 2011003929 - Nguyễn Văn Anh
2. 2011010091 - Trần Thị Bảo  
3. 2011010708 - Lê Minh Chiến
4. 2011020456 - Phạm Thị Diệu
5. 2011030789 - Huỳnh Văn Em

## 📸 BƯỚC 1: CHUẨN BỊ ẢNH

### Cách 1: Tạo folder thủ công

```bash
# Tạo folder cho mỗi sinh viên (tên folder = MSSV)
mkdir "main\Dataset\FaceData\2011003929"
mkdir "main\Dataset\FaceData\2011010091"
mkdir "main\Dataset\FaceData\2011010708"
mkdir "main\Dataset\FaceData\2011020456"
mkdir "main\Dataset\FaceData\2011030789"
```

### Cách 2: Chạy script tự động tạo folder

```bash
python create_student_folders.py
```

### Yêu cầu về ảnh:

- **Số lượng**: 20-30 ảnh/người
- **Chất lượng**: Rõ nét, khuôn mặt chiếm 60-70% khung hình
- **Góc độ**: Thẳng, nghiêng trái/phải 15-30°
- **Ánh sáng**: Đủ sáng, không quá tối hoặc quá chói
- **Định dạng**: JPG, JPEG, PNG
- **Nên có**: 
  - Đeo kính / Không đeo kính
  - Nhiều biểu cảm khác nhau
  - Môi trường khác nhau (trong nhà, ngoài trời)

**❌ TRÁNH:**
- Ảnh mờ, nhòe
- Khuôn mặt quá nhỏ
- Che khuất nhiều (khẩu trang, mũ)
- Ánh sáng từ phía sau (backlight)

## 🎯 BƯỚC 2: THÊM ẢNH VÀO FOLDER

### Ví dụ cấu trúc:

```
main/Dataset/FaceData/
├── 2011003929/
│   ├── img_001.jpg
│   ├── img_002.jpg
│   ├── img_003.jpg
│   └── ... (20-30 ảnh)
├── 2011010091/
│   ├── img_001.jpg
│   └── ...
└── ...
```

### Quy tắc đặt tên:

- ✅ Tên folder: **PHẢI** giống chính xác MSSV (VD: `2011003929`)
- ✅ Tên file ảnh: Tùy ý (VD: `anh1.jpg`, `photo_001.png`)
- ❌ **KHÔNG** có khoảng trắng trong tên folder
- ❌ **KHÔNG** có ký tự đặc biệt trong tên folder

## 🔍 BƯỚC 3: KIỂM TRA FOLDER

Chạy script kiểm tra xem đã đúng chưa:

```bash
python check_face_folders.py
```

Script sẽ báo cáo:
- ✅ Folder nào hợp lệ
- ⚠️ Folder nào cần sửa
- 📭 Folder nào rỗng (cần thêm ảnh)
- 📸 Sinh viên nào chưa có ảnh

**Ví dụ output:**

```
======================================================================
✅ FOLDER HỢP LỆ (5)
======================================================================
   ✓ 2011003929          → 2011003929     ( 25 ảnh)
   ✓ 2011010091          → 2011010091     ( 30 ảnh)
   ✓ 2011010708          → 2011010708     ( 22 ảnh)
   ✓ 2011020456          → 2011020456     ( 28 ảnh)
   ✓ 2011030789          → 2011030789     ( 27 ảnh)
```

## 🤖 BƯỚC 4: TRAIN MODEL

Khi đã có đủ ảnh, train model:

```bash
python train_face_model.py
```

**Output mong đợi:**

```
========================================
🎓 TRAINING FACE RECOGNITION MODEL
========================================

📂 Scanning dataset...
   Found 5 students

👤 Processing student: 2011003929
   ✓ Detected 25 faces
   ✓ Extracted 25 embeddings

👤 Processing student: 2011010091
   ✓ Detected 30 faces
   ✓ Extracted 30 embeddings

...

✅ Training completed!
   Total students: 5
   Total embeddings: 132
   Model saved: main/Models/facemodel.pkl
```

## ✅ BƯỚC 5: KIỂM TRA NHẬN DIỆN

### 5.1. Chạy server:

```bash
python manage.py runserver
```

### 5.2. Đăng nhập giảng viên:

- Truy cập: http://127.0.0.1:8000/
- Chọn "Giảng viên"
- Đăng nhập

### 5.3. Tạo buổi điểm danh:

1. Vào "Quản lý lớp học"
2. Chọn lớp
3. Click "Bắt đầu buổi điểm danh"
4. Chọn "Điểm danh bằng khuôn mặt"

### 5.4. Test nhận diện:

- Cho từng sinh viên ngồi trước webcam
- Hệ thống sẽ hiển thị:
  ```
  Đang nhận diện...
  Độ tin cậy: 0.85
  
  2011003929 - Nguyễn Văn Anh
  ✓ Điểm danh thành công
  ```

### 5.5. Kiểm tra log trong terminal:

Terminal sẽ hiện log chi tiết:

```
➡️ insert_attendance called: session_id=1, student_id='2011003929'
🔍 Normalized: '2011003929' → '2011003929'
✅ Exact match: 2011003929 - Nguyễn Văn Anh
✓ Attendance marked: 2011003929 - Nguyễn Văn Anh - Present
```

## 🔧 TROUBLESHOOTING

### Vấn đề 1: Không nhận diện được

**Triệu chứng:**
- Màn hình hiện "UNKNOWN"
- Confidence < 0.50

**Giải pháp:**

1. **Kiểm tra ảnh training:**
   ```bash
   python check_face_folders.py
   ```
   - Đảm bảo mỗi người có 20-30 ảnh
   - Ảnh rõ nét, đủ sáng

2. **Train lại model:**
   ```bash
   del main\Models\facemodel.pkl
   python train_face_model.py
   ```

3. **Cải thiện điều kiện nhận diện:**
   - Tăng ánh sáng
   - Ngồi thẳng, nhìn thẳng camera
   - Khoảng cách 50-100cm từ camera
   - Khuôn mặt chiếm 60-70% màn hình

### Vấn đề 2: Nhận diện sai người

**Triệu chứng:**
- Log hiển thị: `⚠️ Fuzzy match: '2011003929' → 2011010091 (Trần Thị Bảo)`
- Nhận A thành B

**Giải pháp:**

1. **Kiểm tra tên folder:**
   ```bash
   python check_face_folders.py
   ```
   - Tên folder PHẢI giống chính xác MSSV
   - Không có khoảng trắng, ký tự đặc biệt

2. **Đổi tên folder sai:**
   ```bash
   # Ví dụ: Đổi " 2011003929" thành "2011003929"
   ren "main\Dataset\FaceData\ 2011003929" "2011003929"
   ```

3. **Train lại:**
   ```bash
   python train_face_model.py
   ```

### Vấn đề 3: Nhận diện quá lâu (>3s)

**Triệu chứng:**
- Mỗi lần nhận diện mất 3-5 giây

**Giải pháp:**

1. **Kiểm tra CPU/GPU:**
   - Hệ thống v2.0 đã tối ưu: 3s → 1s
   - Nếu vẫn chậm, có thể do máy yếu

2. **Giảm số frame:**
   - Mở `main/view/reg.py`
   - Tìm dòng: `REQUIRED_FRAMES = 10`
   - Đổi thành: `REQUIRED_FRAMES = 5`

3. **Tắt anti-spoofing:**
   - Trong `main/view/reg.py`
   - Tìm: `if prediction == 1:  # Real face`
   - Comment lại hoặc set thành `if True:`

### Vấn đề 4: Folder "processed" bị lỗi

**Triệu chứng:**
- Script báo: `📂 processed` (folder rỗng)
- PathImageFolder trong DB chứa "/processed/"

**Giải pháp:**

1. **Xóa folder processed:**
   ```bash
   rd /s /q "main\Dataset\FaceData\processed"
   ```

2. **Cập nhật DB (tùy chọn):**
   - Trong DB, PathImageFolder nên trỏ trực tiếp:
   - `./main/Dataset/FaceData/2011003929` (không có /processed/)

## 📊 KIỂM TRA HIỆU SUẤT

### Benchmark mong đợi (v2.0):

| Chỉ số | v1.0 | v2.0 |
|--------|------|------|
| Tỷ lệ nhận diện | ~10% | ~70% |
| Thời gian nhận diện | 3-5s | 1-2s |
| Confidence threshold | 0.90 | 0.50 |
| Số frame cần | 30 | 10 |

### Test accuracy:

```bash
# Test với 5 sinh viên
# Mỗi người test 10 lần
# Kỳ vọng: 7-8/10 lần nhận đúng
```

## 📚 TÀI LIỆU THAM KHẢO

- **HUONG_DAN_TRAINING_FACE.md**: Chi tiết về training
- **CAI_TIEN_NHAN_DIEN_V2.md**: So sánh v1.0 vs v2.0
- **HUONG_DAN_SU_DUNG.md**: Hướng dẫn sử dụng toàn bộ hệ thống

## 🆘 HỖ TRỢ

Nếu vẫn gặp vấn đề:

1. Kiểm tra log trong terminal
2. Chạy `python check_face_folders.py` để kiểm tra
3. Đảm bảo đã train lại model sau mỗi thay đổi
4. Gửi log chi tiết để được hỗ trợ

---

**Chúc bạn setup thành công! 🎉**
