import asyncio
import csv
import os

import aiohttp
import copy
import logging
import pyquery as pq

from .FetchBase.utils import headers, DEBUG, send_data
from bot.fetch_modules.FetchBase.FetchBase import FetchBase
from bot.fetch_modules.FetchBase.ReManga import ReManga
from bot.fetch_modules.FetchBase.utils import send_request_multiple


class Fetch_mintmanga(FetchBase):
    def __init__(self, bot, running, check_id):

        self.running = running
        self.check_id = check_id
        self.bot = bot

        self.fetch_name = 'mintmanga'
        self.accuracy = 0.7

        self.endpoint_clear = 'https://mintmanga.live'
        self.endpoint = 'https://mintmanga.live/list?sortType=RATING&offset={}'
        self.items_count = 0
        self.items_response = []

        self.total_items = 0
        self.fetches = 0

        self.fetches_items = []

        self.output = []

    async def request_append(self, session, url):
        result = await send_request_multiple(session, url)
        self.items_response.append(result)

    async def fetch_single_manga(self, session, url):
        chapters = []
        try:
            result = await send_request_multiple(session, url)
            if result:
                query = pq.PyQuery(result.replace('. item-title', '.item-title'))
                name = query.find('.names > .name').text()
                en_name = query.find('.names > .eng-name').text()
                original_name = query.find('.names > .original-name').text()
                chapters = list(i.text() for i in query.find('td.item-title > a').items())
                all_chaps = []
                for chap in chapters:
                    res = chap.split(' - ')
                    actual_chap = ''
                    if len(res) == 2:
                        for i in res[1]:
                            if i in '0123456789':
                                actual_chap += i
                            else:
                                break
                        try:
                            actual_chap = int(actual_chap)
                        except ValueError:
                            continue
                        all_chaps.append(actual_chap)
                manga_item = {
                    'ru_title': name,
                    'en_title': en_name,
                    'orig_title': original_name,
                    'max_chapter': max(all_chaps)
                }
                result = await self.proceed_remanga_reverse(manga_item, session, rating=self.accuracy)
                if result:
                    self.output.append(result)
                self.fetches += 1
            else:
                raise Exception('No result were got from server')
        except Exception as e:
            for chap in chapters:
                print(chap)
            logging.error(f'{url} fetching - error, skipping. Error: {e}')
            self.fetches += 1

    @staticmethod
    async def proceed_remanga(item, session):
        titles_all = [item['en_title'], item['ru_title'], item['orig_title']]
        title = item['en_title'] or item['ru_title'] or item['orig_title']
        max_chap = item['max_chapter']
        find_result = await ReManga.find_remanga(title, session)
        proceed_result = await ReManga.compare_remanga(titles_all, max_chap, find_result)
        if proceed_result:
            new_item = copy.deepcopy(item)
            new_item['remanga_data'] = proceed_result
            # logging.info(new_item)
            return new_item
        return

    @staticmethod
    async def proceed_remanga_reverse(item, session, rating=0.51):
        title = item['en_title'] or item['orig_title'] or item['ru_title']
        max_chap = item['max_chapter']
        find_result = await ReManga.find_remanga(title, session)
        proceed_result = await ReManga.compare_remanga_reverse(title, max_chap, find_result, required_rating=rating)
        if proceed_result:
            new_item = copy.deepcopy(item)
            new_item['remanga_data'] = proceed_result
            # logging.info(new_item) if DEBUG else None
            return new_item
        return

    async def prepare(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage start')
        async with aiohttp.ClientSession(headers=headers) as session:
            result = await send_request_multiple(session, self.endpoint.format(0))
            query = pq.PyQuery(result)
            item_count = int(list(query.find('.pagination > .step').items())[-1].text())
            actual = item_count if not DEBUG else 1
            loop = asyncio.get_running_loop()
            for i in range(0, 70 * actual, 70):
                url = self.endpoint.format(i)
                loop.create_task(self.request_append(session, url))
                await asyncio.sleep(0.5)
            while len(self.items_response) < actual:
                await asyncio.sleep(1)
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage complete')

    async def run(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage start')
        self.total_items = 0
        curr_loop = asyncio.get_running_loop()
        async with aiohttp.ClientSession(headers=headers) as session:
            for item in self.items_response:
                query = pq.PyQuery(item)
                links = [i.attr('href') for i in query.find('.desc > h3 > a').items()]
                self.total_items += len(links)
                for url in links:
                    curr_loop.create_task(self.fetch_single_manga(session, self.endpoint_clear + url))
                    await asyncio.sleep(0.5)
            while self.fetches < self.total_items:
                await asyncio.sleep(10)
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage complete')

    async def complete(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage start')
        await send_data(self.output, self.running, self.check_id, self.bot, self.fetch_name,
                        ru_key='ru_title', en_key='en_title', orig_key='orig_title',
                        chap_key='max_chapter', re_items_key='remanga_data')
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage complete')

    async def execute(self):
        try:
            await self.prepare()
            await self.run()
            await self.complete()
            return True
        except Exception as e:
            logging.critical(f'FETCH {self.fetch_name.upper()}: FAILED, {e}')
            return False
