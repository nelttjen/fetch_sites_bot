import asyncio
import logging

import aiohttp

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from .FetchBase.ReManga import ReManga
from .FetchBase.FetchBase import FetchBase
from .FetchBase.utils import DEBUG, headers, send_data
from bot.bot_core import DRIVER_EXECUTABLE_PATH

class Fetch_mangalib(FetchBase):
    def _is_exist_page(self):
        try:
            if self.driver.find_element(By.CLASS_NAME, 'empty'):
                return False
        except:
            return True

    async def _get_elements_from_page(self, ):
        elements = self.driver.find_elements(By.CLASS_NAME, 'media-card')

        formatted_elements = []

        for element in elements:
            href = element.get_attribute('href')
            _id = element.get_attribute('data-media-id')
            slug = element.get_attribute('data-media-slug')
            if _id not in self.ids:
                formatted_elements.append({'href': href, 'id': _id, 'slug': slug})
                self.ids.append(_id)

        return formatted_elements

    async def get_elements_hard(self, year):
        for __type in self.TYPES:
            for k in range(1, 30):
                link = self._generate_api_link(page=k, year_max=year, year_min=year, int_type=__type, rating=2)
                self.driver.get(link)
                if not self._is_exist_page():
                    break
                self.title_data.extend(await self._get_elements_from_page())

    def _generate_api_link(self, sort='rate', _dir='desc', page=1, year_min='', year_max='',
                           rating: int = None, int_type: int = None):
        args = {'sort': sort, 'dir': _dir, 'page': page, 'year[min]': year_min, 'year[max]': year_max,
                'caution[]': rating, 'types[]': int_type}
        link = self.endpoint
        items = []
        for item in args:
            value = args.get(item)
            if value:
                items.append(f'{item}={value}')
        return f'{link}?{"&".join(items)}'

    async def get_titles(self):
        for i in range(self.API_YEAR_START, self.API_YEAR_END + 1):

            if i in self.EXTRA_PROBLEM_YEARS:
                await self.get_elements_hard(i)

            for k in range(1, 30):
                await asyncio.sleep(0.1)
                link = self._generate_api_link(page=k, year_max=str(i), year_min=str(i))
                self.driver.get(link)
                if not self._is_exist_page():
                    break
                self.title_data.extend(await self._get_elements_from_page())

    def __init__(self, bot, running, check_id):
        self.running = running
        self.check_id = check_id
        self.bot = bot

        self.fetch_name = 'mangalib'
        self.accuracy = 0.65

        self.endpoint = 'https://mangalib.me/manga-list'
        self.API_YEAR_START = 1930 if not DEBUG else 1997
        self.API_YEAR_END = 2022 if not DEBUG else 1997
        self.TYPES = (1, 5, 8, 9, 4, 6)
        self.RATING = (0, 1)
        self.EXTRA_PROBLEM_YEARS = (2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022)

        try:
            opts = ChromeOptions()
            prefs = {"profile.managed_default_content_settings.images": 2}
            opts.add_experimental_option("prefs", prefs)
            # opts.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
            # opts.add_argument('headless')
            # opts.add_argument('window-size=0x0')
            self.driver = Chrome(executable_path=DRIVER_EXECUTABLE_PATH, chrome_options=opts)
            self.error = False
        except:
            self.error = True

        self.title_data = []
        self.ids = []

        self.re_diff_items = []

    async def prepare(self):
        if self.error:
            return
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage start')
        await self.get_titles()
        logging.info(f'FETCH {self.fetch_name.upper()}: prepare stage complete')

    async def run(self):
        if self.error:
            return
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage start')
        async with aiohttp.ClientSession(headers=headers) as session:
            for item in self.title_data:
                await asyncio.sleep(0.1)
                try:
                    link = item['href']
                    self.driver.get(link)
                    try:
                        ru_name = self.driver.find_element(By.CSS_SELECTOR, '.media-name__main').text
                    except:
                        ru_name = ''
                    try:
                        en_name = self.driver.find_element(By.CSS_SELECTOR, '.media-name__alt').text
                    except:
                        logging.warning(f"{link} - skipping, no name detected")
                        continue
                    try:
                        og_name = self.driver.find_element(By.CSS_SELECTOR, '.media-info-list__value > div').text
                    except:
                        og_name = ''
                    __new = {
                        'ru_title': ru_name,
                        'en_title': en_name,
                        'og_title': og_name,
                        'dir': link
                    }
                    self.re_diff_items.append(__new)
                except Exception as e:
                    logging.error(f'{item["href"]} - error, skipping, message: {e}')
        logging.info(f'FETCH {self.fetch_name.upper()}: run stage complete')

    async def complete(self):
        if self.error:
            for user in self.running[self.check_id]['users']:
                await self.bot.send_message(user, f'{self.fetch_name} - Невозможно запустить проверку. '
                                                  f'Не найден драйвер для управления страницами. '
                                                  f'Инструкцию по установке и настройке можно найти здесь: '
                                                  f'https://github.com/nelttjen/'
                                                  f'fetch_sites_bot/blob/main/driver/README.MD')
            return
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage start')
        await send_data(self.re_diff_items, self.running, self.check_id, self.bot, self.fetch_name,
                        ru_key='ru_title', en_key='en_title', orig_key='og_title', dir="dir")
        logging.info(f'FETCH {self.fetch_name.upper()}: complete stage complete')
