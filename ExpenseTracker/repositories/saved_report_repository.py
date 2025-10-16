import sqlite3
from datetime import date
from typing import List
from interfaces.isaved_report import SavedReport, ISavedReport
from models.report import Report
from services.db import DB_NAME

class SavedReportRepository(ISavedReport):

    def save_report(self, report: Report, month: int, year: int) -> bool:
        try:
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                report_date = date(year, month, 1)

                c.execute('''
                        INSERT OR REPLACE INTO saved_reports (
                            date, month, year,
                            total, total_monthly_income, income_usage_percent,
                            income_saved, avg_per_day, budget_used_percent,
                            budget_cap, remaining_budget, is_on_track
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                    report_date, month, year,
                    report.total,
                    report.total_monthly_income,
                    report.income_usage_percent,
                    report.income_saved,
                    report.avg_per_day,
                    report.budget_used_percent,
                    report.budget_cap,
                    report.remaining_budget,
                    int(report.is_on_track)
                ))
                conn.commit()
                return True
        except Exception as e:
            print("Error saving report:", e)
            return False

    def find_report(self, month: int, year: int) -> bool:
        try:
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute("SELECT 1 FROM saved_reports WHERE month = ? AND year = ?", (month, year))
                return c.fetchone() is not None
        except Exception as e:
            print("Error checking for saved report:", e)
            return False

    def get_all_saved_reports(self) -> List[SavedReport] | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""
                            SELECT date, month, year, total, total_monthly_income, income_usage_percent,
                                   income_saved, avg_per_day, budget_used_percent,
                                   budget_cap, remaining_budget, is_on_track
                            FROM saved_reports
                            ORDER BY year, month
                        """)
            rows = c.fetchall()

            if not rows:
                return None

            reports = [
                SavedReport(
                    date=date.fromisoformat(row[0]),
                    month=row[1],
                    year=row[2],
                    total=row[3],
                    total_monthly_income=row[4],
                    income_usage_percent=row[5],
                    income_saved=row[6],
                    avg_per_day=row[7],
                    budget_used_percent=row[8],
                    budget_cap=row[9],
                    remaining_budget=row[10],
                    is_on_track=bool(row[11])
                )
                for row in rows
            ]
            return reports

    def get_saved_report_budget(self, month: int, year: int) -> float | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT budget_cap
                FROM saved_reports
                WHERE month = ? AND year = ?
            """, (month, year))
            result = c.fetchone()
            return result[0] if result else None

