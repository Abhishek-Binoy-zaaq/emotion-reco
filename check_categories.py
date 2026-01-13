import os
import django
import json

# Setup Django environment
import sys
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') 
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from emotions.models import VideoCategory

def check_categories():
    user, _ = User.objects.get_or_create(username='test_debug_user', is_staff=True)
    client = APIClient()
    client.force_authenticate(user=user)
    
    print("Fetching categories...")
    response = client.get('/api/categories/')
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
        
    data = response.data
    results = data.get('results', data) if isinstance(data, dict) else data
    
    print(f"Total categories: {len(results)}")
    
    names = [c['name'] for c in results]
    seen = set()
    dupes = [x for x in names if x in seen or seen.add(x)]
    
    if dupes:
        print(f"DUPLICATES FOUND IN API: {dupes}")
        print("Full list:")
        print(names)
    else:
        print("No duplicates in API response.")
        print(f"Names: {names}")

if __name__ == "__main__":
    check_categories()
