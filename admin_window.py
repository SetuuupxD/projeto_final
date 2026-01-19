import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk
from database import db_connect
from payment_history import PaymentHistoryWindow
from utils import get_art_path
from datetime import datetime


class AdminWindow:
    def __init__(self, root, is_admin, username):
        self.root = root
        self.is_admin = is_admin
        self.username = username

        # Palette
        self.primary = "#1B5E20"
        self.bg_gray = "#F2F2F2"
        self.white = "#FFFFFF"

        # Window
        self.root.title("Sistema Escolar — Administração" if self.is_admin else "Sistema Escolar — Usuário")
        self.root.geometry("1280x720")
        self.root.minsize(1000, 600)
        self.root.configure(bg=self.bg_gray)

        self.setup_styles()
        self.setup_ui()

        # load students after UI built
        self.root.after(200, self.load_students)

        # banner check (admin only)
        if self.is_admin:
            self.root.after(600, self.check_overdue_payments_and_show_alerts)

    # ---------------- Styles ----------------
    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=self.bg_gray)
        style.configure("TLabel", background=self.bg_gray, foreground="#000", font=("Segoe UI", 11))
        style.configure("TEntry", padding=6, relief="flat", fieldbackground=self.white)
        style.configure("Green.TButton", background=self.primary, foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Green.TButton", background=[("active", "#2E7D32")])

        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10), fieldbackground=self.white)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=self.primary, foreground=self.white)

    # ---------------- UI ----------------
    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=self.primary)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(header, text="Painel Administrativo — Escola IEGV", bg=self.primary, fg=self.white,
                 font=("Segoe UI", 18, "bold"), pady=12).pack(side="left", padx=18)

        logo_path = get_art_path("logo.png")
        if Path(logo_path).exists():
            try:
                img = Image.open(logo_path).resize((48, 48))
                self.logo_small = ImageTk.PhotoImage(img)
                tk.Label(header, image=self.logo_small, bg=self.primary).pack(side="right", padx=12)
            except Exception:
                pass

        # BANNER (row 1) - initially hidden; will be grid'ed when needed
        self.banner_frame = tk.Frame(self.root, bg="#FFCDD2")
        self.banner_label = tk.Label(self.banner_frame, text="", bg="#FFCDD2", fg="#B71C1C",
                                     font=("Segoe UI", 12, "bold"), pady=6)
        self.banner_label.pack(fill="x")

        # Ensure grid expansion for content area
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(6, weight=1)  # table row will expand

        # SEARCH (row 2)
        self.search_frame = ttk.Frame(self.root)
        self.search_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(10, 8))
        self.search_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.search_frame, text="Buscar:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_student())

        ttk.Button(self.search_frame, text="Buscar", style="Green.TButton", command=self.search_student).grid(row=0, column=2, padx=6)
        ttk.Button(self.search_frame, text="Limpar", style="Green.TButton", command=self.load_students).grid(row=0, column=3, padx=6)

        # FORM (row 3)
        self.form_frame = tk.LabelFrame(self.root, text="Cadastro de Alunos", bg=self.bg_gray,
                                       font=("Segoe UI", 12, "bold"))
        self.form_frame.grid(row=3, column=0, sticky="ew", padx=14, pady=8)
        for i in range(6):
            self.form_frame.grid_columnconfigure(i, weight=1)

        labels = ["Nome", "Professor", "Turma", "Data de Pagamento", "Forma de Pagamento", "Assinatura"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(self.form_frame, text=label + ":", bg=self.bg_gray, fg=self.primary,
                     font=("Segoe UI", 11, "bold")).grid(row=0, column=i, padx=4)
            ent = ttk.Entry(self.form_frame)
            ent.grid(row=1, column=i, padx=4, pady=4, sticky="ew")
            self.entries[label] = ent

        # BUTTONS (row 4)
        self.buttons_frame = tk.Frame(self.root, bg=self.bg_gray)
        self.buttons_frame.grid(row=4, column=0, sticky="ew", padx=14, pady=6)
        for i in range(4):
            self.buttons_frame.grid_columnconfigure(i, weight=1)

        ttk.Button(self.buttons_frame, text="Cadastrar", style="Green.TButton", command=self.add_student).grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(self.buttons_frame, text="Atualizar", style="Green.TButton", command=self.update_student).grid(row=0, column=1, padx=5, sticky="ew")
        ttk.Button(self.buttons_frame, text="Deletar", style="Green.TButton", command=self.delete_student).grid(row=0, column=2, padx=5, sticky="ew")
        ttk.Button(self.buttons_frame, text="Limpar Campos", style="Green.TButton", command=self.clear_inputs).grid(row=0, column=3, padx=5, sticky="ew")

        # ADMIN buttons (row 5)
        if self.is_admin:
            self.admin_btns = tk.Frame(self.root, bg=self.bg_gray)
            self.admin_btns.grid(row=5, column=0, sticky="ew", padx=14, pady=(0, 8))
            self.admin_btns.grid_columnconfigure(0, weight=1)
            ttk.Button(self.admin_btns, text="Histórico de Pagamentos", style="Green.TButton", command=self.open_payment_history).grid(column=0, row=0, sticky="ew", pady=4)
            ttk.Button(self.admin_btns, text="Validar Pagamento", style="Green.TButton", command=self.validate_payment).grid(column=0, row=1, sticky="ew", pady=4)

        # TABLE (row 6)
        self.table_frame = tk.Frame(self.root, bg=self.bg_gray)
        self.table_frame.grid(row=6, column=0, sticky="nsew", padx=14, pady=10)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        cols = ["Nome", "Professor", "Turma", "Data de Pagamento", "Forma de Pagamento", "Assinatura", "Status"]
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll_y.set)

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # FOOTER (row 7)
        self.footer = tk.Label(self.root, text=f"Logado como: {self.username} {'(Admin)' if self.is_admin else ''}",
                               bg=self.bg_gray, fg="#555", font=("Segoe UI", 10))
        self.footer.grid(row=7, column=0, sticky="ew", pady=4)

    # ---------------- Banner & overdue check ----------------
    def check_overdue_payments_and_show_alerts(self):
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT nome, payment_date FROM alunos WHERE status_pagamento='Pendente' AND payment_date IS NOT NULL")
        rows = cur.fetchall()
        conn.close()

        atrasados = []
        hoje = datetime.now().date()

        for nome, data in rows:
            try:
                dt = datetime.strptime(data, "%d/%m/%Y").date()
                if dt < hoje:
                    atrasados.append((nome, data))
            except Exception:
                continue

        if not atrasados:
            # ensure banner is hidden
            try:
                self.banner_frame.grid_forget()
            except Exception:
                pass
            return

        msg = f"⚠ Existem {len(atrasados)} alunos com pagamentos atrasados! Pesquise usando Buscar."
        self.banner_label.config(text=msg)
        # show banner right below header
        self.banner_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(8,4))

        # popup list
        lista = "\n".join([f"{n} — vencido em {d}" for n, d in atrasados])
        messagebox.showwarning("Pagamentos Atrasados", lista)

    # ---------------- CRUD ----------------
    def load_students(self):
        try:
            self.tree.delete(*self.tree.get_children())
        except Exception:
            pass
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""SELECT id, nome, professor, turma, payment_date, payment_method, assinatura, status_pagamento FROM alunos ORDER BY nome""")
        for row in cur.fetchall():
            status = "✔️ Pago" if row[-1] == "Pago" else "❌ Pendente"
            self.tree.insert("", "end", iid=row[0], values=row[1:-1] + (status,))
        conn.close()

    def search_student(self):
        term = self.search_var.get().strip()
        conn = db_connect()
        cur = conn.cursor()
        if term == "":
            cur.execute("SELECT id, nome, professor, turma, payment_date, payment_method, assinatura, status_pagamento FROM alunos ORDER BY nome")
        else:
            like = f"%{term}%"
            cur.execute("""SELECT id, nome, professor, turma, payment_date, payment_method, assinatura, status_pagamento
                           FROM alunos WHERE nome LIKE ? OR professor LIKE ? OR turma LIKE ? ORDER BY nome""", (like, like, like))
        rows = cur.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            status = row[-1]
            status_display = "✔️ Pago" if status == "Pago" else "❌ Pendente"
            self.tree.insert("", "end", iid=row[0], values=row[1:-1] + (status_display,))

    def add_student(self):
        vals = [self.entries[k].get().strip() for k in self.entries]
        if not vals[0]:
            messagebox.showerror("Erro", "O campo Nome é obrigatório.")
            return
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO alunos (nome, professor, turma, payment_date, payment_method, assinatura, status_pagamento) VALUES (?,?,?,?,?,?,?)",
                    (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], "Pendente"))
        conn.commit()
        conn.close()
        self.load_students()
        self.clear_inputs()
        messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso.")

    def update_student(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Erro", "Selecione um registro.")
            return
        sid = int(sel[0])
        vals = [self.entries[k].get().strip() for k in self.entries]
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET nome=?, professor=?, turma=?, payment_date=?, payment_method=?, assinatura=? WHERE id=?",
                    (*vals, sid))
        conn.commit()
        conn.close()
        self.load_students()
        messagebox.showinfo("Sucesso", "Registro atualizado.")

    def delete_student(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Erro", "Selecione um registro.")
            return
        sid = int(sel[0])
        if messagebox.askyesno("Confirmação", "Deseja deletar este registro?"):
            conn = db_connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM alunos WHERE id=?", (sid,))
            conn.commit()
            conn.close()
            self.load_students()
            messagebox.showinfo("Sucesso", "Registro deletado.")

    def clear_inputs(self):
        for e in self.entries.values():
            e.delete(0, "end")

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        for k, v in zip(list(self.entries.keys()), vals[:6]):
            self.entries[k].delete(0, "end")
            self.entries[k].insert(0, v)

    def open_payment_history(self):
        if not self.is_admin:
            messagebox.showerror("Acesso negado", "Histórico de pagamentos disponível apenas para administradores.")
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Atenção", "Selecione um aluno para ver o histórico.")
            return
        sid = int(sel[0])
        name = self.tree.item(sel[0], "values")[0]
        PaymentHistoryWindow(sid, name)

    def validate_payment(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Atenção", "Selecione um aluno.")
            return
        sid = int(sel[0])
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("UPDATE alunos SET status_pagamento='Pago' WHERE id=?", (sid,))
        conn.commit()
        conn.close()
        self.load_students()
        messagebox.showinfo("Sucesso", "Pagamento validado!")

