import logging

from .FetchBase.FetchBase import FetchBase
from .FetchBase.utils import DEBUG, send_request_multiple, send_data
from .FetchBase.ReManga import ReManga


class Fetch_mangahub(FetchBase):
    def __init__(self, bot, running, check_id):
        self.running = running
        self.check_id = check_id
        self.bot = bot

        self.fetch_name = 'mangahub'
        self.endpoint = 'https://mangahub.ru/search/manga?query=&catalog_view=grid&page={}'

    async def prepare(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage start')

        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage complete')

    async def run(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage start')

        logging.info(f'FETCH {self.fetch_name.upper()}: run stage complete')

    async def complete(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage start')

        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage complete')