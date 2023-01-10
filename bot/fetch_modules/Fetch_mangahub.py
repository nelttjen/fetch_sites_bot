import asyncio
import copy
import logging

import aiohttp
import pyquery as pq

from .FetchBase.FetchBase import FetchBase
from .FetchBase.utils import DEBUG, send_request_multiple, send_data, headers
from .FetchBase.ReManga import ReManga


class Fetch_mangahub(FetchBase):
    def __init__(self, bot, running, check_id):
        self.running = running
        self.check_id = check_id
        self.bot = bot

        self.fetch_name = 'mangahub'
        self.endpoint = 'https://mangahub.ru/explore/sort-is-rating?page={}'
        self.endpoint_clear = 'https://mangahub.ru'
        self.accuracy = 0.65

        self.count = 0
        self.prepare_count = 0
        self.prepare_items = []

        self.re_diff_items = []
        self.fetches = 0

    async def make_prepare(self, endpoint, session):
        try:
            result = await send_request_multiple(session, endpoint)
            if not result or not await self.process_result(result, session):
                logging.error(f'FETCH {self.fetch_name.upper()}: {endpoint} - failed, skipping')
        except Exception as e:
            logging.error(f'FETCH {self.fetch_name.upper()}: {endpoint} - failed, skipping, ERROR: {e}')

    async def process_single(self, link, session):
        try:
            result_1 = await send_request_multiple(session, link)
            query_1 = pq.PyQuery(result_1)
            ru_name = query_1.find('h1.text-truncate').text()
            try:
                en_name = list(query_1.find('.d-lg-table-row > .attr-value').items())[-1].text().split(' / ')[0]
                og_name = list(query_1.find('.d-lg-table-row > .attr-value').items())[-1].text().split(' / ')[1]
            except:
                try:
                    en_name = list(query_1.find('.d-lg-table-row > .attr-value').items())[-1].text().split(' / ')[0]
                    og_name = ''
                except:
                    en_name, og_name = '', ''

            new_item = {
                'title_ru': ru_name,
                'title_en': en_name,
                'title_og': og_name,
                'dir': link
            }
            self.prepare_items.append(new_item)
        except Exception as e:
            logging.error(f'{link} process error, skipping, MESSAGE: {e}')
        finally:
            self.prepare_count += 1

    async def process_result(self, result, session):
        try:
            query = pq.PyQuery(result)
            items = list(query.find('.fast-view-layer').items())
            for item in items:
                link = self.endpoint_clear + item.attr('href')
                self.count += 1
                await asyncio.sleep(0.5)
                asyncio.create_task(self.process_single(link, session))
            return True
        except:
            return False

    async def prepare(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage start')
        async with aiohttp.ClientSession(headers=headers) as session:
            f_page = await send_request_multiple(session, self.endpoint.format(1))
            f_query = pq.PyQuery(f_page)
            try:
                pages = int(list(f_query.find('.pagination > .page-item > .page-link').items())[-2].text()) or 500
            except:
                pages = 999
            for i in range(1, pages if not DEBUG else 2):
                asyncio.create_task(self.make_prepare(self.endpoint.format(i), session))
                await asyncio.sleep(0.5)
            while self.count > self.prepare_count:
                await asyncio.sleep(3)
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage complete')

    async def run(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage start')
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage complete')

    async def complete(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage start')
        await send_data(self.prepare_items, self.running, self.check_id, self.bot,
                        self.fetch_name, ru_key='title_ru', en_key='title_en', orig_key='title_og',
                        dir="dir")
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage complete')