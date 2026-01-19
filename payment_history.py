import tkinter as tk
from tkinter import ttk, messagebox
from database import db_connect
from datetime import datetime

class PaymentHistoryWindow:
    def __init__(self, student_id: int, student_name: str):
        self.student_id = student_id
        self.student_name = student_name
        self.root = tk.Toplevel()
        self.root.title(f"Histórico de Pagamentos — {student_name}")
        self.center_window(760, 460)

        ttk.Label(self.root, text=f"Pagamentos — {student_name}", font=("Segoe UI", 12, "bold")).pack(pady=8)

        cols = ("Mês", "Ano", "Data", "Forma", "Valor", "Status")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center", width=110)
        self.tree.pack(fill="both", expand=True, padx=12, pady=8)

        form = ttk.Frame(self.root)
        form.pack(pady=6)
        self.month = ttk.Entry(form, width=8)
        self.year = ttk.Entry(form, width=6)
        self.p_date = ttk.Entry(form, width=12)
        self.p_method = ttk.Entry(form, width=12)
        self.amount = ttk.Entry(form, width=8)

        fields = [("Mês", self.month), ("Ano", self.year), ("Data", self.p_date), ("Forma", self.p_method), ("Valor", self.amount)]
        for i, (lbl, w) in enumerate(fields):
            ttk.Label(form, text=lbl).grid(row=0, column=i*2, padx=4)
            w.grid(row=0, column=i*2+1, padx=4)

        btns = ttk.Frame(self.root)
        btns.pack(pady=6)
        ttk.Button(btns, text="Adicionar", command=self.add_payment).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Marcar Pago", command=self.validate_payment).grid(row=0, column=1, padx=6)
        ttk.Button(btns, text="Fechar", command=self.root.destroy).grid(row=0, column=2, padx=6)

        self.load_history()

    def db_connect(self):
        return db_connect()

    def load_history(self):
        self.tree.delete(*self.tree.get_children())
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT id, month, year, payment_date, payment_method, amount, status_pagamento FROM payments WHERE student_id=? ORDER BY year DESC, month DESC", (self.student_id,))
        for row in cur.fetchall():
            pid, month, year, pdate, method, amount, status = row
            amount_display = f"R$ {amount:.2f}" if amount is not None else ""
            self.tree.insert("", "end", iid=pid, values=(month, year, pdate, method, amount_display, status))
        conn.close()

    def add_payment(self):
        try:
            amount = float(self.amount.get().strip())
        except Exception:
            messagebox.showerror("Erro", "Valor inválido.")
            return

        month = self.month.get().strip()
        year = self.year.get().strip()
        date = self.p_date.get().strip()
        method = self.p_method.get().strip()

        if not (month and year and date and method):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        # validar year 
        try:
            year_i = int(year)
            if year_i < 1900 or year_i > 2100:
                raise ValueError
        except Exception:
            messagebox.showerror("Erro", "Ano inválido.")
            return

        # validar date
        try:
            datetime.strptime(date, "%d/%m/%Y")
        except Exception:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO payments (student_id, month, year, payment_date, payment_method, amount, status_pagamento) VALUES (?,?,?,?,?,?,?)",
                    (self.student_id, month, year, date, method, amount, "Pendente"))
        conn.commit()
        conn.close()
        self.load_history()
        messagebox.showinfo("Sucesso", "Pagamento adicionado.")

    def validate_payment(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um pagamento.")
            return
        pid = int(sel[0])
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("UPDATE payments SET status_pagamento='Pago' WHERE id= ?", (pid,))
        conn.commit()
        conn.close()
        self.load_history()
        messagebox.showinfo("Sucesso", "Pagamento marcado como Pago.")

    def center_window(self, w, h):
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")