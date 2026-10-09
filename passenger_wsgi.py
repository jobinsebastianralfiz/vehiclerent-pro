# Entry point for Namecheap (cPanel "Setup Python App" / Passenger).
# Railway uses gunicorn with config.wsgi and ignores this file.
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from config.wsgi import application  # noqa: E402,F401
