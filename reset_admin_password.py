"""
Reset admin password
Run with: type reset_admin_password.py | python manage.py shell
"""

from django.contrib.auth.models import User

try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print('✓ Admin password reset to: admin123')
except User.DoesNotExist:
    print('✗ Admin user not found')
