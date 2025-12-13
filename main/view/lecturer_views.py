import os
import time
from datetime import date, timedelta, datetime

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import Paginator
from django.http import Http404
from django.http import StreamingHttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.views.decorators import gzip

from main.decorators import lecturer_required
from main.models import StaffInfo, StudentClassDetails, ClassSession
from main.src.anti_spoof_predict import AntiSpoofPredict
from main.src.generate_patches import CropImage
from main.src.utility import parse_model_name
from main.view.reg import *
from main.models import BlogPost

model_test = AntiSpoofPredict(0)
image_cropper = CropImage()

model_dir = "main/resources/anti_spoof_models"
device_id = 0

for model_name in os.listdir(model_dir):
    h_input, w_input, model_type, scale = parse_model_name(model_name)


@lecturer_required
def lecturer_dashboard_view(request):
    blog_posts = BlogPost.objects.filter(type__in=["ALL", "GV"])
    return render(request, 'lecturer/lecturer_home.html', {'blog_posts': blog_posts})


@lecturer_required
def lecturer_schedule_view(request):
    id_lecturer = request.session.get('id_staff')
    week_start_param = request.GET.get('week_start')

    if week_start_param:
        try:
            week_start = date.fromisoformat(week_start_param)
        except ValueError:
            raise Http404("Invalid date format for week_start parameter")
    else:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    end_of_week = week_start + timedelta(days=6)

    lecturer_classes = Classroom.objects.filter(
        id_lecturer__id_staff=id_lecturer,
        begin_date__lte=end_of_week,
        end_date__gte=week_start
    ).order_by('day_of_week_begin', 'begin_time')

    previous_week_start = week_start - timedelta(days=7)
    next_week_start = week_start + timedelta(days=7)

    previous_week_start = previous_week_start.strftime("%Y-%m-%d")
    next_week_start = next_week_start.strftime("%Y-%m-%d")

    context = {
        'lecturer_classes': lecturer_classes,
        'start_of_week': week_start,
        'end_of_week': end_of_week,
        'previous_week_start': previous_week_start,
        'next_week_start': next_week_start,
    }
    return render(request, 'lecturer/lecturer_schedule.html', context)


@lecturer_required
def lecturer_profile_view(request):
    id_lecturer = request.session['id_staff']
    lecturer = StaffInfo.objects.get(id_staff=id_lecturer)

    if request.method == 'POST':
        lecturer.staff_name = request.POST['lecturer_name']
        lecturer.email = request.POST['email']
        lecturer.phone = request.POST['phone']
        lecturer.address = request.POST['address']
        lecturer.birthday = datetime.strptime(request.POST['birthday'], '%d/%m/%Y').date()
        lecturer.save()
        messages.success(request, 'Thay đổi thông tin thành công.')

    context = {'lecturer': lecturer}

    return render(request, 'lecturer/lecturer_profile.html', context)


@lecturer_required
def lecturer_change_password_view(request):
    id_lecturer = request.session['id_staff']
    lecturer = StaffInfo.objects.get(id_staff=id_lecturer)

    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if check_password(old_password, lecturer.password):
            if new_password == confirm_password:
                lecturer.password = make_password(new_password)
                lecturer.save()
                update_session_auth_hash(request, lecturer)
                messages.success(request, 'Đổi mật khẩu thành công.')
            else:
                messages.error(request, 'Mật khẩu mới không khớp.')
        else:
            messages.error(request, 'Mật khẩu cũ không đúng.')

    return render(request, 'lecturer/lecturer_change_password.html')


@lecturer_required
def lecturer_attendance_class_view(request):
    id_lecturer = request.session.get('id_staff')

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    end_of_week = week_start + timedelta(days=6)

    lecturer_classes = Classroom.objects.filter(
        id_lecturer__id_staff=id_lecturer,
        begin_date__lte=end_of_week,
        end_date__gte=week_start
    ).order_by('day_of_week_begin', 'begin_time')

    day_of_week_today = today.isoweekday()

    context = {
        'lecturer_classes': lecturer_classes,
        'start_of_week': week_start,
        'end_of_week': end_of_week,
        'day_of_week_today': day_of_week_today,
    }

    return render(request, 'lecturer/lecturer_attendance_class.html', context)


# ================== DEPRECATED - OLD ATTENDANCE FLOW ==================
# ⚠️ KHÔNG SỬ DỤNG - ĐÃ CHUYỂN SANG SESSION-BASED FLOW
# Các function này được giữ lại để backward compatibility nhưng không khuyến nghị
# Nên dùng: lecturer_start_session() -> lecturer_mark_attendance_session() -> lecturer_close_session()
# ======================================================================

# @lecturer_required
# def lecturer_mark_attendance(request, classroom_id):
#     """⚠️ DEPRECATED - Use lecturer_mark_attendance_session instead"""
#     pass

# def lecturer_mark_attendance_by_face(request, classroom_id):
#     """⚠️ DEPRECATED - Use lecturer_mark_attendance_by_face_session instead"""
#     pass

# @gzip.gzip_page
# def live_video_feed2(request, classroom_id):
#     """⚠️ DEPRECATED - Use live_video_feed_session instead"""
#     pass

# ================== END DEPRECATED FLOW ==================


@lecturer_required
def lecturer_history_list_classroom_view(request):
    id_lecturer = request.session.get('id_staff')
    classroom_per_page = 10
    page_number = request.GET.get('page')

    classrooms = Classroom.objects.filter(
        id_lecturer__id_staff=id_lecturer
    ).order_by('day_of_week_begin', 'begin_time')

    paginator = Paginator(classrooms, classroom_per_page)
    page = paginator.get_page(page_number)

    context = {'classrooms': page}

    return render(request, 'lecturer/lecturer_history_list_classroom.html', context)


@lecturer_required
def lecturer_attendance_history_view(request, classroom_id):
    classroom = Classroom.objects.get(pk=classroom_id)
    students_attendance = Attendance.objects.filter(id_classroom=classroom).order_by('id_student')

    student_per_page = 10
    page_number = request.GET.get('page')
    pagniator = Paginator(students_attendance, student_per_page)
    page = pagniator.get_page(page_number)

    context = {
        'students_attendance': page,
        'classroom': classroom
    }

    return render(request, 'lecturer/lecturer_attendance_history.html', context)


@lecturer_required
def lecturer_list_classroom_view(request):
    id_lecturer = request.session.get('id_staff')
    classroom_per_page = 10
    page_number = request.GET.get('page')

    classrooms = Classroom.objects.filter(
        id_lecturer__id_staff=id_lecturer
    ).order_by('day_of_week_begin', 'begin_time')

    paginator = Paginator(classrooms, classroom_per_page)
    page = paginator.get_page(page_number)

    context = {'classrooms': page}

    return render(request, 'lecturer/lecturer_list_classroom.html', context)


@lecturer_required
def lecturer_calculate_attendance_points_view(request, classroom_id):
    """Xem điểm chuyên cần - TÍNH ĐỘNG dựa trên số buổi học thực tế"""
    classroom = Classroom.objects.get(pk=classroom_id)
    students_in_class = StudentClassDetails.objects.filter(id_classroom=classroom)
    student_per_page = 10
    page_number = request.GET.get('page')
    
    # Đếm tổng số buổi học ĐÃ ĐÓNG (đã hoàn thành)
    total_expected_sessions = ClassSession.objects.filter(
        id_classroom=classroom,
        status='CLOSED'
    ).count()
    
    # Nếu chưa có buổi nào, báo cảnh báo
    if total_expected_sessions == 0:
        messages.warning(request, 'Lớp này chưa có buổi học nào được ghi nhận! Vui lòng mở và đóng buổi điểm danh trước.')
        total_expected_sessions = 1  # Tránh chia 0
    
    student_attendance_counts = []
    for student in students_in_class:
        # Đếm theo session (chính xác hơn)
        absent_count = Attendance.objects.filter(
            id_session__id_classroom=classroom,
            id_session__status='CLOSED',
            id_student=student.id_student,
            attendance_status=1
        ).count()
        
        present_count = Attendance.objects.filter(
            id_session__id_classroom=classroom,
            id_session__status='CLOSED',
            id_student=student.id_student,
            attendance_status=2
        ).count()
        
        late_count = Attendance.objects.filter(
            id_session__id_classroom=classroom,
            id_session__status='CLOSED',
            id_student=student.id_student,
            attendance_status=3
        ).count()

        total_number_attendance = absent_count + late_count + present_count
        total_attendance_present = late_count + present_count
        
        # TÍNH ĐIỂM ĐỘNG: dựa trên số buổi thực tế
        # Công thức: ((Vắng*0 + Muộn*0.5 + Có mặt*1) / Tổng buổi) * 3 điểm
        if total_expected_sessions > 0:
            total_attendance_percentage = round(
                (((absent_count * 0) + (late_count * 0.5) + present_count) / total_expected_sessions) * 3,
                2
            )
        else:
            total_attendance_percentage = 0
        
        # Quy định vắng tối đa 20% số buổi
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
            'max_allowed_absence': max_allowed_absence,
        })

    paginator = Paginator(student_attendance_counts, student_per_page)
    page = paginator.get_page(page_number)

    context = {
        'students_in_class': page,
        'classroom': classroom,
        'total_expected_sessions': total_expected_sessions,
    }

    return render(request, 'lecturer/lecturer_calculate_attendance_points.html', context)


# ================== QUẢN LÝ BUỔI HỌC (CLASS SESSION) ==================

@lecturer_required
def lecturer_start_session(request, classroom_id):
    """Bắt đầu buổi điểm danh - Tạo session và khởi tạo bản ghi Vắng cho tất cả SV"""
    classroom = get_object_or_404(Classroom, pk=classroom_id)
    today = date.today()
    id_lecturer = request.session.get('id_staff')
    
    # Kiểm tra có phải ngày học không
    if classroom.day_of_week_begin != today.isoweekday():
        messages.error(request, f'Hôm nay không phải ngày học của lớp {classroom.name}!')
        return redirect('lecturer_attendance')
    
    # Kiểm tra đã có session hôm nay chưa
    existing_session = ClassSession.objects.filter(
        id_classroom=classroom,
        session_date=today
    ).first()
    
    if existing_session:
        if existing_session.status == 'CLOSED':
            messages.error(request, f'Buổi học hôm nay đã đóng, không thể điểm danh lại!')
            return redirect('lecturer_attendance')
        elif existing_session.status == 'OPEN':
            messages.info(request, f'Buổi học #{existing_session.session_number} đang mở. Tiếp tục điểm danh.')
            return redirect('lecturer_mark_attendance_session', session_id=existing_session.id_session)
    
    # Tính số buổi học (session_number)
    session_count = ClassSession.objects.filter(id_classroom=classroom).count()
    
    # Tạo session mới
    session = ClassSession.objects.create(
        id_classroom=classroom,
        session_date=today,
        session_number=session_count + 1,
        status='OPEN',
        opened_at=datetime.now(),
        opened_by_id=id_lecturer
    )
    
    # Tạo bản ghi VẮNG cho tất cả sinh viên trong lớp
    students_in_class = StudentClassDetails.objects.filter(id_classroom=classroom)
    attendance_records = []
    for student_detail in students_in_class:
        attendance_records.append(Attendance(
            id_session=session,
            id_classroom=classroom,
            id_student=student_detail.id_student,
            check_in_time=datetime.now(),
            attendance_status=1,  # Vắng
            check_in_method='MANUAL'
        ))
    
    # Bulk create để tối ưu performance
    Attendance.objects.bulk_create(attendance_records)
    
    messages.success(request, f'✓ Đã mở buổi điểm danh #{session.session_number} - {classroom.name}')
    return redirect('lecturer_mark_attendance_session', session_id=session.id_session)


@lecturer_required
def lecturer_mark_attendance_session(request, session_id):
    """Điểm danh thủ công theo session - Cho phép xem và sửa cả khi đã đóng"""
    session = get_object_or_404(ClassSession, pk=session_id)
    
    # Kiểm tra quyền (chỉ giảng viên của lớp mới được điểm danh)
    id_lecturer = request.session.get('id_staff')
    if session.id_classroom.id_lecturer_id != id_lecturer:
        messages.error(request, 'Bạn không có quyền điểm danh lớp này!')
        return redirect('lecturer_attendance')
    
    # ✅ THAY ĐỔI: Cho phép xem khi CLOSED, nhưng không cho sửa (trừ khi reopen)
    # Đã bỏ kiểm tra session.status == 'CLOSED' để vẫn hiển thị trang
    
    attendances = Attendance.objects.filter(id_session=session).select_related('id_student').order_by('id_student__student_name')
    
    if request.method == 'POST':
        # Chỉ cho phép POST khi session OPEN
        if session.status != 'OPEN':
            messages.error(request, 'Buổi điểm danh đã đóng! Vui lòng mở lại để chỉnh sửa.')
            return redirect('lecturer_mark_attendance_session', session_id=session_id)
        
        updated_count = 0
        for attendance in attendances:
            new_status = request.POST.get(f'attendance_status_{attendance.id_student.id_student}')
            if new_status and int(new_status) != attendance.attendance_status:
                attendance.attendance_status = int(new_status)
                attendance.check_in_time = datetime.now()
                attendance.check_in_method = 'MANUAL'
                attendance.modified_by_id = id_lecturer
                attendance.save()
                updated_count += 1
        
        messages.success(request, f'✓ Cập nhật {updated_count} bản ghi điểm danh thành công!')
        return redirect('lecturer_mark_attendance_session', session_id=session_id)
    
    context = {
        'session': session,
        'classroom': session.id_classroom,
        'attendances': attendances,
    }
    return render(request, 'lecturer/lecturer_mark_attendance_session.html', context)


@lecturer_required
def lecturer_mark_attendance_by_face_session(request, session_id):
    """Điểm danh bằng khuôn mặt theo session"""
    session = get_object_or_404(ClassSession, pk=session_id)
    
    # Kiểm tra quyền
    id_lecturer = request.session.get('id_staff')
    if session.id_classroom.id_lecturer_id != id_lecturer:
        messages.error(request, 'Bạn không có quyền điểm danh lớp này!')
        return redirect('lecturer_attendance')
    
    if session.status == 'CLOSED':
        messages.error(request, 'Buổi điểm danh đã đóng!')
        return redirect('lecturer_attendance')
    
    attendances = Attendance.objects.filter(id_session=session).select_related('id_student')
    
    context = {
        'session': session,
        'classroom': session.id_classroom,
        'attendances': attendances,
    }
    return render(request, 'lecturer/lecturer_mark_attendance_by_face_session.html', context)


@gzip.gzip_page
def live_video_feed_session(request, session_id):
    """Video feed cho điểm danh khuôn mặt theo session"""
    return StreamingHttpResponse(
        main(session_id),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )


@lecturer_required
def lecturer_close_session(request, session_id):
    """Đóng buổi điểm danh - Không sửa được nữa"""
    session = get_object_or_404(ClassSession, pk=session_id)
    
    # Kiểm tra quyền
    id_lecturer = request.session.get('id_staff')
    if session.id_classroom.id_lecturer_id != id_lecturer:
        messages.error(request, 'Bạn không có quyền thao tác với lớp này!')
        return redirect('lecturer_attendance')
    
    if session.status != 'OPEN':
        messages.error(request, 'Buổi điểm danh không ở trạng thái mở!')
        return redirect('lecturer_attendance')
    
    session.status = 'CLOSED'
    session.closed_at = datetime.now()
    session.save()
    
    # Thống kê
    total_students = Attendance.objects.filter(id_session=session).count()
    present_count = Attendance.objects.filter(id_session=session, attendance_status__in=[2, 3]).count()
    absent_count = Attendance.objects.filter(id_session=session, attendance_status=1).count()
    
    messages.success(request, 
        f'✓ Đã đóng buổi #{session.session_number} - {session.id_classroom.name}<br>'
        f'Có mặt: {present_count}/{total_students} | Vắng: {absent_count}'
    )
    return redirect('lecturer_attendance')


@lecturer_required
def lecturer_reopen_session(request, session_id):
    """Mở lại buổi điểm danh đã đóng để chỉnh sửa"""
    session = get_object_or_404(ClassSession, pk=session_id)
    
    # Kiểm tra quyền (chỉ giảng viên của lớp)
    id_lecturer = request.session.get('id_staff')
    if session.id_classroom.id_lecturer_id != id_lecturer:
        messages.error(request, 'Bạn không có quyền thao tác với lớp này!')
        return redirect('lecturer_attendance')
    
    if session.status != 'CLOSED':
        messages.warning(request, 'Buổi điểm danh chưa đóng, không cần mở lại!')
        return redirect('lecturer_mark_attendance_session', session_id=session_id)
    
    # Mở lại session
    session.status = 'OPEN'
    session.closed_at = None
    session.save()
    
    messages.success(request, 
        f'✓ Đã mở lại buổi #{session.session_number} - {session.id_classroom.name}. '
        f'Bạn có thể chỉnh sửa điểm danh.'
    )
    return redirect('lecturer_mark_attendance_session', session_id=session_id)


@lecturer_required
def lecturer_session_list(request):
    """Đánh sách tất cả các buổi học của giảng viên"""
    id_lecturer = request.session.get('id_staff')
    
    # Lấy tất cả sessions của giảng viên
    sessions = ClassSession.objects.filter(
        id_classroom__id_lecturer_id=id_lecturer
    ).select_related('id_classroom').order_by('-session_date', '-session_number')
    
    # Thống kê cho mỗi session
    session_stats = []
    for session in sessions:
        total = Attendance.objects.filter(id_session=session).count()
        present = Attendance.objects.filter(id_session=session, attendance_status__in=[2, 3]).count()
        absent = Attendance.objects.filter(id_session=session, attendance_status=1).count()
        
        session_stats.append({
            'session': session,
            'total': total,
            'present': present,
            'absent': absent,
            'present_percent': round((present / total * 100) if total > 0 else 0, 1)
        })
    
    context = {
        'session_stats': session_stats,
    }
    return render(request, 'lecturer/lecturer_session_list.html', context)
