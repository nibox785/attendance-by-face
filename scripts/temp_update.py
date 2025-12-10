from main.models import StaffInfo, Role, StaffRole  
lecturer_role = Role.objects.get(name='Lecturer')  
for sid in ['1079440959', '1250767097', '1304868666']:  
    staff = StaffInfo.objects.get(id_staff=sid)  
    StaffRole.objects.filter(staff=staff).delete()  
    StaffRole.objects.create(staff=staff, role=lecturer_role)  
    print(f'Updated {sid}')  
