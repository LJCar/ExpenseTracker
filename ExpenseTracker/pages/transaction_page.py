from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime, date
from typing import cast, Literal
from tkcalendar import DateEntry
from repositories.transaction_repository import TransactionRepository
from repositories.category_repository import CategoryRepository
from models.transaction import Transaction
from pages.manage_transactions_page import render_manage_transaction_page


def render_transaction_page(main_frame, go_back_callback):
    for widget in main_frame.winfo_children():
        widget.destroy()

    repo = TransactionRepository()
    cat_repo = CategoryRepository()

    # -- Top frame with back button --
    top_frame = ttk.Frame(main_frame)
    top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
    top_frame.columnconfigure(0, weight=1)

    # Back Button
    back_btn = ttk.Button(top_frame, text="⬅️ Back to Home", command=lambda: go_back_callback(main_frame))
    back_btn.grid(row=0, column=0, sticky="w")

    # Manage Button
    manage_btn = ttk.Button(top_frame, text="📋 Manage Transactions",
                            command=lambda: render_manage_transaction_page(main_frame, go_back_callback))
    manage_btn.grid(row=0, column=1, sticky="e")

    # -- Title --
    ttk.Label(main_frame, text="Add a New Transaction").grid(row=1, column=0, columnspan=2, pady=10)

    # -- Description --
    ttk.Label(main_frame, text="Description").grid(row=2, column=0, columnspan=2, sticky="w", padx=10)
    desc_entry = ttk.Entry(main_frame, width=60)
    desc_entry.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    # -- Left Column --
    left_column = ttk.Frame(main_frame)
    left_column.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

    ttk.Label(left_column, text="Amount").pack(anchor="w")
    amount_entry = ttk.Entry(left_column)
    amount_entry.pack(pady=5, fill="x")

    ttk.Label(left_column, text="Type").pack(anchor="w")
    type_combobox = ttk.Combobox(left_column, values=["DEBIT", "CREDIT"], state="readonly")
    type_combobox.pack(pady=5, fill="x")

    ttk.Label(left_column, text="Category").pack(anchor="w")
    categories = cat_repo.get_all_categories()
    category_names = [c.name for c in categories]
    category_ids = {c.name: c.id for c in categories}
    category_combobox = ttk.Combobox(left_column, values=category_names, state="readonly")
    category_combobox.pack(pady=5, fill="x")

    # -- Right Column --
    right_column = ttk.Frame(main_frame)
    right_column.grid(row=4, column=1, padx=10, pady=5, sticky="nsew")

    ttk.Label(right_column, text="Date").pack(anchor="w")
    date_entry = DateEntry(right_column, date_pattern='yyyy-mm-dd')
    date_entry.set_date(date.today())
    date_entry.pack(pady=5, fill="x")

    # -- Submit logic  --
    def submit_transaction():
        try:
            transaction = Transaction(
                id=None,
                description=desc_entry.get(),
                amount=float(amount_entry.get()),
                type=cast(Literal["DEBIT", "CREDIT"], type_combobox.get()),
                category_id=category_ids[category_combobox.get()],
                date=datetime.strptime(date_entry.get(), '%Y-%m-%d').date()
            )
            if repo.add_transaction(transaction):
                messagebox.showinfo("Success", "Transaction added!")

                # Reset form
                desc_entry.delete(0, tk.END)
                amount_entry.delete(0, tk.END)
                category_combobox.set('')
            else:
                messagebox.showwarning("Failed", "Could not add transaction.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -- Add Transaction Button --
    ttk.Button(right_column, text="Add Transaction", command=submit_transaction).pack(pady=5, fill="x")


