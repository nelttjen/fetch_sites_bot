import asyncio
import copy
import logging
import aiohttp
import pyquery

from .FetchBase.FetchBase import FetchBase
from .FetchBase.utils import DEBUG, send_request_multiple, send_data, headers
from .FetchBase.ReManga import ReManga


class Fetch_mangaovh(FetchBase):
    def __init__(self, bot, running, check_id):
        self.running = running
        self.check_id = check_id
        self.bot = bot

        self.fetch_name = 'mangaovh'
        self.endpoint = 'https://api.manga.ovh/book/catalog'
        self.endpoint_not_api = 'https://manga.ovh/manga/{}'
        self.payload = {
            "pagination": {
                "page": 0,
                "size": 100000 if not DEBUG else 20
            },
            "sort": {
                "field": "VIEWS_COUNT",
                "order": "DESC"
            },
            "where": {
                "longStrip": None,
                "type": "COMIC"
            }
        }

        self.accuracy = 0.65

        self.prepare_count = 0
        self.prepare_items = []

        self.fetches = 0
        self.re_diff_items = []

    async def process_prepare(self, session, item):
        try:
            link = self.endpoint_not_api.format(item['id'])
            ru_name = item["name"].get('ru') or ''
            en_name = item["name"].get('en') or ''
            og_name = item["name"].get('original') or ''

            self.prepare_items.append({
                'title_ru': ru_name,
                'title_en': en_name,
                'title_og': og_name,
                'dir': link
            })
        except Exception as e:
            logging.error(f'{item["name"]["ru"]}: error, skipping, message: {e}')
        finally:
            self.prepare_count += 1

    async def prepare(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage start')
        async with aiohttp.ClientSession(headers=headers) as session:
            all_titles = await send_request_multiple(session, self.endpoint, response_type='json', method='post',
                                                     post_payload=self.payload)
            for item in all_titles:
                asyncio.create_task(self.process_prepare(session, item))
                await asyncio.sleep(0.5)
            while self.prepare_count < len(all_titles):
                await asyncio.sleep(3)

        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage complete')

    async def run(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage start')
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage complete')

    async def complete(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage start')
        await send_data(self.prepare_items, self.running, self.check_id, self.bot,
                        self.fetch_name, ru_key='title_ru', en_key='title_en', orig_key='title_og',
                        dir='dir')
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage complete')