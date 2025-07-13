import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import timedelta
from tkinter import ttk
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tkinter import filedialog
import calendar
import sqlite3

conn = sqlite3.connect("ExpenseTracker.db")
c = conn.cursor()

# Create default tables for expenses
c.execute('''CREATE TABLE IF NOT EXISTS food (
                id INTEGER,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                purchase_date DATE NOT NULL,
                repeat INTEGER DEFAULT 0
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS housing (
                    id INTEGER,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    purchase_date DATE NOT NULL,
                    repeat INTEGER DEFAULT 0
                  )''')

c.execute('''CREATE TABLE IF NOT EXISTS clothing (
                    id INTEGER,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    purchase_date DATE NOT NULL,
                    repeat INTEGER DEFAULT 0
                  )''')

c.execute('''CREATE TABLE IF NOT EXISTS entertainment (
                    id INTEGER,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    purchase_date DATE NOT NULL,
                    repeat INTEGER DEFAULT 0
                  )''')

c.execute('''CREATE TABLE IF NOT EXISTS utilities (
                    id INTEGER,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    purchase_date DATE NOT NULL,
                    repeat INTEGER DEFAULT 0
                  )''')
# Commit the changes and close the connection to the database
conn.commit()
conn.close()


# Helper function get all the categories form database
def get_categories():
    conn = sqlite3.connect("ExpenseTracker.db")
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    categories = [row[0] for row in c.fetchall()]
    conn.close()
    return categories


def validate_len(text):
    return len(text) <= 25


def validate_amount(value):
    try:
        float(value) and float(value) > 0
        return True
    except ValueError:
        return False


def validate_number(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


report = ""  # Global str is populated for when save report is called


def add_expense():
    add_window = tk.Toplevel(root)
    add_window.title("Add Expense")

    def add_to_database():
        category = category_combobox.get().strip()
        repeat_mapping = {"Yearly": 365, "Weekly": 7, "Daily": 1, '0': 0}
        repeat_custom_mapping = {"Years": 365, "Weeks": 7, "Days": 1, '0': 0}
        conn = sqlite3.connect("ExpenseTracker.db")
        c = conn.cursor()
        try:
            amount = "{:.2f}".format(float(amount_entry.get()))
            if len(repeat_combobox.get().split()) == 2:
                if repeat_combobox.get().split()[1] == "Months":
                    repeat_value = -30 * int(repeat_combobox.get().split()[0])
                else:
                    repeat_value = int(repeat_combobox.get().split()[0]) * repeat_custom_mapping[
                        repeat_combobox.get().split()[1]]
            elif repeat_combobox.get().split()[0] == "Monthly":
                repeat_value = -30
            else:
                repeat_value = repeat_mapping[repeat_combobox.get()]

            category_table_name = f'"{category.lower()}"'
            # Check if category exists
            c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (category_table_name,))
            existing_category = c.fetchone()

            if not existing_category:
                # Category doesn't exist, add new category
                c.execute(f'''CREATE TABLE IF NOT EXISTS {category_table_name} (
                                    id INTEGER,
                                    description TEXT NOT NULL,
                                    amount REAL NOT NULL,
                                    purchase_date DATE NOT NULL,
                                    repeat INTEGER DEFAULT 0
                                )''')

            c.execute(f"SELECT MAX(id) FROM {category_table_name}")
            last_id = c.fetchone()[0]
            id_value = last_id + 1 if last_id else 1

            # Add expense
            c.execute(
                f"INSERT INTO {category_table_name} (id, description, amount, purchase_date, repeat) VALUES (?, ?, ?, ?, ?)",
                (id_value, description_entry.get(), amount, date_entry.get(), repeat_value))

            selected_date = datetime.strptime(date_entry.get(), '%Y-%m-%d').date()

            if repeat_value < 0:
                purchase_date = date_entry.get()
                monthly = int(repeat_value / -30)
                for i in range(12 - selected_date.month):
                    get_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                    next_date = get_date + relativedelta(months=monthly)
                    purchase_date = next_date.strftime('%Y-%m-%d')
                    c.execute(
                        f"INSERT INTO {category_table_name} "
                        f"(id, description, amount, purchase_date, repeat) VALUES (?, ?, ?, ?, ?)",
                        (id_value, description_entry.get().strip(), amount, purchase_date, repeat_value))

            if repeat_value > 0:
                purchase_date = date_entry.get()
                for i in range(int(365 / repeat_value)):
                    get_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                    next_date = get_date + timedelta(repeat_value)
                    purchase_date = next_date.strftime('%Y-%m-%d')
                    c.execute(
                        f"INSERT INTO {category_table_name} "
                        f"(id, description, amount, purchase_date, repeat) VALUES (?, ?, ?, ?, ?)",
                        (id_value, description_entry.get().strip(), amount, purchase_date, repeat_value))

            conn.commit()
            messagebox.showinfo("Success", "Expense added successfully!")
            add_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred: "
                                          f"{str(e)} Amount must be greater than zero")
            add_window.lift()
        finally:
            update_report()
            conn.close()

    category_label = tk.Label(add_window, text="Category:")
    category_label.grid(row=0, column=0, padx=10, pady=5)
    categories = get_categories()
    category_combobox = ttk.Combobox(add_window, values=categories, validate="key",
                                     validatecommand=(add_window.register(validate_len), "%P"))
    category_combobox.grid(row=0, column=1, padx=10, pady=5)
    category_combobox.current(0)

    description_label = tk.Label(add_window, text="Description:")
    description_label.grid(row=1, column=0, padx=10, pady=5)
    description_entry = tk.Entry(add_window, validate="key",
                                 validatecommand=(add_window.register(validate_len), "%P"))
    description_entry.grid(row=1, column=1, padx=10, pady=5)

    amount_label = tk.Label(add_window, text="Amount:")
    amount_label.grid(row=2, column=0, padx=10, pady=5)
    amount_entry = tk.Entry(add_window, validate="key", validatecommand=(add_window.register(validate_amount), "%P"))
    amount_entry.grid(row=2, column=1, padx=10, pady=5)

    date_label = tk.Label(add_window, text="Date:")
    date_label.grid(row=3, column=0, padx=10, pady=5)
    date_entry = DateEntry(add_window, date_pattern="YYYY-MM-DD", state="readonly")
    date_entry.grid(row=3, column=1, padx=10, pady=5)

    repeat_label = tk.Label(add_window, text="Repeat:")
    repeat_label.grid(row=4, column=0, padx=10, pady=5)
    repeat_combobox = ttk.Combobox(add_window, values=["Yearly", "Monthly", "Weekly", "Daily", "Custom"],
                                   state="readonly")
    repeat_combobox.set(0)
    repeat_combobox.grid(row=4, column=1, padx=10, pady=5)

    def show_custom_repeat_window():
        custom_window = tk.Toplevel(add_window)
        custom_window.title("Custom Repeat")
        custom_window.geometry("350x150")

        custom_repeat_label = tk.Label(custom_window, text="Repeat Every...")
        custom_repeat_label.grid(row=0, column=0, padx=10, pady=5)
        custom_repeat_entry = tk.Entry(custom_window,
                                       validate="key", validatecommand=(add_window.register(validate_number), "%P"))
        custom_repeat_entry.grid(row=0, column=1, padx=10, pady=5)

        time_unit_label = tk.Label(custom_window)
        time_unit_label.grid(row=1, column=0, padx=10, pady=5)
        time_unit_combobox = ttk.Combobox(custom_window, values=["Days", "Months", "Years", "Weeks"], state="readonly")
        time_unit_combobox.set("Days")
        time_unit_combobox.grid(row=1, column=1, padx=10, pady=5)

        def add_custom_repeat():
            repeat_value = custom_repeat_entry.get()
            time_unit = time_unit_combobox.get()
            repeat_combobox.set(f"{repeat_value} {time_unit}")
            custom_window.destroy()

        add_custom_button = tk.Button(custom_window, text="Add", command=add_custom_repeat)
        add_custom_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    def toggle_custom_repeat(*args):
        if repeat_combobox.get() == "Custom":
            show_custom_repeat_window()

    repeat_combobox.bind("<<ComboboxSelected>>", toggle_custom_repeat)

    add_button = tk.Button(add_window, text="Add Expense", command=add_to_database)
    add_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)


def delete_expense():
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Expense")

    def confirm_delete_category():
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete this category?"):
            delete_category()

    def delete_category():
        try:
            category = category_combobox.get()
            category_table_name = f'"{category.lower()}"'
            conn = sqlite3.connect("ExpenseTracker.db")
            c = conn.cursor()
            c.execute(f"DROP TABLE IF EXISTS {category_table_name}")
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Category '{category}' deleted successfully!")
            delete_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred: {str(e)}")
            delete_window.lift()
        finally:
            update_report()

    def delete_from_database():
        try:
            if (expense_combobox.get() == "" or expense_combobox.get() == []
                    or expense_combobox.get() == "No Expenses Found"):
                raise Exception("There is nothing selected to be deleted")
            category = category_combobox.get()
            selected_date = date_entry.get()
            expense_description = expense_combobox.get().split("-")[0].strip()

            category_table_name = f'"{category.lower()}"'

            conn = sqlite3.connect("ExpenseTracker.db")
            c = conn.cursor()

            c.execute(f"DELETE FROM {category_table_name} WHERE purchase_date = ? AND description = ?",
                      (selected_date, expense_description))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Expense deleted successfully!")
            delete_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred: {str(e)}")
            delete_window.lift()

        finally:
            update_report()

    category_label = tk.Label(delete_window, text="Category:")
    category_label.grid(row=0, column=0, padx=10, pady=5)
    categories = get_categories()
    category_combobox = ttk.Combobox(delete_window, values=categories, state="readonly")
    category_combobox.grid(row=0, column=1, padx=10, pady=5)
    category_combobox.current(0)

    date_label = tk.Label(delete_window, text="Date:")
    date_label.grid(row=1, column=0, padx=10, pady=5)
    date_entry = DateEntry(delete_window, date_pattern="YYYY-MM-DD", state="readonly")
    date_entry.grid(row=1, column=1, padx=10, pady=5)
    date_entry.set_date(datetime.now().date())

    expense_label = tk.Label(delete_window, text="Expense:")
    expense_label.grid(row=2, column=0, padx=10, pady=5)
    expense_combobox = ttk.Combobox(delete_window, state="readonly")
    expense_combobox.grid(row=2, column=1, padx=10, pady=5)
    expense_combobox.set("")

    def update_expenses_dropdown(*args):
        selected_category = category_combobox.get()
        selected_date = date_entry.get()
        category_table_name = f'"{selected_category.lower()}"'
        conn = sqlite3.connect("ExpenseTracker.db")
        c = conn.cursor()
        c.execute(f"SELECT description, amount FROM {category_table_name} WHERE purchase_date = ?", (selected_date,))
        expenses = [f"{expense[0]} - ${expense[1]:.2f}" for expense in c.fetchall()]
        conn.close()
        expense_combobox.set("")
        expense_combobox['values'] = expenses
        if len(expenses) == 0:
            expense_combobox.set("No Expenses Found")

    update_expenses_dropdown()
    category_combobox.bind("<<ComboboxSelected>>", update_expenses_dropdown)
    date_entry.bind("<<DateEntrySelected>>", update_expenses_dropdown)

    delete_button = tk.Button(delete_window, text="Delete Expense", command=delete_from_database)
    delete_button.grid(row=2, column=2, columnspan=1, padx=10, pady=10)

    delete_category_button = tk.Button(delete_window, text="Delete Category", command=confirm_delete_category)
    delete_category_button.grid(row=0, column=2, columnspan=1, padx=10, pady=10)


root = tk.Tk()
root.title("Expense Tracker")
root.geometry("830x600")


def generate_weekly_report():
    selected_date = date_entry.get_date()
    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    if hasattr(root, 'report_frame'):
        root.report_frame.destroy()

    root.report_frame = tk.Frame(root, bd=2, relief="ridge")
    root.report_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    total_expenses = 0

    # Create a canvas and a scrollbar
    canvas = tk.Canvas(root.report_frame, width=400, height=400)  # Set the desired width and height
    scrollbar = ttk.Scrollbar(root.report_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the labels
    inner_frame = tk.Frame(canvas, width=400, height=400)  # Set the same width and height as the canvas
    inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    global report
    report = ""

    # Function to fetch and display expenses for a given category
    def display_category_expenses(category, row):
        nonlocal total_expenses
        category_table_name = f'"{category.lower()}"'
        conn = sqlite3.connect("ExpenseTracker.db")
        c = conn.cursor()
        c.execute(
            f"SELECT description, amount, id, purchase_date FROM {category_table_name} WHERE purchase_date BETWEEN ? AND ?",
            (start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')))
        expenses = c.fetchall()
        conn.close()

        tk.Label(inner_frame, text=category, font=("Helvetica", 12, "bold")).grid(row=row, column=0, sticky="w")
        category_total = 0
        global report
        if expenses:
            all_expenses = {}
            for i, expense in enumerate(expenses):
                report += f"{expense[3]} | {expense[0]}: {expense[1]:.2f}\n"
                if expense[2] not in all_expenses:
                    all_expenses[expense[2]] = [expense[0], expense[1]]
                else:
                    all_expenses[expense[2]][1] += expense[1]
                category_total += expense[1]  # Add expense amount to category total
            total_expenses += category_total  # Add category total to total expenses
            for i, key in enumerate(all_expenses):
                tk.Label(inner_frame, text=f"{all_expenses[key][0]}: ${all_expenses[key][1]:.2f}").grid(
                    row=row + i + 1, column=0,
                    sticky="w")
            report += f"Total for {category}: ${category_total:.2f}\n"
            report += f"--------------------------------\n"
            tk.Label(inner_frame, text=f"Total for {category}: ${category_total:.2f}").grid(
                row=row + len(expenses) + 1, column=0, sticky="w")
        else:
            report += f"No expenses for this category" + "\n"
            report += f"--------------------------------\n"
            tk.Label(inner_frame, text="No expenses for this category").grid(row=row + 1, column=0, sticky="w")

        # Adjust grid row dynamically to ensure visibility of all labels
        return row + len(expenses) + 2

    # Display expenses for each category
    categories = get_categories()
    current_row = 0
    for idx, category in enumerate(categories):
        report += f"|{category}|\n"
        current_row = display_category_expenses(category, current_row)

    report += f"Total Weekly Expenses: ${total_expenses:.2f}\n"
    # Display total expenses
    tk.Label(inner_frame, text="Total Weekly Expenses:", font=("Helvetica", 12, "bold")).grid(
        row=current_row, column=0, sticky="w")
    tk.Label(inner_frame, text=f"${total_expenses:.2f}", font=("Helvetica", 12, "bold")).grid(
        row=current_row, column=1, sticky="w")


def generate_monthly_report():
    selected_date = date_entry.get_date()
    start_of_month = selected_date.replace(day=1)
    end_of_month = start_of_month.replace(day=calendar.monthrange(selected_date.year, selected_date.month)[1])

    if hasattr(root, 'report_frame'):
        root.report_frame.destroy()

    root.report_frame = tk.Frame(root, bd=2, relief="ridge")
    root.report_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    total_expenses = 0
    category_expenses = {}  # Dictionary to store expenses for each category

    # Create a canvas and a scrollbar
    canvas = tk.Canvas(root.report_frame, width=780, height=400)
    scrollbar = ttk.Scrollbar(root.report_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the labels
    inner_frame = tk.Frame(canvas, width=780, height=400)
    inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    global report
    report = ""

    # Function to fetch and display expenses for a given category
    def display_category_expenses(category, row):
        nonlocal total_expenses
        category_table_name = f'"{category.lower()}"'
        conn = sqlite3.connect("ExpenseTracker.db")
        c = conn.cursor()
        c.execute(
            f"SELECT description, amount, id, purchase_date FROM {category_table_name} WHERE purchase_date BETWEEN ? AND ?",
            (start_of_month.strftime('%Y-%m-%d'), end_of_month.strftime('%Y-%m-%d')))

        expenses = c.fetchall()
        conn.close()

        tk.Label(inner_frame, text=category, font=("Helvetica", 12, "bold")).grid(row=row, column=0, sticky="w")
        category_total = 0
        global report
        if expenses:
            all_expenses = {}
            for i, expense in enumerate(expenses):
                report += f"{expense[3]} | {expense[0]}: {expense[1]:.2f}\n"
                if expense[2] not in all_expenses:
                    all_expenses[expense[2]] = [expense[0], expense[1]]
                else:
                    all_expenses[expense[2]][1] += expense[1]
                category_total += expense[1]  # Add expense amount to category total
            total_expenses += category_total  # Add category total to total expenses
            for i, key in enumerate(all_expenses):
                tk.Label(inner_frame, text=f"{all_expenses[key][0]}: ${all_expenses[key][1]:.2f}").grid(
                    row=row + i + 1, column=0,
                    sticky="w")
            report += f"Total for {category}: ${category_total:.2f}\n"
            report += f"--------------------------------\n"
            tk.Label(inner_frame, text=f"Total for {category}: ${category_total:.2f}").grid(
                row=row + len(expenses) + 1, column=0, sticky="w")
            category_expenses[category] = category_total  # Store category total in the dictionary
        else:
            report += "No expenses for this category" + "\n"
            report += f"--------------------------------\n"
            tk.Label(inner_frame, text="No expenses for this category").grid(row=row + 1, column=0, sticky="w")

        # Adjust grid row dynamically to ensure visibility of all labels
        return row + len(expenses) + 2

    # Display expenses for each category
    categories = get_categories()
    current_row = 0
    for idx, category in enumerate(categories):
        report += f"|{category}|\n"
        current_row = display_category_expenses(category, current_row)

    # Calculate average expenses for each category for the year
    year_start = selected_date.replace(month=1, day=1)
    year_end = selected_date.replace(month=12, day=31)
    annual_expense_totals = {category: 0 for category in categories}
    for category in categories:
        category_table_name = f'"{category.lower()}"'
        conn = sqlite3.connect("ExpenseTracker.db")
        c = conn.cursor()
        c.execute(f"SELECT SUM(amount) FROM {category_table_name} WHERE purchase_date BETWEEN ? AND ?",
                  (year_start.strftime('%Y-%m-%d'), year_end.strftime('%Y-%m-%d')))
        annual_total = c.fetchone()[0]
        if annual_total:
            annual_expense_totals[category] = annual_total
        conn.close()

    # Calculate average expenses for each category for the year
    average_expenses = {}
    for category, total in annual_expense_totals.items():
        average_expenses[category] = total / 12
    report += "Average Monthly Expenses:" + "\n"
    # Display average expenses for each category
    tk.Label(inner_frame, text="Average Monthly Expenses:", font=("Helvetica", 12, "bold")).grid(
        row=current_row, column=0, sticky="w")
    current_row += 1
    for idx, (category, average) in enumerate(average_expenses.items()):
        report += f"{category}: ${average:.2f}\n"
        tk.Label(inner_frame, text=f"{category}: ${average:.2f}", font=("Helvetica", 10)).grid(
            row=current_row + idx, column=0, sticky="w")

    # Display total expenses
    report += f"--------------------------------\n"
    report += f"Total Monthly Expenses: ${total_expenses:.2f}\n"
    tk.Label(inner_frame, text="Total Monthly Expenses:", font=("Helvetica", 12, "bold")).grid(
        row=current_row + len(average_expenses), column=0, sticky="w")
    tk.Label(inner_frame, text=f"${total_expenses:.2f}", font=("Helvetica", 12, "bold")).grid(
        row=current_row + len(average_expenses), column=1, sticky="w")

    # Calculate total monthly expenses
    total_monthly_expenses = sum(category_expenses.values())

    # Display average expenses and comparison with current month's expenses
    for idx, category in enumerate(categories):
        if category in category_expenses:
            category_total = category_expenses[category]
            average_total = average_expenses[category]
            comparison = "higher than average at " if category_total > average_total else "lower than average at "
            if category_total == average_total:
                comparison = "even with the average at "
            comparison_label = (f"Current {category} monthly expenses are {comparison}"
                                f"{(category_total / total_monthly_expenses) * 100:.2f}% of total monthly expenses")
            report += f"--------------------------------\n"
            report += (f"Current {category} monthly expenses are {comparison} "
                       f"{(category_total / total_monthly_expenses) * 100:.2f}% of total monthly expenses\n")
            tk.Label(inner_frame, text=comparison_label).grid(row=current_row + idx, column=1, sticky="e")


def update_report(*args):
    # If frequency is weekly and date is selected, generate weekly report
    if frequency_combobox.get() == "Weekly":
        generate_weekly_report()
    # If frequency is monthly and date is selected, generate monthly report
    elif frequency_combobox.get() == "Monthly":
        generate_monthly_report()


def save_report():
    try:
        report_content = report
        if len(report) == 0:
            raise Exception("Report cannot be empty")
        # Generate the report content based on the selected frequency
        if frequency_combobox.get() == "Weekly":
            generate_weekly_report()
            report_content = report
        elif frequency_combobox.get() == "Monthly":
            generate_monthly_report()
            report_content = report

        # Open a file dialog to select the save location
        file_path = tk.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

        if file_path:
            # Write the report to file
            with open(file_path, "w") as file:
                file.write(report_content)

            messagebox.showinfo("Success", "Report saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred: {str(e)}")


# Combobox for selecting frequency
frequency_label = tk.Label(root, text="Track Expenses:", font=("Helvetica", 14))
frequency_label.grid(row=0, column=0, padx=10, pady=10)

frequency_combobox = ttk.Combobox(root, values=["Weekly", "Monthly"], state="readonly")
frequency_combobox.grid(row=0, column=1, padx=0, pady=0, sticky="w")
frequency_combobox.current(0)
frequency_combobox.bind("<<ComboboxSelected>>", update_report)

date_entry = DateEntry(root, date_pattern="YYYY-MM-DD", state="readonly")
date_entry.set_date(datetime.now().date())
date_entry.grid(row=0, column=2, padx=10, pady=5)
date_entry.bind("<<DateEntrySelected>>", update_report)

add_button = tk.Button(root, text="Add Expense", command=add_expense)
add_button.grid(row=1, column=0, padx=10, pady=0, sticky="w")

delete_button = tk.Button(root, text="Delete Expense", command=delete_expense)
delete_button.grid(row=1, column=0, padx=100, pady=0, sticky="w", columnspan=2)

save_button = tk.Button(root, text="Save Report", command=save_report)
save_button.grid(row=1, column=2, padx=10, pady=10)

generate_weekly_report()  # Generate initial report

root.mainloop()
