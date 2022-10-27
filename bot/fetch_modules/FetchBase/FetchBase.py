from abc import abstractmethod, ABC


class FetchBase(ABC):

    @abstractmethod
    async def prepare(self):
        pass

    @abstractmethod
    async def run(self):
        pass

    @abstractmethod
    async def complete(self):
        pass

    @abstractmethod
    async def execute(self):
        pass


