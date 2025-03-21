import requests

# Replace with your login URL and credentials
login_url = "http://securelogin.arubanetworks.com/cgi-bin/login"
payload = {
    "username": "your_username",
    "password": "your_password"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded"
}

session = requests.Session()
response = session.post(login_url, data=payload, headers=headers)

if response.ok:
    print("Login successful!")
else:
    print("Login failed!")