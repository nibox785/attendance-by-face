
# Hệ thống điểm danh sinh viên bằng khuôn mặt

Hệ thống điểm danh sinh viên bằng khuôn mặt là một ứng dụng sử dụng công nghệ nhận diện khuôn mặt để xác định sự hiện diện của sinh viên trong các buổi học

## Tech Stack

**Language:** Python

**Framework:** Django

**Database:** MySQL


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

### 8. Start the server

```bash
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000

## Login Credentials

After importing data with `--password 123456`:

### Student Login
- **Username**: Student ID (e.g., `2011003929`)
- **Password**: `123456`

### Staff/Lecturer Login
- **Username**: Staff ID (e.g., `1079440959`)
- **Password**: `123456`

### Admin Login (if created via createsuperuser)
- **Username**: Your chosen username
- **Password**: Your chosen password

## Database Structure

The system uses the following main tables:
- `auth_user` - User authentication
- `main_role` - User roles
- `main_staffinfo` - Staff/Lecturer information
- `main_studentinfo` - Student information
- `main_classroom` - Classroom information
- `main_studentclassdetails` - Student enrollments
- `main_blogpost` - Announcements

## Reset Password

If you forget the password, you can reset it by running:

```bash
python manage.py import_all_data --password new_password
```

This will update all user passwords to the new password without affecting other data.