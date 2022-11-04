from .Fetch_mangalib import Fetch_mangalib


class Fetch_yaoilib(Fetch_mangalib):
    def __init__(self, bot, running, check_id):
        super(Fetch_yaoilib, self).__init__(bot, running, check_id)

        self.fetch_name = 'yaoilib'
        self.accuracy = 0.65

        self.endpoint = 'https://yaoilib.me/manga-list'