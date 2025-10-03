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

            c.execute("""SELECT SUM(amount), AVG(amount), COUNT(*) 
                         FROM transactions 
                         WHERE type = 'DEBIT' AND date BETWEEN ? AND ?""",
                      (start_date.isoformat(), end_date.isoformat()))
            total, average, tx_count = c.fetchone()
            if total is None:
                return None

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
                average=average,
                category_totals=category_totals,
                category_percentages=category_percentages,
                transaction_count=tx_count,
                days_covered=days_covered,
                avg_per_day=round(avg_per_day, 2),
                projected_total=projected_total,
                budget_used_percent=budget_used_percent,
                budget_cap=budget_cap,
                remaining_budget=remaining_budget,
                is_on_track=is_on_track
            )


    def get_report_by_month(self, year: int, month: int) -> Report | None:
        start_date = date(year, month, 1)
        end_day = monthrange(year, month)[1]
        end_date = date(year, month, end_day)
        report = self.get_report_by_term(start_date, end_date)

        if not report:
            return None

        target_month_str = f"{year}-{month:02d}"
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""
                    SELECT AVG(month_total)
                    FROM (
                        SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS month_total
                        FROM transactions
                        WHERE t_type = 'DEBIT' AND strftime('%Y-%m', date) != ?
                        GROUP BY month
                    )
                """, (target_month_str,))
            avg_month_total = c.fetchone()[0] or 0
            report.average = round(avg_month_total, 2)

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

