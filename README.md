
# Hệ thống điểm danh sinh viên bằng khuôn mặt

Hệ thống điểm danh sinh viên bằng khuôn mặt là một ứng dụng sử dụng công nghệ nhận diện khuôn mặt để xác định sự hiện diện của sinh viên trong các buổi học

## Tech Stack

**Language:** Python

**Framework:** Django

**Database:** MySQL

## Project Structure

```
attendance-by-face/
├── main/                          # Main Django app
│   ├── view/                      # View controllers
│   ├── Dataset/FaceData/          # Student face images (MSSV folders)
│   ├── Models/                    # Face recognition models
│   └── migrations/                # Database migrations
├── templates/                     # HTML templates
│   ├── admin/                     # Admin dashboard templates
│   ├── lecturer/                  # Lecturer portal templates
│   └── student/                   # Student portal templates
├── static/                        # Static files (CSS, JS, images)
├── Database/                      # JSON data for import
├── docs/                          # Documentation files
├── scripts/                       # Utility scripts
├── FaceByAttendance/              # Django project settings
├── manage.py                      # Django management script
├── train_face_model.py            # Face recognition training script
└── requirements_v3.10.txt         # Python dependencies
```

For detailed documentation, see **[docs/](docs/)** folder.


## Run Locally

### 1. Clone the project

```bash
git clone https://github.com/ITDEV-UTH/View-Attendance-By-Face.git
cd View-Attendance-By-Face
```

### 2. Create and activate virtual environment

```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

- If use python version 3.7

    ```bash
    pip install -r requirements_v3.7.txt
    ```

- If use python version 3.10

    ```bash
    pip install -r requirements_v3.10.txt
    ```

- Install MySQL client

    ```bash
    pip install mysqlclient
    ```

### 4. Configure MySQL Database

Create a MySQL database named `attendance_by_face` and update the database settings in `FaceByAttendance/setting.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'attendance_by_face',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### 5. Run migrations

```bash
# Create migration files
python manage.py makemigrations

# Apply database migrations
python manage.py migrate
```

### 6. Import data from JSON files

Import all data (students, staff, classrooms, etc.) into MySQL database:

```bash
# Import with default password '123456' for all users
python manage.py import_all_data --password 123456
```

**Note:** This command will import data from all JSON files in the `Database/` folder:
- `Role.json` - User roles
- `StaffInfo.json` - Staff/Lecturer information
- `StaffRole.json` - Staff role assignments
- `StudentInfo.json` - Student information
- `Classroom.json` - Classroom information
- `StudentClassDetails.json` - Student-classroom enrollments
- `BlogPost.json` - Blog posts/announcements

The `--password` flag sets a common password for all user accounts. You can change `123456` to any password you prefer.

### 7. Create superuser (Optional)

To access Django admin panel:

```bash
python manage.py createsuperuser
```

### 8. Train Face Recognition Model (REQUIRED for face attendance)

**Important:** Face recognition won't work without training the model first!

```bash
# First time setup - Create sample directory structure
python train_face_model.py

# Add student face photos to: main/Dataset/FaceData/STUDENT_ID/
# Each student needs 5-10 photos (front, left, right angles)

# Train the model
python train_face_model.py
```

See detailed guide: **[docs/HUONG_DAN_TRAINING_FACE.md](docs/HUONG_DAN_TRAINING_FACE.md)**

### 9. Start the server

```bash
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000

## Login Credentials

After importing data with `--password 123456`:

### Student Login
- **Username**: `2011003929` (Nguyễn Văn Anh) - Đăng ký 4 môn
- **Username**: `2011010091` (Trần Thị Bảo) - Đăng ký 3 môn
- **Username**: `2011010708` (Lê Minh Chiến) - Đăng ký 3 môn
- **Username**: `2011020456` (Phạm Thị Diệu) - Đăng ký 3 môn
- **Username**: `2011030789` (Huỳnh Văn Em) - Đăng ký 2 môn
- **Password**: `123456` (all students)

### Staff/Lecturer Login
- **Username**: `1079440959` (TS. Nguyễn Văn An)
- **Username**: `1250767097` (ThS. Trần Thị Bình)
- **Username**: `1304868666` (PGS.TS. Lê Văn Cường)
- **Password**: `123456` (all staff)

### Admin Login
**For Admin Dashboard** (http://127.0.0.1:8000/login):
- **Username**: `admin001` (Quản trị viên)
- **Password**: `123456`

**For Django Admin Panel** (http://127.0.0.1:8000/admin):
- **Username**: `admin`
- **Password**: `admin123`

## Database Structure

The system uses the following main tables:
- `auth_user` - User authentication (54 accounts)
- `main_role` - User roles (4 roles)
- `main_staffinfo` - Staff/Lecturer information (3 lecturers)
- `main_studentinfo` - Student information (5 students)
- `main_classroom` - Classroom information (8 classes)
- `main_studentclassdetails` - Student enrollments (15 enrollments)
- `main_blogpost` - Announcements (2 posts)

## Current Academic Schedule

### Semester 1 (2024-2025) - Học kỳ 1
**Duration**: September 2, 2024 - December 31, 2025 (Đang diễn ra)

1. **Lập trình Python** (ID: 1)
   - Lecturer: TS. Nguyễn Văn An
   - Schedule: Tuesday (Thứ 3), 7:30-10:30
   - Students: 3 enrolled

2. **Cấu trúc dữ liệu và giải thuật** (ID: 2)
   - Lecturer: ThS. Trần Thị Bình
   - Schedule: Wednesday (Thứ 4), 13:00-16:00
   - Students: 3 enrolled

3. **Cơ sở dữ liệu** (ID: 3)
   - Lecturer: PGS.TS. Lê Văn Cường
   - Schedule: Thursday (Thứ 5), 7:30-10:30
   - Students: 3 enrolled

4. **Lập trình Web** (ID: 4)
   - Lecturer: TS. Nguyễn Văn An
   - Schedule: Friday (Thứ 6), 13:00-16:00
   - Students: 3 enrolled

5. **Trí tuệ nhân tạo** (ID: 5)
   - Lecturer: ThS. Trần Thị Bình
   - Schedule: Saturday (Thứ 7), 7:30-10:30
   - Students: 3 enrolled

### Old Classes (Completed)
**Duration**: September 2, 2024 - December 20, 2024

6. **Mạng máy tính** (ID: 6)
7. **Hệ điều hành** (ID: 7)
8. **Lập trình Java** (ID: 8)

## Attendance System Usage Guide

### How to Mark Attendance (Session-Based)

The system uses a **session-based attendance** approach to ensure data accuracy and prevent duplicate records.

#### For Lecturers:

**1. Start Attendance Session**
- Go to: **Quản lý điểm danh** (Attendance Management)
- Click the green **"Bắt đầu điểm danh"** button for today's class
- System automatically:
  - Creates a new session for that class
  - Initializes ALL students as "Absent" (Vắng)
  - Opens the attendance marking page

**2. Mark Attendance - 3 Options:**

**Option A: Manual Attendance** (Thủ công)
- In the attendance table, use the dropdown for each student
- Select status: **Vắng** (Absent) / **Có mặt** (Present) / **Muộn** (Late)
- Click **"Lưu thay đổi"** (Save Changes) button at the bottom
- System automatically records:
  - Who made the change (`modified_by`)
  - When it was changed (`modified_at`)
  - Method: MANUAL

**Option B: Face Recognition** (Nhận diện khuôn mặt)
- Click blue **"Điểm danh bằng khuôn mặt"** button
- Allow camera access
- Students stand in front of camera (one at a time)
- System automatically:
  - Detects and recognizes face
  - Updates from "Vắng" → "Có mặt" or "Muộn" (if late > 15 min)
  - Method: FACE
  - Shows green box with student name when recognized
- Optimized for speed (15 frames = ~1.5 seconds)

**Option C: Combined Method**
- Use face recognition for most students
- Use manual marking for:
  - Students who forgot their face data
  - Students who arrived after session closed
  - Corrections/adjustments

**3. Close Session**
- Click red **"Đóng buổi điểm danh"** button when done
- System shows statistics (Present/Absent count)
- Session status changes to CLOSED

**4. Reopen Session (if needed)**
- Go to **"Lịch sử điểm danh"** (Attendance History)
- Find the closed session
- Click yellow **"Mở lại để chỉnh sửa"** button
- Make changes
- Click **"Lưu thay đổi"**
- Close session again when done

#### Key Features:

✅ **No Duplicate Records**: Each student has exactly ONE attendance record per session  
✅ **Flexible Editing**: Can reopen and edit closed sessions  
✅ **Audit Trail**: Tracks who modified, when, and how (MANUAL/FACE)  
✅ **Dynamic Grading**: Attendance score calculated based on actual number of sessions  
✅ **Fast Recognition**: Optimized face detection (~1.5 seconds per student)  
✅ **Anti-Spoofing**: Detects fake photos/videos  

#### Attendance Rules:

- **Present (Có mặt)**: Check-in within 15 minutes of class start → 1 point
- **Late (Muộn)**: Check-in after 15 minutes → 0.5 points  
- **Absent (Vắng)**: No check-in → 0 points  
- **Maximum Absence**: 20% of total sessions (automatic calculation)  
- **Final Score**: (Present×1 + Late×0.5) / Total Sessions × 3 points  

### For Students:

**View Attendance:**
- Login to student portal
- Go to **"Tình điểm chuyên cần"** (Attendance Record)
- View your attendance for each class
- See detailed statistics and scores

---

## Reset Password

If you forget the password, you can reset it by running:

```bash
python manage.py import_all_data --password new_password
```

This will update all user passwords to the new password without affecting other data.