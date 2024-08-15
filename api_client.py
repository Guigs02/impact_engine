from abc import ABC, abstractmethod
from typing import Any, List, Dict

class APIClient(ABC):
    @abstractmethod
    def set_params(self, q: str = "", sort: str = None, size: str = "1000", fields: List[str] = []) -> None:
        pass

    @abstractmethod
    def set_record(self, record: str) -> None:
        pass

    @abstractmethod
    def fetch_all_pages(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def process_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_data(self) -> List[Dict[str, Any]]:
        pass
