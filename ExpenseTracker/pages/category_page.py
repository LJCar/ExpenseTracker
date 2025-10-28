from tkinter import ttk, messagebox, Toplevel
import tkinter as tk
from repositories.category_repository import CategoryRepository
from models.category import Category

def render_category_page(main_frame, go_back_callback):
    for widget in main_frame.winfo_children():
        widget.destroy()

    repo = CategoryRepository()

    # Top bar with back button
    top_frame = ttk.Frame(main_frame)
    top_frame.pack(fill="x", anchor="nw")
    ttk.Button(top_frame, text="⬅️ Back to Home", command=lambda: go_back_callback(main_frame)).pack(side="left", padx=5, pady=5)

    ttk.Label(main_frame, text="📂 Manage Categories", font=("Arial", 14, "bold")).pack(pady=10)

    # Main layout frame
    layout_frame = ttk.Frame(main_frame)
    layout_frame.pack(padx=20, pady=10, fill="both", expand=True)

    # LEFT SIDE: List of categories
    list_frame = ttk.Frame(layout_frame)
    list_frame.grid(row=0, column=0, sticky="ns")

    category_listbox = tk.Listbox(list_frame, width=30, height=15)
    category_listbox.pack(side="left", fill="y")
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=category_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    category_listbox.config(yscrollcommand=scrollbar.set)

    def refresh_categories():
        category_listbox.delete(0, tk.END)
        for c in repo.get_all_categories():
            category_listbox.insert(tk.END, c.name.capitalize())

    refresh_categories()

    # RIGHT SIDE: Buttons
    button_frame = ttk.Frame(layout_frame)
    button_frame.grid(row=0, column=1, padx=20, sticky="n")

    def open_add_popup():
        popup = Toplevel(main_frame)
        popup.title("Add Category")
        popup.geometry("300x150")
        popup.resizable(False, False)

        ttk.Label(popup, text="Category Name:").pack(pady=10)
        entry = ttk.Entry(popup, width=25)
        entry.pack(pady=5)

        def submit_add():
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("Input Error", "Name cannot be empty.", parent=popup)
                return

            category = Category(id=None, name=name)
            success = repo.add_category(category)
            if success:
                messagebox.showinfo("Success", f"Category '{name}' added.", parent=popup)
                popup.destroy()
                refresh_categories()
            else:
                messagebox.showinfo("Note", f"Category '{name}' already exists.", parent=popup)

        ttk.Button(popup, text="Add", command=submit_add).pack(pady=10)

    def delete_selected():
        selected = category_listbox.curselection()
        if selected:
            name = category_listbox.get(selected[0])
            confirm = messagebox.askyesno("Confirm Deletion", f"Delete '{name}'?", parent=main_frame)
            if confirm:
                success = repo.delete_category_by_name(name)
                if success:
                    messagebox.showinfo("Deleted", f"Category '{name}' deleted.", parent=main_frame)
                    refresh_categories()
                else:
                    messagebox.showerror("Error", "Could not delete category.", parent=main_frame)
        else:
            messagebox.showwarning("No Selection", "Select a category first.", parent=main_frame)

    ttk.Button(button_frame, text="➕ Add Category", command=open_add_popup).pack(pady=(0, 20), fill="x")
    ttk.Button(button_frame, text="🗑 Delete Selected", command=delete_selected).pack(fill="x")