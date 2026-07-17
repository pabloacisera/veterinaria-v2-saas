from abc import ABC, abstractmethod


class MercadoPagoPlatformService(ABC):
    @abstractmethod
    def create_preapproval(self, plan: str, email: str, success_url: str) -> dict: ...

    @abstractmethod
    def get_preapproval(self, preapproval_id: str) -> dict: ...
