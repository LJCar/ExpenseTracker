from abc import ABC, abstractmethod
from typing import List
from ..models.transaction import Transaction
from datetime import date

class ITransaction(ABC):

    @abstractmethod
    def add_transaction(self, transaction: Transaction) -> bool:
        pass

    @abstractmethod
    def get_all_transactions(self) -> List[Transaction] | None:
        pass

    @abstractmethod
    def get_transactions_by_type(self, t_type: str) -> List[Transaction] | None:
        pass

    @abstractmethod
    def get_transaction_by_description(self, description: str) -> List[Transaction] | None:
        pass

    @abstractmethod
    def get_transactions_by_category_id(self, c_id: int) -> List[Transaction] | None:
        pass

    @abstractmethod
    def get_transactions_by_month(self, year: int, month: int) -> List[Transaction] | None:
        pass

    @abstractmethod
    def get_transactions_by_year(self, year: int) -> List[Transaction] | None:
        pass

    @abstractmethod
    def get_transaction_by_week(self, input_date: date) -> List[Transaction] | None:
        pass

    @abstractmethod
    def get_transaction_by_day(self, input_date: date) -> List[Transaction] | None:
        pass

    @abstractmethod
    def delete_transaction(self, transaction: Transaction) -> bool:
        pass