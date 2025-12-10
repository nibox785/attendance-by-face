# 🛠️ Utility Scripts

Thư mục này chứa các script tiện ích hỗ trợ quản lý hệ thống.

## 📜 Danh sách scripts

### 👤 Quản lý sinh viên
- **`create_student_folders.py`** - Tự động tạo thư mục cho tất cả sinh viên trong database
  ```bash
  python scripts/create_student_folders.py
  ```

- **`check_face_folders.py`** - Kiểm tra folder cấu trúc vs database
  ```bash
  python scripts/check_face_folders.py
  ```

- **`check_face_data.py`** - Kiểm tra dữ liệu ảnh khuôn mặt
  ```bash
  python scripts/check_face_data.py
  ```

### 🔧 Maintenance
- **`update_roles.py`** - Cập nhật roles cho user
  ```bash
  python scripts/update_roles.py
  ```

- **`temp_update.py`** - Script tạm thời cho updates

## ⚠️ Lưu ý
- Các script này chỉ dùng cho maintenance và debugging
- Không chạy trong production environment
- Backup database trước khi chạy scripts modify data
