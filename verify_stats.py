import sys
import os
from django.conf import settings
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

try:
    url = reverse('session-aggregate-report')
    print(f"URL resolved: {url}")
except Exception as e:
    print(f"URL reverse failed: {e}")
    sys.exit(1)

User = get_user_model()
try:
    # Try to use existing admin or create one
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('debug_admin', 'debug@example.com', 'password')
        print("Created new debug_admin")
    else:
        print(f"Using existing admin: {admin_user.username}")

    client = Client()
    client.force_login(admin_user)
    response = client.get(url)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error Content: {response.content.decode('utf-8')}")
    else:
        print(f"Success Content preview: {response.content[:200]}")
except Exception as e:
    print(f"Execution failed: {e}")
    import traceback
    traceback.print_exc()
