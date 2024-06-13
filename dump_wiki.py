import asyncio
import email.utils
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
        k: str(gi.get(k)).replace(f'{k}=', '').strip() for k in
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


def parse_email(v):
    x = v.split('|')

    x[0] = x[0].strip()
    if not x[0]:
        x[0] = None

    if len(x) == 2:
        x[1] = x[1].strip()
        if not x[1]:
            x[1] = None

    elif x[0]:
        e = list(email.utils.parseaddr(x[0]))
        x = (e[1], None) if e[1] else (None, x[0])

    x = (x[0], x[1] if len(x) == 2 else None)

    if not x[0] and not x[1]:
       return None

    if x[0] == 'someguy@example.com':
        return None

    if not x[0] and x[1] == 'unknown':
        return None

    return x


def parse_emails(v):
    emails = []
    for s in v.split(','):
        s = s.strip()

        if s.startswith('{{email|'):
            s = s.removeprefix('{{email|').removesuffix('}}')

            if x := parse_email(s):
                emails.append(x)

        elif s:
            emails.append((None, s))

    return emails


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
            key = str(tm.get('version')).replace('version=', '').strip() if tm.has('version') else ''
            cur = tab.setdefault(key, [])
            continue

        if cur is None:
            tab[''] = cur = []

        db = {
            k: str(tm.get(k)).replace(f'{k}=', '').replace('\u200E', '').strip()
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

        db['maintainers'] = parse_emails(str(tm.get('maintainer')).replace('maintainer=', '')) if tm.has('maintainer') else []

        db['contributors'] = parse_emails(str(tm.get('contributors')).replace('contributors=', '')) if tm.has('contributors') else []

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
        maint += parse_emails(str(tm.get('maintainer')).replace('maintainer=', '')) if tm.has('maintainer') else []
        contr += parse_emails(str(tm.get('contributors')).replace('contributors=', '')) if tm.has('contributors') else []

    for tm in tmpl:
        page.remove(tm)

    return maint, contr


def parse_players(page):
    secs = page.get_sections(matches='Players')

    players = []

    for sec in secs:
        v = str(sec)
        i = 0
        while True:
            try:
                i = v.index('{{email|', i) + 8
            except ValueError:
                break

            try:
                e = v.index('}}', i + 1)
            except ValueError:
                e = len(v)

            x = parse_email(v[i:e])
            if x:
                players.append(x)

            i = e + 1

    for sec in secs:
        page.remove(sec)

    return players


def extract(e):
    fields = e.split('|')
    img = fields[0].replace('Image:', '').strip()
    alt = '' if len(fields) < 2 else fields[1].strip()

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

    print('')


if __name__ == '__main__':
    asyncio.run(run())
