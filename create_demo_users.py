"""
Script to create demo users for the application
Run with: python manage.py shell < create_demo_users.py
"""

from django.contrib.auth.models import User

# Create admin user
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('✓ Admin user created: username=admin, password=admin123')
else:
    print('✓ Admin user already exists')

# Create regular user
if not User.objects.filter(username='user').exists():
    user = User.objects.create_user(
        username='user',
        email='user@example.com',
        password='user123',
        first_name='Regular',
        last_name='User'
    )
    print('✓ Regular user created: username=user, password=user123')
else:
    print('✓ Regular user already exists')

print('\n✅ Demo users are ready!')
print('Admin: username=admin, password=admin123')
print('User: username=user, password=user123')
