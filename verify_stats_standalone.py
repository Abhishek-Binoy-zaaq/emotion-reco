import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

print("--- START VERIFICATION ---")

found_url = False
url = ""

try:
    # 1. Check URL resolution
    print("Checking URL reversal for 'session-aggregate-report'...")
    url = reverse('session-aggregate-report')
    print(f"[OK] URL resolved: {url}")
    found_url = True
except Exception as e:
    print(f"[FAIL] URL reverse failed: {e}")

# 2. Check View Response
if found_url:
    try:
        User = get_user_model()
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('debug_admin_sf', 'debug_sf@example.com', 'password')
            print("Created new debug_admin_sf")
        
        client = Client()
        client.force_login(admin_user)
        
        print(f"Fetching {url}...")
        response = client.get(url)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"[OK] Success! Content length: {len(response.content)}")
            print(f"Preview: {response.content[:100]}")
        else:
            print(f"[FAIL] Error response.")
            print(f"Content: {response.content.decode('utf-8')[:500]}")
            
    except Exception as e:
        print(f"[FAIL] Request failed: {e}")
        import traceback
        traceback.print_exc()

print("--- END VERIFICATION ---")
