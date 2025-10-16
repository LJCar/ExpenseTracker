from abc import ABC, abstractmethod
from typing import List
from models.saved_report import SavedReport
from models.report import Report

class ISavedReport(ABC):

    @abstractmethod
    def save_report(self, report: Report, month: int, year: int) -> bool:
        pass

    @abstractmethod
    def find_report(self, month: int, year: int) -> bool:
        pass

    @abstractmethod
    def get_all_saved_reports(self) -> List[SavedReport] | None:
        pass

    @abstractmethod
    def get_saved_report_budget(self, month: int, year: int) -> float | None:
        pass