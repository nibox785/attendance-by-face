# PHÂN TÍCH SỰ BẤT NHẤT QUÁN TRONG HỆ THỐNG ĐIỂM DANH

**Ngày phân tích:** 12/12/2025  
**Người phân tích:** GitHub Copilot  
**Mục đích:** Xác định các vấn đề mơ hồ và không nhất quán giữa Admin và Giảng viên

---

## 🚨 CÁC VẤN ĐỀ NGHIÊM TRỌNG

### 1. ❌ **ĐƯỜNG DẪN ẢNH KHÔNG NHẤT QUÁN**

#### **Vấn đề:**
Hệ thống sử dụng **3 đường dẫn khác nhau** cho cùng 1 mục đích:

| Vị trí | Đường dẫn | Có dấu "./" | Có "processed" |
|--------|-----------|-------------|----------------|
| **Admin - capture ảnh** | `./main/Dataset/FaceData/processed/{id}` | ✅ Có | ✅ Có |
| **Admin - lưu PathImageFolder** | `./main/Dataset/FaceData/processed/{id}` | ✅ Có | ✅ Có |
| **Admin - training** | `main/Dataset/FaceData/processed` | ❌ Không | ✅ Có |
| **train_face_model.py** | `main/Dataset/FaceData` | ❌ Không | ❌ KHÔNG |
| **Lecturer - recognition (reg.py)** | Đọc từ model (không rõ path) | - | - |

#### **Hậu quả:**
- ✗ Admin train được nhưng Lecturer không nhận diện được
- ✗ Ảnh được lưu vào `processed/` nhưng script `train_face_model.py` đọc từ `FaceData/` (thiếu `/processed`)
- ✗ Path có dấu "./" đầu không tương thích giữa các module

#### **Ví dụ cụ thể:**
```python
# Admin views (admin_views.py line 691)
output_dir = f"./main/Dataset/FaceData/processed/{id}"  # ✓ Đúng

# train_face_model.py (line 23)
FACE_DATA_DIR = 'main/Dataset/FaceData'  # ✗ SAI - thiếu /processed

# Admin training (admin_views.py line 44)
data_dir = 'main/Dataset/FaceData/processed'  # ✓ Đúng nhưng thiếu "./"
```

---

### 2. ❌ **LOGIC CAPTURE ẢNH KHÁC NHAU**

#### **Admin Capture Logic:**
```python
# admin_views.py - capture()
while image_count < 300:  # Chụp 300 ảnh
    cropped_face = cv2.resize(cropped_face, (160, 160))
    image_filename = os.path.join(output_dir, f"{id}_{image_count}.jpg")
    cv2.imwrite(image_filename, cropped_face)
```

**Đặc điểm:**
- ✅ Chụp 300 ảnh cho 1 sinh viên
- ✅ Resize về 160x160
- ✅ Lưu vào `processed/MSSV/MSSV_0.jpg, MSSV_1.jpg, ...`
- ❌ **KHÔNG** có anti-spoof check
- ❌ **KHÔNG** có face alignment (MTCNN)

#### **Lecturer Recognition (reg.py):**
```python
# reg.py - main()
# Chỉ nhận diện, KHÔNG chụp ảnh
# Đọc model đã train sẵn từ 'main/Models/facemodel.pkl'
```

**Vấn đề:** 
- ✗ **Giảng viên KHÔNG capture ảnh sinh viên**
- ✗ Chỉ Admin mới có chức năng capture

---

### 3. ❌ **TRAINING LOGIC KHÔNG ĐỒNG BỘ**

Hệ thống có **3 cách training khác nhau**:

#### **Cách 1: Admin Web UI (admin_views.py - main())**
```python
data_dir = 'main/Dataset/FaceData/processed'  # ✓ Đúng path
classifier_filename = 'main/Models/facemodel.pkl'
# SỬ DỤNG: SVC(kernel='linear', probability=True)
```

#### **Cách 2: Script CLI (train_face_model.py)**
```python
FACE_DATA_DIR = 'main/Dataset/FaceData'  # ✗ SAI - Thiếu /processed
OUTPUT_CLASSIFIER_PATH = 'main/Models/facemodel.pkl'
# SỬ DỤNG: SVC(kernel='linear', probability=True, C=1.0)
```

#### **Cách 3: Lecturer (KHÔNG CÓ)**
- ❌ Giảng viên **KHÔNG THỂ** train lại model
- ❌ Phải nhờ Admin train

**Vấn đề:**
- ✗ Cùng output file `facemodel.pkl` nhưng **train từ 2 thư mục khác nhau**
- ✗ Cách 1 đọc từ `processed/`, Cách 2 đọc từ gốc `FaceData/`
- ✗ Nếu dùng script CLI, sẽ **KHÔNG TÌM THẤY ẢNH** (vì ảnh nằm trong `/processed`)

---

### 4. ❌ **FACE DETECTION KHÔNG NHẤT QUÁN**

| Giai đoạn | Phương pháp | Kích thước | Anti-spoof | Face Align |
|-----------|-------------|------------|------------|------------|
| **Admin Capture** | `AntiSpoofPredict.get_bbox()` | 160x160 | ✅ Có | ❌ Không |
| **Training** | `detect_face.detect_face()` (MTCNN) | 160x160 | ❌ Không | ✅ Có |
| **Recognition (Lecturer)** | `detect_face.detect_face()` (MTCNN) | 160x160 | ✅ Có | ✅ Có |

**Vấn đề:**
- ✗ **Admin capture** dùng `AntiSpoofPredict` (không align face)
- ✗ **Training + Recognition** dùng MTCNN (có align face)
- ✗ Ảnh từ Admin **KHÔNG ĐƯỢC ALIGN** nên chất lượng nhận diện kém

**Giải thích:**
- MTCNN detect + align face với facial landmarks (5 điểm: 2 mắt, mũi, 2 góc miệng)
- Admin chỉ crop bounding box thô → ảnh lệch, không chuẩn
- Training + Recognition align lại → mismatch giữa ảnh train và ảnh gốc

---

### 5. ❌ **FLOW ĐIỂM DANH KHÔNG RÕ RÀNG**

#### **Flow cũ (Deprecated - còn trong code):**
```python
# lecturer_views.py
lecturer_mark_attendance(classroom_id)  # ✗ KHÔNG dùng session
lecturer_mark_attendance_by_face(classroom_id)  # ✗ KHÔNG dùng session
```

**Vấn đề:**
- Trực tiếp tạo `Attendance` record theo `classroom_id` + `date`
- KHÔNG quản lý session → dễ trùng lặp bản ghi
- KHÔNG track được "Buổi học thứ mấy"

#### **Flow mới (Session-based - khuyến nghị):**
```python
# 1. Bắt đầu buổi học
lecturer_start_session(classroom_id)
  → Tạo ClassSession
  → Khởi tạo Attendance cho TẤT CẢ sinh viên (status = Vắng)

# 2. Điểm danh
lecturer_mark_attendance_session(session_id)  # Manual
lecturer_mark_attendance_by_face_session(session_id)  # Face recognition

# 3. Đóng buổi
lecturer_close_session(session_id)
```

**Vấn đề:**
- ✗ Cả 2 flow **ĐỀU TỒN TẠI** trong code (gây nhầm lẫn)
- ✗ URL cũ vẫn hoạt động → có thể dùng nhầm flow cũ
- ✗ Flow cũ không cập nhật `check_in_method = 'FACE'` hoặc `modified_by`

---

### 6. ❌ **KHÔNG ĐỒNG BỘ GIỮA DB VÀ FILE SYSTEM**

#### **Kịch bản 1: Xóa sinh viên**
```python
# admin_views.py - admin_student_delete()
StudentInfo.objects.filter(id_student=id_student).delete()  # Xóa DB
shutil.rmtree(f"./main/Dataset/FaceData/processed/{id_student}")  # Xóa ảnh
```

**Vấn đề:**
- ✅ Có xóa cả DB và file
- ✗ **KHÔNG TỰ ĐỘNG train lại model**
- ✗ Model vẫn còn dữ liệu sinh viên cũ → nhận diện sai

#### **Kịch bản 2: Thêm ảnh mới**
```python
# Admin capture 300 ảnh cho sinh viên mới
# ✗ PHẢI BẤM "Train" THỦ CÔNG
# ✗ Nếu quên train → không nhận diện được
```

**Đề xuất:**
- Auto-trigger training sau khi capture/delete
- Hoặc warning rõ ràng "Cần train lại model"

---

### 7. ❌ **CẤU HÌNH MODEL PHÂN TÁN**

```python
# admin_views.py (Web UI Training)
TRAIN_STATUS = 0
mode = 'TRAIN'
data_dir = 'main/Dataset/FaceData/processed'
model = 'main/Models/20180402-114759.pb'
classifier_filename = 'main/Models/facemodel.pkl'
batch_size = 90
min_nrof_images_per_class = 20

# train_face_model.py (CLI Script)
INPUT_IMAGE_SIZE = 160
FACENET_MODEL_PATH = 'main/Models/20180402-114759.pb'
OUTPUT_CLASSIFIER_PATH = 'main/Models/facemodel.pkl'
FACE_DATA_DIR = 'main/Dataset/FaceData'  # ✗ SAI
MIN_FACE_SIZE = 20

# reg.py (Recognition)
INPUT_IMAGE_SIZE = 160
CLASSIFIER_PATH = 'main/Models/facemodel.pkl'
FACENET_MODEL_PATH = 'main/Models/20180402-114759.pb'
```

**Vấn đề:**
- ✗ Cùng 1 config nhưng **KHAI BÁO 3 NƠI**
- ✗ Nếu sửa 1 chỗ, phải nhớ sửa 2 chỗ còn lại
- ✗ Dễ quên và gây mismatch

---

## ✅ ĐỀ XUẤT KHẮC PHỤC

### **Ưu tiên 1: Thống nhất đường dẫn ảnh**

Tạo file `main/config.py`:
```python
# main/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Face Data Paths
FACE_DATA_DIR = os.path.join(BASE_DIR, 'main', 'Dataset', 'FaceData', 'processed')
FACENET_MODEL = os.path.join(BASE_DIR, 'main', 'Models', '20180402-114759.pb')
CLASSIFIER_MODEL = os.path.join(BASE_DIR, 'main', 'Models', 'facemodel.pkl')

# Training Config
INPUT_IMAGE_SIZE = 160
MIN_IMAGES_PER_STUDENT = 20
BATCH_SIZE = 90
```

Sửa **TẤT CẢ** file import từ `config.py` thay vì hardcode.

---

### **Ưu tiên 2: Loại bỏ flow cũ**

- ❌ Xóa hoặc comment out:
  - `lecturer_mark_attendance(classroom_id)`
  - `lecturer_mark_attendance_by_face(classroom_id)`
  - `live_video_feed2(classroom_id)`
- ✅ Chỉ giữ flow session-based:
  - `lecturer_start_session()` → `lecturer_mark_attendance_session()` → `lecturer_close_session()`

---

### **Ưu tiên 3: Chuẩn hóa capture + training**

**Bước 1:** Sửa Admin capture dùng MTCNN để align face
```python
# admin_views.py - capture()
# THAY ĐỔI: Dùng detect_face.detect_face() thay vì AntiSpoofPredict.get_bbox()
# Để ảnh được align giống như lúc training
```

**Bước 2:** Sửa `train_face_model.py` đọc đúng path
```python
# train_face_model.py
FACE_DATA_DIR = 'main/Dataset/FaceData/processed'  # THÊM /processed
```

**Bước 3:** Auto-trigger training sau capture
```python
# admin_views.py - capture()
if image_count >= 300:
    CAPTURE_STATUS = 1
    # ✅ THÊM: Auto training
    threading.Thread(target=main).start()
```

---

### **Ưu tiên 4: Thêm validation và warning**

```python
def check_system_consistency():
    """Kiểm tra tính nhất quán của hệ thống"""
    errors = []
    
    # Check 1: Model tồn tại
    if not os.path.exists(CLASSIFIER_MODEL):
        errors.append("Model chưa được train!")
    
    # Check 2: Số ảnh vs số sinh viên trong model
    with open(CLASSIFIER_MODEL, 'rb') as f:
        model, class_names = pickle.load(f)
    
    students_in_db = StudentInfo.objects.count()
    students_in_model = len(class_names)
    
    if students_in_db != students_in_model:
        errors.append(f"DB có {students_in_db} SV, model có {students_in_model} SV. Cần train lại!")
    
    # Check 3: Ảnh trong /processed vs DB
    for student in StudentInfo.objects.all():
        folder = os.path.join(FACE_DATA_DIR, student.id_student)
        if not os.path.exists(folder):
            errors.append(f"Sinh viên {student.id_student} chưa có ảnh!")
    
    return errors
```

Gọi `check_system_consistency()` trước khi điểm danh.

---

## 📊 BẢNG SO SÁNH ADMIN VS LECTURER

| Chức năng | Admin | Lecturer | Nhất quán? |
|-----------|-------|----------|-----------|
| **Capture ảnh SV** | ✅ Có | ❌ Không | ❌ Không |
| **Training model** | ✅ Có (Web + Script) | ❌ Không | ❌ Không |
| **Điểm danh manual** | ❌ Không | ✅ Có | ✅ OK |
| **Điểm danh face** | ❌ Không | ✅ Có | ✅ OK |
| **Anti-spoof check** | ✅ Có (capture) | ✅ Có (recognition) | ✅ OK |
| **Face alignment** | ❌ Không | ✅ Có | ❌ **MẤT NHẤT QUÁN** |
| **Path ảnh** | `./main/.../processed/` | Không rõ | ❌ **MƠ HỒ** |
| **Quản lý session** | ❌ Không | ✅ Có | ✅ OK |

---

## 🎯 KẾT LUẬN

### **Nguyên nhân chính:**
1. ❌ Đường dẫn ảnh không thống nhất (`./` vs không `./`, `processed/` vs không)
2. ❌ Có 2 flow điểm danh (cũ + mới) chạy song song
3. ❌ Face detection khác nhau (AntiSpoof vs MTCNN)
4. ❌ Training script đọc sai thư mục
5. ❌ Không auto-sync giữa DB, file system và model

### **Khuyến nghị:**
1. ✅ Tạo `main/config.py` để centralize configuration
2. ✅ Xóa flow cũ, chỉ giữ session-based
3. ✅ Sửa admin capture dùng MTCNN align face
4. ✅ Fix `train_face_model.py` đọc đúng path `/processed`
5. ✅ Thêm system health check trước khi điểm danh
6. ✅ Auto-trigger training hoặc hiển thị warning rõ ràng

---

**Tài liệu này sẽ được cập nhật sau khi khắc phục.**
