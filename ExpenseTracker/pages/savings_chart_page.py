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

    # --- Cumulative saved calculation ---
    cumulative_saved = []
    running_total = 0
    for val in income_saved:
        running_total += val
        cumulative_saved.append(running_total)
    total_saved = running_total

    # --- Color markers based on usage % ---
    colors = ["green" if percent <= 60 else "red" for percent in usage_percent]

    # --- Build figure ---
    fig = go.Figure()

    # --- Custom hover data for Spent line ---
    customdata = []
    for spent_val, income_val, usage_val, saved_val, budget_val in zip(spent, income, usage_percent, income_saved,
                                                                       budget):
        # Color-coded usage %
        usage_color = "green" if usage_val <= 60 else "red"
        formatted_usage = f'<span style="color:{usage_color}">{usage_val:.2f}%</span>'

        # Color-coded Spent (red if over budget)
        spent_color = "red" if spent_val > budget_val else "black"
        formatted_spent = f'<b><span style="color:{spent_color}">Spent: ${spent_val:,.2f}</span></b>'

        # Append customdata tuple
        customdata.append((income_val, formatted_usage, budget_val, formatted_spent))

    # --- Spent Line (Red) ---
    fig.add_trace(go.Scatter(
        x=months,
        y=spent,
        mode="lines+markers",
        name="Spent",
        line=dict(color="#C62828", width=2),
        marker=dict(color=colors, size=8),
        customdata=customdata,
        hovertemplate=(
            "%{customdata[3]}<br>"  # ✅ dynamic color spent line
            "Budget Cap: $%{customdata[2]:,.2f}<br>"
            "Income: $%{customdata[0]:,.2f}<br>"
            "Usage: %{customdata[1]}<extra></extra>"
        )
    ))

    # --- Monthly Income Saved (Green Line) with color-coded hover ---
    hover_colors = ["green" if val > 0 else "red" for val in income_saved]
    formatted_savings = [
        f"<span style='color:{'green' if val > 0 else 'red'}'>${val:,.2f}</span>"
        for val in income_saved
    ]

    fig.add_trace(go.Scatter(
        x=months,
        y=income_saved,
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