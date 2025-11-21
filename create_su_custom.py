import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zenstore.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
    print("Superuser created.")
else:
    print("Superuser exists.")