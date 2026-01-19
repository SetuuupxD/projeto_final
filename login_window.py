import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk

from utils import get_art_path
from database import verify_user
from admin_window import AdminWindow


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login — Sistema Escolar IEGV")
        self.root.geometry("300x450")
        self.root.configure(bg="#F2F2F2")
        self.root.resizable(False, False)

        self.primary = "#1B5E20"
        self.white = "#FFFFFF"

        self._setup_styles()
        self._build_ui()

    # --------------------------
    # Estilos Modernos
    # --------------------------
    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        style.configure("TEntry", padding=8, relief="flat", font=("Segoe UI", 11))
        style.configure("Green.TButton",
                        background=self.primary,
                        foreground="white",
                        font=("Segoe UI", 11, "bold"),
                        padding=10)
        style.map("Green.TButton",
                  background=[("active", "#2E7D32")])

    # --------------------------
    # Interface
    # --------------------------
    def _build_ui(self):
        # Logo
        logo_path = get_art_path("logo.png")

        if Path(logo_path).exists():
            try:
                img = Image.open(logo_path).resize((120, 120))
                self.logo_img = ImageTk.PhotoImage(img)
                tk.Label(self.root, image=self.logo_img, bg="#F2F2F2").pack(pady=(25, 10))
            except:
                tk.Label(self.root, text="IEGV", font=("Segoe UI", 32, "bold"),
                         fg=self.primary, bg="#F2F2F2").pack(pady=10)
        else:
            tk.Label(self.root, text="IEGV", font=("Segoe UI", 32, "bold"),
                     fg=self.primary, bg="#F2F2F2").pack(pady=10)

        frame = tk.Frame(self.root, bg="#F2F2F2")
        frame.pack(pady=5, padx=40, fill="x")

        tk.Label(frame, text="Usuário", font=("Segoe UI", 11, "bold"),
                 fg=self.primary, bg="#F2F2F2").pack(anchor="w")
        self.user_entry = ttk.Entry(frame)
        self.user_entry.pack(fill="x", pady=5)

        tk.Label(frame, text="Senha", font=("Segoe UI", 11, "bold"),
                 fg=self.primary, bg="#F2F2F2").pack(anchor="w", pady=(10, 0))
        self.pass_entry = ttk.Entry(frame, show="*")
        self.pass_entry.pack(fill="x", pady=5)

        ttk.Button(frame, text="Entrar",
                   style="Green.TButton",
                   command=self._login).pack(pady=20, fill="x")

        self.root.bind("<Return>", lambda e: self._login())

        self.user_entry.focus_set()

    # --------------------------
    # Login
    # --------------------------
    def _login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if username == "" or password == "":
            messagebox.showerror("Erro", "Preencha usuário e senha.")
            return

        ok, is_admin = verify_user(username, password)

        if not ok:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")
            return

        # LOGIN OK → Abre o sistema
        self.root.destroy()
        app = tk.Tk()
        AdminWindow(app, is_admin=is_admin, username=username)
        app.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
