from abc import ABC, abstractmethod
from datetime import date
from models.report import Report


class IReport(ABC):

    @abstractmethod
    def get_report_by_month(self, year: int, month: int) -> Report | None:
        pass

    @abstractmethod
    def get_report_by_year(self, year: int) -> Report | None:
        pass

    @abstractmethod
    def get_report_by_week(self, input_date: date) -> Report | None:
        pass

    @abstractmethod
    def get_report_by_day(self, input_date: date) -> Report | None:
        pass

    @abstractmethod
    def get_report_by_term(self, start_date: date, end_date: date, budget_cap: float) -> Report | None:
        pass

