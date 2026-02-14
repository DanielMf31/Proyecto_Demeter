import customtkinter as ctk
import json
import webbrowser
import os
from tkinter import messagebox
from proyecto_demeter.shared.config.provider import settings

class LoginWindow(ctk.CTk):
    """
    Simple Login Window reading from config/users.json.
    """
    def __init__(self):
        super().__init__()
        
        self.title("Demeter - Login")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Use centralized config path
        self.config_path = os.path.join(settings.CONFIG_DIR, "users.json")
        
        self.authenticated = False

        self._create_ui()

    def _create_ui(self):
        # Title
        self.label_title = ctk.CTkLabel(self, text="Demeter System", font=("Roboto", 24))
        self.label_title.pack(pady=(40, 20))

        # Username
        self.entry_user = ctk.CTkEntry(self, placeholder_text="Username")
        self.entry_user.pack(pady=10)

        # Password
        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.entry_pass.pack(pady=10)

        # Login Button
        self.btn_login = ctk.CTkButton(self, text="Login", command=self.check_login)
        self.btn_login.pack(pady=10)

        # Dev Bypass
        self.btn_bypass = ctk.CTkButton(self, text="Bypass (Dev)", command=self.bypass_login, fg_color="#555555", hover_color="#333333")
        self.btn_bypass.pack(pady=5)
        
        # Bind Enter key
        self.bind('<Return>', lambda event: self.check_login())

    def check_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()

        if not os.path.exists(self.config_path):
            messagebox.showerror("Error", f"Config file not found: {self.config_path}")
            return

        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
            
            # Data structure is {"users": [{"username": "...", "password": "..."}]}
            users_list = data.get("users", [])
            valid_user = False
            
            for u in users_list:
                if u.get("username") == user and u.get("password") == pwd:
                    valid_user = True
                    break
            
            if valid_user:
                self.authenticated = True
                self.destroy() # Close login window to proceed
            else:
                messagebox.showerror("Login Failed", "Invalid Username or Password")
        except Exception as e:
            messagebox.showerror("Error", f"Login Error: {e}")

    def bypass_login(self):
        """Skip authentication for development."""
        print("⚠️  Developer Bypass Activated")
        self.authenticated = True
        self.destroy()

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
