import asyncio
import copy
import logging
import aiohttp
import pyquery as pq

from .FetchBase.FetchBase import FetchBase
from .FetchBase.ReManga import ReManga
from .FetchBase.utils import send_request_multiple, DEBUG, headers, send_data


class Fetch_mangachan(FetchBase):
    def __init__(self, bot, running, check_id):
        self.running = running
        self.check_id = check_id
        self.bot = bot

        self.fetch_name = 'mangachan'
        self.endpoint = 'https://manga-chan.me/mostfavorites?offset={}'
        self.accuracy = 0.65

        self.prepare_items = []

        self.re_diff_items = []
        self.fetches = 0

    async def process_result(self, result):
        try:
            with open('test.html', 'w', encoding='utf-8') as f:
                f.write(result)
            query = pq.PyQuery(result)
            items = list(query.find('.content_row').items())
            for item in items:
                names = item.find('a.title_link').text()
                name_en = names.split('(')[0].strip().replace("'s", '')
                name_ru = names.split('(')[1].replace(')', '')
                chapter = int(item.find('.item2 > span > b').text().replace(' глав', ''))
                self.prepare_items.append({
                    'title_ru': name_ru,
                    'title_en': name_en,
                    'title_og': '',
                    'chapter': chapter
                })
            return True
        except:
            return False

    async def proceed_remanga(self, item, sesssion):
        try:
            name = item.get('title_en')
            chapter = item.get('chapter')
            re_query = await ReManga.find_remanga(name, sesssion)
            re_items = await ReManga.compare_remanga_reverse(name, chapter, re_query, required_rating=self.accuracy)
            if re_items:
                __copy = copy.deepcopy(item)
                __copy['remanga'] = re_items
                self.re_diff_items.append(__copy)
        finally:
            self.fetches += 1

    async def prepare(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage start')
        async with aiohttp.ClientSession(headers=headers) as session:
            for i in range(0, 9999999 if not DEBUG else 20, 20):
                await asyncio.sleep(0.5)
                result = await send_request_multiple(session, self.endpoint.format(i))
                if not result or not await self.process_result(result):
                    logging.error(f'FETCH {self.fetch_name.upper()}: {self.endpoint.format(i)} - failed, skipping')
                    continue
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage complete')

    async def run(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage start')
        async with aiohttp.ClientSession(headers=headers) as session:
            for item in self.prepare_items:
                asyncio.create_task(self.proceed_remanga(item, session))
                await asyncio.sleep(0.3)
            while self.fetches != len(self.prepare_items):
                await asyncio.sleep(3)
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage complete')

    async def complete(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage start')
        print(self.re_diff_items)
        await send_data(self.re_diff_items, self.running, self.check_id, self.bot,
                        self.fetch_name, ru_key='title_ru', en_key='title_en', orig_key='title_og',
                        chap_key='chapter', re_items_key='remanga')
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage complete')