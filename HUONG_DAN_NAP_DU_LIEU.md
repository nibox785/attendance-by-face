# Hướng dẫn nạp dữ liệu vào MySQL

## Bước 1: Kích hoạt virtual environment
```bash
.venv\Scripts\activate
```

## Bước 2: Đảm bảo đã cài đặt MySQL driver
```bash
pip install mysqlclient
```

## Bước 3: Chạy migration (nếu chưa chạy)
```bash
python manage.py makemigrations
python manage.py migrate
```

## Bước 4: Import tất cả dữ liệu từ file JSON vào MySQL

### Cách 1: Dùng hash mật khẩu có sẵn trong JSON (không biết mật khẩu gốc)
```bash
python manage.py import_all_data
```

### Cách 2: Đặt mật khẩu chung cho TẤT CẢ tài khoản (sinh viên + nhân viên)
```bash
python manage.py import_all_data --password 123456
```
*Thay `123456` bằng mật khẩu bạn muốn đặt*

## Bước 5: Kiểm tra dữ liệu trong MySQL Workbench
```sql
-- Kiểm tra số lượng bản ghi
SELECT COUNT(*) FROM auth_user;           -- Tài khoản đăng nhập
SELECT COUNT(*) FROM main_role;            -- Vai trò
SELECT COUNT(*) FROM main_staffinfo;       -- Nhân viên
SELECT COUNT(*) FROM main_staffrole;       -- Phân quyền nhân viên
SELECT COUNT(*) FROM main_studentinfo;     -- Sinh viên
SELECT COUNT(*) FROM main_classroom;       -- Lớp học
SELECT COUNT(*) FROM main_studentclassdetails; -- Danh sách sinh viên trong lớp
SELECT COUNT(*) FROM main_blogpost;        -- Bài viết thông báo

-- Xem dữ liệu mẫu
SELECT * FROM main_studentinfo LIMIT 5;
SELECT * FROM auth_user LIMIT 5;
```

## Bước 6: Tạo tài khoản admin để quản trị
```bash
python manage.py createsuperuser
```
Nhập thông tin:
- Username: admin
- Email: admin@example.com
- Password: (chọn mật khẩu)

## Bước 7: Khởi động server
```bash
python manage.py runserver
```

## Đăng nhập

### Sinh viên
- **Username**: Mã sinh viên (ví dụ: `2011003929`)
- **Password**: 
  - Nếu dùng `--password 123456` → nhập `123456`
  - Nếu không dùng `--password` → không biết được (vì đã hash)

### Nhân viên/Giảng viên
- **Username**: Mã nhân viên (ví dụ: `2949769422`)
- **Password**: Tương tự như sinh viên

### Admin (tạo bằng createsuperuser)
- **Username**: admin
- **Password**: mật khẩu bạn đã đặt

## Lưu ý quan trọng

1. **Nếu muốn biết mật khẩu để đăng nhập**, BẮT BUỘC phải chạy lại lệnh với `--password`:
   ```bash
   python manage.py import_all_data --password 123456
   ```

2. **Chạy lại lệnh import** sẽ CẬP NHẬT dữ liệu (không bị trùng lặp)

3. **Cấu trúc file đã tạo**:
   ```
   main/
   └── management/
       ├── __init__.py
       └── commands/
           ├── __init__.py
           └── import_all_data.py  ← Lệnh import
   ```

## Xử lý lỗi thường gặp

### Lỗi: "No module named 'mysqlclient'"
```bash
pip install mysqlclient
```

### Lỗi: "table doesn't exist"
```bash
python manage.py migrate
```

### Lỗi: "file not found Database/StudentInfo.json"
- Đảm bảo chạy lệnh tại thư mục gốc project (có file `manage.py`)
- Kiểm tra thư mục `Database/` có đầy đủ file JSON

## Các bảng được import

✅ Role (vai trò)
✅ StaffInfo (nhân viên/giảng viên)  
✅ StaffRole (phân quyền nhân viên)
✅ StudentInfo (sinh viên)
✅ Classroom (lớp học)
✅ StudentClassDetails (danh sách sinh viên trong lớp)
✅ BlogPost (bài viết thông báo)
✅ auth_user (tài khoản đăng nhập cho sinh viên + nhân viên)
