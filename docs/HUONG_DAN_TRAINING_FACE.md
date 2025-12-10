# HƯỚNG DẪN TRAINING FACE RECOGNITION MODEL

## 🎯 Mục đích

Hệ thống cần **train model** từ ảnh khuôn mặt của sinh viên để có thể nhận diện chính xác. Nếu không có model hoặc model chưa train đủ sinh viên → **Không nhận diện được**.

---

## 📋 Chuẩn bị

### Bước 1: Thu thập ảnh khuôn mặt sinh viên

Mỗi sinh viên cần **5-10 ảnh** với yêu cầu:

✅ **Chất lượng ảnh:**
- Độ phân giải tối thiểu: **200x200 pixels** (khuyến nghị 640x480+)
- Rõ nét, không mờ, không bị nhiễu
- Ánh sáng tốt (không quá tối hoặc quá sáng)
- Nền đơn giản (tránh nền lộn xộn)

✅ **Góc chụp:**
- Nhìn thẳng: 3-4 ảnh
- Hơi nghiêng trái: 1-2 ảnh
- Hơi nghiêng phải: 1-2 ảnh
- Hơi ngửa/cúi: 1 ảnh (tùy chọn)

✅ **Biểu cảm:**
- Bình thường, nghiêm túc
- Có thể thêm 1-2 ảnh mỉm cười nhẹ
- Tránh che mặt (khẩu trang, kính râm, mũ)

❌ **Tránh:**
- Ảnh mờ, thiếu sáng
- Góc chụp quá nghiêng (> 45°)
- Khuôn mặt quá nhỏ trong ảnh
- Nhiều người trong 1 ảnh
- Che mặt bằng tay, vật dụng

---

## 🗂️ Cấu trúc thư mục

Tạo thư mục theo cấu trúc:

```
main/Dataset/FaceData/
├── 2011003929/          # Mã số sinh viên 1
│   ├── 1.jpg
│   ├── 2.jpg
│   ├── 3.jpg
│   ├── 4.jpg
│   └── 5.jpg
├── 2011010091/          # Mã số sinh viên 2
│   ├── anh1.jpg
│   ├── anh2.jpg
│   ├── anh3.jpg
│   ├── anh4.jpg
│   └── anh5.jpg
└── 2011010708/          # Mã số sinh viên 3
    ├── face1.png
    ├── face2.png
    ├── face3.png
    └── face4.png
```

**Lưu ý:**
- Tên thư mục = **Mã số sinh viên** (chính xác 100%)
- Tên file ảnh: tùy ý (VD: 1.jpg, anh1.png, face_01.jpeg)
- Format ảnh: JPG, JPEG, PNG

---

## 🚀 Chạy Training Script

### Bước 2: Tạo cấu trúc thư mục (lần đầu)

```bash
python train_face_model.py
```

Script sẽ hỏi:
```
Bạn có muốn tạo cấu trúc thư mục mẫu? (y/n):
```

Nhập `y` → Tạo thư mục mẫu cho 5 sinh viên

### Bước 3: Thêm ảnh vào thư mục

1. Vào thư mục `main/Dataset/FaceData/`
2. Vào thư mục con của từng sinh viên (VD: `2011003929`)
3. Copy 5-10 ảnh khuôn mặt vào đó
4. Đặt tên ảnh tùy ý (1.jpg, 2.jpg, ...)

### Bước 4: Chạy training

```bash
python train_face_model.py
```

**Quá trình training:**

```
============================================================
🎓 FACE RECOGNITION MODEL TRAINER
============================================================

📦 Loading FaceNet model...

📊 Tìm thấy 5 sinh viên:
   - 2011003929: 7 ảnh
   - 2011010091: 6 ảnh
   - 2011010708: 5 ảnh
   - 2011020456: 8 ảnh
   - 2011030789: 5 ảnh

🖼️ Tổng cộng: 31 ảnh

🔍 Detecting và aligning faces...
Processed 10/31 images
Processed 20/31 images
Processed 31/31 images
✅ Detected 29 faces

🧠 Extracting face embeddings...
Processed 1/1 batches

🎓 Training SVM classifier...

💾 Saving classifier to main/Models/facemodel.pkl...

✅ Training hoàn tất!
📊 Thống kê:
   - Số sinh viên: 5
   - Tổng số ảnh: 29
   - Trung bình: 5.8 ảnh/sinh viên

👥 Danh sách sinh viên đã train:
   1. 2011003929 (7 ảnh)
   2. 2011010091 (6 ảnh)
   3. 2011010708 (5 ảnh)
   4. 2011020456 (8 ảnh)
   5. 2011030789 (5 ảnh)

🎉 SUCCESS! Model đã sẵn sàng sử dụng!
```

**Thời gian:** 
- 30 ảnh: ~2-3 phút
- 100 ảnh: ~5-7 phút
- 300 ảnh: ~15-20 phút

---

## ✅ Kiểm tra kết quả

### File model được tạo:

```
main/Models/facemodel.pkl
```

### Test nhận diện:

1. Khởi động server:
   ```bash
   python manage.py runserver
   ```

2. Đăng nhập giảng viên: `1079440959` / `123456`

3. Vào **"Quản lý điểm danh"** → **"Bắt đầu điểm danh"**

4. Click **"Điểm danh bằng khuôn mặt"**

5. Test với sinh viên đã train:
   - Đứng trước camera
   - Nhìn thẳng
   - Chờ 1-2 giây
   - ✅ Nếu OK: Hiện tên + thanh progress bar → Điểm danh thành công
   - ❌ Nếu không: Hiện "KHÔNG CHẮC CHẮN" + top 3 predictions

---

## 🔧 Xử lý lỗi thường gặp

### Lỗi 1: "No face detected"

**Nguyên nhân:** Ảnh không phát hiện được khuôn mặt

**Giải pháp:**
- Kiểm tra ảnh có khuôn mặt rõ ràng không
- Thử ảnh khác với khuôn mặt lớn hơn
- Đảm bảo ánh sáng tốt trong ảnh

### Lỗi 2: "Cannot read image"

**Nguyên nhân:** File ảnh bị lỗi hoặc format không hỗ trợ

**Giải pháp:**
- Kiểm tra file có mở được bằng trình xem ảnh không
- Chuyển sang format JPG/PNG
- Tải lại ảnh nếu bị corrupt

### Lỗi 3: Model không nhận diện chính xác

**Nguyên nhân:** 
- Quá ít ảnh training
- Ảnh training khác xa với thực tế

**Giải pháp:**
1. Thêm nhiều ảnh hơn (8-10 ảnh/người)
2. Chụp ảnh training trong cùng điều kiện với khi điểm danh:
   - Cùng camera
   - Cùng ánh sáng
   - Cùng khoảng cách
3. Train lại model
4. Giảm threshold nếu cần (đã giảm xuống 0.5)

### Lỗi 4: "KHÔNG CHẮC CHẮN" khi điểm danh

**Nguyên nhân:** Confidence score < 50%

**Giải pháp:**
1. **Ngay lập tức:**
   - Sinh viên đứng gần camera hơn
   - Bật đèn sáng hơn
   - Nhìn thẳng vào camera
   - Không che mặt

2. **Lâu dài:**
   - Thêm ảnh training cho sinh viên đó
   - Chụp ảnh trong điều kiện tương tự
   - Train lại model

3. **Tạm thời:**
   - Dùng **điểm danh thủ công**
   - Sau đó train lại model

---

## 📊 Benchmark chất lượng

### Độ chính xác theo số ảnh:

| Số ảnh/người | Độ chính xác | Ghi chú |
|--------------|--------------|---------|
| 1-2 ảnh | 40-60% | ❌ Quá thấp, không khuyến nghị |
| 3-4 ảnh | 60-75% | ⚠️ Chấp nhận được, nhưng nên thêm |
| 5-7 ảnh | 75-90% | ✅ Tốt, đủ dùng |
| 8-10 ảnh | 90-95% | ✅ Rất tốt, khuyến nghị |
| 10+ ảnh | 95%+ | ✅ Xuất sắc |

### Điều kiện tối ưu:

✅ **Ánh sáng:** Tự nhiên hoặc đèn trắng, không chói
✅ **Khoảng cách:** 50-100cm từ camera
✅ **Góc nhìn:** Thẳng (±15°)
✅ **Kích thước khuôn mặt:** Chiếm 40-60% frame
✅ **Nền:** Đơn giản, không lộn xộn

---

## 🔄 Cập nhật model

### Khi nào cần train lại?

- ✅ Có sinh viên mới
- ✅ Thêm ảnh cho sinh viên hiện tại
- ✅ Đổi camera (khác độ phân giải, màu sắc)
- ✅ Thay đổi vị trí điểm danh (khác ánh sáng)
- ✅ Model nhận diện kém

### Quy trình cập nhật:

1. Thêm ảnh mới vào thư mục tương ứng
2. Chạy lại: `python train_face_model.py`
3. Model cũ sẽ bị ghi đè
4. Restart server (Ctrl+C → `python manage.py runserver`)
5. Test lại

**Lưu ý:** Backup model cũ nếu cần:
```bash
copy main\Models\facemodel.pkl main\Models\facemodel_backup.pkl
```

---

## 💡 Tips nâng cao

### 1. Chụp ảnh training tốt

Sử dụng **script chụp ảnh tự động**:

```python
# Chạy trong Python console
import cv2
import os

def capture_faces(student_id, num_photos=10):
    """Chụp ảnh tự động cho sinh viên"""
    output_dir = f'main/Dataset/FaceData/{student_id}'
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    count = 0
    
    print(f"Chụp {num_photos} ảnh cho sinh viên {student_id}")
    print("Nhấn SPACE để chụp, ESC để thoát")
    
    while count < num_photos:
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.putText(frame, f"So anh: {count}/{num_photos}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Nhan SPACE de chup", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Capture', frame)
        
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            filename = f'{output_dir}/{count+1}.jpg'
            cv2.imwrite(filename, frame)
            print(f'Saved: {filename}')
            count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print(f'Hoàn thành! Đã chụp {count} ảnh.')

# Sử dụng
capture_faces('2011003929', 10)
```

### 2. Kiểm tra chất lượng ảnh

```python
import cv2
import numpy as np

def check_image_quality(image_path):
    """Kiểm tra chất lượng ảnh"""
    img = cv2.imread(image_path)
    
    # Kiểm tra độ mờ (Laplacian variance)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Kiểm tra độ sáng
    brightness = np.mean(gray)
    
    print(f"File: {image_path}")
    print(f"  Blur score: {blur_score:.2f} {'✅' if blur_score > 100 else '❌ Too blurry'}")
    print(f"  Brightness: {brightness:.2f} {'✅' if 50 < brightness < 200 else '❌ Too dark/bright'}")
    
    return blur_score > 100 and 50 < brightness < 200

# Test
check_image_quality('main/Dataset/FaceData/2011003929/1.jpg')
```

### 3. Batch training cho nhiều lớp

Nếu có nhiều lớp, có thể import danh sách sinh viên từ database:

```python
from main.models import StudentInfo

# Lấy tất cả sinh viên
students = StudentInfo.objects.all()

print(f"Cần thêm ảnh cho {students.count()} sinh viên:")
for student in students:
    student_dir = f'main/Dataset/FaceData/{student.id_student}'
    
    if not os.path.exists(student_dir):
        os.makedirs(student_dir)
        print(f"  ⚠️ {student.id_student} - {student.student_name}: Chưa có ảnh")
    else:
        num_images = len([f for f in os.listdir(student_dir) 
                         if f.lower().endswith(('.jpg', '.png'))])
        status = "✅" if num_images >= 5 else "⚠️"
        print(f"  {status} {student.id_student} - {student.student_name}: {num_images} ảnh")
```

---

## 🎯 Checklist trước khi triển khai

- [ ] Đã thu thập đủ 5-10 ảnh cho mỗi sinh viên
- [ ] Ảnh rõ nét, ánh sáng tốt, đa dạng góc độ
- [ ] Đã chạy training script thành công
- [ ] File `main/Models/facemodel.pkl` đã được tạo
- [ ] Đã test nhận diện với ít nhất 3 sinh viên
- [ ] Độ chính xác đạt > 80% trong test
- [ ] Đã backup model cũ (nếu có)
- [ ] Server đã restart sau khi train

---

**Cập nhật:** 10/12/2025  
**Version:** 2.0 - Enhanced Recognition
