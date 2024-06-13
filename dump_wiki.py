import asyncio
import glob
import json
import os
import sys

import mwparserfromhell


def parse_game_info(page):
    gi = page.filter_templates(matches=lambda n: n.name == 'GameInfo')
    if not gi or len(gi) < 1:
        raise RuntimeError('No GameInfo')

    if len(gi) > 1:
        raise RuntimeError('Multiple GameInfo')

    gi = gi[0]

    ret = {
        k: str(gi.get(k)).replace(f'{k}=', '') for k in
        [
            'image',
            'publisher',
            'year',
            'era',
            'topic',
            'series',
            'scale',
            'players',
            'length'
        ]
        if gi.has(k)
    }

    page.remove(gi)

    return ret


def parse_emails(block):
    emails = block.filter_templates(matches=lambda n: n.name == 'email')
    return [
        {
            'name': str(e.params[1]) if len(e.params) > 1 else '',
            'address': str(e.params[0])
        }
        for e in emails
        if str(e.params[0]) != 'someguy@example.com'
    ]


def parse_emails_str(s):
    block = mwparserfromhell.parse(str(s))
    return parse_emails(block)


def parse_modules(page):
    names = [
        'ModuleFilesTable2',
        'ModuleVersion2',
        'ModuleFile2',
        'ModuleFilesTable',
        'ModuleVersion',
        'ModuleFile'
    ]

    tmpl = page.filter_templates(
        matches=lambda n : n.name in names,
        recursive=False
    )

    tab = {}
    cur = None

    for tm in tmpl:
        if tm.name in ('ModuleFilesTable', 'ModuleFilesTable2'):
            continue

        if tm.name in ('ModuleVersion', 'ModuleVersion2'):
            key = str(tm.get('version')).replace('version=', '') if tm.has('version') else ''
            cur = tab.setdefault(key, [])
            continue

        if cur is None:
            tab[''] = cur = []

        db = {
            k: str(tm.get(k)).replace(f'{k}=', '').replace('\u200E', '')
            for k in
            [
                'filename',
                'decription',
                'date',
                'size',
                'compatibility'
            ]
            if tm.has(k)
        }
        
        db['maintainers'] = parse_emails_str(tm.get('maintainer')) if tm.has('maintainer') else []

        db['contributors'] = parse_emails_str(tm.get('contributors')) if tm.has('contributors') else []

        cur.append(db)

    for tm in tmpl:
        page.remove(tm)

    return tab


def parse_module_contact_info(page):
    tmpl = page.filter_templates(
        matches=lambda n: n.name == 'ModuleContactInfo',
        recursive=False
    )

    maint = []
    contr = []

    for tm in tmpl:
        maint += parse_emails_str(tm.get('maintainer')) if tm.has('maintainer') else []
        contr += parse_emails_str(tm.get('contributors')) if tm.has('contributors') else []

    for tm in tmpl:
        page.remove(tm)

    return maint, contr


def parse_players(page):
    secs = page.get_sections(matches='Players')

    players = [e for sec in secs for e in parse_emails(sec)]

    for sec in secs:
        page.remove(sec)

    return players


def extract(e):
    fields = e.split('|')
    img = fields[0].replace('Image:', '')
    alt = '' if len(fields) < 2 else fields[1]

    return {
        'img': img,
        'alt': alt
    }


def parse_gallery(page):
    tags = page.filter_tags(matches = lambda n: n.tag == 'gallery')

    if not tags:
        return []

    images = [
        extract(e) for tag in tags for e in tag.contents.split('\n') if e != ''
    ]

    for tag in tags:
        page.remove(tag)

    return images


def remove_headings(page):
    to_remove = [
        'Comments',
        'Module Information',
        'Files',
        'Screen Shots',
        'Screenshots'
    ]

    headings = page.filter_headings(matches='|'.join(to_remove))
    for h in headings:
        page.remove(h)


def remove_cruft(page):
    try:
        page.remove('__NOTOC__')
    except ValueError:
        pass

    secs = page.get_sections(matches='Files')
    for sec in secs:
        try:
            sec.remove('|}')
        except ValueError:
            pass


async def parse_page(inpath, outpath):
    with open(inpath, 'r') as infile:
        p = json.load(infile)['parse']

    wikitext = p['wikitext']['*'].strip()

    # skip some pages 
    if wikitext.startswith('#REDIRECT'):
        return

    if 'Category:DeleteMe' in wikitext:
        return

    if 'Category:Banned' in wikitext:
        return

    title = p['title'].removeprefix('Module:')
    t = mwparserfromhell.parse(wikitext)

    ginfo = parse_game_info(t)
    modules = parse_modules(t)
    maintainer, contributors = parse_module_contact_info(t)
    gallery = parse_gallery(t)
    players = parse_players(t)

    remove_cruft(t)
    remove_headings(t) 

    page = {
        'title': title, 
        'info': ginfo,
        'maintainer': maintainer,
        'contributors': contributors,
        'modules': modules,
        'gallery': gallery,
        'players': players,
        'readme': t.strip()
    }

    with open(outpath, 'w') as outfile:
        print(json.dumps(page, indent=2), file=outfile)

    print('.', end='', flush=True)


async def run():
    ipath = 'data/wikitext'
    opath = 'data/pagejson'

    async with asyncio.TaskGroup() as tg:
        for f in glob.glob(f"{ipath}/[0-9]*"):
            b = os.path.basename(f)
            tg.create_task(parse_page(f, f"{opath}/{b}.json"))


if __name__ == '__main__':
    asyncio.run(run())
