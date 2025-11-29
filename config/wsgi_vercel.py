"""
WSGI config for Vercel deployment
"""
import os
import sys

# Add the project directory to the path
project_home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_prod')
os.environ.setdefault('DJANGO_SKIP_SYSTEM_CHECKS', '1')

# Import Django and set it up
import django
from django.core.wsgi import get_wsgi_application

# Configure Django
django.setup()

# Get the WSGI application
application = get_wsgi_application()

# For Vercel compatibility
app = application