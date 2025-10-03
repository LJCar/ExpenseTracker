from dataclasses import dataclass
from typing import Literal
from datetime import date

@dataclass
class Transaction:
    id: int | None
    description: str
    amount: float
    type: Literal["DEBIT", "CREDIT"]
    category_id: int
    date: date