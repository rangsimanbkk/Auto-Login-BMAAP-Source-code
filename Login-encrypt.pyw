import os
import json
import time
import requests
import tkinter as tk
import platform
import subprocess
from tkinter import messagebox
from cryptography.fernet import Fernet

CONFIG_DIR = "config"
LOG_DIR = "Log"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LOG_FILE = os.path.join(LOG_DIR, "connection_log.txt")
KEY_FILE = os.path.join(CONFIG_DIR, "key.key")
LOGIN_URL = "http://securelogin.arubanetworks.com/cgi-bin/login"
CHECK_URL = "https://www.google.com"

# Configuration
target_wifi_names = ["BMAAP"]  # Add any target SSIDs here

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Generate or load encryption key
def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key

encryption_key = load_key()
cipher = Fernet(encryption_key)

# Encrypt data
def encrypt_data(data):
    return cipher.encrypt(data.encode()).decode()

# Decrypt data
def decrypt_data(data):
    return cipher.decrypt(data.encode()).decode()

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            try:
                config = json.load(file)
                return {
                    "username": decrypt_data(config["username"]),
                    "password": decrypt_data(config["password"])
                }
            except Exception:
                return {"username": "", "password": ""}
    return {"username": "", "password": ""}

def save_config(username, password):
    with open(CONFIG_FILE, "w") as file:
        json.dump({
            "username": encrypt_data(username),
            "password": encrypt_data(password)
        }, file)

def log_status(status):
    with open(LOG_FILE, "a") as file:
        file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {status}\n")

def check_internet():
    try:
        requests.get(CHECK_URL, timeout=5)
        return True
    except requests.RequestException:
        return False

def login(username, password):
    data = {"username": username, "password": password}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        session = requests.Session()
        response = session.post(LOGIN_URL, data=data, headers=headers, timeout=5)
        if response.status_code == 200:
            log_status("Login successful")
        else:
            log_status(f"Login failed: {response.status_code}")
    except requests.RequestException as e:
        log_status(f"Login error: {e}")

def prompt_credentials():
    root = tk.Tk()
    root.title("Enter Login Credentials")
    root.geometry("300x200")  # Increased width for button alignment
    root.resizable(False, False)
    
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = (screen_height - 200) // 2
    root.geometry(f"300x200+{x}+{y}")
    
    config = load_config()

    tk.Label(root, text="Enter Username:", font=("Arial", 12)).pack(pady=5)
    username_entry = tk.Entry(root, font=("Arial", 12))
    username_entry.insert(0, config["username"])
    username_entry.pack(pady=5)
    username_entry.focus_set()
    username_entry.select_range(0, tk.END)
    
    tk.Label(root, text="Enter Password:", font=("Arial", 12)).pack(pady=5)
    password_entry = tk.Entry(root, show='*', font=("Arial", 12))
    password_entry.insert(0, config["password"])
    password_entry.pack(pady=5)

    # Frame for button alignment
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    def save_and_exit(event=None):
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            save_config(username, password)
            messagebox.showinfo("Success", "Credentials Saved!")
            root.destroy()
        else:
            exit(0)

    def close_and_exit():
        root.destroy()
        exit(0)

    save_button = tk.Button(button_frame, text="Save", command=save_and_exit, font=("Arial", 12), width=10)
    save_button.pack(side=tk.LEFT, padx=5)

    close_button = tk.Button(button_frame, text="Close", command=close_and_exit, font=("Arial", 12), width=10)
    close_button.pack(side=tk.RIGHT, padx=5)
    
    root.protocol("WM_DELETE_WINDOW", close_and_exit)  # Ensures script stops if window is closed
    root.bind('<Return>', save_and_exit)
    root.mainloop()

def get_wifi_name():
    os_type = platform.system()
    try:
        if os_type == "Windows":
            output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
            wifi_names = []
            blocks = output.split("Name")  # Splits output by interfaces
            for block in blocks:
                for line in block.splitlines():
                    if "SSID" in line and "BSSID" not in line:
                        ssid = line.split(":", 1)[1].strip()
                        if ssid:  # Avoid empty SSIDs
                            wifi_names.append(ssid)
                        break
            return wifi_names

        elif os_type == "Darwin":  # macOS
            output = subprocess.check_output(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"]
            ).decode()
            for line in output.split("\n"):
                if " SSID" in line:
                    return [line.split(":")[1].strip()]

        elif os_type == "Linux":
            output = subprocess.check_output(["iwgetid", "-r"]).decode().strip()
            return [output] if output else []

        else:
            return []
    except subprocess.CalledProcessError:
        return []

def main():
    config = load_config()
    if not config["username"] or not config["password"]:
        prompt_credentials()
    
    while True:
            # Get current Wi-Fi
            current_wifis = get_wifi_name()
            matched_wifi = next((wifi for wifi in current_wifis if wifi in target_wifi_names), None)

            if matched_wifi:
                if check_internet():
                    log_status(f'Connected to Wi-Fi : "{matched_wifi}". Internet OK.')
                else:
                    log_status(f'Connected to Wi-Fi : "{matched_wifi}". No Internet.')
                    login(config["username"], config["password"])
                    time.sleep(3)
                    if check_internet():
                        log_status(f'Internet OK.')
            else:
                log_status('Not connected to BMAAP. Skipping login.')
            time.sleep(60)

if __name__ == "__main__":
    main()
