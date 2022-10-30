import asyncio
import copy
import logging
import aiohttp

from .FetchBase.FetchBase import FetchBase
from .FetchBase.utils import send_request_multiple, headers, DEBUG, send_data
from .FetchBase.ReManga import ReManga


class Fetch_newmanga(FetchBase):

    def __init__(self, bot, running, check_id):

        self.running = running
        self.check_id = check_id
        self.bot = bot

        self.fetch_name = 'newmanga'
        self.accuracy = 0.65

        self.endpoint_api = 'https://neo.newmanga.org/catalogue'
        self.json_payload = {
            "query": "",
            "sort": {
                "kind": "RATING",
                "dir": "DESC"
            },
            "filter": {
                "hidden_projects": [],
                "genres": {
                    "excluded": [],
                    "included": []},
                "tags": {
                    "excluded": [],
                    "included": []},
                "type": {
                    "allowed": []
                },
                "translation_status": {
                    "allowed": []
                }, "released_year": {
                    "min": None,
                    "max": None
                },
                "require_chapters": True,
                "original_status": {
                    "allowed": []
                },
                "adult": {
                    "allowed": []
                }
            },
            "pagination": {
                "page": 1,
                "size": 50
            }
        }

        self.api_items = []
        self.completed = 0
        self.diff_items = []

    async def proceed_remanga(self, item, session):
        query = item.get('title_og') or item.get('title_en') or item.get('title_ru')
        try:
            remanga_query = await ReManga.find_remanga(query, session)
            remanga_result = await ReManga.compare_remanga_reverse(query, item.get('chapters'), remanga_query,
                                                                   required_rating=self.accuracy)
            if remanga_result:
                new_dict = copy.deepcopy(item)
                new_dict['remanga'] = remanga_result
                self.diff_items.append(new_dict)
        except Exception as e:
            logging.error(f'proceed_remanga: {query} ERROR - skipping, {e}')
        finally:
            self.completed += 1

    async def prepare(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage start')
        async with aiohttp.ClientSession(headers=headers) as session:
            for i in range(1, 2 if DEBUG else 9999):
                await asyncio.sleep(0.3)
                payload = copy.deepcopy(self.json_payload)
                payload['pagination']['page'] = i
                result = await send_request_multiple(session, self.endpoint_api, response_type='json', method='post',
                                                     post_payload=payload)
                if not result['result']['hits']:
                    break
                items = [i['document'] for i in result['result']['hits']]
                for item in items:
                    title_ru = item.get('title_ru') or ''
                    title_en = item.get('title_en') or ''
                    title_og = item.get('title_og') or ''
                    chapters = item.get('count_chapters')
                    self.api_items.append({
                        'title_ru': title_ru,
                        'title_en': title_en,
                        'title_og': title_og,
                        'chapters': chapters,
                    })
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage complete')

    async def run(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage start')
        async with aiohttp.ClientSession(headers=headers) as session:
            for item in self.api_items:
                asyncio.create_task(self.proceed_remanga(item, session))
                await asyncio.sleep(0.1)
            while self.completed != len(self.api_items):
                await asyncio.sleep(3)
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage complete')

    async def complete(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage start')
        await send_data(self.diff_items, self.running, self.check_id, self.bot,
                        self.fetch_name, ru_key='title_ru', en_key='title_en',
                        orig_key='title_og', chap_key='chapters', re_items_key='remanga')
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage complete')

    async def execute(self):
        try:
            await self.prepare()
            await self.run()
            await self.complete()
            return True
        except Exception as e:
            logging.critical(f'FETCH NEWMANGA: FAILED, {e}')
            return False
