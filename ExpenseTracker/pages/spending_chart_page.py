from tkinter import ttk, messagebox
import plotly.graph_objects as go
from datetime import datetime
from plotly.offline import plot
from repositories.saved_report_repository import SavedReportRepository
import tempfile
import webbrowser

def render_spending_chart_page(reports):

    if not reports:
        return messagebox.showinfo("No Reports", "No Saved Reports available.")

    # Sort reports by date
    reports = sorted(reports, key=lambda r: datetime(r.year, r.month, 1))

    months = [f"{datetime(r.year, r.month, 1).strftime('%b %Y')}" for r in reports]
    spent = [r.total for r in reports]
    budget = [r.budget_cap for r in reports]
    income = [r.total_monthly_income for r in reports]
    usage_percent = [r.income_usage_percent for r in reports]
    income_saved = [r.income_saved for r in reports]
    total_saved = sum(income_saved)

    colors = ['green' if percent <= 60 else 'red' for percent in usage_percent]

    fig = go.Figure()

    customdata = []
    for income_val, usage_val, saved_val in zip(income, usage_percent, income_saved):
        # Color-coded usage %
        usage_color = "green" if usage_val <= 60 else "red"
        formatted_usage = f'<span style="color:{usage_color}">{usage_val:.2f}%</span>'

        # Color-coded income saved
        saved_color = "green" if saved_val >= 0 else "red"
        formatted_saved = f'<span style="color:{saved_color}">${saved_val:.2f}</span>'

        customdata.append((income_val, formatted_usage, formatted_saved))

    # Spent Line
    fig.add_trace(go.Scatter(
        x=months,
        y=spent,
        mode='lines+markers',
        name='Spent',
        line=dict(color='blue', width=2),
        marker=dict(color=colors, size=8),
        customdata=customdata,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Spent: $%{y:.2f}<br>"
            "Income: $%{customdata[0]:.2f}<br>"
            "Usage: %{customdata[1]}<br>"
            "Income Saved: %{customdata[2]}<extra></extra>"
        )
    ))

    # Budget Line
    fig.add_trace(go.Scatter(
        x=months,
        y=budget,
        mode='lines+markers',
        name='Budget Cap',
        line=dict(color='gray', width=2, dash='dash'),
        hovertemplate='<b>%{x}</b><br>Budget: $%{y:.2f}<extra></extra>'
    ))


    # Income Saved Annotation
    fig.add_annotation(
        text=f"Total Income Saved: ${total_saved:,.2f}",
        xref="paper", yref="paper",
        x=0.5, y=1.2,
        showarrow=False,
        font=dict(size=16, color="darkgreen", family="Arial"),
        align="center"
    )

    fig.update_layout(
        title="Spending vs Budget Cap YTD",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(x=0.85, y=1.15),
        margin=dict(t=140, l=60, r=40, b=60),
        width=1200,
        height=600,
        plot_bgcolor='rgba(240,248,255,0.8)',
        paper_bgcolor='rgba(255,255,255,1)',
    )

    # Save and open in browser
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
        plot(fig, filename=tmpfile.name, auto_open=False)
        browser_path = tmpfile.name

    webbrowser.open_new_tab(f"file://{browser_path}")