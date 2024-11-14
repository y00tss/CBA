from abc import ABC, abstractmethod


class DocumentWorkAbstract(ABC):
    @abstractmethod
    async def start_flow(self):
        pass

    @abstractmethod
    async def create_report(self):
        pass

    @abstractmethod
    async def get_updated_document(self, user_name: str):
        pass
