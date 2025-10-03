import tkinter as tk
from tkinter import ttk
from services.db import initialize_database
from pages.transaction_page import render_transaction_page
from pages.category_page import render_category_page
from pages.manage_transactions_page import render_manage_transaction_page
from pages.report_page import render_report_page

def main():
    root = tk.Tk()
    root.title("Expense Tracker")
    root.geometry("600x400")

    # Create a shared main content frame
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    render_main_menu(main_frame)

    root.mainloop()

def render_main_menu(main_frame):
    # Clear existing widgets from main_frame
    for widget in main_frame.winfo_children():
        widget.destroy()
    main_frame.master.geometry("600x400")

    # Welcome label
    welcome_label = ttk.Label(main_frame, text="Welcome to Expense Tracker!", font=("Helvetica", 16))
    welcome_label.pack(pady=20)

    # Add Transaction button
    add_button = ttk.Button(
        main_frame,
        text="➕ Add Transaction",
        command=lambda: render_transaction_page(main_frame, render_main_menu)
    )
    add_button.pack(pady=10)

    # Manage Transactions button
    ttk.Button(main_frame, text="📋 Manage Transactions",
               command=lambda: render_manage_transaction_page(main_frame, render_main_menu)).pack(pady=10)

    # Manage Categories button
    ttk.Button(main_frame, text="📂 Manage Categories",
               command=lambda: render_category_page(main_frame, render_main_menu)).pack(pady=10)

    ttk.Button(
        main_frame,
        text="📈 View Monthly Report",
        command=lambda: render_report_page(main_frame, render_main_menu)).pack(pady=10)

if __name__ == "__main__":
    initialize_database()
    print("Database initialized.")
    main()