import os
import sys

# Ensure api-gateway root is on sys.path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
API_GATEWAY_DIR = os.path.dirname(CURRENT_DIR)
if API_GATEWAY_DIR not in sys.path:
    sys.path.insert(0, API_GATEWAY_DIR)

from vercel_app import app

# Expose ASGI app
