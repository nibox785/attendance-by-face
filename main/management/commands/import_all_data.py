from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from main.models import (
    Role, StaffInfo, StaffRole, StudentInfo, 
    Classroom, StudentClassDetails, BlogPost
)
from pathlib import Path
import json
from datetime import datetime


class Command(BaseCommand):
    help = "Import tất cả dữ liệu từ các file JSON trong thư mục Database vào MySQL"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            dest="default_password",
            help="Đặt mật khẩu chung cho tất cả tài khoản (plaintext). Nếu không truyền, dùng hash có sẵn trong JSON.",
        )

    def handle(self, *args, **opts):
        default_pw = opts.get("default_password")
        
        self.stdout.write(self.style.WARNING("Bắt đầu import dữ liệu vào MySQL..."))
        
        try:
            with transaction.atomic():
                # 1. Import Role
                self.import_roles()
                
                # 2. Import StaffInfo
                self.import_staff(default_pw)
                
                # 3. Import StaffRole
                self.import_staff_roles()
                
                # 4. Import StudentInfo
                self.import_students(default_pw)
                
                # 5. Import Classroom
                self.import_classrooms()
                
                # 6. Import StudentClassDetails
                self.import_student_class_details()
                
                # 7. Import BlogPost
                self.import_blog_posts()
                
            self.stdout.write(self.style.SUCCESS("\n✓ Hoàn thành import tất cả dữ liệu!"))
            self.print_summary()
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"\n✗ Lỗi khi import: {str(e)}"))
            raise

    def import_roles(self):
        """Import Role từ Database/Role.json"""
        file_path = Path("Database/Role.json")
        if not file_path.exists():
            self.stdout.write(self.style.WARNING(f"  Bỏ qua: không tìm thấy {file_path}"))
            return
            
        data = json.loads(file_path.read_text(encoding="utf-8"))
        created = updated = 0
        
        for item in data:
            obj, is_created = Role.objects.update_or_create(
                id=item["id"],
                defaults={"name": item["name"]}
            )
            if is_created:
                created += 1
            else:
                updated += 1
                
        self.stdout.write(f"  Role: {created} tạo mới, {updated} cập nhật")

    def import_staff(self, default_pw):
        """Import StaffInfo từ Database/StaffInfo.json và tạo tài khoản auth_user"""
        file_path = Path("Database/StaffInfo.json")
        if not file_path.exists():
            self.stdout.write(self.style.WARNING(f"  Bỏ qua: không tìm thấy {file_path}"))
            return
            
        data = json.loads(file_path.read_text(encoding="utf-8"))
        User = get_user_model()
        created_staff = updated_staff = 0
        created_users = updated_users = 0
        
        for item in data:
            # Xác định password hash cho StaffInfo
            if default_pw:
                staff_password_hash = make_password(default_pw)
            elif item.get("password"):
                staff_password_hash = item["password"]
            else:
                staff_password_hash = make_password("changeme123")
            
            # Import StaffInfo
            obj, is_created = StaffInfo.objects.update_or_create(
                id_staff=item["id_staff"],
                defaults={
                    "staff_name": item["staff_name"],
                    "email": item["email"],
                    "phone": item["phone"],
                    "address": item["address"],
                    "birthday": item["birthday"],
                    "password": staff_password_hash,
                }
            )
            if is_created:
                created_staff += 1
            else:
                updated_staff += 1
            
            # Tạo tài khoản đăng nhập
            user, ucreated = User.objects.get_or_create(username=item["id_staff"])
            user.email = item["email"]
            if default_pw:
                user.set_password(default_pw)
            elif item.get("password"):
                user.password = item["password"]
            else:
                user.set_password("changeme123")
            user.is_staff = True
            user.is_active = True
            user.save()
            
            if ucreated:
                created_users += 1
            else:
                updated_users += 1
                
        self.stdout.write(
            f"  StaffInfo: {created_staff} tạo mới, {updated_staff} cập nhật | "
            f"Users: {created_users} tạo mới, {updated_users} cập nhật"
        )

    def import_staff_roles(self):
        """Import StaffRole từ Database/StaffRole.json"""
        file_path = Path("Database/StaffRole.json")
        if not file_path.exists():
            self.stdout.write(self.style.WARNING(f"  Bỏ qua: không tìm thấy {file_path}"))
            return
            
        data = json.loads(file_path.read_text(encoding="utf-8"))
        created = updated = 0
        skipped = 0
        
        for item in data:
            try:
                staff = StaffInfo.objects.get(id_staff=item["staff_id"])
                role = Role.objects.get(id=item["role_id"])
                
                obj, is_created = StaffRole.objects.get_or_create(
                    staff=staff,
                    role=role
                )
                if is_created:
                    created += 1
                else:
                    updated += 1
            except (StaffInfo.DoesNotExist, Role.DoesNotExist) as e:
                skipped += 1
                
        msg = f"  StaffRole: {created} tạo mới, {updated} đã tồn tại"
        if skipped > 0:
            msg += f", {skipped} bỏ qua (thiếu FK)"
        self.stdout.write(msg)

    def import_students(self, default_pw):
        """Import StudentInfo từ Database/StudentInfo.json và tạo tài khoản auth_user"""
        file_path = Path("Database/StudentInfo.json")
        if not file_path.exists():
            self.stdout.write(self.style.WARNING(f"  Bỏ qua: không tìm thấy {file_path}"))
            return
            
        data = json.loads(file_path.read_text(encoding="utf-8"))
        User = get_user_model()
        created_students = updated_students = 0
        created_users = updated_users = 0
        
        for item in data:
            # Xác định password hash cho StudentInfo
            if default_pw:
                student_password_hash = make_password(default_pw)
            elif item.get("password"):
                student_password_hash = item["password"]
            else:
                student_password_hash = make_password("changeme123")
            
            # Import StudentInfo
            obj, is_created = StudentInfo.objects.update_or_create(
                id_student=item["id_student"],
                defaults={
                    "student_name": item["student_name"],
                    "email": item["email"],
                    "phone": item["phone"],
                    "address": item["address"],
                    "birthday": item["birthday"],
                    "PathImageFolder": item.get("PathImageFolder", ""),
                    "password": student_password_hash,
                }
            )
            if is_created:
                created_students += 1
            else:
                updated_students += 1
            
            # Tạo tài khoản đăng nhập
            user, ucreated = User.objects.get_or_create(username=item["id_student"])
            user.email = item["email"]
            if default_pw:
                user.set_password(default_pw)
            elif item.get("password"):
                user.password = item["password"]
            else:
                user.set_password("changeme123")
            user.is_active = True
            user.save()
            
            if ucreated:
                created_users += 1
            else:
                updated_users += 1
                
        self.stdout.write(
            f"  StudentInfo: {created_students} tạo mới, {updated_students} cập nhật | "
            f"Users: {created_users} tạo mới, {updated_users} cập nhật"
        )

    def import_classrooms(self):
        """Import Classroom từ Database/Classroom.json"""
        file_path = Path("Database/Classroom.json")
        if not file_path.exists():
            self.stdout.write(self.style.WARNING(f"  Bỏ qua: không tìm thấy {file_path}"))
            return
            
        data = json.loads(file_path.read_text(encoding="utf-8"))
        created = updated = 0
        skipped = 0
        
        for item in data:
            try:
                lecturer = None
                if item.get("id_lecturer_id"):
                    try:
                        lecturer = StaffInfo.objects.get(id_staff=item["id_lecturer_id"])
                    except StaffInfo.DoesNotExist:
                        pass
                
                obj, is_created = Classroom.objects.update_or_create(
                    id_classroom=item["id_classroom"],
                    defaults={
                        "name": item["name"],
                        "begin_date": item["begin_date"],
                        "end_date": item["end_date"],
                        "day_of_week_begin": item["day_of_week_begin"],
                        "begin_time": item["begin_time"],
                        "end_time": item["end_time"],
                        "id_lecturer": lecturer,
                    }
                )
                if is_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                skipped += 1
                
        msg = f"  Classroom: {created} tạo mới, {updated} cập nhật"
        if skipped > 0:
            msg += f", {skipped} bỏ qua"
        self.stdout.write(msg)

    def import_student_class_details(self):
        """Import StudentClassDetails từ Database/StudentClassDetails.json"""
        file_path = Path("Database/StudentClassDetails.json")
        if not file_path.exists():
            self.stdout.write(self.style.WARNING(f"  Bỏ qua: không tìm thấy {file_path}"))
            return
            
        data = json.loads(file_path.read_text(encoding="utf-8"))
        created = updated = 0
        skipped = 0
        
        for item in data:
            try:
                classroom = Classroom.objects.get(id_classroom=item["id_classroom_id"])
                student = StudentInfo.objects.get(id_student=item["id_student_id"])
                
                obj, is_created = StudentClassDetails.objects.get_or_create(
                    id_classroom=classroom,
                    id_student=student
                )
                if is_created:
                    created += 1
                else:
                    updated += 1
            except (Classroom.DoesNotExist, StudentInfo.DoesNotExist) as e:
                skipped += 1
                
        msg = f"  StudentClassDetails: {created} tạo mới, {updated} đã tồn tại"
        if skipped > 0:
            msg += f", {skipped} bỏ qua (thiếu FK)"
        self.stdout.write(msg)

    def import_blog_posts(self):
        """Import BlogPost từ Database/BlogPost.json"""
        file_path = Path("Database/BlogPost.json")
        if not file_path.exists():
            self.stdout.write(self.style.WARNING(f"  Bỏ qua: không tìm thấy {file_path}"))
            return
            
        data = json.loads(file_path.read_text(encoding="utf-8"))
        created = updated = 0
        
        for item in data:
            obj, is_created = BlogPost.objects.update_or_create(
                id=item["id"],
                defaults={
                    "title": item["title"],
                    "body": item["body"],
                    "type": item["type"],
                }
            )
            if is_created:
                created += 1
            else:
                updated += 1
                
        self.stdout.write(f"  BlogPost: {created} tạo mới, {updated} cập nhật")

    def print_summary(self):
        """In tổng kết số lượng bản ghi trong từng bảng"""
        User = get_user_model()
        
        self.stdout.write(self.style.SUCCESS("\n📊 Tổng kết dữ liệu trong MySQL:"))
        self.stdout.write(f"  - auth_user: {User.objects.count()} tài khoản")
        self.stdout.write(f"  - Role: {Role.objects.count()} vai trò")
        self.stdout.write(f"  - StaffInfo: {StaffInfo.objects.count()} nhân viên")
        self.stdout.write(f"  - StaffRole: {StaffRole.objects.count()} phân quyền")
        self.stdout.write(f"  - StudentInfo: {StudentInfo.objects.count()} sinh viên")
        self.stdout.write(f"  - Classroom: {Classroom.objects.count()} lớp học")
        self.stdout.write(f"  - StudentClassDetails: {StudentClassDetails.objects.count()} ghi danh")
        self.stdout.write(f"  - BlogPost: {BlogPost.objects.count()} bài viết")
