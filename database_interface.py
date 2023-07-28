from abc import ABC, abstractmethod


class DatabaseInterface(ABC):
    @abstractmethod
    def create_database(self):
        pass

    @abstractmethod
    def get_all_from_table(self, table: str):
        pass

    @abstractmethod
    def clear_catalog(self):
        pass

    @abstractmethod
    def insert_listing(self, id_num: int, model: str, price: int) -> bool:
        pass

    @abstractmethod
    def delete_listing(self, id_num: int):
        pass

    @abstractmethod
    def search_watchlist(self, id_num: int) -> tuple[int, str, int]:
        pass

    @abstractmethod
    def insert_watchlist(self, id_num: int, model: str, price: int) -> bool:
        pass

    @abstractmethod
    def remove_from_watchlist(self, id_num: int):
        pass

    @abstractmethod
    def insert_model(self, model: str) -> bool:
        pass

    @abstractmethod
    def delete_model(self, model: str):
        pass
