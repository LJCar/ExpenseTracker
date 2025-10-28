from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Report:
    total: float
    category_totals: Dict[str, float]
    category_percentages: Dict[str, float]

    total_monthly_income: float
    income_usage_percent: float
    income_sources: Dict[str, float]
    income_source_percentages: Dict[str, float]
    income_saved: float

    transaction_count: int
    days_covered: int
    avg_per_day: float
    projected_total: float
    budget_used_percent: float

    budget_cap: float = 0.0
    remaining_budget: float = 0.0
    is_on_track: bool = True
    transactions: list[dict] = field(default_factory=list)







