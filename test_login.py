"""
Test login authentication
Run with: type test_login.py | python manage.py shell
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

print("\n=== Testing Authentication ===\n")

# Test admin login
print("Testing admin login...")
admin_user = authenticate(username='admin', password='admin123')
if admin_user:
    print(f"✓ Admin authentication successful!")
    print(f"  - Username: {admin_user.username}")
    print(f"  - Is staff: {admin_user.is_staff}")
    print(f"  - Is active: {admin_user.is_active}")
else:
    print("✗ Admin authentication FAILED")
    # Check if user exists
    try:
        user = User.objects.get(username='admin')
        print(f"  - User exists but password is wrong")
        print(f"  - Is active: {user.is_active}")
    except User.DoesNotExist:
        print("  - User does not exist")

print("\nTesting user login...")
regular_user = authenticate(username='user', password='user123')
if regular_user:
    print(f"✓ User authentication successful!")
    print(f"  - Username: {regular_user.username}")
    print(f"  - Is staff: {regular_user.is_staff}")
    print(f"  - Is active: {regular_user.is_active}")
else:
    print("✗ User authentication FAILED")
    try:
        user = User.objects.get(username='user')
        print(f"  - User exists but password is wrong")
        print(f"  - Is active: {user.is_active}")
    except User.DoesNotExist:
        print("  - User does not exist")
