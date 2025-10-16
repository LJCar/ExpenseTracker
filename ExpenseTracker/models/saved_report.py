from dataclasses import dataclass
from datetime import date

@dataclass
class SavedReport:
    date: date
    month: int
    year: int
    total: float
    total_monthly_income: float
    income_usage_percent: float
    income_saved: float
    avg_per_day: float
    budget_used_percent: float
    budget_cap: float
    remaining_budget: float
    is_on_track: bool