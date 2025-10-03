from dataclasses import dataclass
from typing import Dict

@dataclass
class Report:
    total: float
    average: float
    category_totals: Dict[str, float]
    category_percentages: Dict[str, float]

    transaction_count: int
    days_covered: int
    avg_per_day: float
    projected_total: float
    budget_used_percent: float

    budget_cap: float = 0.0
    remaining_budget: float = 0.0
    is_on_track: bool = True







