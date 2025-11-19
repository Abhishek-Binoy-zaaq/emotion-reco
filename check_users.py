"""
Check existing users
Run with: type check_users.py | python manage.py shell
"""

from django.contrib.auth.models import User

print("\n=== Existing Users ===")
users = User.objects.all()

if not users:
    print("No users found in database!")
else:
    for user in users:
        print(f"\nUsername: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is staff: {user.is_staff}")
        print(f"Is superuser: {user.is_superuser}")

print(f"\nTotal users: {users.count()}")
