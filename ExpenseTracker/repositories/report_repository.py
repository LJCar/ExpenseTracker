import sqlite3
from datetime import date, timedelta
from calendar import monthrange
from interfaces.ireport import IReport
from models.report import Report
from services.db import DB_NAME

class ReportRepository(IReport):

    def get_report_by_term(self, start_date: date, end_date: date, budget_cap: float) -> Report | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()

            c.execute("""SELECT SUM(amount), COUNT(*) 
                         FROM transactions 
                         WHERE type = 'DEBIT' AND date BETWEEN ? AND ?""",
                      (start_date.isoformat(), end_date.isoformat()))
            total, tx_count = c.fetchone()
            if total is None:
                return None

            c.execute("""SELECT SUM(amount)
                         FROM transactions 
                         WHERE type = 'CREDIT' AND date BETWEEN ? AND ?""",
                      (start_date.isoformat(), end_date.isoformat()))
            total_income = c.fetchone()[0] or 0.0

            income_usage_percent = round((total / total_income * 100), 2) if total_income > 0 else 0.0
            income_saved = total_income - total if total_income > 0 else 0.0

            c.execute("""
                SELECT LOWER(TRIM(description)) AS normalized_desc, SUM(amount)
                FROM transactions
                WHERE type = 'CREDIT' AND date BETWEEN ? AND ?
                GROUP BY normalized_desc
            """, (start_date.isoformat(), end_date.isoformat()))

            income_rows = c.fetchall()
            cleaned_income_sources = {}
            for raw_desc, amt in income_rows:
                desc_clean = raw_desc.strip().title()
                if desc_clean in cleaned_income_sources:
                    cleaned_income_sources[desc_clean] += amt
                else:
                    cleaned_income_sources[desc_clean] = amt

            income_sources = cleaned_income_sources

            income_source_percentages = {
                desc: round((amt / total_income * 100), 2) for desc, amt in income_sources.items()
            } if total_income > 0 else {}


            c.execute("""
                SELECT categories.name, SUM(transactions.amount)
                FROM transactions
                JOIN categories ON transactions.category_id = categories.id
                WHERE transactions.type = 'DEBIT'
                AND transactions.date BETWEEN ? AND ?
                GROUP BY transactions.category_id
            """, (start_date.isoformat(), end_date.isoformat()))
            rows = c.fetchall()

            category_totals = {row[0]: row[1] for row in rows}
            category_percentages = {name: round((amt / total * 100), 2) for name, amt in category_totals.items()}

            today = date.today()
            if start_date.year == today.year and start_date.month == today.month:
                end_date = min(end_date, today)
            days_covered = (end_date - start_date).days + 1
            avg_per_day = total / days_covered if days_covered else 0
            full_month_days = monthrange(start_date.year, start_date.month)[1]
            projected_total = round(avg_per_day * full_month_days, 2)

            remaining_budget = round(budget_cap - total, 2)
            is_on_track = projected_total <= budget_cap

            if total is not None:
                budget_used_percent = round((total / budget_cap) * 100, 2) if budget_cap else 0.0

            return Report(
                total=total,
                category_totals=category_totals,
                category_percentages=category_percentages,
                total_monthly_income=total_income,
                income_usage_percent=income_usage_percent,
                income_saved=income_saved,
                income_sources=income_sources,
                income_source_percentages=income_source_percentages,
                transaction_count=tx_count,
                days_covered=days_covered,
                avg_per_day=round(avg_per_day, 2),
                projected_total=projected_total,
                budget_used_percent=budget_used_percent,
                budget_cap=budget_cap,
                remaining_budget=remaining_budget,
                is_on_track=is_on_track
            )


    def get_report_by_month(self, year: int, month: int, budget_cap: float) -> Report | None:
        start_date = date(year, month, 1)
        full_month_days = monthrange(year, month)[1]
        end_date = date(year, month, full_month_days)

        today = date.today()
        if year == today.year and month == today.month:
            end_date = today
        report = self.get_report_by_term(start_date, end_date, budget_cap)

        if not report:
            return None

        return report

    def get_report_by_year(self, year: int) -> Report | None:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        return self.get_report_by_term(start_date, end_date)

    def get_report_by_week(self, input_date: date) -> Report | None:
        start_date = input_date - timedelta(days=input_date.weekday())
        end_date = start_date + timedelta(days=6)
        return self.get_report_by_term(start_date, end_date)

    def get_report_by_day(self, input_date: date) -> Report | None:
        return self.get_report_by_term(input_date, input_date)

