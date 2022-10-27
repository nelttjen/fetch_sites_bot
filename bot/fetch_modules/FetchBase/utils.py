import asyncio
import logging


async def send_request(session, url, response_type='text'):
    if response_type not in ('text', 'json'):
        return False
    logging.info(f'sending: {url.replace(" ", "%20")}')
    async with session.get(url) as response:
        if response.status == 200:
            if response_type == 'text':
                return await response.text()
            else:
                return await response.json()
        else:
            return False


async def send_request_multiple(session, url, tries=5, sleep=120) -> str:
    __count = 0

    result = await send_request(session, url)

    while result is False and __count < tries:
        await asyncio.sleep(sleep)
        result = await send_request(session, url)
        __count += 1
        logging.warning(f'FETCH 1: request {url.split("=")[-1]} fail: {__count} time, sleeping {sleep} sec')
    if __count >= 5:
        result = ''
    return result