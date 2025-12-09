from functools import wraps

from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'Admin' in request.session.get('staff_role', []):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('error_403')

    return _wrapped_view


def lecturer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        staff_roles = request.session.get('staff_role', [])
        # Cho phép Lecturer, Staff và Faculty truy cập
        if any(role in staff_roles for role in ['Lecturer', 'Staff', 'Faculty']):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('error_403')

    return _wrapped_view


def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'id_student' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('error_403')

    return _wrapped_view


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'Staff' in request.session.get('staff_role', []):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('error_403')

    return _wrapped_view
