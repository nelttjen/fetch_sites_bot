from .FetchBase.FetchBase import FetchBase
import requests
import logging
import pyquery as pq
from asyncio import sleep
import aiohttp
from bot.fetch_modules.FetchBase.utils import send_request_multiple, send_data, headers


class Fetch_shikimori(FetchBase):
    def __init__(self, bot, running, check_id):
        self.running = running
        self.check_id = check_id
        self.bot = bot

        self.fetch_name = 'shikimori'
        self.accuracy = 0.65
        self.max_page = 0

        self.endpoint = 'https://shikimori.one/mangas/page/'
        self.output = []

    async def _get_max_pages(self):
        first_page_json = requests.get(url=f'{self.endpoint}1.json', headers=headers).json()
        return first_page_json['pages_count']

    async def _fetch_page(self, session, url):
        result = await send_request_multiple(session=session, url=url)
        if result:
            query = pq.PyQuery(result)
            container = query('.cc-entries > article.c-column')
            for item in container.items():
                link = item('a').attr('href')
                other_names_data = await send_request_multiple(session=session, url=f'{link}/other_names')
                original_name = list(pq.PyQuery(other_names_data).find('.line-container .value').items())[0]

                self.output.append({
                    'ru_title': item('span.name-ru').text(),
                    'en_title': item('span.name-en').text(),
                    'orig_title': original_name.text(),
                    'dir': link
                })

                await sleep(0.3)

    async def prepare(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage start')
        self.max_page = await self._get_max_pages()

    async def run(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage start')
        async with aiohttp.ClientSession(headers=headers) as session:
            #await self._fetch_page(session=session, url=f'{self.endpoint}1')
            for page in range(1, self.max_page + 1):
                await self._fetch_page(session=session, url=f'{self.endpoint}{page}')
                await sleep(0.5)

            logging.info(f'FETCH {self.fetch_name.upper()}: run stage complete')

    async def complete(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage start')
        await send_data(self.output, self.running, self.check_id, self.bot, self.fetch_name,
                        ru_key='ru_title', en_key='en_title', orig_key='orig_title', dir="dir") 
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage complete')

                



    