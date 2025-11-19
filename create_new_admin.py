"""
Create a new admin account
Run with: type create_new_admin.py | python manage.py shell
"""

from django.contrib.auth.models import User

# Delete old admin if exists
try:
    old_admin = User.objects.get(username='admin')
    old_admin.delete()
    print('✓ Deleted old admin account')
except User.DoesNotExist:
    pass

# Create fresh admin
admin = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123',
    first_name='Admin',
    last_name='User'
)
print('✓ Created fresh admin account')
print('  Username: admin')
print('  Password: admin123')
print('\nYou can now login!')
