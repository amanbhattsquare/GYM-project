"""
WSGI config for GYM project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GYM.settings')

# application = get_wsgi_application()




"""
WSGI config for GYM project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Add your project directory to the Python path
path = '/home/squarefit/www/GYM-project'
if path not in sys.path:
    sys.path.insert(0, path)

# Add the GYM directory too
gym_path = '/home/squarefit/www/GYM-project/GYM'
if gym_path not in sys.path:
    sys.path.insert(0, gym_path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GYM.settings')

application = get_wsgi_application()
