from abc import ABC, abstractmethod
from typing import List
from models.category import Category

class ICategory(ABC):

    @abstractmethod
    def get_all_categories(self) -> List[Category]:
        pass

    @abstractmethod
    def get_category_by_id(self, category_id: int) -> Category | None:
        pass

    @abstractmethod
    def get_category_by_name(self, category_name: str) -> Category | None:
        pass

    @abstractmethod
    def add_category(self, category: Category) -> None:
        pass

    @abstractmethod
    def delete_category_by_name(self, category_name: str) -> None:
        pass
