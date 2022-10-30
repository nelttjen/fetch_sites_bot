import logging
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

    async def execute(self):
        try:
            await self.prepare()
            await self.run()
            await self.complete()
            return True
        except Exception as e:
            logging.critical(f'FETCH {self.fetch_name.upper()}: FAILED, Error message: {e}')
            return False


