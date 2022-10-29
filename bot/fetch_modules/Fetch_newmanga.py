import copy
import logging
import aiohttp

from .FetchBase.FetchBase import FetchBase
from .FetchBase.utils import send_request_multiple, headers


class Fetch_newmanga(FetchBase):

    def __init__(self, bot, running, check_id):

        self.running = running
        self.check_id = check_id
        self.bot = bot

        self.fetch_name = 'newmanga'
        self.accuracy = 0.7

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

    async def prepare(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage start')
        async with aiohttp.ClientSession(headers=headers) as session:
            for i in range(1, 3):
                payload = copy.deepcopy(self.json_payload)
                payload['pagination']['page'] = i
                result = await send_request_multiple(session, self.endpoint_api, response_type='json', method='post',
                                                     post_payload=payload)
                logging.info(result)
                logging.info('=====')
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage complete')

    async def run(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage start')

        logging.info(f'FETCH {self.fetch_name.upper()}: run stage complete')

    async def complete(self):
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage start')

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
