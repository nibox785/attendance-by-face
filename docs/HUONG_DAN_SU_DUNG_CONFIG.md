# HƯỚNG DẪN SỬ DỤNG CENTRALIZED CONFIG

## 📋 Tổng Quan

Từ nay, **TẤT CẢ** cấu hình quan trọng được quản lý tập trung tại:
```
main/config.py
```

## ✅ Các Vấn Đề Đã Được Khắc Phục

### 1. **Thống nhất đường dẫn ảnh**
- ✅ Đã sửa `train_face_model.py` đọc từ `main/Dataset/FaceData/processed/`
- ✅ Loại bỏ dấu `./` không nhất quán
- ✅ Tất cả module đều dùng chung config

### 2. **Loại bỏ flow điểm danh cũ**
- ✅ Đã comment out các function deprecated trong `lecturer_views.py`:
  - `lecturer_mark_attendance(classroom_id)` 
  - `lecturer_mark_attendance_by_face(classroom_id)`
  - `live_video_feed2(classroom_id)`
- ✅ Đã comment out URL routes cũ
- ✅ Chỉ giữ lại **session-based flow** (khuyến nghị)

### 3. **Centralized configuration**
- ✅ Tạo `main/config.py` với tất cả constants
- ✅ Cập nhật các file import từ config:
  - `train_face_model.py`
  - `main/view/admin_views.py`
  - `main/view/reg.py`

## 📁 Cấu Trúc Config Mới

```python
# main/config.py

# Paths
FACE_DATA_DIR = 'main/Dataset/FaceData/processed'
FACENET_MODEL_PATH = 'main/Models/20180402-114759.pb'
CLASSIFIER_MODEL_PATH = 'main/Models/facemodel.pkl'

# Training config
INPUT_IMAGE_SIZE = 160
MIN_IMAGES_PER_STUDENT = 20
BATCH_SIZE = 90
CONFIDENCE_THRESHOLD = 0.80

# Attendance config
LATE_THRESHOLD_MINUTES = 15
MAX_ABSENCE_RATIO = 0.20

# ... và nhiều config khác
```

## 🔧 Cách Sử Dụng

### Trong Python code:

```python
# ✅ ĐÚNG - Import từ config
from main.config import (
    FACE_DATA_DIR,
    CLASSIFIER_MODEL_PATH,
    INPUT_IMAGE_SIZE,
)

# ❌ SAI - Hardcode
FACE_DATA_DIR = 'main/Dataset/FaceData/processed'
```

### Trong Django views:

```python
from main.config import (
    FACE_DATA_DIR_RELATIVE,
    LATE_THRESHOLD_MINUTES,
)

# Sử dụng trong logic
if time_diff > LATE_THRESHOLD_MINUTES * 60:
    status = "Muộn"
```

## 🛠️ Helper Functions Có Sẵn

### 1. Kiểm tra tính nhất quán hệ thống

```python
from main.config import validate_system_consistency

result = validate_system_consistency()

if not result['is_consistent']:
    print("⚠️ WARNINGS:")
    for warning in result['warnings']:
        print(f"  - {warning}")
    
    print("\n💡 RECOMMENDATIONS:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
```

**Output mẫu:**
```
⚠️ WARNINGS:
  - Mismatch: DB có 5 sinh viên, model có 3 sinh viên
  - 2 sinh viên chưa có ảnh: 1111111111, 1949982760

💡 RECOMMENDATIONS:
  - Train lại model để đồng bộ
  - Capture ảnh cho các sinh viên này
```

### 2. Lấy thông tin hệ thống

```python
from main.config import get_system_info

info = get_system_info()
print(f"Sinh viên trong DB: {info['students_in_db']}")
print(f"Sinh viên trong Model: {info['students_in_model']}")
print(f"Sinh viên có ảnh: {info['students_with_images']}")
```

### 3. Lấy đường dẫn ảnh sinh viên

```python
from main.config import get_student_face_dir

student_dir = get_student_face_dir('2011003929')
# Output: '/path/to/main/Dataset/FaceData/processed/2011003929'
```

## 📊 Kiểm Tra Trước Khi Chạy

```bash
python manage.py shell
```

```python
from main.config import check_paths_exist, validate_system_consistency

# Kiểm tra paths
status = check_paths_exist()
if not status['status']:
    print("Missing:", status['missing'])
    print("Errors:", status['errors'])

# Kiểm tra consistency
result = validate_system_consistency()
print("Consistent:", result['is_consistent'])
```

## 🔄 Training Với Config Mới

### Trước đây (Sai):
```bash
python train_face_model.py
# ❌ Đọc từ main/Dataset/FaceData (thiếu /processed)
```

### Bây giờ (Đúng):
```bash
python train_face_model.py
# ✅ Tự động đọc từ config: main/Dataset/FaceData/processed
# ✅ Hiển thị: "✓ Loaded config from main.config"
```

## 🎯 Flow Điểm Danh Mới (Session-Based)

### ✅ ĐÚNG - Sử dụng session:

```python
# 1. Bắt đầu buổi học
lecturer_start_session(classroom_id)
  → Tạo ClassSession
  → Khởi tạo Attendance cho TẤT CẢ sinh viên (status = Vắng)

# 2. Điểm danh
lecturer_mark_attendance_session(session_id)  # Manual
lecturer_mark_attendance_by_face_session(session_id)  # Face

# 3. Đóng buổi
lecturer_close_session(session_id)
```

### ❌ SAI - Flow cũ (deprecated):

```python
# ĐÃ BỊ COMMENT OUT - KHÔNG DÙNG NỮA
# lecturer_mark_attendance(classroom_id)
# lecturer_mark_attendance_by_face(classroom_id)
```

## 📝 Chỉnh Sửa Config

### Nếu muốn thay đổi ngưỡng muộn:

```python
# main/config.py
LATE_THRESHOLD_MINUTES = 10  # Từ 15 phút → 10 phút
```

**Lưu ý:** Chỉ sửa ở `main/config.py`, KHÔNG sửa ở file khác!

### Nếu muốn thay đổi số ảnh capture:

```python
# main/config.py
RECOMMENDED_IMAGES_PER_STUDENT = 200  # Từ 300 → 200
```

## 🐛 Troubleshooting

### Lỗi: ImportError: cannot import name 'FACE_DATA_DIR'

**Nguyên nhân:** File `main/config.py` chưa được tạo

**Giải pháp:**
```bash
# Kiểm tra file tồn tại
ls main/config.py

# Nếu không có, pull lại từ repo hoặc tạo lại
```

### Lỗi: Model không tìm thấy

**Kiểm tra:**
```python
from main.config import check_paths_exist
status = check_paths_exist()
print(status)
```

### Lỗi: DB và Model không khớp

**Kiểm tra:**
```python
from main.config import validate_system_consistency
result = validate_system_consistency()
print(result)
```

**Sửa:**
```bash
# Train lại model
python train_face_model.py
```

## ✨ Lợi Ích

1. ✅ **Dễ bảo trì**: Sửa 1 chỗ, áp dụng toàn hệ thống
2. ✅ **Tránh lỗi**: Không còn mismatch giữa các module
3. ✅ **Dễ debug**: Helper functions kiểm tra consistency
4. ✅ **Rõ ràng**: Tất cả config ở 1 nơi
5. ✅ **An toàn**: Type hints và validation

## 📚 Tham Khảo

- File config: `main/config.py`
- Phân tích chi tiết: `docs/PHAN_TICH_BAT_NHAT_QUAN_HE_THONG.md`
- Hướng dẫn training: `docs/HUONG_DAN_TRAINING_FACE.md`

---

**Cập nhật:** 12/12/2025  
**Version:** 2.0 (Centralized Config)
