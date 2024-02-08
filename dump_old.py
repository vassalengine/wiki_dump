import asyncio
import contextlib
import email.utils
import glob
import json
import os.path
import re
import sqlite3

import dateutil.parser
import pandoc

# TODO: get talk pages
# TODO: fix up text
# TODO: why are some file URLs missing?


def split_item(item):
    if item:
        try:
            k, v = item.split('=', maxsplit=1)
            k = k.strip()
            v = v.strip().strip('\u200E')
            return k, v
        except ValueError:
            # skip keys which have no value
            print(f"skipping item '{item}'")

    return None, None


def iterate_items(t, i):
    e = len(t)
    stack = 2
    split_beg = i

    while i < e and stack > 0:
        if t[i] in ('{', '['):
            stack += 1
        elif t[i] in ('}', ']'):
            stack -= 1
            if stack == 0:
                # end split here
                yield i, t[split_beg:i-1]
                split_beg = i + 1

        elif t[i] == '|':
            if stack == 2:
                # end split here
                yield i, t[split_beg:i]
                split_beg = i + 1

        i += 1

    if stack != 0:
        raise RuntimeError()


def make_cols_vals(rec):
    return ', '.join(rec.keys()), ', '.join(':' + k for k in rec.keys())


def do_insert(conn, table, rec):
    cols, vals = make_cols_vals(rec)
    c = conn.cursor()
    c.execute(f"INSERT INTO {table} ({cols}) VALUES({vals}) RETURNING id", rec)
    return c.fetchone()[0]


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


def parse_players(v):
    players = []
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

    return players


def parse_emails(v):
    emails = []
    for s in v.split(','):
        s = s.strip()

        if s.startswith('{{email|'):
            s = s.removeprefix('{{email|').removesuffix('}}')

            x = parse_email(s)
            if x:
                emails.append(x)

        elif s:
            emails.append((None, s))

    return emails


# TODO: could get date, version out of module
def parse_date(v):
    try:
        d = dateutil.parser.parse(v)
        d = d.strftime("%Y-%m-%d")
#        if v != d:
#            print(f"{v} => {d}")
        return d
    except dateutil.parser.ParserError:
        return v;


def add_or_get_user(conn, u):
    c = conn.cursor()

    # lookup by email
    if u[0]:
        c.execute("SELECT id FROM users WHERE email = ? COLLATE NOCASE", (u[0],))
        r = c.fetchone()
        if r:
            return r[0]

    # lookup by username
    if u[1]:
        c.execute("SELECT id FROM users WHERE username = ? COLLATE NOCASE", (u[1],))
        r = c.fetchone()
        if r:
            return r[0]

    # lookup by name
    if u[1]:
        c.execute("SELECT id FROM users WHERE realname = ? COLLATE NOCASE", (u[1],))
        r = c.fetchone()
        if r:
            return r[0]

    rec = {
        'email': u[0],
        'realname': u[1] or '',
        'username': u[1] or '',
        'matched': False
    }

    cols, vals = make_cols_vals(rec)
    c.execute(f"INSERT INTO users ({cols}) VALUES({vals}) RETURNING id", rec)
    return c.fetchone()[0]


def get_url(filename, files):
    filename = filename.replace('_', ' ')
    filename = filename[0].capitalize() + filename[1:]
    return files.get(f"File:{filename}", None)


img_base_url = 'https://vassalengine.org/wiki/File'

ginfo_re = re.compile(r'{{GameInfo\s*\|')
cinfo_re = re.compile(r'{{ModuleContactInfo\s*\|')
mfile_re = re.compile(r'{{ModuleFile2?\s*\|')
text_cruft_re = re.compile(r'__NOTOC__|{{ModuleFilesTable2?}}.*?\|}|{{ModuleVersion2?\|.*?}}', re.DOTALL)
section_re = re.compile(r'==\s*(.*?)\s*==')

div_open_re = re.compile(r'<div.*?>')
gallery_open_re = re.compile(r'<gallery.*?>')

def iterate_sections(text):
    sbeg = 0
    send = 0
    sec_header = None

    while send < len(text):
        m = section_re.search(text, send)
        if not m:
            break
       
        # this section runs from sbeg to the start of the next header 
        send = m.start(0)
        yield sec_header, text[sbeg:send]

        # the next section starts at the end of this header 
        sbeg = m.end(0)
        sec_header = m.group(1)
        send = sbeg 

    # dump the trailing section
    yield sec_header, text[sbeg:]


def parse_gallery(text):
    yield from text.split('\n')


def title_sort_key(title):
    # TODO: Figure out what to do with Die, Der, Das, L', La, Le, Les, Una

    if title.startswith('A la'):
        # Spanish: A is not an article
        return title

    for art in ('The', 'A', 'An'):
        if title.startswith(art + ' '):
            return title[len(art) + 1:] + ', ' + art

    return title


def process_wikitext(conn, files, filename, num):
    print(num)

    with open(filename, 'r') as f:
        p = json.load(f)['parse']

    num = str(num)

    t = p['wikitext']['*'].strip()
    title = p['title'].removeprefix('Module:')

    # skip redirects
    if t.startswith('#REDIRECT '):
        return

    if 'Category:DeleteMe' in t:
        return 

    if 'Category:Banned' in t:
        return

    mrec = {
        'game_title': title,
        'game_title_sort_key': title_sort_key(title), 
        'id': num
    }

    text = ''

    # split sections
    for sec_title, sec in iterate_sections(t):

        # parse GameInfo
        m = ginfo_re.search(sec)
        if m:
            for i, item in iterate_items(sec, m.end(0)):
                k, v = split_item(item)
                if k and v:
                    mrec[f"game_{k}"] = v

            # strip out GameInfo
            sec = sec[0:m.start(0)] + sec[i+1:]

            imgname = mrec.get('game_image', None)
            if imgname is not None:
                url = get_url(imgname, files)
                if url is not None:
                    mrec['game_image'] = url

        # parse ModuleContactInfo
        m = cinfo_re.search(sec)
        if m:
            for i, item in iterate_items(sec, m.end(0)):
                k, v = split_item(item)
                if k and v:
                    if k == 'maintainer':
                        for e in parse_emails(v):
                            uid = add_or_get_user(conn, e)
                        
                            conn.execute(f"INSERT INTO owners (user_id, project_id) VALUES(?, ?)", (uid, num))
                    elif k == 'contributors':
                        for e in parse_emails(v):
                            uid = add_or_get_user(conn, e)
                            
                            conn.execute(f"INSERT INTO module_contributors (user_id, project_id) VALUES(?, ?)", (uid, num))
                    else:
                        mrec[k] = v

            # strip out ModuleContactInfo
            sec = sec[0:m.start(0)] + sec[i+1:]
       
        # parse ModuleFiles
        i = 0
        while True:
            m = mfile_re.search(sec, i)
            if not m:
                break

            frec = {
                'project_id': num
            }

            maintainer = None
            contributors = None

            for i, item in iterate_items(sec, m.end(0)):
                k, v = split_item(item)
                if k and v and k != 'size':
                    if k == 'maintainer':
                        maintainer = v
                    elif k == 'contributors':
                        contributors = v
                    else: 
                        if k == 'date':
                            v = parse_date(v)

                        frec[k] = v

            # strip out ModuleFiles
            sec = sec[0:m.start(0)] + sec[i+1:]
            i = m.start(0)

            filename = frec.get('filename', None)
            if filename is not None:
                url = get_url(filename, files)
                if url is not None:
                    frec['fileurl'] = url

            fid = do_insert(conn, 'files', frec)

            if maintainer:
                for e in parse_emails(maintainer):
                    uid = add_or_get_user(conn, e)
                    conn.execute(f"INSERT INTO file_maintainers (user_id, file_id) VALUES(?, ?)", (uid, fid))

            if contributors:
                for e in parse_emails(contributors):
                    uid = add_or_get_user(conn, e)
                    conn.execute(f"INSERT INTO file_contributors (user_id, file_id) VALUES(?, ?)", (uid, fid))

        # parse Players section 
        if sec_title == 'Players':
            m = div_open_re.search(sec)
            if m:
                dbeg = m.start(0)
                dend = sec.index('</div>', dbeg) + 6

                for p in parse_players(sec[dbeg:dend]):
                    pid = add_or_get_user(conn, p)
                    conn.execute(f"INSERT INTO players (user_id, project_id) VALUES(?, ?)", (pid, num))

                sec = sec[0:dbeg] + sec[dend:]

#        elif sec_title in ('Screen Shots', 'Screenshots'):
#            m = gallery_open_re.search(sec)
#            if m:
#                dbeg = m.start(0)
#                dend = sec.index('</gallery>', dbeg) + 10
#
#                for imgname in parse_gallery(sec[dbeg:dend]):
#                    if imgname is not None:
#                        url = get_url(imgname, files)
#                        if url is not None:
#                            print(imgname, url) 
#
#                sec = sec[0:dbeg] + sec[dend:]

        # trim out other cruft from text
        sec = text_cruft_re.sub('', sec)
        sec = sec.strip()

        if sec:
            # add back section title
            if sec_title and sec_title not in ('Comments'):
                text += f"== {sec_title} ==\n"
        
            text += f"{sec}\n"

    p = pandoc.read(text, format='mediawiki')
    text = pandoc.write(p, format='markdown')

    mrec['text'] = text

    do_insert(conn, 'projects', mrec)


def create_db(conn):
    with conn as cur:
        cur.execute('DROP TABLE IF EXISTS projects')
        cur.execute('''
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    game_title TEXT,
    game_title_sort_key TEXT,
    game_publisher TEXT,
    game_year TEXT,
    game_era TEXT,
    game_topic TEXT,
    game_scale TEXT,
    game_players TEXT,
    game_length TEXT,
    game_series TEXT,
    game_image TEXT,
    text TEXT
)
        ''')

        cur.execute('DROP TABLE IF EXISTS owners')
        cur.execute('''
CREATE TABLE owners (
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    UNIQUE(user_id, project_id),
    FOREIGN KEY(user_id)
    REFERENCES users(id),
    FOREIGN KEY(project_id)
    REFERENCES projects(id)
)
        ''')
        
        cur.execute('DROP TABLE IF EXISTS module_contributors')
        cur.execute('CREATE TABLE module_contributors(user_id INTEGER NOT NULL, project_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(project_id) REFERENCES projects(id))')

        cur.execute('DROP TABLE IF EXISTS files')
        cur.execute('CREATE TABLE files(id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, filename, fileurl, filetype, description, date, compatibility, FOREIGN KEY(project_id) REFERENCES projects(id))')

        cur.execute('DROP TABLE IF EXISTS file_maintainers')
        cur.execute('CREATE TABLE file_maintainers(user_id INTEGER NOT NULL, file_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(file_id) REFERENCES files(id))')
        
        cur.execute('DROP TABLE IF EXISTS file_contributors')
        cur.execute('CREATE TABLE file_contributors(user_id INTEGER NOT NULL, file_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(file_id) REFERENCES files(id))')

        cur.execute('DROP TABLE IF EXISTS users')
        cur.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    realname TEXT,
    email TEXT,
    matched INTEGER NOT NULL,
    UNIQUE(email)
)
    ''')

        cur.execute('DROP TABLE IF EXISTS players')
        cur.execute('CREATE TABLE players(user_id INTEGER NOT NULL, project_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(project_id) REFERENCES projects(id))')


def populate_users(conn, upath):
    with open(upath, 'r') as f:
        users = json.load(f)

    with conn as cur:
        for u in users:
            rec = {
                'email': u['email'],
                'realname': u['name'],
                'username': u['username'],
                'matched': True
            }
            do_insert(cur, 'users', rec)


async def process_wikitext_async(conn, files, filename, num):
    with conn as cur:
        process_wikitext(cur, files, filename, num)


async def run():
    with open('data/files.json', 'r') as f:
        files = json.load(f)

    upath = 'data/users.json'
    dbpath = 'projects.db'

    with contextlib.closing(sqlite3.connect(dbpath)) as conn:
        with conn as cur:
            create_db(conn)
            populate_users(conn, upath)

        async with asyncio.TaskGroup() as tg:
#        for f in sorted(glob.glob('data/[0-9]*'), key=lambda x: int(os.path.basename(x)))[2883:]:
            for f in glob.glob('data/[0-9]*'):
                num = int(os.path.basename(f))
                tg.create_task(process_wikitext_async(conn, files, f, num))

#        process_wikitext(conn, files, 'data/875', 875)


if __name__ == '__main__':
    asyncio.run(run())
