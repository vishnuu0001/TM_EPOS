import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_DIR = os.path.dirname(CURRENT_DIR)
if SERVICE_DIR not in sys.path:
    sys.path.insert(0, SERVICE_DIR)

from main import app

# Vercel expects an ASGI app variable named `app`
