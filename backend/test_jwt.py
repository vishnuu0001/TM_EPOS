import jwt
from datetime import datetime, timedelta

# Same secret key as in config
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Create a test token
payload = {
    "sub": "test-user-id",
    "email": "admin@epos.com",
    "exp": datetime.utcnow() + timedelta(minutes=1440)
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print("Generated token:", token)

# Try to decode it
try:
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("Decoded successfully:", decoded)
except Exception as e:
    print("Decode failed:", e)

# Now let's decode a real token from the API
import requests

response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin@epos.com", "password": "Admin@123"}
)
print("\nLogin response:", response.status_code)
real_token = response.json()["access_token"]
print("Real token:", real_token[:50] + "...")

# Decode the real token
try:
    decoded = jwt.decode(real_token, SECRET_KEY, algorithms=[ALGORITHM])
    print("Real token decoded:", decoded)
except Exception as e:
    print("Real token decode failed:", e)
