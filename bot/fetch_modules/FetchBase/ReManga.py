from bot.fetch_modules.FetchBase.utils import send_request


class ReManga:
    @staticmethod
    async def find_remanga(orig_name, session):
        endpoint = f'https://api.remanga.org/api/search/?query={orig_name}&count=8&field=titles&page=1'
        response = await send_request(session, endpoint, response_type='json')
        items = []
        for item in response['content']:
            title_id = item['id']
            title_eng = item['en_name'].lower()
            chapters = item['count_chapters']
            _dir = item['dir']
            items.append({
                'title_id': title_id,
                'title_eng': title_eng,
                'chapters': chapters,
                'dir': _dir
            })
        return items

    @staticmethod
    async def compare_remanga(names, chapter, remanga_items, required_rating=0.5) -> list:
        items_return = []

        for item in remanga_items:
            max_rating = 0.0
            name = item['title_eng']
            for mu_name in names:
                if not mu_name:
                    continue
                list_of_words = mu_name.lower().split(' ')
                count = 0
                for word in list_of_words:
                    if word in name:
                        count += 1
                cur_rating = count / len(list_of_words)
                max_rating = max(max_rating, cur_rating)
            if max_rating >= required_rating:
                chapters_re = item['chapters']
                if chapters_re < chapter:
                    items_return.append(item)
        return items_return

    @staticmethod
    async def compare_remanga_reverse(orig_name, chapter, remanga_items, required_rating=0.51) -> list:
        items_return = []

        for item in remanga_items:
            re_name = item['title_eng']
            word_list = re_name.split(' ')
            counts = 0
            for word in word_list:
                if word.strip().replace("'s", '').lower() in orig_name.lower():
                    counts += 1
            if counts / len(word_list) >= required_rating:
                chapters_re = item['chapters']
                if chapters_re < chapter:
                    items_return.append(item)
        return items_return
