"""
Script tự động tạo folder cho sinh viên chưa có ảnh
"""

import os
import json

FACE_DATA_DIR = 'main/Dataset/FaceData'
STUDENT_DB_FILE = 'Database/StudentInfo.json'

def create_student_folders():
    print("=" * 70)
    print("📂 TẠO FOLDER CHO SINH VIÊN")
    print("=" * 70)
    
    # Kiểm tra FaceData
    if not os.path.exists(FACE_DATA_DIR):
        os.makedirs(FACE_DATA_DIR)
        print(f"✓ Đã tạo thư mục: {FACE_DATA_DIR}")
    
    # Đọc database
    if not os.path.exists(STUDENT_DB_FILE):
        print(f"❌ Không tìm thấy file: {STUDENT_DB_FILE}")
        return
    
    with open(STUDENT_DB_FILE, 'r', encoding='utf-8') as f:
        students = json.load(f)
    
    print(f"\n📊 Tổng số sinh viên trong DB: {len(students)}\n")
    
    # Lấy danh sách folder hiện có
    existing_folders = set()
    if os.path.exists(FACE_DATA_DIR):
        existing_folders = {f for f in os.listdir(FACE_DATA_DIR) 
                          if os.path.isdir(os.path.join(FACE_DATA_DIR, f))}
    
    print(f"Folder hiện có: {len(existing_folders)}\n")
    
    # Tạo folder cho sinh viên chưa có
    created = 0
    skipped = 0
    
    for student in students:
        student_id = student['id_student'].strip()
        folder_path = os.path.join(FACE_DATA_DIR, student_id)
        
        if student_id in existing_folders:
            print(f"⏭️  Bỏ qua: {student_id:15} - {student['student_name']:30} (đã tồn tại)")
            skipped += 1
        else:
            try:
                os.makedirs(folder_path)
                print(f"✅ Tạo mới: {student_id:15} - {student['student_name']:30}")
                created += 1
            except Exception as e:
                print(f"❌ Lỗi:    {student_id:15} - {student['student_name']:30} ({e})")
    
    # Tổng kết
    print("\n" + "=" * 70)
    print("📊 TỔNG KẾT")
    print("=" * 70)
    print(f"   ✅ Đã tạo mới: {created} folder")
    print(f"   ⏭️  Đã tồn tại: {skipped} folder")
    print(f"   📂 Tổng cộng: {created + skipped} folder")
    
    if created > 0:
        print("\n" + "=" * 70)
        print("📸 BƯỚC TIẾP THEO")
        print("=" * 70)
        print("   1. Thêm ảnh vào các folder vừa tạo")
        print("      - Mỗi folder cần 20-30 ảnh")
        print("      - Ảnh rõ nét, khuôn mặt chiếm 60-70% khung hình")
        print("      - Nhiều góc độ, biểu cảm khác nhau")
        print()
        print("   2. Kiểm tra folder:")
        print("      python check_face_folders.py")
        print()
        print("   3. Train model:")
        print("      python train_face_model.py")
        print()
        print("📖 Xem chi tiết: SETUP_FACE_RECOGNITION.md")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    create_student_folders()
