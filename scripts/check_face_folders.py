"""
Script kiểm tra tên folder trong FaceData (không cần database)
Chỉ kiểm tra cấu trúc folder và đưa ra gợi ý
"""

import os
import re
import json

FACE_DATA_DIR = 'main/Dataset/FaceData'
STUDENT_DB_FILE = 'Database/StudentInfo.json'

def normalize_student_id(student_id):
    """Chuẩn hóa mã sinh viên"""
    if not student_id:
        return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(student_id)).strip().upper()

def check_face_data_folders():
    """Kiểm tra thư mục FaceData"""
    
    print("=" * 70)
    print("🔍 KIỂM TRA THƯ MỤC FACE DATA")
    print("=" * 70)
    
    # Kiểm tra FaceData
    if not os.path.exists(FACE_DATA_DIR):
        print(f"❌ Thư mục {FACE_DATA_DIR} không tồn tại!")
        return
    
    # Lấy danh sách folder
    folders = []
    for item in os.listdir(FACE_DATA_DIR):
        full_path = os.path.join(FACE_DATA_DIR, item)
        if os.path.isdir(full_path):
            # Đếm số ảnh
            num_images = len([f for f in os.listdir(full_path)
                            if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            folders.append({
                'name': item,
                'normalized': normalize_student_id(item),
                'num_images': num_images
            })
    
    print(f"\n📊 Tổng số folder: {len(folders)}")
    
    # Phân loại folder
    valid = []
    suspicious = []
    empty = []
    
    for folder in folders:
        if folder['num_images'] == 0:
            empty.append(folder)
        elif len(folder['normalized']) < 5 or not folder['normalized'].isdigit():
            suspicious.append(folder)
        else:
            valid.append(folder)
    
    # Hiển thị folder hợp lệ
    if valid:
        print("\n" + "=" * 70)
        print(f"✅ FOLDER HỢP LỆ ({len(valid)})")
        print("=" * 70)
        
        for folder in sorted(valid, key=lambda x: x['name'])[:20]:
            status = "✓" if folder['name'] == folder['normalized'] else "⚠"
            print(f"   {status} {folder['name']:20} → {folder['normalized']:15} ({folder['num_images']:3} ảnh)")
        
        if len(valid) > 20:
            print(f"   ... và {len(valid) - 20} folder khác")
    
    # Hiển thị folder cần sửa
    if suspicious:
        print("\n" + "=" * 70)
        print(f"⚠️  FOLDER CẦN KIỂM TRA ({len(suspicious)})")
        print("=" * 70)
        print("   Tên folder có thể không đúng định dạng MSSV:")
        print()
        
        for folder in suspicious:
            print(f"   ❌ {folder['name']:20} → normalized: {folder['normalized']:15} ({folder['num_images']} ảnh)")
            
            if not folder['normalized'].isdigit():
                print(f"      💡 Lưu ý: Chứa ký tự không phải số")
            if len(folder['normalized']) < 5:
                print(f"      💡 Lưu ý: Quá ngắn (MSSV thường 10 số)")
            print()
    
    # Hiển thị folder rỗng
    if empty:
        print("\n" + "=" * 70)
        print(f"📭 FOLDER RỖNG ({len(empty)})")
        print("=" * 70)
        print("   Các folder không có ảnh (nên xóa):")
        print()
        
        for folder in empty:
            print(f"   📂 {folder['name']}")
    
    # Kiểm tra database nếu có
    db_students = []
    if os.path.exists(STUDENT_DB_FILE):
        print("\n" + "=" * 70)
        print("🗄️  KIỂM TRA VỚI DATABASE")
        print("=" * 70)
        
        try:
            with open(STUDENT_DB_FILE, 'r', encoding='utf-8') as f:
                db_students = json.load(f)
            
            print(f"   Số sinh viên trong DB: {len(db_students)}")
            
            # Tìm folder trong DB
            db_ids = {normalize_student_id(s['id_student']): s 
                     for s in db_students}
            
            matched = []
            not_in_db = []
            
            for folder in folders:
                if folder['normalized'] in db_ids:
                    student = db_ids[folder['normalized']]
                    matched.append({
                        'folder': folder['name'],
                        'mssv': student['id_student'],
                        'name': student['student_name'],
                        'images': folder['num_images']
                    })
                else:
                    not_in_db.append(folder)
            
            print(f"   Folder khớp với DB: {len(matched)}")
            print(f"   Folder KHÔNG có trong DB: {len(not_in_db)}")
            
            if not_in_db:
                print("\n   ⚠️  Folder không tìm thấy trong DB:")
                for folder in not_in_db[:10]:
                    print(f"      - {folder['name']} (normalized: {folder['normalized']})")
                if len(not_in_db) > 10:
                    print(f"      ... và {len(not_in_db) - 10} folder khác")
            
            # Tìm sinh viên chưa có ảnh
            missing = []
            folder_ids = {f['normalized'] for f in folders}
            for db_id, student in db_ids.items():
                if db_id not in folder_ids:
                    missing.append(student)
            
            if missing:
                print(f"\n   📸 Sinh viên chưa có ảnh: {len(missing)}")
                for student in missing[:10]:
                    print(f"      - {student['id_student']} - {student['student_name']}")
                if len(missing) > 10:
                    print(f"      ... và {len(missing) - 10} sinh viên khác")
        
        except Exception as e:
            print(f"   ❌ Lỗi đọc database: {e}")
    
    # Tổng kết
    print("\n" + "=" * 70)
    print("📊 TỔNG KẾT")
    print("=" * 70)
    print(f"   ✅ Folder hợp lệ: {len(valid)}")
    print(f"   ⚠️  Cần kiểm tra: {len(suspicious)}")
    print(f"   📭 Folder rỗng: {len(empty)}")
    
    total_images = sum(f['num_images'] for f in folders)
    print(f"   📷 Tổng số ảnh: {total_images}")
    
    if total_images > 0:
        avg_images = total_images / len([f for f in folders if f['num_images'] > 0])
        print(f"   📈 Trung bình: {avg_images:.1f} ảnh/người")
    
    # Gợi ý
    print("\n" + "=" * 70)
    print("💡 GỢI Ý")
    print("=" * 70)
    
    if empty:
        print("   1. Xóa folder rỗng:")
        for folder in empty[:3]:
            print(f"      rd /s /q \"{os.path.join(FACE_DATA_DIR, folder['name'])}\"")
    
    if suspicious:
        print("\n   2. Kiểm tra folder nghi ngờ:")
        print("      - Đảm bảo tên folder = MSSV chính xác")
        print("      - Không có khoảng trắng, ký tự đặc biệt")
        print("      - Ví dụ: 2011003929, 2011003930,...")
    
    if valid:
        print("\n   3. Chuẩn bị train model:")
        print("      - Đảm bảo mỗi folder có ít nhất 20-30 ảnh")
        print("      - Ảnh cần rõ nét, nhìn thẳng camera")
        print("      - Chạy: python train_face_model.py")
    
    print("\n" + "=" * 70)
    
    # Tạo báo cáo
    report_file = 'face_data_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("BÁO CÁO KIỂM TRA FACE DATA\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Tổng số folder: {len(folders)}\n")
        f.write(f"Folder hợp lệ: {len(valid)}\n")
        f.write(f"Cần kiểm tra: {len(suspicious)}\n")
        f.write(f"Folder rỗng: {len(empty)}\n\n")
        
        f.write("DANH SÁCH CHI TIẾT:\n\n")
        
        for folder in sorted(folders, key=lambda x: x['name']):
            status = "OK" if folder in valid else "WARN" if folder in suspicious else "EMPTY"
            f.write(f"[{status}] {folder['name']:20} → {folder['normalized']:15} ({folder['num_images']} ảnh)\n")
    
    print(f"\n✅ Đã tạo báo cáo: {report_file}")

if __name__ == '__main__':
    check_face_data_folders()
