from bot.fetch_modules.Fetch_mintmanga import Fetch_mintmanga


class Fetch_readmanga(Fetch_mintmanga):
    # same site
    def __init__(self, running, bot, check_id):
        super(Fetch_readmanga, self).__init__(running, bot, check_id)
        self.fetch_name = 'readmanga'
        self.running = running
        self.bot = bot
        self.check_id = check_id

        self.endpoint_clear = 'https://readmanga.live'
        self.endpoint = 'https://readmanga.live/list?sortType=RATING&offset={}'
