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

        self.count = 0
        self.prepare_count = 0
        self.prepare_items = []

        self.re_diff_items = []
        self.fetches = 0

    async def make_prepare(self, endpoint, session):
        try:
            result = await send_request_multiple(session, endpoint)
            if not result or not await self.process_result(result):
                logging.error(f'FETCH {self.fetch_name.upper()}: {endpoint} - failed, skipping')
        except Exception as e:
            logging.error(f'FETCH {self.fetch_name.upper()}: {endpoint} - failed, skipping, ERROR: {e}')
        finally:
            self.prepare_count += 1

    async def process_result(self, result):
        try:
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
            text = await send_request_multiple(session, self.endpoint.format(0))
            q_len = pq.PyQuery(text)
            try:
                loop_len = int(list(q_len.find('#pagination > span > a').items())[-1].text()) * 20 or 40000
            except:
                loop_len = 40000
            logging.info(loop_len)
            for i in range(0, loop_len if not DEBUG else 20, 20):
                await asyncio.sleep(0.5)
                asyncio.create_task(self.make_prepare(self.endpoint.format(i), session))
                self.count += 1
            while self.prepare_count < self.count:
                await asyncio.sleep(3)
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
        await send_data(self.re_diff_items, self.running, self.check_id, self.bot,
                        self.fetch_name, ru_key='title_ru', en_key='title_en', orig_key='title_og',
                        chap_key='chapter', re_items_key='remanga')
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage complete')