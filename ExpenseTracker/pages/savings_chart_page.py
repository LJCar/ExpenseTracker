from tkinter import ttk, messagebox
import plotly.graph_objects as go
from datetime import datetime
from plotly.offline import plot
import os
import tempfile
import webbrowser

def render_savings_chart_page(reports):
    if not reports:
        return messagebox.showinfo("No Reports", "No Saved Reports available.")

    # --- Sort reports by date ---
    reports = sorted(reports, key=lambda r: datetime(r.year, r.month, 1))

    # --- Prepare data ---
    months = [f"{datetime(r.year, r.month, 1).strftime('%b %Y')}" for r in reports]
    spent = [r.total for r in reports]
    budget = [r.budget_cap for r in reports]
    income = [r.total_monthly_income for r in reports]
    usage_percent = [r.income_usage_percent for r in reports]
    income_saved = [r.income_saved for r in reports]
    monthly_change = [inc - exp for inc, exp in zip(income, spent)]

    # --- Cumulative saved calculation ---
    cumulative_saved = []
    running_total = 0
    for change in monthly_change:
        running_total += change
        cumulative_saved.append(running_total)

    total_saved = running_total

    # --- Color markers based on spending vs income ---
    colors = []
    for inc, spent_val in zip(income, spent):
        if inc == 0:
            colors.append("gray")  # No income data for this month
        elif spent_val / inc <= 0.6:
            colors.append("green")  # Spent <= 60% of income
        else:
            colors.append("red")

    # --- Build figure ---
    fig = go.Figure()

    # --- Custom hover data for Spent line ---
    customdata = []
    for spent_val, income_val, usage_val, saved_val, budget_val in zip(spent, income, usage_percent, income_saved,
                                                                       budget):
        # Recalculate usage to handle >100% logic
        if income_val > 0:
            usage_val = (spent_val / income_val) * 100
        else:
            usage_val = None  # no income that month

        # Color-coded usage %
        usage_color = "green" if usage_val and usage_val <= 60 else "red" if usage_val else "gray"
        formatted_usage = f'<span style="color:{usage_color}">{usage_val:.2f}%</span>' if usage_val else ""

        # Color-coded Spent (red if over budget)
        spent_color = "red" if spent_val > budget_val else "black"
        formatted_spent = f'<b><span style="color:{spent_color}">Spent: ${spent_val:,.2f}</span></b>'

        # Conditional income and usage text
        if income_val > 0:
            income_text = f"Income: ${income_val:,.2f}<br>"
            usage_text = f"Usage: {formatted_usage}<br>" if usage_val else ""
            no_income_note = ""
        else:
            income_text = ""
            usage_text = ""
            no_income_note = (
                "<span style='color:gray; font-style:italic; font-size:11px; "
                "margin-left:6px; display:block;'>↳ No income data for this month</span>"
            )

        hover_html = (
            f"{formatted_spent}<br>"
            f"Budget Cap: ${budget_val:,.2f}<br>"
            f"{income_text}"
            f"{usage_text}"
            f"{no_income_note}"
        )

        customdata.append(hover_html)

    # --- Spent Line (Red) ---
    fig.add_trace(go.Scatter(
        x=months,
        y=spent,
        mode="lines+markers",
        name="Spent",
        line=dict(color="#C62828", width=2),
        marker=dict(color=colors, size=8),
        customdata=customdata,
        hovertemplate="%{customdata}<extra></extra>"
    ))

    # --- Monthly Income Saved (Green Line) with + / - logic ---
    hover_colors = ["green" if change > 0 else "red" for change in monthly_change]
    formatted_savings = [
        f"<span style='color:{'green' if change > 0 else 'red'}'>"
        f"{'+' if change > 0 else ''}${change:,.2f}</span>"
        for change in monthly_change
    ]

    fig.add_trace(go.Scatter(
        x=months,
        y=monthly_change,
        mode="lines+markers",
        name="Monthly Income Saved",
        line=dict(color="#2E7D32", width=2),
        marker=dict(color=hover_colors, size=6),
        fill="tozeroy",
        fillcolor="rgba(67,160,71,0.1)",
        customdata=formatted_savings,
        hovertemplate="<b>Monthly Income Saved:</b> %{customdata}<extra></extra>"
    ))

    # --- Cumulative Income Saved (Dotted Green Line) ---
    fig.add_trace(go.Scatter(
        x=months,
        y=cumulative_saved,
        mode="lines+markers",
        name="Savings",
        line=dict(color="#81C784", width=2, dash="dot"),
        marker=dict(color="#66BB6A", size=6),
        hovertemplate="<b>Savings: $%{y:,.2f}</b><extra></extra>"
    ))

    # --- Annotation for Total Saved ---
    fig.add_annotation(
        text=f"Total Income Saved (YTD): ${total_saved:,.2f}",
        xref="paper", yref="paper",
        x=0.5, y=1.18,
        showarrow=False,
        font=dict(size=16, color="darkgreen", family="Arial"),
        align="center"
    )

    # --- Layout ---
    fig.update_layout(
        title="YTD Spending and Savings Progress",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(x=0.76, y=1.15),
        margin=dict(t=140, l=60, r=40, b=60),
        width=1200,
        height=600,
        plot_bgcolor="rgba(240,248,255,0.8)",
        paper_bgcolor="rgba(255,255,255,1)",
    )

    # --- Save and open in browser ---
    report_name = f"Savings_Chart_{datetime.now().strftime('%Y')}.html"
    tmp_dir = tempfile.gettempdir()
    browser_path = os.path.join(tmp_dir, report_name)

    plot(fig, filename=browser_path, auto_open=False)
    webbrowser.open_new_tab(f"file://{browser_path}")