import os
import json
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet

CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
KEY_FILE = os.path.join(CONFIG_DIR, "key.key")

# Load encryption key
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

# Load config with decryption
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

# Save config with encryption
def save_config(username, password):
    with open(CONFIG_FILE, "w") as file:
        json.dump({
            "username": encrypt_data(username),
            "password": encrypt_data(password)
        }, file, indent=4)
    messagebox.showinfo("Success", "Configuration Saved!")

def open_editor():
    root = tk.Tk()
    root.title("Edit Config")
    root.geometry("250x180")

    # Center window on screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 250) // 2
    y = (screen_height - 180) // 2
    root.geometry(f"250x180+{x}+{y}")
    
    config = load_config()
    
    tk.Label(root, text="Enter Username:", font=("Arial", 12)).pack(pady=5)
    username_entry = tk.Entry(root, font=("Arial", 12))
    username_entry.insert(0, config.get("username", ""))
    username_entry.pack(pady=5)
    username_entry.focus_set()
    username_entry.select_range(0, tk.END)
    
    tk.Label(root, text="Enter Password:", font=("Arial", 12)).pack(pady=5)
    password_entry = tk.Entry(root, show="*", font=("Arial", 12))
    password_entry.insert(0, config.get("password", ""))
    password_entry.pack(pady=5)
    
    def save_and_exit(event=None):
        username = username_entry.get()
        password = password_entry.get()
        save_config(username, password)
        root.destroy()
    
    save_button = tk.Button(root, text="Save", command=save_and_exit, font=("Arial", 12))
    save_button.pack(pady=10)
    
    root.bind('<Return>', save_and_exit)
    
    root.mainloop()

if __name__ == "__main__":
    open_editor()
