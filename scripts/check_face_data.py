"""
Script kiểm tra và sửa lỗi tên thư mục trong FaceData
Đảm bảo tên folder khớp chính xác với MSSV trong database
"""

import os
import sys
import django

# Setup Django
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceByAttendance.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Lỗi kết nối Django/Database: {e}")
    print("\n💡 Kiểm tra:")
    print("   1. MySQL server đang chạy")
    print("   2. Mật khẩu trong FaceByAttendance/settings.py")
    print("   3. Database 'attendance_by_face' tồn tại")
    sys.exit(1)

from main.models import StudentInfo
import re

FACE_DATA_DIR = 'main/Dataset/FaceData'

def normalize_student_id(student_id):
    """Chuẩn hóa mã sinh viên"""
    if not student_id:
        return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(student_id)).strip().upper()

def check_face_data_folders():
    """Kiểm tra thư mục FaceData và tìm lỗi"""
    
    print("=" * 70)
    print("🔍 KIỂM TRA THƯ MỤC FACE DATA")
    print("=" * 70)
    
    if not os.path.exists(FACE_DATA_DIR):
        print(f"❌ Thư mục {FACE_DATA_DIR} không tồn tại!")
        return
    
    # Lấy danh sách sinh viên từ DB
    all_students = StudentInfo.objects.all()
    db_student_ids = {normalize_student_id(s.id_student): s for s in all_students}
    
    print(f"\n📊 Tổng quan:")
    print(f"   - Số sinh viên trong DB: {len(db_student_ids)}")
    
    # Lấy danh sách folder
    folders = [f for f in os.listdir(FACE_DATA_DIR) 
              if os.path.isdir(os.path.join(FACE_DATA_DIR, f))]
    
    print(f"   - Số folder trong FaceData: {len(folders)}")
    
    # Phân tích
    matched = []
    mismatched = []
    unknown = []
    
    for folder in folders:
        normalized = normalize_student_id(folder)
        
        if normalized in db_student_ids:
            student = db_student_ids[normalized]
            matched.append({
                'folder': folder,
                'student': student,
                'match': 'exact' if folder == student.id_student else 'normalized'
            })
        else:
            # Tìm gần đúng
            found = False
            for db_id, student in db_student_ids.items():
                if normalized in db_id or db_id in normalized:
                    mismatched.append({
                        'folder': folder,
                        'normalized': normalized,
                        'student': student,
                        'suggestion': student.id_student
                    })
                    found = True
                    break
            
            if not found:
                unknown.append({
                    'folder': folder,
                    'normalized': normalized
                })
    
    # Hiển thị kết quả
    print("\n" + "=" * 70)
    print("✅ KHỚP CHÍNH XÁC ({} folder)".format(len(matched)))
    print("=" * 70)
    
    for item in matched[:10]:  # Chỉ hiện 10 đầu
        status = "✓" if item['match'] == 'exact' else "⚠"
        print(f"   {status} {item['folder']:15} → {item['student'].id_student:12} - {item['student'].student_name}")
    
    if len(matched) > 10:
        print(f"   ... và {len(matched) - 10} folder khác")
    
    if mismatched:
        print("\n" + "=" * 70)
        print("⚠️  CẦN SỬA ({} folder)".format(len(mismatched)))
        print("=" * 70)
        print("   Tên folder không khớp chính xác với MSSV trong DB:")
        print()
        
        for item in mismatched:
            print(f"   ❌ Folder: {item['folder']}")
            print(f"      Normalized: {item['normalized']}")
            print(f"      Nên đổi thành: {item['suggestion']} ({item['student'].student_name})")
            print()
    
    if unknown:
        print("\n" + "=" * 70)
        print("❓ KHÔNG TÌM THẤY TRONG DB ({} folder)".format(len(unknown)))
        print("=" * 70)
        print("   Các folder này không khớp với bất kỳ sinh viên nào:")
        print()
        
        for item in unknown:
            num_images = len([f for f in os.listdir(os.path.join(FACE_DATA_DIR, item['folder']))
                            if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            print(f"   ❌ {item['folder']:15} (normalized: {item['normalized']}) - {num_images} ảnh")
        
        print("\n   💡 Gợi ý:")
        print("      - Kiểm tra xem MSSV có đúng không")
        print("      - Xóa folder nếu không cần")
        print("      - Đổi tên folder thành MSSV chính xác")
    
    # Sinh viên chưa có ảnh
    missing = []
    for db_id, student in db_student_ids.items():
        has_folder = any(normalize_student_id(f) == db_id for f in folders)
        if not has_folder:
            missing.append(student)
    
    if missing:
        print("\n" + "=" * 70)
        print("📸 SINH VIÊN CHƯA CÓ ẢNH ({} người)".format(len(missing)))
        print("=" * 70)
        print("   Cần thêm ảnh cho các sinh viên sau:")
        print()
        
        for student in missing[:20]:  # Chỉ hiện 20 đầu
            print(f"   📷 {student.id_student:12} - {student.student_name}")
        
        if len(missing) > 20:
            print(f"   ... và {len(missing) - 20} sinh viên khác")
    
    # Tổng kết
    print("\n" + "=" * 70)
    print("📊 TỔNG KẾT")
    print("=" * 70)
    print(f"   ✅ Khớp chính xác: {len(matched)} folder")
    print(f"   ⚠️  Cần sửa: {len(mismatched)} folder")
    print(f"   ❌ Không tìm thấy: {len(unknown)} folder")
    print(f"   📷 Chưa có ảnh: {len(missing)} sinh viên")
    print()
    
    # Gợi ý hành động
    if mismatched or unknown or missing:
        print("🔧 HÀNH ĐỘNG ĐỀ XUẤT:")
        print()
        
        if mismatched:
            print("   1. Đổi tên folder để khớp chính xác với MSSV:")
            for item in mismatched[:3]:
                old_path = os.path.join(FACE_DATA_DIR, item['folder'])
                new_path = os.path.join(FACE_DATA_DIR, item['suggestion'])
                print(f"      ren \"{old_path}\" \"{item['suggestion']}\"")
        
        if unknown:
            print("\n   2. Xóa hoặc đổi tên folder không hợp lệ:")
            for item in unknown[:3]:
                path = os.path.join(FACE_DATA_DIR, item['folder'])
                print(f"      rd /s /q \"{path}\"")
        
        if missing:
            print(f"\n   3. Thêm ảnh cho {len(missing)} sinh viên chưa có ảnh")
            print(f"      Chạy: python capture_student_faces.py")
        
        print("\n   4. Sau khi sửa xong, train lại model:")
        print("      python train_face_model.py")
    else:
        print("✅ TẤT CẢ ĐỀU OK! Có thể train model ngay:")
        print("   python train_face_model.py")
    
    print("\n" + "=" * 70)

def auto_fix_folders():
    """Tự động sửa tên folder"""
    print("\n🔧 TỰ ĐỘNG SỬA TÊN FOLDER")
    print("=" * 70)
    
    choice = input("Bạn có muốn tự động đổi tên folder? (y/n): ")
    if choice.lower() != 'y':
        print("Hủy bỏ.")
        return
    
    if not os.path.exists(FACE_DATA_DIR):
        print(f"❌ Thư mục {FACE_DATA_DIR} không tồn tại!")
        return
    
    all_students = StudentInfo.objects.all()
    db_student_ids = {normalize_student_id(s.id_student): s for s in all_students}
    
    folders = [f for f in os.listdir(FACE_DATA_DIR) 
              if os.path.isdir(os.path.join(FACE_DATA_DIR, f))]
    
    fixed = 0
    for folder in folders:
        normalized = normalize_student_id(folder)
        
        if normalized in db_student_ids:
            student = db_student_ids[normalized]
            correct_name = student.id_student
            
            if folder != correct_name:
                old_path = os.path.join(FACE_DATA_DIR, folder)
                new_path = os.path.join(FACE_DATA_DIR, correct_name)
                
                try:
                    os.rename(old_path, new_path)
                    print(f"✓ Đã đổi: '{folder}' → '{correct_name}'")
                    fixed += 1
                except Exception as e:
                    print(f"✗ Lỗi khi đổi '{folder}': {e}")
    
    print(f"\n✅ Đã sửa {fixed} folder")
    print("🔄 Chạy lại script để kiểm tra:")
    print("   python check_face_data.py")

if __name__ == '__main__':
    check_face_data_folders()
    
    if '--fix' in sys.argv:
        auto_fix_folders()
