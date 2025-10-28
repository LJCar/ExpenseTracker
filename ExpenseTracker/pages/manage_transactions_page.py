from tkinter import ttk, messagebox
import tkinter as tk
import calendar
from datetime import datetime, date
from repositories.transaction_repository import TransactionRepository
from repositories.category_repository import CategoryRepository
from models.transaction import Transaction
from tkcalendar import DateEntry


def render_manage_transaction_page(main_frame, go_back_callback):
    for widget in main_frame.winfo_children():
        widget.destroy()

    main_frame.master.geometry("900x600")

    repo = TransactionRepository()
    cat_repo = CategoryRepository()

    # === Top Bar ===
    top_bar = ttk.Frame(main_frame)
    top_bar.pack(fill="x", padx=10, pady=5)

    ttk.Button(top_bar, text="⬅️ Back", command=lambda: go_back_callback(main_frame)).pack(side="left")

    search_var = tk.StringVar()
    search_entry = ttk.Entry(top_bar, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=5)
    ttk.Button(top_bar, text="Search 🔍", command=lambda: filter_transactions()).pack(side="left")

    # Month & Year filter
    current_year = date.today().year
    current_month = date.today().month

    month_var = tk.StringVar(value=str(current_month))
    year_var = tk.StringVar(value=str(current_year))

    month_names = list(calendar.month_name)[1:]
    month_var = tk.StringVar(value=month_names[date.today().month - 1])

    ttk.Label(top_bar, text="Month").pack(side="left", padx=(20, 2))
    month_cb = ttk.Combobox(top_bar, textvariable=month_var, values=month_names, width=10, state="readonly")
    month_cb.pack(side="left")

    ttk.Label(top_bar, text="Year").pack(side="left", padx=(10, 2))
    year_cb = ttk.Combobox(top_bar, textvariable=year_var, values=[str(y) for y in range(current_year-5, current_year+1)], width=6)
    year_cb.pack(side="left")

    ttk.Button(top_bar, text="Refresh", command=lambda: filter_transactions(clear_search=True)).pack(side="left", padx=10)

    # === Treeview ===
    columns = ("date", "description", "category", "type", "amount")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)

    tree.heading("date", text="Date")
    tree.heading("description", text="Description")
    tree.heading("category", text="Category")
    tree.heading("type", text="Type")
    tree.heading("amount", text="Amount")

    tree.column("date", width=100)
    tree.column("description", width=200)
    tree.column("category", width=120)
    tree.column("type", width=80)
    tree.column("amount", width=80)

    tree.pack(fill="both", expand=True, padx=10, pady=5)

    # === Bottom Buttons ===
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill="x", padx=10, pady=5)

    ttk.Button(btn_frame, text="Delete Selected", command=lambda: delete_selected()).pack(side="right", padx=5)
    ttk.Button(btn_frame, text="Edit Selected", command=lambda: open_edit_popup()).pack(side="right")

    # === Helper Functions ===

    def populate_tree(transactions):
        tree.delete(*tree.get_children())
        if not transactions:
            return

        for t in transactions:
            category = cat_repo.get_category_by_id(t.category_id)
            tree.insert("", "end", iid=str(t.id), values=(
                t.date,
                t.description,
                category.name.capitalize() if category else "Unknown",
                t.type,
                f"{t.amount:.2f}"
            ))

    def filter_transactions(clear_search=False):
        try:
            if clear_search:
                search_var.set("")

            month = list(calendar.month_name).index(month_var.get())
            year = int(year_var.get())
            desc = search_var.get().strip()

            if desc:
                txs = repo.get_transactions_by_description(desc)
            else:
                txs = repo.get_transactions_by_month(year, month)
            populate_tree(txs)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter transactions: {e}")

    def delete_selected():
        selected = tree.selection()
        if not selected:
            return messagebox.showwarning("No selection", "Please select a transaction to delete.")

        t_id = int(selected[0])

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete transaction #{t_id}?"):
            if repo.delete_transaction(t_id):
                messagebox.showinfo("Deleted", f"Transaction #{t_id} deleted.")
                filter_transactions()
            else:
                messagebox.showerror("Error", "Could not delete transaction.")

    def open_edit_popup():
        selected = tree.selection()
        if not selected:
            return messagebox.showwarning("No selection", "Select a transaction to edit.")

        t_id = int(selected[0])
        item = tree.item(selected[0])
        t_date, desc, category, type, amt = item["values"]

        popup = tk.Toplevel()
        popup.title("Edit Transaction")
        popup.geometry("300x400")

        ttk.Label(popup, text="Description").pack()
        desc_entry = ttk.Entry(popup)
        desc_entry.insert(0, desc)
        desc_entry.pack(pady=5)

        ttk.Label(popup, text="Amount").pack()
        amt_entry = ttk.Entry(popup)
        amt_entry.insert(0, amt)
        amt_entry.pack(pady=5)

        ttk.Label(popup, text="Type").pack()
        type_cb = ttk.Combobox(popup, values=["DEBIT", "CREDIT"], state="readonly")
        type_cb.set(type)
        type_cb.pack(pady=5)

        ttk.Label(popup, text="Category").pack()
        categories = cat_repo.get_all_categories()
        category_names = [c.name.capitalize() for c in categories]
        category_ids = {c.name: c.id for c in categories}
        cat_cb = ttk.Combobox(popup, values=category_names, state="readonly")
        cat_cb.set(category)
        cat_cb.pack(pady=5)

        ttk.Label(popup, text="Date").pack()
        date_entry = DateEntry(popup, date_pattern="yyyy-mm-dd")
        date_entry.set_date(t_date)
        date_entry.pack(pady=5)

        def update_transaction():
            try:
                updated = Transaction(
                    id=t_id,
                    description=desc_entry.get(),
                    amount=float(amt_entry.get()),
                    type=type_cb.get(),
                    category_id=category_ids[cat_cb.get()],
                    date=datetime.strptime(date_entry.get(), '%Y-%m-%d').date()
                )
                if TransactionRepository().delete_transaction(t_id) and TransactionRepository().add_transaction(updated):
                    messagebox.showinfo("Updated", "Transaction updated.")
                    popup.destroy()
                    filter_transactions()
                else:
                    messagebox.showerror("Error", "Could not update transaction.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(popup, text="Save Changes", command=update_transaction).pack(pady=10)

    # Load current month by default
    filter_transactions()