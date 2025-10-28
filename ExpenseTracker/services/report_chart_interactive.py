import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
from collections import defaultdict
import calendar


def export_interactive_chart(report, output_path, month_name, year):
    """Interactive spending chart with color-coded total."""

    # --- Data prep ---
    month_index = list(calendar.month_name).index(month_name)
    days_in_month = calendar.monthrange(int(year), month_index)[1]
    days = list(range(1, days_in_month + 1))
    dates = [datetime(int(year), month_index, d) for d in days]

    categories = sorted(report.category_totals.keys())
    daily_spend = {cat: defaultdict(float) for cat in categories}
    total_daily = defaultdict(float)

    for tx in report.transactions:
        if str(tx.get("type", "")).strip().upper() == "DEBIT":
            try:
                d = datetime.strptime(tx["date"], "%Y-%m-%d").day
            except Exception:
                continue
            cat = tx.get("category", "").strip()
            amt = float(tx.get("amount", 0))
            matched = next((c for c in categories if c.lower() == cat.lower()), None)
            if matched:
                daily_spend[matched][d] += amt
            total_daily[d] += amt

    totals = [total_daily[d] for d in days]
    total_monthly = sum(totals)
    budget_cap = float(getattr(report, "budget_cap", 0.0))

    # --- Color for title total ---
    total_color = "#C62828" if budget_cap > 0 and total_monthly > budget_cap else "#2E7D32"

    # --- Colors for bars ---
    palette = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#17becf", "#ff7f0e", "#8c564b"]
    color_map = {cat: palette[i % len(palette)] for i, cat in enumerate(categories)}

    # --- Hover text ---
    total_hover = []
    for d in days:
        total = total_daily[d]
        if total == 0:
            total_hover.append("<b>Total:</b> $0.00<br><i>No spending recorded</i>")
            continue
        lines = []
        for cat in categories:
            amt = daily_spend[cat][d]
            if amt > 0:
                color = color_map[cat]
                swatch = f"<span style='color:{color};font-size:14px'>&#9632;</span>"
                lines.append(f"{swatch} <span style='font-weight:600'>{cat.capitalize()}</span>: ${amt:,.2f}")
        breakdown_html = "<br>".join(lines)
        total_hover.append(f"<b>Total:</b> ${total:,.2f}" + (f"<br><br>{breakdown_html}" if breakdown_html else ""))

    # --- Figure setup ---
    fig = go.Figure()

    # Total spending line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=totals,
            mode="lines+markers",
            name="Total Spending",
            line=dict(color="gray", width=2, dash="dot"),
            marker=dict(color="#FFA500", size=7),
            text=total_hover,
            hovertemplate="%{text}<extra></extra>",
        )
    )

    # Category bars
    for cat in categories:
        fig.add_trace(
            go.Bar(
                x=dates,
                y=[daily_spend[cat][d] for d in days],
                name=cat.capitalize(),
                marker_color=color_map[cat],
                opacity=0.7,
                visible="legendonly",
                hoverinfo="skip",
            )
        )

    # --- Title text (with budget cap below if present) ---
    title_lines = [
        f"<b>Daily Spending Trends — {month_name} {year}</b>",
        f"<span style='font-size:18px; color:{total_color};'>${total_monthly:,.2f}</span>",
    ]
    if budget_cap > 0:
        title_lines.append(
            f"<span style='font-size:14px; color:#888;'>Budget Cap: ${budget_cap:,.2f}</span>"
        )

    base_title = "<br>".join(title_lines)

    # --- Layout ---
    fig.update_layout(
        title=dict(
            text=base_title,
            x=0.5,
            y=0.90,  # lower title slightly to avoid overlap
            xanchor="center",
            yanchor="top",
        ),
        xaxis_title="Day of Month",
        yaxis_title="Amount ($)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(title="Categories", x=1.02, y=1),
        margin=dict(l=60, r=180, t=100, b=60),  # extra top margin
        height=720,
        font=dict(size=13),
        hoverlabel=dict(namelength=0, align="left"),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.45, y=1.18,  # push buttons higher
                showactive=False,
                bgcolor="#f5f5f5",
                bordercolor="#ccc", borderwidth=1,
                pad={"r": 10, "t": 6, "b": 6, "l": 10},
                buttons=[
                    dict(
                        label="Focus Mode",
                        method="update",
                        args=[
                            {"visible": [True] + [False] * len(categories)},
                            {"title.text": base_title},
                        ],
                    ),
                    dict(
                        label="Detail Mode",
                        method="update",
                        args=[
                            {"visible": [True] + [True] * len(categories)},
                            {"title.text": base_title},
                        ],
                    ),
                ],
            )
        ],
        xaxis=dict(
            tickformat="%d",
            dtick="D1",
            hoverformat="%A, %b %-d",
            range=[
                datetime(int(year), month_index, 1) - timedelta(days=0.5),
                datetime(int(year), month_index, days_in_month) + timedelta(days=0.5),
            ],
        ),
    )

    # --- Export ---
    html_path = os.path.splitext(output_path)[0] + "_Interactive.html"
    fig.write_html(html_path)
    return html_path