from tkinter import ttk, messagebox
import tkinter as tk
from datetime import date
import calendar
from calendar import monthrange
from repositories.report_repository import ReportRepository
from repositories.saved_report_repository import SavedReportRepository

def render_report_page(main_frame, go_back_callback):
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- Title & Navigation ---
    top_frame = ttk.Frame(main_frame)
    top_frame.pack(fill="x", padx=10, pady=10)

    ttk.Button(top_frame, text="⬅️ Back", command=lambda: go_back_callback(main_frame)).pack(side="left")
    ttk.Label(top_frame, text="📊 Monthly Report", font=("Arial", 16)).pack(side="left", padx=10)

    # --- Input Fields Frame ---
    input_frame = ttk.Frame(main_frame)
    input_frame.pack(padx=10, pady=10, fill="x")

    # Month
    month_names = list(calendar.month_name)[1:]
    current_month = date.today().month
    month_var = tk.StringVar(value=month_names[current_month - 1])
    ttk.Label(input_frame, text="Select Month:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    ttk.Combobox(input_frame, textvariable=month_var, values=month_names, state="readonly").grid(row=0, column=1)

    # Year
    current_year = date.today().year
    year_var = tk.StringVar(value=str(current_year))
    ttk.Label(input_frame, text="Select Year:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
    ttk.Combobox(input_frame, textvariable=year_var,
                 values=[str(y) for y in range(current_year - 5, current_year + 1)], width=6, state="readonly").grid(row=0, column=3)

    # Budget Cap
    budget_var = tk.StringVar()
    ttk.Label(input_frame, text="Budget Cap ($):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(input_frame, textvariable=budget_var).grid(row=1, column=1)

    # -- Auto-detect a Saved Report --
    def detect_saved_report(*args):
        selected_month = list(calendar.month_name).index(month_var.get())
        selected_year = int(year_var.get())
        repo = SavedReportRepository()
        saved_budget = repo.get_saved_report_budget(selected_month, selected_year)
        if saved_budget:
            budget_var.set(f"{float(saved_budget):.2f}")
            fetch_report()
        else:
            fetch_report()

    month_var.trace_add("write", detect_saved_report)
    year_var.trace_add("write", detect_saved_report)

    # Fetch Button
    def fetch_report():
        try:
            if budget_var.get() == "":
                reset_report_display()
                return messagebox.showinfo("No Budget", "Add a Budget Cap for the month.")
            month = list(calendar.month_name).index(month_var.get())
            year = int(year_var.get())
            budget = float(budget_var.get())

            repo = ReportRepository()

            report = repo.get_report_by_month(year, month, budget)

            if not report:
                reset_report_display()
                return messagebox.showinfo("No Data", "No transactions found for the selected period.")

            display_report(report)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(input_frame, text="📈 Generate Report", command=fetch_report).grid(row=1, column=3, padx=5)

    # Placeholder for report content
    report_frame = ttk.Frame(main_frame)
    report_frame.pack(padx=10, pady=10, fill="both", expand=True)

    save_button_frame = ttk.Frame(main_frame)
    save_button_frame.pack(fill="x", padx=10, pady=10)

    # Save Report Button
    save_button = ttk.Button(save_button_frame, text="💾 Save Report")
    save_button.pack(side="right")
    save_button.pack_forget()

    def display_report(report):
        for widget in report_frame.winfo_children():
            widget.destroy()

        main_frame.winfo_toplevel().geometry("800x600")

        ttk.Label(report_frame, text=f"📅 Report for {month_var.get()} {year_var.get()}", font=("Arial", 14, "bold")).pack(pady=(0, 10))

        # --- Income Section (Only if income exists) ---
        if report.total_monthly_income > 0:
            # --- Income Summary Section ---
            ttk.Label(report_frame, text="Income Summary", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))

            income_summary_frame = ttk.Frame(report_frame)
            income_summary_frame.pack(fill="x", pady=(5, 5))

            # Left: Income Breakdown Table
            left_income_frame = ttk.Frame(income_summary_frame)
            left_income_frame.pack(side="left", anchor="n", padx=(0, 40))

            if len(report.income_sources) > 1:
                ttk.Label(left_income_frame, text="Source", width=20).grid(row=0, column=0, sticky="w")
                ttk.Label(left_income_frame, text="Amount ($)", width=12).grid(row=0, column=1, sticky="w")
                ttk.Label(left_income_frame, text="% of Income", width=12).grid(row=0, column=2, sticky="w")

                for i, (desc, amt) in enumerate(report.income_sources.items(), start=1):
                    ttk.Label(left_income_frame, text=desc).grid(row=i, column=0, sticky="w")
                    ttk.Label(left_income_frame, text=f"${amt:.2f}").grid(row=i, column=1, sticky="w")
                    ttk.Label(left_income_frame, text=f"{report.income_source_percentages[desc]:.2f}%").grid(row=i,
                                                                                                             column=2,
                                                                                                             sticky="w")
            else:
                single_desc = next(iter(report.income_sources))
                amt = report.income_sources[single_desc]
                ttk.Label(left_income_frame, text="Income Source", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                                                    pady=(5, 2))
                ttk.Label(left_income_frame, text=f"{single_desc}: ${amt:.2f}").pack(anchor="w")

            # Right: Summary Info
            right_income_frame = ttk.Frame(income_summary_frame)
            right_income_frame.pack(side="left", anchor="n")

            income_info = [
                f"Total Income: ${report.total_monthly_income:.2f}",
                f"Income Used: {report.income_usage_percent:.2f}%",
                f"Income Saved: ${report.income_saved:.2f}"
            ]
            for line in income_info:
                ttk.Label(right_income_frame, text=line).pack(anchor="w")

            # --- Horizontal Separator ---
            ttk.Separator(report_frame, orient="horizontal").pack(fill="x", pady=15)


        # Determine if month is ongoing
        today = date.today()
        selected_year = int(year_var.get())
        selected_month = list(calendar.month_name).index(month_var.get())
        is_current_month = (selected_year == today.year and selected_month == today.month)

        # Determine if month is over
        last_day = monthrange(selected_year, selected_month)[1]
        month_is_done = (selected_year < today.year) or \
                        (selected_year == today.year and selected_month < today.month) or \
                        (selected_year == today.year and selected_month == today.month and today.day == last_day)

        info = [
            f"Total Spent: ${report.total:.2f}",
            f"Transactions: {report.transaction_count}",
            f"Avg/Day: ${report.avg_per_day:.2f}",
        ]

        # Only include these if the month isn't finished yet
        if is_current_month:
            info.extend([
                f"Days Covered: {report.days_covered}",
                f"Projected Total: ${report.projected_total:.2f}",
            ])

        info.extend([
            f"Remaining Budget: ${report.remaining_budget:.2f}",
            f"Budget Used: {report.budget_used_percent:.2f}%",
            f"On Track: {'✅ Yes' if report.is_on_track else '❌ No'}"
        ])

        spending_and_categories = ttk.Frame(report_frame)
        spending_and_categories.pack(fill="x", pady=(15, 5))

        # --- Left: Spending Summary ---
        spending_frame = ttk.Frame(spending_and_categories)
        spending_frame.pack(side="left", anchor="n", padx=(0, 40))

        for line in info:
            ttk.Label(spending_frame, text=line).pack(anchor="w")

        # --- Right: Category Breakdown ---
        category_frame = ttk.Frame(spending_and_categories)
        category_frame.pack(side="left", anchor="n")

        ttk.Label(category_frame, text="Category Breakdown", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))

        breakdown_table = ttk.Frame(category_frame)
        breakdown_table.pack()

        ttk.Label(breakdown_table, text="Category", width=20).grid(row=0, column=0, sticky="w")
        ttk.Label(breakdown_table, text="Total ($)", width=12).grid(row=0, column=1, sticky="w")
        ttk.Label(breakdown_table, text="% of Total", width=12).grid(row=0, column=2, sticky="w")

        for i, (cat, amt) in enumerate(report.category_totals.items(), start=1):
            ttk.Label(breakdown_table, text=cat).grid(row=i, column=0, sticky="w")
            ttk.Label(breakdown_table, text=f"${amt:.2f}").grid(row=i, column=1, sticky="w")
            ttk.Label(breakdown_table, text=f"{report.category_percentages[cat]:.2f}%").grid(row=i, column=2,
                                                                                             sticky="w")
        if month_is_done:
            repo = SavedReportRepository()
            selected_month = list(calendar.month_name).index(month_var.get())
            selected_year = int(year_var.get())
            saved_budget = repo.get_saved_report_budget(selected_month, selected_year)

            # Only show save button if there's no saved report OR if the budget differs
            if saved_budget is None or float(f"{saved_budget:.2f}") != float(f"{report.budget_cap:.2f}"):
                save_button.configure(command=lambda: save_report_to_db(report))
                save_button.pack(side="right")
            else:
                save_button.pack_forget()
        else:
            save_button.pack_forget()

    def save_report_to_db(report):
        repo = SavedReportRepository()
        selected_month = list(calendar.month_name).index(month_var.get())
        selected_year = int(year_var.get())
        existing = repo.find_report(selected_month, selected_year)
        confirm = True

        if existing:
            confirm = messagebox.askyesno("Overwrite?", "A report for this month already exists. Overwrite it?")

        if confirm:
            try:
                repo.save_report(report, selected_month, selected_year)
                messagebox.showinfo("Success", f"Report for {month_var.get()} {year_var.get()} saved.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def reset_report_display():
        for widget in report_frame.winfo_children():
            widget.destroy()
        ttk.Label(report_frame, text="📭 No report loaded.", font=("Arial", 12, "italic")).pack(pady=10)
        save_button.pack_forget()

    repo = SavedReportRepository()
    reports = repo.get_all_saved_reports()
    recent_reports = sorted(
        [r for r in reports if r.budget_cap is not None],
        key=lambda r: (r.year, r.month),
        reverse=True
    )[:5]

    if recent_reports:
        estimated_budget = min(r.budget_cap for r in recent_reports)
        budget_var.set(f"{estimated_budget:.2f}")
        fetch_report()