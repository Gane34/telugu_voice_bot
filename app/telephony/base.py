from abc import ABC, abstractmethod


class TelephonyProvider(ABC):
    @abstractmethod
    def dial(self, number: str):
        raise NotImplementedError

    @abstractmethod
    def answer(self):
        raise NotImplementedError

    @abstractmethod
    def hangup(self):
        raise NotImplementedError

    @abstractmethod
    def send_audio(self, chunks):
        raise NotImplementedError

    @abstractmethod
    def receive_audio(self):
        raise NotImplementedError

    @abstractmethod
    def get_call_status(self):
        raise NotImplementedError
