# PHÂN TÍCH VÀ CẢI THIỆN HỆ THỐNG ĐIỂM DANH

## 1. PHÂN TÍCH HIỆN TRẠNG

### 1.1. Luồng hoạt động hiện tại

#### **Giảng viên điểm danh:**
1. Giảng viên đăng nhập → Dashboard
2. Chọn "Điểm danh" → Xem danh sách lớp trong tuần
3. **Chỉ điểm danh được vào đúng ngày học** (kiểm tra `day_of_week_begin`)
4. Hai phương thức:
   - **Thủ công**: Chọn dropdown trạng thái cho từng sinh viên
   - **Khuôn mặt**: Dùng webcam nhận diện + Anti-spoofing

#### **Sinh viên xem điểm danh:**
1. Sinh viên đăng nhập → Dashboard
2. Xem lịch học, điểm chuyên cần, lịch sử điểm danh
3. **CHỈ XEM**, không thể tự điểm danh

### 1.2. Cấu trúc database

```
StaffInfo (Giảng viên)
├── id_staff (PK)
├── staff_name, email, phone, address, birthday
└── roles (ManyToMany qua StaffRole)

StudentInfo (Sinh viên)  
├── id_student (PK)
├── student_name, email, phone, birthday
└── PathImageFolder (thư mục ảnh khuôn mặt)

Classroom (Lớp học)
├── id_classroom (PK)
├── name, begin_date, end_date
├── day_of_week_begin (1-7: Thứ 2 - CN)
├── begin_time, end_time
├── id_lecturer (FK → StaffInfo)
└── students (ManyToMany qua StudentClassDetails)

Attendance (Bảng điểm danh)
├── id_attendance (PK)
├── check_in_time (DateTime)
├── attendance_status (1=Vắng, 2=Có mặt, 3=Muộn)
├── id_classroom (FK)
└── id_student (FK)
```

## 2. VẤN ĐỀ PHÁT HIỆN

### 2.1. ⚠️ Logic nghiệp vụ không rõ ràng

#### **Vấn đề 1: Cơ chế tạo bản ghi điểm danh**
**File:** `main/view/reg.py` - Hàm `insert_attendance()` (Dòng 32-65)

```python
# LOGIC SAI: Tạo attendance cho TẤT CẢ sinh viên với status=1 (Vắng)
for student in students_in_class:
    attendance, created = Attendance.objects.get_or_create(
        id_student=student,
        id_classroom=classroom,
        check_in_time__date=datetime.now(),
        defaults={
            'check_in_time': datetime.now(),
            'attendance_status': 1,  # ❌ Mặc định tất cả là VẮNG
        })
```

**❌ VẤN ĐỀ:**
- Mỗi khi **1 sinh viên** điểm danh bằng khuôn mặt → tạo bản ghi "Vắng" cho **TẤT CẢ** sinh viên khác
- Không phù hợp với logic thực tế
- Gây dư thừa dữ liệu

**✅ GIẢI PHÁP:**
- Nên tách riêng việc "Khởi tạo bản ghi" và "Cập nhật trạng thái"
- Giảng viên nên **bắt đầu buổi điểm danh** → Hệ thống tự tạo bản ghi Vắng cho tất cả
- Khi sinh viên điểm danh → Cập nhật trạng thái

---

#### **Vấn đề 2: Logic xác định muộn**
**File:** `main/view/reg.py` - Dòng 38-42

```python
time_difference = (datetime.combine(datetime.now(), current_time.time())
                   - datetime.combine(datetime.now(), begin_time))

if time_difference.total_seconds() > 900:  # 15 phút
    attendance_status = 3  # Muộn
else:
    attendance_status = 2  # Đúng giờ
```

**✅ Logic này ĐÚNG**, nhưng:
- Chỉ áp dụng khi điểm danh bằng **khuôn mặt** (tự động)
- Khi giảng viên điểm danh **thủ công** → Giảng viên tự chọn → Có thể không nhất quán

**✅ ĐỀ XUẤT:**
- Áp dụng logic tự động này cho CẢ 2 phương thức
- Thêm trường `check_in_method` (Manual/Face) để theo dõi

---

#### **Vấn đề 3: Tính điểm chuyên cần hardcode**
**File:** `main/view/lecturer_views.py` - Dòng 353

```python
# ❌ HARDCODE: Chia cho 9 buổi (không linh hoạt)
total_attendance_percentage = round((((absent_count * 0) + (late_count * 0.5) + present_count) / 9) * 3, 2)
```

**❌ VẤN ĐỀ:**
- Giả định cố định **9 buổi học**
- Nếu lớp có 10, 12, 15 buổi → Sai hoàn toàn
- Sinh viên nghỉ > 2 buổi → "Nghỉ quá quy định" (hardcode)

**✅ GIẢI PHÁP:**
```python
# Tính tổng số buổi học dự kiến dựa trên begin_date, end_date, day_of_week
total_expected_sessions = calculate_total_sessions(classroom)
total_attendance_percentage = round((((absent_count * 0) + (late_count * 0.5) + present_count) / total_expected_sessions) * 3, 2)
```

---

#### **Vấn đề 4: Quy trình điểm danh chưa đồng bộ**

**Điểm danh thủ công** (`lecturer_mark_attendance`):
```python
# ✅ Giảng viên chọn trạng thái cho từng SV
for student in students_in_class:
    attendance_status = request.POST.get(f'attendance_status_{student_id.id_student}')
    attendance, created = Attendance.objects.get_or_create(...)
```

**Điểm danh bằng khuôn mặt** (`insert_attendance` trong reg.py):
```python
# ⚠️ Tự động tạo "Vắng" cho tất cả → Cập nhật "Có mặt" cho người nhận diện được
for student in students_in_class:
    attendance, created = Attendance.objects.get_or_create(..., defaults={'attendance_status': 1})
# Sau đó cập nhật cho sinh viên được nhận diện
attendance.attendance_status = attendance_status
```

**❌ VẤN ĐỀ:**
- Hai phương thức hoạt động **KHÁC NHAU**
- Phương thức khuôn mặt tạo bản ghi "Vắng" cho tất cả → Không cần thiết
- Không có cơ chế "Kết thúc buổi điểm danh"

---

### 2.2. ⚠️ Thiếu tính năng quan trọng

#### **1. Không có quản lý "Buổi học" (Session)**
- Hiện tại chỉ dựa vào `check_in_time__date` để phân biệt buổi học
- Nếu 1 lớp học **2 buổi trong 1 ngày** → Không phân biệt được
- Không có cơ chế "Mở điểm danh" / "Đóng điểm danh"

**✅ ĐỀ XUẤT: Tạo model `ClassSession`**
```python
class ClassSession(models.Model):
    id_session = models.BigAutoField(primary_key=True)
    id_classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    session_date = models.DateField()  # Ngày học
    session_number = models.IntegerField()  # Buổi thứ mấy (1, 2, 3...)
    status = models.CharField(max_length=20)  # PENDING, OPEN, CLOSED
    opened_at = models.DateTimeField(null=True)  # Giảng viên mở lúc nào
    closed_at = models.DateTimeField(null=True)  # Đóng lúc nào
    opened_by = models.ForeignKey(StaffInfo, on_delete=models.SET_NULL, null=True)
```

**Lợi ích:**
- Giảng viên **Mở buổi điểm danh** → Hệ thống tạo bản ghi "Vắng" cho tất cả SV
- Sinh viên chỉ điểm danh được khi session **OPEN**
- **Đóng buổi điểm danh** → Không thể sửa đổi nữa

---

#### **2. Không có báo cáo thống kê tổng quan**
- Thiếu dashboard thống kê tỷ lệ điểm danh theo lớp, theo tuần
- Không có biểu đồ xu hướng vắng/muộn
- Không có cảnh báo sinh viên vắng nhiều

---

#### **3. Không có log/audit trail**
- Không biết ai sửa đổi điểm danh lúc nào
- Không theo dõi được lịch sử thay đổi
- Không có cơ chế khiếu nại/điều chỉnh

---

## 3. ĐỀ XUẤT CẢI THIỆN

### 3.1. Tái cấu trúc luồng điểm danh

#### **Luồng MỚI đề xuất:**

```
[GIẢNG VIÊN]
1. Mở buổi học → Click "Bắt đầu điểm danh"
   ↓
2. Hệ thống tạo ClassSession (status=OPEN)
   ↓
3. Tạo bản ghi Attendance cho TẤT CẢ sinh viên (status=VẮNG)
   ↓
4. Giảng viên chọn phương thức:
   ├─→ [THỦ CÔNG] Chọn dropdown từng sinh viên
   └─→ [KHUÔN MẶT] Bật webcam, nhận diện
       ↓
5. Cập nhật trạng thái (Có mặt/Muộn) dựa trên thời gian check-in
   ↓
6. Kết thúc buổi học → Click "Đóng điểm danh"
   ↓
7. ClassSession (status=CLOSED) → Không sửa được nữa

[SINH VIÊN]
- Xem lịch sử điểm danh theo buổi
- Xem điểm chuyên cần tự động tính
- (Tùy chọn) Khiếu nại nếu sai
```

---

### 3.2. Cải tiến code cụ thể

#### **File 1: `main/models.py` - Thêm model ClassSession**

```python
class ClassSession(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Chưa bắt đầu'),
        ('OPEN', 'Đang điểm danh'),
        ('CLOSED', 'Đã kết thúc'),
    ]
    
    id_session = models.BigAutoField(primary_key=True)
    id_classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='sessions')
    session_date = models.DateField()
    session_number = models.IntegerField()  # Buổi 1, 2, 3...
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    opened_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    opened_by = models.ForeignKey(StaffInfo, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['id_classroom', 'session_date', 'session_number']
    
    def __str__(self):
        return f"{self.id_classroom.name} - Buổi {self.session_number} - {self.session_date}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        (1, 'Vắng'),
        (2, 'Có mặt'),
        (3, 'Muộn'),
    ]
    
    METHOD_CHOICES = [
        ('MANUAL', 'Thủ công'),
        ('FACE', 'Nhận diện khuôn mặt'),
    ]
    
    id_attendance = models.BigAutoField(primary_key=True)
    id_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='attendances')  # ← THAY ĐỔI
    id_student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField()
    attendance_status = models.IntegerField(choices=STATUS_CHOICES)
    check_in_method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='MANUAL')  # ← MỚI
    modified_at = models.DateTimeField(auto_now=True)  # ← MỚI: Tracking thay đổi
    modified_by = models.ForeignKey(StaffInfo, on_delete=models.SET_NULL, null=True, blank=True)  # ← MỚI
    
    class Meta:
        unique_together = ['id_session', 'id_student']
```

---

#### **File 2: `main/view/lecturer_views.py` - Thêm quản lý session**

```python
@lecturer_required
def lecturer_start_session(request, classroom_id):
    """Bắt đầu buổi điểm danh - Tạo session và bản ghi Vắng cho tất cả SV"""
    classroom = Classroom.objects.get(pk=classroom_id)
    today = date.today()
    
    # Kiểm tra đã có session hôm nay chưa
    existing_session = ClassSession.objects.filter(
        id_classroom=classroom,
        session_date=today
    ).first()
    
    if existing_session:
        if existing_session.status == 'CLOSED':
            messages.error(request, 'Buổi học hôm nay đã đóng, không thể điểm danh lại!')
            return redirect('lecturer_attendance')
        else:
            # Session đã mở rồi, chuyển đến trang điểm danh
            return redirect('lecturer_mark_attendance_session', session_id=existing_session.id_session)
    
    # Tính số buổi (session_number)
    session_count = ClassSession.objects.filter(id_classroom=classroom).count()
    
    # Tạo session mới
    session = ClassSession.objects.create(
        id_classroom=classroom,
        session_date=today,
        session_number=session_count + 1,
        status='OPEN',
        opened_at=datetime.now(),
        opened_by_id=request.session.get('id_staff')
    )
    
    # Tạo bản ghi VẮNG cho tất cả sinh viên
    students_in_class = StudentClassDetails.objects.filter(id_classroom=classroom)
    for student_detail in students_in_class:
        Attendance.objects.create(
            id_session=session,
            id_student=student_detail.id_student,
            check_in_time=datetime.now(),
            attendance_status=1,  # Vắng
            check_in_method='MANUAL'
        )
    
    messages.success(request, f'Đã mở buổi điểm danh #{session.session_number}')
    return redirect('lecturer_mark_attendance_session', session_id=session.id_session)


@lecturer_required
def lecturer_mark_attendance_session(request, session_id):
    """Điểm danh thủ công theo session"""
    session = ClassSession.objects.get(pk=session_id)
    
    if session.status != 'OPEN':
        messages.error(request, 'Buổi điểm danh đã đóng!')
        return redirect('lecturer_attendance')
    
    attendances = Attendance.objects.filter(id_session=session).select_related('id_student')
    
    if request.method == 'POST':
        for attendance in attendances:
            new_status = request.POST.get(f'attendance_status_{attendance.id_student.id_student}')
            if new_status and int(new_status) != attendance.attendance_status:
                attendance.attendance_status = int(new_status)
                attendance.check_in_time = datetime.now()
                attendance.modified_by_id = request.session.get('id_staff')
                attendance.save()
        
        messages.success(request, 'Cập nhật điểm danh thành công!')
        return redirect('lecturer_mark_attendance_session', session_id=session_id)
    
    context = {
        'session': session,
        'classroom': session.id_classroom,
        'attendances': attendances,
    }
    return render(request, 'lecturer/lecturer_mark_attendance_session.html', context)


@lecturer_required
def lecturer_close_session(request, session_id):
    """Đóng buổi điểm danh - Không sửa được nữa"""
    session = ClassSession.objects.get(pk=session_id)
    
    if session.status != 'OPEN':
        messages.error(request, 'Buổi điểm danh không ở trạng thái mở!')
        return redirect('lecturer_attendance')
    
    session.status = 'CLOSED'
    session.closed_at = datetime.now()
    session.save()
    
    messages.success(request, f'Đã đóng buổi điểm danh #{session.session_number}')
    return redirect('lecturer_attendance')
```

---

#### **File 3: `main/view/reg.py` - Sửa hàm insert_attendance**

```python
def insert_attendance(session_id, student_id):
    """
    Cập nhật điểm danh khi nhận diện khuôn mặt thành công
    """
    session = ClassSession.objects.get(pk=session_id)
    
    if session.status != 'OPEN':
        return "ERROR: Buổi điểm danh đã đóng"
    
    classroom = session.id_classroom
    current_time = datetime.now()
    begin_time = classroom.begin_time
    
    # Tính toán trạng thái (Muộn nếu > 15 phút)
    time_difference = (datetime.combine(datetime.now(), current_time.time())
                       - datetime.combine(datetime.now(), begin_time))
    
    if time_difference.total_seconds() > 900:  # 15 phút
        attendance_status = 3  # Muộn
    else:
        attendance_status = 2  # Đúng giờ
    
    # Cập nhật bản ghi đã có (đã tạo sẵn khi mở session)
    try:
        attendance = Attendance.objects.get(
            id_session=session,
            id_student_id=student_id
        )
        
        # Chỉ cập nhật nếu chưa điểm danh (status = 1 Vắng)
        if attendance.attendance_status == 1:
            attendance.attendance_status = attendance_status
            attendance.check_in_time = current_time
            attendance.check_in_method = 'FACE'
            attendance.save()
            return f"SUCCESS: {student_id} - {'Đúng giờ' if attendance_status == 2 else 'Muộn'}"
        else:
            return f"INFO: {student_id} đã điểm danh rồi"
            
    except Attendance.DoesNotExist:
        return f"ERROR: Sinh viên {student_id} không có trong lớp này"
```

---

#### **File 4: Tính điểm chuyên cần động**

```python
def calculate_total_sessions(classroom):
    """
    Tính tổng số buổi học dự kiến dựa trên:
    - begin_date, end_date
    - day_of_week_begin
    """
    total_weeks = (classroom.end_date - classroom.begin_date).days // 7
    return total_weeks  # Mỗi tuần 1 buổi


@lecturer_required
def lecturer_calculate_attendance_points_view(request, classroom_id):
    classroom = Classroom.objects.get(pk=classroom_id)
    students_in_class = StudentClassDetails.objects.filter(id_classroom=classroom)
    
    # Tính tổng số buổi học dự kiến
    total_expected_sessions = ClassSession.objects.filter(
        id_classroom=classroom,
        status='CLOSED'
    ).count()
    
    if total_expected_sessions == 0:
        messages.warning(request, 'Chưa có buổi học nào được ghi nhận!')
        total_expected_sessions = 1  # Tránh chia 0
    
    student_attendance_counts = []
    for student in students_in_class:
        absent_count = Attendance.objects.filter(
            id_session__id_classroom=classroom,
            id_student=student.id_student,
            attendance_status=1
        ).count()
        
        present_count = Attendance.objects.filter(
            id_session__id_classroom=classroom,
            id_student=student.id_student,
            attendance_status=2
        ).count()
        
        late_count = Attendance.objects.filter(
            id_session__id_classroom=classroom,
            id_student=student.id_student,
            attendance_status=3
        ).count()
        
        total_number_attendance = absent_count + late_count + present_count
        total_attendance_present = late_count + present_count
        
        # Tính điểm động dựa trên số buổi thực tế
        total_attendance_percentage = round(
            (((absent_count * 0) + (late_count * 0.5) + present_count) / total_expected_sessions) * 3,
            2
        )
        
        # Quy định vắng tối đa 20%
        max_allowed_absence = int(total_expected_sessions * 0.2)
        is_over_limit = absent_count > max_allowed_absence
        
        student_attendance_counts.append({
            'student': student,
            'absent_count': absent_count,
            'late_count': late_count,
            'present_count': present_count,
            'total_number_attendance': total_number_attendance,
            'total_attendance_present': total_attendance_present,
            'total_attendance_percentage': total_attendance_percentage,
            'total_expected_sessions': total_expected_sessions,
            'is_over_limit': is_over_limit,
        })
    
    context = {
        'students_in_class': student_attendance_counts,
        'classroom': classroom,
    }
    
    return render(request, 'lecturer/lecturer_calculate_attendance_points.html', context)
```

---

## 4. KẾ HOẠCH TRIỂN KHAI

### Giai đoạn 1: Tái cấu trúc cơ bản (1-2 tuần)
- [x] Tạo model `ClassSession`
- [ ] Migration database (cẩn thận với dữ liệu cũ!)
- [ ] Sửa views: Thêm start/close session
- [ ] Cập nhật templates: UI mở/đóng buổi học

### Giai đoạn 2: Cải thiện logic (1 tuần)
- [ ] Sửa `insert_attendance()` trong `reg.py`
- [ ] Tính điểm động thay vì hardcode /9
- [ ] Thêm tracking `check_in_method`, `modified_by`

### Giai đoạn 3: Tính năng nâng cao (2 tuần)
- [ ] Dashboard thống kê tổng quan
- [ ] Báo cáo xuất Excel
- [ ] Cảnh báo sinh viên vắng nhiều
- [ ] Lịch sử thay đổi điểm danh (audit log)

### Giai đoạn 4: Testing & Deployment
- [ ] Unit tests cho logic mới
- [ ] Test với dữ liệu thật
- [ ] Đào tạo người dùng
- [ ] Triển khai production

---

## 5. TÓM TẮT VẤN ĐỀ CHÍNH

| Vấn đề | Mức độ | Ảnh hưởng | Giải pháp |
|--------|--------|-----------|-----------|
| Tạo bản ghi "Vắng" cho tất cả SV mỗi lần 1 người điểm danh | **CAO** | Dư thừa dữ liệu, logic sai | Tạo ClassSession, khởi tạo 1 lần |
| Hardcode điểm /9 buổi | **CAO** | Không linh hoạt, sai kết quả | Tính động dựa trên số buổi thực tế |
| Không có quản lý "Buổi học" | **CAO** | Không phân biệt buổi, không kiểm soát | Thêm model ClassSession |
| Hai phương thức điểm danh khác logic | **TRUNG BÌNH** | Không đồng bộ | Thống nhất qua ClassSession |
| Thiếu audit trail | **TRUNG BÌNH** | Không truy vết được | Thêm modified_by, modified_at |
| Không có dashboard thống kê | **THẤP** | Khó quản lý tổng quan | Thêm tính năng báo cáo |

---

## 6. KẾT LUẬN

Hệ thống hiện tại **HOẠT ĐỘNG ĐƯỢC** nhưng có nhiều điểm **CHƯA TỐI ƯU**:

✅ **Ưu điểm:**
- Có nhận diện khuôn mặt + Anti-spoofing
- Phân quyền rõ ràng (Admin/Lecturer/Student)
- Giao diện Bootstrap đẹp

❌ **Nhược điểm:**
- Logic điểm danh chưa rõ ràng, gây dư thừa dữ liệu
- Hardcode quá nhiều (9 buổi, 2 buổi vắng...)
- Thiếu quản lý "Buổi học" (Session)
- Không có tracking thay đổi

🎯 **Đề xuất ưu tiên:**
1. **NGAY**: Sửa logic `insert_attendance()` - Không tạo bản ghi Vắng cho tất cả
2. **TUẦN NÀY**: Thêm model `ClassSession`
3. **TUẦN SAU**: Tính điểm động, thêm tracking

---

**Người phân tích:** GitHub Copilot  
**Ngày:** 10/12/2025  
**Version:** 1.0
