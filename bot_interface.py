from abc import ABC, abstractmethod


class BotInterface(ABC):
    @abstractmethod
    def start_bot(self):
        pass

    @abstractmethod
    def stop_bot(self):
        pass

    @abstractmethod
    def send_message(self, message: str):
        pass

    @abstractmethod
    def send_listing_notification(self, model: str, price: int, link: str, watched: bool, image=None):
        pass

    @abstractmethod
    def send_table(self, table_type: str):
        pass

