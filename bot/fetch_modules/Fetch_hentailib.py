from .Fetch_mangalib import Fetch_mangalib


class Fetch_hentailib(Fetch_mangalib):
    def __init__(self, bot, running, check_id):
        super(Fetch_hentailib, self).__init__(bot, running, check_id)

        self.fetch_name = 'hentailib'
        self.accuracy = 0.65

        self.endpoint = 'https://hentailib.me/manga-list'