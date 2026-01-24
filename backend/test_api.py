import requests
import json

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin@epos.com", "password": "Admin@123"}
)
print("Login Response:", response.status_code)
token = response.json()["access_token"]
print("Token received:", token[:50] + "...")

# Test Guest House stats
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/guesthouse/dashboard/stats",
    headers=headers
)
print("\nGuest House Stats Response:", response.status_code)
print(json.dumps(response.json(), indent=2))

# Test Guest House rooms
response = requests.get(
    "http://localhost:8000/api/guesthouse/rooms",
    headers=headers
)
print("\nGuest House Rooms Response:", response.status_code)
print(json.dumps(response.json(), indent=2))

# Test Guest House bookings
response = requests.get(
    "http://localhost:8000/api/guesthouse/bookings",
    headers=headers
)
print("\nGuest House Bookings Response:", response.status_code)
print(json.dumps(response.json(), indent=2))
