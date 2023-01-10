import asyncio
import csv
import logging
import os

headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
        }

DEBUG = True


async def send_request(session, url, response_type='text', method='get', post_payload=None):
    if post_payload is None:
        post_payload = dict()
    method = method.lower()
    if response_type not in ('text', 'json'):
        return False
    if method not in ('get', 'post'):
        return False

    logging.info(f'sending {method}: {url.replace(" ", "%20")}')
    async with session.get(url) if method.lower() == 'get' else session.post(url, json=post_payload) as response:
        if response.status == 200:
            if response_type == 'text':
                return await response.text()
            else:
                return await response.json()
        else:
            return False


async def send_request_multiple(session, url, tries=5, sleep=120, response_type='text',
                                method='get', post_payload=None):
    __count = 0

    result = await send_request(session, url, response_type=response_type, method=method, post_payload=post_payload)

    while result is False and __count < tries:
        await asyncio.sleep(sleep)
        result = await send_request(session, url, response_type=response_type, method=method, post_payload=post_payload)
        __count += 1
        logging.warning(f'FETCH 1: request {url.split("=")[-1]} fail: {__count} time, sleeping {sleep} sec')
    if __count >= 5:
        result = ''
    return result


async def send_data(output, running, check_id, bot, fetch_name,
                    ru_key, en_key, orig_key, dir):
    first_row = ['Русс название', 'Англ название', 'Ориг название']
    rows = [first_row, ]
    for item in output:
        ru_name = item[ru_key].replace(',', '').replace(';', '')
        en_name = item[en_key].replace(',', '').replace(';', '')
        orig_name = item[orig_key].replace(',', '').replace(';', '')
        dir_href = item[dir].replace(',', '').replace(';', '')
        rows.append([ru_name, en_name, orig_name, dir_href])
    logging.info(f'Saving data to output_{fetch_name}.csv...')
    with open(f'output_{fetch_name}.csv', 'w', encoding="utf-8-sig", newline="") as mint_out:
        writer = csv.writer(mint_out, delimiter=';')
        writer.writerows(rows)
    logging.info('Data saved, sending document to users...')
    print(check_id, running, running[check_id])
    for user_id in running[check_id]['users']:
        await bot.send_message(user_id, f'Проверка {fetch_name} завершена, отправка файла...')
        await bot.send_document(user_id, open(f'output_{fetch_name}.csv', 'rb'))
    logging.info('Send complete, deleting file...')
    os.remove(f'output_{fetch_name}.csv')
    logging.info('Done')
