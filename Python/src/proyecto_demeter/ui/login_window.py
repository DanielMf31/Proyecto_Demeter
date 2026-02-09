import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success_callback):
        super().__init__(parent)
        self.title("Demeter Login")
        self.geometry("300x250")
        self.resizable(False, False)
        
        self.on_success = on_success_callback
        self.users_db = self.load_users()
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.setup_ui()

    def load_users(self):
        try:
            # Assuming config/users.json is relative to project root or Python dir
            # Adjust path based on where main.py runs
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            config_path = os.path.join(base_dir, "config", "users.json")
            
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Config Error", f"Could not load users.json:\n{e}")
            return {}

    def setup_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(frame, text="🔐 Acceso Seguro", font=("Arial", 14, "bold")).pack(pady=10)

        # User
        ttk.Label(frame, text="Usuario:").pack(anchor="w")
        self.entry_user = ttk.Entry(frame)
        self.entry_user.pack(fill="x", pady=5)
        self.entry_user.focus()

        # Pass
        ttk.Label(frame, text="Contraseña:").pack(anchor="w")
        self.entry_pass = ttk.Entry(frame, show="*")
        self.entry_pass.pack(fill="x", pady=5)
        
        # Bind Enter key
        self.entry_pass.bind("<Return>", lambda e: self.validate_login())

        # Button
        ttk.Button(frame, text="Entrar", command=self.validate_login).pack(pady=20, fill="x")

    def validate_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        if username in self.users_db and self.users_db[username] == password:
            self.destroy()
            self.on_success()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            self.entry_pass.delete(0, "end")

    def on_close(self):
        self.destroy()
        # If closed without login, app should exit
        import sys
        sys.exit(0)
