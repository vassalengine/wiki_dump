import asyncio
import contextlib
import datetime
import email.utils
import glob
import json
import os.path
import re
import sqlite3

import dateutil.parser
import pypandoc
import semver

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


def do_insert(conn, table, id_col, rec):
    cols, vals = make_cols_vals(rec)
    c = conn.cursor()
    c.execute(f"INSERT INTO {table} ({cols}) VALUES({vals}) RETURNING {id_col}", rec)
    return c.fetchone()[0]


def do_insert_or_ignore(conn, table, id_col, rec):
    cols, vals = make_cols_vals(rec)
    c = conn.cursor()
    c.execute(f"INSERT OR IGNORE INTO {table} ({cols}) VALUES({vals}) RETURNING {id_col}", rec)
    r = c.fetchone()
    return r[0] if r else None


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

            if x := parse_email(s):
                emails.append(x)

        elif s:
            emails.append((None, s))

    return emails


# TODO: could get date, version out of module
def parse_date(v):
    try:
        d = dateutil.parser.parse(v)
#        d = d.strftime("%Y-%m-%d")
#        if v != d:
#            print(f"{v} => {d}")
        return d.timestamp() * (10**9)
    except dateutil.parser.ParserError:
        return v;


def add_or_get_package(conn, proj_id, pkg):
    c = conn.cursor()

    c.execute("SELECT package_id FROM packages_w WHERE project_id = ? AND name = ?", (proj_id, pkg))
    if r := c.fetchone():
        return r[0]

    c.execute("INSERT INTO packages_w (project_id, name) VALUES(?, ?) RETURNING package_id", (proj_id, pkg))
    return c.fetchone()[0]


def add_or_get_user(conn, u):
    c = conn.cursor()

    # lookup by email
    if u[0]:
        c.execute("SELECT user_id FROM users_w WHERE email = ? COLLATE NOCASE", (u[0],))
        if r := c.fetchone():
            return r[0]

    # lookup by username
    if u[1]:
        c.execute("SELECT user_id FROM users_w WHERE username = ? COLLATE NOCASE", (u[1],))
        if r := c.fetchone():
            return r[0]

    # lookup by name
    if u[1]:
        c.execute("SELECT user_id FROM users_w WHERE realname = ? COLLATE NOCASE", (u[1],))
        if r := c.fetchone():
            return r[0]

    rec = {
        'email': u[0],
        'realname': u[1] or '',
        'username': u[1] or '',
        'matched': False
    }

    cols, vals = make_cols_vals(rec)
    c.execute(f"INSERT INTO users_w ({cols}) VALUES({vals}) RETURNING user_id", rec)
    return c.fetchone()[0]


def normalize_filename(filename):
    filename = filename.replace('_', ' ')
    return filename[0].capitalize() + filename[1:]


def fname_for_meta(filename):
    filename = normalize_filename(filename)
    return f"File:{filename}"


def get_url(filename, file_meta):
    if meta := file_meta.get(fname_for_meta(filename)):
        return meta['url']
    return None 


def get_publisher(filename, file_meta):
    if meta := file_meta.get(fname_for_meta(filename)):
        return meta['user']
    return None 


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


def parse_game_info(sec, mrec, file_meta):
    # parse GameInfo
    if m := ginfo_re.search(sec):
        for i, item in iterate_items(sec, m.end(0)):
            k, v = split_item(item)
            if k and v:
                mrec[f"game_{k}"] = v

        # strip out GameInfo
        sec = sec[0:m.start(0)] + sec[i+1:]

    return sec


def parse_module_contact_info(sec, mrec, owners, contribs):
    # parse ModuleContactInfo
    if m := cinfo_re.search(sec):
        for i, item in iterate_items(sec, m.end(0)):
            k, v = split_item(item)
            if k and v:
                if k == 'maintainer':
                    owners += parse_emails(v)
                elif k == 'contributors':
                    contribs += parse_emails(v)
                else:
                    mrec[k] = v

        # strip out ModuleContactInfo
        sec = sec[0:m.start(0)] + sec[i+1:]

    return sec


def parse_module_file(sec, m, i, num, file_meta, file_ctimes):
    frec = {
        'project_id': num,
        'semver': -1
    }

    fmaints = []
    fcontribs = []
    fpub = None
    pkg = None

    for i, item in iterate_items(sec, m.end(0)):
        k, v = split_item(item)
        if k and v and k != 'size':
            if k == 'maintainer':
                fmaints += parse_emails(v)
            elif k == 'contributors':
                fcontribs += parse_emails(v)
            else:
                if k == 'date':
                    v = parse_date(v)

                frec[k] = v

    # strip out ModuleFiles
    sec = sec[0:m.start(0)] + sec[i+1:]
    i = m.start(0)

    if version := frec.get('version'):
        frec['version_raw'] = version
        del frec['version']

    if filename := frec.get('filename'):
        if url := get_url(filename, file_meta):
            frec['fileurl'] = url

        if ctime := file_ctimes.get(f"File:{filename.replace('_', ' ')}"):
            frec['published_at'] = ctime

        fpub = get_publisher(filename, file_meta)

        pkg = try_extract_package(filename)

    return sec, i, frec, fmaints, fcontribs, fpub, pkg


def parse_players_section(sec, num, players):
    # parse Players section
    if m := div_open_re.search(sec):
        dbeg = m.start(0)
        dend = sec.index('</div>', dbeg) + 6

        players += parse_players(sec[dbeg:dend])

        sec = sec[0:dbeg] + sec[dend:]

    return sec


image_prefix_re = re.compile(r'^(Image|File)\s*:\s*', flags=re.IGNORECASE)


def parse_screenshot_image(filename, file_meta, file_ctimes):
    irec = {}

    if filename:
        if filename.startswith("[[") and filename.endswith("]]"):
            filename = filename[2:-2]

        filename = filename.lstrip().split('|')[0].replace('%20', ' ').rstrip()
        filename = image_prefix_re.sub('', filename)
        filename = filename[0:1].upper() + filename[1:]

        if filename:
            irec['filename'] = filename

            if url := get_url(filename, file_meta):
                irec['url'] = url

            if ctime := file_ctimes.get(f"File:{filename.replace('_', ' ')}"):
                irec['published_at'] = ctime

            if ipub := get_publisher(filename, file_meta):
                irec['published_by'] = ipub

    return irec


def parse_screenshots_section(sec, file_meta, file_ctimes, images):
    # parse screenshots section
    if m := gallery_open_re.search(sec):
        gbeg = m.start(0)
        gend_beg = sec.index('</gallery>', gbeg)
        gend = gend_beg + 10

        inner = sec[m.end(0):gend_beg]

        for imgname in parse_gallery(inner):
            imgname = imgname.strip()
            if irec := parse_screenshot_image(imgname, file_meta, file_ctimes):
                images.append(irec)

        sec = sec[0:gbeg] + sec[gend:]

    return sec


def do_insert_users(conn, table, id_col, e, id_val):
    uid = add_or_get_user(conn, e)
    conn.execute(
        f"INSERT OR IGNORE INTO {table} (user_id, {id_col}) VALUES(?, ?)",
        (uid, id_val)
    )


def process_wikitext(conn, file_meta, file_ctimes, page_ctimes, filename, num):
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
        'project_id': num,
        'created_at': page_ctimes[f"Module:{title}"]
    }

    text = ''

    players = []
    owners = []
    contribs = []
    images = []

    possible_owners = []
    possible_contribs = []

    # split sections
    for sec_title, sec in iterate_sections(t):
        sec = parse_game_info(sec, mrec, file_meta)
        sec = parse_module_contact_info(sec, mrec, owners, contribs)

        # parse ModuleFiles
        i = 0
        while True:
            m = mfile_re.search(sec, i)
            if not m:
                break

            sec, i, frec, fmaints, fcontribs, fpub, pkg = parse_module_file(
                sec, m, i, num, file_meta, file_ctimes
            )

            if pkg:
                pkg_id = add_or_get_package(conn, num, pkg)
                frec['package_id'] = pkg_id

            if fpub:
                frec['published_by'] = add_or_get_user(conn, (None, fpub))                
            fid = do_insert(conn, 'files_w', 'file_id', frec)

            for e in fmaints:
                do_insert_users(conn, 'file_maintainers_w', 'file_id', e, fid)

            for e in fcontribs:
                do_insert_users(conn, 'file_contributors_w', 'file_id', e, fid)

            possible_owners += fmaints
            possible_contribs += fcontribs

        if sec_title == 'Players':
            sec = parse_players_section(sec, num, players)
        elif sec_title in ('Screen Shots', 'Screenshots'):
            sec = parse_screenshots_section(sec, file_meta, file_ctimes, images)

        # trim out other cruft from text
        sec = text_cruft_re.sub('', sec)
        sec = sec.strip()

        if sec:
            # add back section title
            if sec_title and sec_title not in ('Comments'):
                text += f"== {sec_title} ==\n"

            text += f"{sec}\n"

    # convert the remaining wikitext to markdown
    readme = pypandoc.convert_text(text, 'md', format='mediawiki')

    # remove spurious HTML comments
    readme = readme.replace("""```{=html}
<!-- -->
```""", '')

    mrec['text'] = readme

    # convert game image url to game image name
    if imgname := mrec.get('game_image'):
        if url := get_url(imgname, file_meta):
            imgname = normalize_filename(imgname)
            mrec['game_image'] = imgname 

            if irec := parse_screenshot_image(imgname, file_meta, file_ctimes):
                images.append(irec)

    do_insert(conn, 'projects_w', 'project_id', mrec)

    for e in players:
        do_insert_users(conn, 'players_w', 'project_id', e, num)

    # try to ensure we have somebody as an owner
    if not owners:
        owners = contribs
        if not owners:
            owners = possible_owners
            if not owners:
                owners = possible_contribs

    for e in owners:
        do_insert_users(conn, 'owners_w', 'project_id', e, num)

    for e in contribs:
        do_insert_users(conn, 'module_contributors_w', 'project_id', e, num)

    for e in images:
        e['project_id'] = num 
        if ipub := e.get('published_by'):
            e['published_by'] = add_or_get_user(conn, (None, ipub))                
        do_insert_or_ignore(conn, 'images_w', 'project_id', e)


def create_db(conn):
    with conn as cur:
        cur.execute('DROP TABLE IF EXISTS projects_w')
        cur.execute('''
CREATE TABLE projects_w (
    project_id INTEGER PRIMARY KEY,
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
    created_at INTEGER,
    text TEXT
)
        ''')

        cur.execute('DROP TABLE IF EXISTS owners_w')
        cur.execute('''
CREATE TABLE owners_w (
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    UNIQUE(user_id, project_id),
    FOREIGN KEY(user_id) REFERENCES users_w(user_id),
    FOREIGN KEY(project_id) REFERENCES projects_w(project_id)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS module_contributors_w')
        cur.execute('''
CREATE TABLE module_contributors_w (
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users_w(user_id),
    FOREIGN KEY(project_id) REFERENCES projects_w(project_id)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS files_w')
        cur.execute('''
CREATE TABLE files_w (
    file_id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    package_id INTEGER,
    filename TEXT,
    basename TEXT,
    fileurl TEXT,
    filetype TEXT,
    version_raw TEXT,
    version TEXT,
    version_major INTEGER,
    version_minor INTEGER,
    version_patch INTEGER,
    version_pre TEXT,
    version_build TEXT,
    semver INTEGER NOT NULL,
    description TEXT,
    date TEXT,
    size INTEGER,
    checksum TEXT,
    published_at INTEGER,
    published_by INTEGER,
    compatibility TEXT,
    FOREIGN KEY(project_id) REFERENCES projects_w(project_id),
    FOREIGN KEY(package_id) REFERENCES packages_w(package_id),
    FOREIGN KEY(published_by) REFERENCES users_w(user_id)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS file_maintainers_w')
        cur.execute('''
CREATE TABLE file_maintainers_w (
    user_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users_w(user_id),
    FOREIGN KEY(file_id) REFERENCES files_w(file_id)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS file_contributors_w')
        cur.execute('''
CREATE TABLE file_contributors_w (
    user_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users_w(user_id),
    FOREIGN KEY(file_id) REFERENCES files_w(file_id)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS users_w')
        cur.execute('''
CREATE TABLE users_w (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    realname TEXT,
    email TEXT,
    matched INTEGER NOT NULL,
    UNIQUE(email)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS players_w')
        cur.execute('''
CREATE TABLE players_w (
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    UNIQUE(user_id, project_id),
    FOREIGN KEY(user_id) REFERENCES users_w(user_id),
    FOREIGN KEY(project_id) REFERENCES projects_w(project_id)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS packages_w')
        cur.execute('''
CREATE TABLE packages_w (
    package_id INTEGER PRIMARY KEY NOT NULL,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects_w(project_id),
    UNIQUE(project_id, name)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS releases_w')
        cur.execute('''
CREATE TABLE releases_w (
    release_id INTEGER PRIMARY KEY NOT NULL,
    package_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    version TEXT,
    version_major INTEGER,
    version_minor INTEGER,
    version_patch INTEGER,
    version_pre TEXT,
    version_build TEXT,
    url TEXT,
    size INTEGER,
    checksum TEXT,
    published_at INTEGER,
    published_by INTEGER,
    FOREIGN KEY(package_id) REFERENCES packages(package_id),
    FOREIGN KEY(published_by) REFERENCES users_w(user_id)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS images_w')
        cur.execute('''
CREATE TABLE images_w (
  project_id INTEGER NOT NULL,
  filename TEXT NOT NULL,
  url TEXT,
  published_at INTEGER,
  published_by INTEGER,
  FOREIGN KEY(project_id) REFERENCES projects(project_id),
  FOREIGN KEY(published_by) REFERENCES users(user_id),
  UNIQUE(project_id, filename)
)
        ''')


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
            do_insert(cur, 'users_w', 'user_id', rec)


ver_zero_fix_re = re.compile(r'^((?:0|[1-9]\d*)\.)0+(\d+)')


def try_semver(version):
    try:
        return semver.Version.parse(version)
    except ValueError:
        try:
            return semver.Version.parse(version + '.0')
        except ValueError:
            try:
                return semver.Version.parse(version + '.0.0')
            except ValueError:
                return None


def try_parse_version(version):
    # strip leading "version" letters
    if version.startswith("Version"):
        version = version[7:]
    elif version.startswith("ver") or version.startswith("Ver"):
        version = version[3:]
    elif version.startswith("v."):
        version = version[2:]
    elif version.startswith("v") or version.startswith("V"):
        version = version[1:]

    version = version.strip()

    if v := try_semver(version):
        return v

    version = ver_zero_fix_re.sub(r'\1\2', version)

    if v := try_semver(version):
        return v

    return None


ext_re = re.compile(r'(?i)\.(v?(mod|mdx)|zip)$')
ver_re = re.compile(r'v?\d+([_.-]\d+)*$')


def try_extract_version(filename):
    filename = ext_re.sub('', filename)

    if vu := ver_re.search(filename):
        vu = vu.group(0).replace('_', '.').replace('-', '.')
        return try_parse_version(vu)

    return None


def try_extract_package(filename):
    filename = ext_re.sub('', filename)

    if vu := ver_re.search(filename):
        return filename[:vu.start(0)].rstrip(" _-")

# TODO: these are probably not great package names
    return filename


def populate_versions(conn, vpath):
    with conn as cur:
        # insert version information from reading modulefiles
        with open(vpath, 'r') as f:
            for line in f:
                s = line.split('\t', maxsplit=3)

                url, size, sha256 = s[0:3]
                url = url.strip()
  
                v = None

                if len(s) == 4:
                    version = s[3].strip()
                    v = try_parse_version(version)

                if v is not None:
                    cur.execute('''
UPDATE files_w
SET
    version_raw = ?,
    version = ?,
    version_major = ?,
    version_minor = ?,
    version_patch = ?,
    version_pre = ?,
    version_build = ?,
    semver = 1,
    size = ?,
    checksum = ?
WHERE fileurl = ?
                        ''',
                        (
                            version,
                            str(v),
                            v.major,
                            v.minor,
                            v.patch,
                            v.prerelease,
                            v.build,
                            size,
                            sha256,
                            url
                        )
                    )

                else:
                    cur.execute('''
UPDATE files_w
SET
    size = ?,
    checksum = ?
WHERE fileurl = ?
                        ''',
                        (
                            size,
                            sha256,
                            url
                        )
                    )

        # no version information
        cur.execute('''
UPDATE files_w
SET semver = 0
WHERE version_raw IS NULL
AND INSTR(filename, "0") == 0
AND INSTR(filename, "1") == 0
AND INSTR(filename, "2") == 0
AND INSTR(filename, "3") == 0
AND INSTR(filename, "4") == 0
AND INSTR(filename, "5") == 0
AND INSTR(filename, "6") == 0
AND INSTR(filename, "7") == 0
AND INSTR(filename, "8") == 0
AND INSTR(filename, "9") == 0
            '''
        )

        # try to extract version from filename
        rows = cur.execute('''
SELECT file_id, filename
FROM files_w
WHERE semver = -1
AND version_raw IS NULL
            '''
        )

        for row in rows:
            if row[1] is not None:
                if v := try_extract_version(row[1]):
                    cur.execute('''
UPDATE files_w
SET
    version = ?,
    version_major = ?,
    version_minor = ?,
    version_patch = ?,
    version_pre = ?,
    version_build = ?,
    semver = 1
WHERE file_id = ?
                        ''',
                        (
                            str(v),
                            v.major,
                            v.minor,
                            v.patch,
                            v.prerelease,
                            v.build,
                            row[0]
                        )
                    )


def convert_for_gls(conn):
    with conn as cur:
        cur.execute('''
INSERT INTO users (user_id, username)
SELECT user_id, username
FROM users_w
WHERE matched = 1
            '''
        )

# TODO: modified at should be max of all timestamps associated with
# the project
        cur.execute('''
INSERT INTO projects (
    project_id,
    name,
    created_at,
    modified_at,
    modified_by,
    revision,
    description,
    game_title,
    game_title_sort,
    game_publisher,
    game_year,
    readme
)
SELECT
    projects_w.project_id,
    CAST(projects_w.project_id AS TEXT),
    projects_w.created_at,
    projects_w.created_at,
    MIN(owners_w.user_id),
    1,
    projects_w.game_title,
    projects_w.game_title,
    projects_w.game_title_sort_key,
    COALESCE(projects_w.game_publisher, ""),
    COALESCE(projects_w.game_year, ""),
    projects_w.text
FROM projects_w
JOIN owners_w
ON projects_w.project_id = owners_w.project_id 
GROUP BY projects_w.project_id
            '''
        )

        cur.execute('''
INSERT INTO players (user_id, project_id)
SELECT players_w.user_id, players_w.project_id
FROM players_w
JOIN users_w
ON players_w.user_id = users_w.user_id
WHERE users_w.matched = 1
            '''
        )

        cur.execute('''
INSERT INTO owners (user_id, project_id)
SELECT owners_w.user_id, owners_w.project_id
FROM owners_w
JOIN users_w
ON owners_w.user_id = users_w.user_id
WHERE users_w.matched = 1
            '''
        )

        cur.execute('''
INSERT INTO releases_w (
    package_id,
    version,
    version_major,
    version_minor,
    version_patch,
    version_pre,
    version_build,
    url,
    filename,
    size,
    checksum,
    published_at,
    published_by
)
SELECT
    files_w.package_id,
    files_w.version,
    files_w.version_major,
    files_w.version_minor,
    files_w.version_patch,
    COALESCE(files_w.version_pre, ""),
    COALESCE(files_w.version_build, ""),
    files_w.fileurl,
    files_w.filename,
    files_w.size,
    files_w.checksum,
    files_w.published_at,
    files_w.published_by
FROM files_w
WHERE files_w.filename IS NOT NULL
    AND files_w.package_id IS NOT NULL
            '''
        )

        cur.execute('''
INSERT OR IGNORE INTO packages (
    package_id,
    project_id,
    name,
    created_at,
    created_by
)
SELECT
    packages_w.package_id,
    packages_w.project_id,
    packages_w.name,
	MIN(files_w.published_at),
	files_w.published_by
FROM packages_w
JOIN files_w
ON packages_w.package_id = files_w.package_id
GROUP BY packages_w.package_id
            '''
        )

        cur.execute('''
INSERT OR IGNORE INTO releases (
    release_id,
    package_id,
    version,
    version_major,
    version_minor,
    version_patch,
    version_pre,
    version_build,
    url,
    filename,
    size,
    checksum,
    published_at,
    published_by
)
SELECT
    release_id,
    package_id,
    version,
    version_major,
    version_minor,
    version_patch,
    version_pre,
    version_build,
    url,
    filename,
    size,
    checksum,
    published_at,
    published_by
FROM releases_w
            '''
        )

        cur.execute('''
INSERT OR IGNORE INTO authors (
    user_id,
    release_id
)
SELECT
    user_id,
    file_id
FROM file_maintainers_w
            '''
        )

        cur.execute('''
INSERT OR IGNORE INTO authors (
    user_id,
    release_id
)
SELECT
    user_id,
    file_id
FROM file_contributors_w
            '''
        )
 
        cur.execute('''
INSERT INTO images (
    project_id,
    filename,
    url,
    published_at,
    published_by
)
SELECT
    project_id,
    filename,
    url,
    published_at,
    published_by
FROM images_w
WHERE url IS NOT NULL
    AND published_at IS NOT NULL
    AND published_by IS NOT NULL
            '''
        )

        cur.execute('''
UPDATE projects
SET image = x.filename
FROM (
    SELECT images.filename, images.project_id
    FROM projects_w
    LEFT JOIN images
    ON projects_w.project_id = images.project_id
        AND projects_w.game_image = images.filename
) AS x
WHERE projects.project_id = x.project_id 
            '''
        )

# FIXME: should also check mtime of page, might be later
        cur.execute('''
UPDATE projects
SET modified_at = x.published_at
FROM (
    SELECT MAX(releases.published_at) AS published_at, packages.project_id
    FROM releases
    JOIN packages
    ON packages.package_id = releases.package_id
    GROUP BY packages.project_id 
) AS x
WHERE projects.project_id = x.project_id 
            '''
        )

        cur.execute('''
INSERT INTO project_data (
    project_data_id,
    project_id,
    description,
    game_title,
    game_title_sort,
    game_publisher,
    game_year,
    readme,
    image
)
SELECT
    project_id,
    project_id,
    description,
    game_title,
    game_title_sort,
    game_publisher,
    game_year,
    readme,
    image
FROM projects
            '''
        ) 

        cur.execute('''
INSERT INTO project_revisions (
    project_id,
    name,
    created_at,
    modified_at,
    modified_by,
    revision,
    project_data_id
)
SELECT
    project_id,
    name,
    created_at,
    modified_at,
    modified_by,
    1,
    project_id
FROM projects
            '''
        )


async def process_wikitext_async(conn, files, file_ctimes, page_ctimes, filename, num):
    with conn as cur:
        try:
            process_wikitext(cur, files, file_ctimes, page_ctimes, filename, num)
        except Exception as e:
            raise RuntimeError(f"!!! {num}") from e


async def run():
    fpath = 'data/files.json'
    upath = 'data/users.json'
    vpath = 'data/versions'
    wpath = 'data/wikitext'
    p_ctime_path = 'data/page_ctimes.json'
    f_ctime_path = 'data/file_ctimes.json'
    dbpath = 'projects.db'

    with open(fpath, 'r') as f:
        files = json.load(f)

    with open(f_ctime_path, 'r') as f:
        file_ctimes = json.load(f)

    file_ctimes = { k: datetime.datetime.fromisoformat(v).timestamp() * (10**9) for k, v in file_ctimes.items() }

    with open(p_ctime_path, 'r') as f:
        page_ctimes = json.load(f)

    page_ctimes = { k: datetime.datetime.fromisoformat(v).timestamp() * (10**9) for k, v in page_ctimes.items() }

    with contextlib.closing(sqlite3.connect(dbpath)) as conn:
        create_db(conn)
        populate_users(conn, upath)

        async with asyncio.TaskGroup() as tg:
#        for f in sorted(glob.glob('data/[0-9]*'), key=lambda x: int(os.path.basename(x)))[2883:]:
            for f in glob.glob(f"{wpath}/[0-9]*"):
                num = int(os.path.basename(f))
                tg.create_task(process_wikitext_async(conn, files, file_ctimes, page_ctimes, f, num))

#        process_wikitext(conn, files, 'data/875', 875)

        populate_versions(conn, vpath)
        convert_for_gls(conn)


if __name__ == '__main__':
    asyncio.run(run())
