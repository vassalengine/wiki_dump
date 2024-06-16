import asyncio
from datetime import datetime
import json
import os
import sys

import aiohttp


async def get_page_list(session, url, ns):
    # get the page list
    pages = []

    params = {
        'action': 'query',
        'format': 'json',
        'list': 'allpages',
        'apnamespace': ns,
        'aplimit': 500
    }

    lastContinue = {}

    while True:
        p = {**params}
        p.update(lastContinue)

        async with session.get(url, params=p) as response:
            result = await response.json()

        if 'query' in result:
            pages += result['query']['allpages']
            print('.', end='', file=sys.stderr)

        if 'continue' not in result:
            break

        lastContinue = result['continue']

    return pages


async def get_time(session, url, title, direction, times):
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'revisions',
        'rvlimit': '1',
        'rvprop': 'timestamp',
        'rvdir': direction
    }

    async with session.get(url, params=params) as response:
        r = await response.json()
        for k, v in r['query']['pages'].items():
            try:
                times[title] = datetime.fromisoformat(v['revisions'][0]['timestamp']).isoformat()
                print('.', end='', file=sys.stderr)
            except KeyError:
                print(v, file=sys.stderr)

            break


async def get_times(session, url, direction, pages):
    times = {}

    async with asyncio.TaskGroup() as tg:
        for i, p in enumerate(pages):
            tg.create_task(get_time(session, url, p['title'], direction, times))

    return times


async def get_ctimes(session, url, pages):
    return await get_times(session, url, 'newer', pages)


async def get_mtimes(session, url, pages):
    return await get_times(session, url, 'older', pages)


async def get_wikitext(session, url, title, outpath):
    params = {
        'page': title,
        'prop': 'wikitext',
        'action': 'parse',
        'format': 'json'
    }

    async with session.get(url, params=params) as response:
        page = await response.json()

    with open(outpath, 'w') as f:
        print(json.dumps(page), file=f)

    print(title, file=sys.stderr)


async def get_all_wikitext(session, url, pages):
    async with asyncio.TaskGroup() as tg:
        for i, p in enumerate(pages):
            tg.create_task(get_wikitext(session, url, p['title'], f"data/wikitext/{i}"))


async def get_file_meta(session, url, title, file_meta):
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'imageinfo',
        'iiprop': 'url|user'
    }

    async with session.get(url, params=params) as response:
        r = await response.json()
        for k, v in r['query']['pages'].items():
            try:
                file_meta[title] = {
                    'url': v['imageinfo'][0]['url'],
                    'user': v['imageinfo'][0]['user']
                }
                print('.', end='', file=sys.stderr)
            except KeyError:
                print(v, file=sys.stderr)

            break


async def get_all_file_meta(session, url, files):
    file_meta = {}

    async with asyncio.TaskGroup() as tg:
        for i, p in enumerate(files):
            tg.create_task(get_file_meta(session, url, p['title'], file_meta))

    return file_meta


async def run():
    os.mkdir('data')

    url = 'https://vassalengine.org/w/api.php'
    conn = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=conn) as session:
        #
        # files
        #
        files = await get_page_list(session, url, 6)
        file_meta = await get_all_file_meta(session, url, files)

        with open('data/files.json', 'w') as f:
            json.dump(file_meta, f, indent=2)

        # the mtime of a file is the ctime of the current version
        file_ctimes = await get_mtimes(session, url, files)

        with open('data/file_ctimes.json', 'w') as f:
            json.dump(file_ctimes, f, indent=2)

        #
        # pages
        #

        pages = await get_page_list(session, url, 100)

        page_ctimes = await get_ctimes(session, url, pages)
        with open('data/page_ctimes.json', 'w') as f:
            json.dump(page_ctimes, f, indent=2)

        os.mkdir('data/wikitext')
        await get_all_wikitext(session, url, pages)


if __name__ == '__main__':
    asyncio.run(run())
