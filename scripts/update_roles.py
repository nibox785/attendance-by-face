import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceByAttendance.settings')
django.setup()

from main.models import StaffInfo, Role, StaffRole

# Get Lecturer role
lecturer_role = Role.objects.get(name='Lecturer')

# Update 3 staff to Lecturer role
staff_ids = ['1079440959', '1250767097', '1304868666']
for sid in staff_ids:
    staff = StaffInfo.objects.get(id_staff=sid)
    # Delete old roles
    StaffRole.objects.filter(staff=staff).delete()
    # Add Lecturer role
    StaffRole.objects.create(staff=staff, role=lecturer_role)
    print(f'✓ Updated {sid} - {staff.staff_name} to Lecturer role')

print('\n✓ All staff updated successfully!')

# Verify
print('\nCurrent roles:')
for s in StaffInfo.objects.all():
    roles = [r.name for r in s.roles.all()]
    print(f'{s.id_staff} - {s.staff_name}: {roles}')
