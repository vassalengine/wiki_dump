import asyncio
import datetime
import contextlib
import glob
import json
import os.path
import re
import sqlite3
import unicodedata

import dateutil.parser
import pypandoc
import semver
import urllib.parse

from versions import try_parse_version


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


def do_insert_users(conn, table, id_col, e, id_val):
    uid = add_or_get_user(conn, e)
    conn.execute(
        f"INSERT OR IGNORE INTO {table} (user_id, {id_col}) VALUES(?, ?)",
        (uid, id_val)
    )


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
    game_players_min INTEGER,
    game_players_max INTEGER,
    game_length TEXT,
    game_length_min INTEGER,
    game_length_max INTEGER,
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
    release_id INTEGER NOT NULL,
    filename TEXT,
    basename TEXT,
    url TEXT,
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
    sha256 TEXT,
    published_at INTEGER,
    published_by INTEGER,
    compatibility_raw TEXT,
    compatibility TEXT,
    FOREIGN KEY(release_id) REFERENCES releases_w(release_id),
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
    version TEXT,
    version_major INTEGER,
    version_minor INTEGER,
    version_patch INTEGER,
    version_pre TEXT,
    version_build TEXT,
    published_at INTEGER,
    published_by INTEGER,
    FOREIGN KEY(package_id) REFERENCES packages_w(package_id),
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
  FOREIGN KEY(project_id) REFERENCES projects_w(project_id),
  FOREIGN KEY(published_by) REFERENCES users_w(user_id),
  UNIQUE(project_id, filename)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS galleries_w')
        cur.execute('''
CREATE TABLE galleries_w (
  project_id INTEGER NOT NULL,
  filename TEXT NOT NULL,
  description TEXT,
  published_at INTEGER,
  published_by INTEGER,
  position INTEGER NOT NULL,
  FOREIGN KEY(project_id) REFERENCES projects_w(project_id),
  FOREIGN KEY(published_by) REFERENCES users_w(user_id),
  FOREIGN KEY(project_id, filename) REFERENCES images_w(project_id, filename),
  UNIQUE(project_id, filename),
  UNIQUE(project_id, position)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS tags_w')
        cur.execute('''
CREATE TABLE tags_w (
  project_id INTEGER NOT NULL,
  tag TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES projects_w(project_id),
  UNIQUE(project_id, tag)
)
        ''')

        cur.execute('DROP TABLE IF EXISTS links_w')
        cur.execute('''
CREATE TABLE links_w (
  project_id INTEGER NOT NULL,
  link TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES projects_w(project_id)
)
        ''')


def populate_users(conn, upath):
    with open(upath, 'r') as f:
        users = json.load(f)

    with conn as cur:
        for u in users:
            rec = {
                'user_id': u['id'],
                'email': u['email'],
                'realname': u['name'],
                'username': u['username'],
                'matched': True
            }
            do_insert(cur, 'users_w', 'user_id', rec)


def add_placeholder_user_emails(conn):
    with conn as cur:
        cur.execute('''
UPDATE users_w
SET email = FORMAT("placeholder+%s@vassal.org", username)
WHERE email IS NULL
        ''')


ver_zero_fix_re = re.compile(r'^((?:0|[1-9]\d*)\.)0+(\d+)')

ext_re = re.compile(r'(?i)\.(v?(mod|mdx)|zip)$')
ver_re = re.compile(r'v?\d+([_.-]\d+)*$')


def try_extract_version(filename):
    filename = ext_re.sub('', filename)

    if vu := ver_re.search(filename):
        vu = vu.group(0)
        if len(vu) < len(filename):
            vu = vu.replace('_', '.').replace('-', '.')
            return try_parse_version(vu)

    return None


def populate_versions(conn, vpath):
    with conn as cur:
        # fill version parts for releases
        rows = cur.execute('''
SELECT release_id, version
FROM releases_w
            '''
        )

        for r in rows:
            try:
                v = semver.Version.parse(r[1])
            except ValueError:
                continue

            cur.execute('''
UPDATE releases_w
SET version_major = ?,
    version_minor = ?,
    version_patch = ?,
    version_pre = ?,
    version_build = ?
WHERE release_id = ?
                ''',
                (
                    v.major,
                    v.minor,
                    v.patch,
                    v.prerelease,
                    v.build,
                    r[0]
                )
            )

        # insert version information from reading modulefiles
        with open(vpath, 'r') as f:
            j = json.load(f)

            for url, d in j.items():
                size = d['size']
                sha256 = d['sha256']
                version = d['version']

                if v := d.get('version_parsed', None):
                    v = semver.Version(major=v[0], minor=v[1], patch=v[2], prerelease=v[3], build=v[4])

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
    sha256 = ?
WHERE url = ?
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
    sha256 = ?
WHERE url = ?
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


vassal_re = re.compile('vassal|engine', re.I)

compat_hashes = {
    '8392bed7a2938557d77377f19ad9fa8ed56f46ef07555e26c20a49125a15273b': None,
    '3ed67d57ef9ae2b9b915944fa506e780e3eab48b7da7d9137f7932975087c3a0': None,
    '4043d8ab0a27fbb8e19853cd4161097059480db16f9c0c43d5f6c37649511817': '<= 2.9.9',
    '83ab8765eda31f48781a566f25e170ab798e1070345454ab1d9ada6351772b13': '<= 2.9.9',
    '895c606b9ff81d36be73d18b705d882a1b014738f5b253ef3bc7af5d9e05ce4c': None,
    '94e80985ce4812c9e50d99211665316f717f1aed79e9391bfea1ef12667889f1': None,
    'b6bc13fb6f2693c19e262747bc8a21f5762f9677f5d7a23e9948122589d70281': None,
    '77032aebc061016acf4c98061cb604ab8fd9e54ee93641503f6f39135031d9ab': None,
    'a1fe80a87b1519f9e45b3a0195888458255b63d020925bf50ac0dd28701666bb': None,
    'fba504e9dd51f9dda4b18cf24313476efc154516aa6f31f529cffd0f0890605a': '>= 3.2.17',
    'c4de2b29d255edcf201edd465195e3cee366e5cacc77b84e42cc864b3ae1e131': '>= 3.2.0, <= 3.4',
    '172ad09d0a0cbeb1002115d4c84f5dcff82df513b26e7df02cc5928e328b5f72': '>= 3.2.0, <= 3.4',
    'a000c078bab580871646f58b30f4638493cac5741c138d60fbb553dc26f0a644': '>= 3.1.14, <= 3.2.2',
    '08a334efe2de86a4161f649dccb439b7f2d079853631881093b389c9016010a1': '>= 3.1.17, <= 3.2.2',
    '681b59211a1cdbf2c8ee84a81f50621d164af0b328cab0255006bc822b31295a': '>= 3.4, <= 3.5',
    'cf48713e4af042016c0abcb2180f645ba6353e82853cd05b4cad31523203833b': '>= 3.5, != 3.6.0, != 3.6.1, != 3.6.2, != 3.6.3 != 3.6.4',
    '8cfdc84a9e48302e1d554fedd41b883843c9dc8db027195d0562602156a885c3': '>= 3.2.17, < 3.4',
    '87adbd9488e1691d069bc88ac39f6c54775b0e4c0070fb04bec16a29ad2860bf': '>= 3.2.17, <= 3.5.8',
    '5effa6cb2eff2ff652cb88d51dd44e54bda3d1746afbe084aa40aecee10c45b4': '>= 3.2.17, <= 3.5.8',
    'be820a44f2ad3b540dd6c7b4e6e8083d7c1c91f338ec5dd9697fb2ef584664f6': '>= 3.2.17, <= 3.5.8',
    'aec53bd77066a9e3bf78f02ee622f47653890e7f0a168d36fc13aa5d9348e9b3': '>= 3.7.0',
}


def populate_compatibility(conn):
    with conn as cur:
        rows = cur.execute('''
SELECT file_id, compatibility_raw, sha256
FROM files_w
WHERE compatibility_raw IS NOT NULL
            '''
        )

        for row in rows:
            version = vassal_re.sub('', row[1], count=1).replace('+', '').replace("'", '').strip()

            compat = None

            if row[2] in compat_hashes:
                cv = compat_hashes[row[2]]
                if cv is None:
                    v = try_parse_version(version)
                    compat = f">= {v}"
                else:
                    compat = cv

            else:
                if version.endswith(' or lower'):
                    version = version.removesuffix(' or lower')
                    op = '<='
                else:
                    op = '>='

                if v := try_parse_version(version):
                    # skip versions which aren't Vassal ones
                    if v.major != 3 or v.minor > 7:
                        continue

                    compat = f"{op} {v}"

            if compat is not None:
                cur.execute('''
UPDATE files_w
SET compatibility = ?
WHERE file_id = ?
                    ''',
                    (
                        compat,
                        row[0]
                    )
                )


def rewrite_image_links(conn):
    with conn as cur:
        rows = cur.execute('''
SELECT
    links_w.link,
    projects_w.project_id,
    links_w.project_id
FROM links_w
JOIN projects_w
ON replace(links_w.link, "_", " ") = projects_w.game_title
            '''
        ).fetchall()

        for r in rows:
            cur.execute('''
UPDATE projects_w
SET text = replace(text, "Module:" || ?, ?)
WHERE projects_w.project_id = ?
                ''',
                r
            )


def apply_fixups(conn):
    with conn as cur:

        # fix sort keys
        sort_fixup = [
            ('¡Apuren el corralito!: The 2nd Battle of Alihuatá, December 1933', 'Apuren el corralito: The 2nd Battle of Alihuatá, December 1933'),
            ('¡Arriba España!', 'Arriba España'),
            ('"The Aragón Front"', 'Aragón Front, The'),
            ("'65: Squad-Level Combat in the Jungles of Vietnam", '65: Squad-Level Combat in the Jungles of Vietnam'),
            ("'CA' Tactical Naval Warfare in the Pacific, 1941-45", 'CA Tactical Naval Warfare in the Pacific, 1941-45'),
            ('(Your Name Here) and the Argonauts', 'Your Name Here and the Argonauts'),
            ("'Wacht am Rhein': The Battle of the Bulge, 16 Dec 44-2 Jan 45", 'Wacht am Rhein: The Battle of the Bulge, 16 Dec 44-2 Jan 45')
        ]

        for sf in sort_fixup:
            cur.execute('''
UPDATE projects_w
SET game_title_sort_key = ?
WHERE game_title = ?
                ''',
                (sf[1], sf[0])
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

        # release publish time is min across all files
        cur.execute('''
UPDATE releases_w
SET published_at = pub.published_at, published_by = pub.published_by
FROM (
    SELECT
        files_w.release_id,
        MIN(files_w.published_at) as published_at,
        files_w.published_by
    FROM files_w
    GROUP BY files_w.release_id
) AS pub
WHERE pub.release_id = releases_w.release_id
            '''
        )

        cur.execute('''
INSERT INTO projects (
    project_id,
    name,
    normalized_name,
    created_at,
    modified_at,
    modified_by,
    revision,
    description,
    game_title,
    game_title_sort,
    game_publisher,
    game_year,
    game_players_min,
    game_players_max,
    game_length_min,
    game_length_max,
    readme
)
SELECT
    projects_w.project_id,
    CAST(projects_w.project_id AS TEXT),
    CAST(projects_w.project_id AS TEXT),
    projects_w.created_at,
    projects_w.created_at,
    MIN(owners_w.user_id),
    1,
    "",
    projects_w.game_title,
    projects_w.game_title_sort_key,
    COALESCE(projects_w.game_publisher, ""),
    COALESCE(projects_w.game_year, ""),
    projects_w.game_players_min,
    projects_w.game_players_max,
    projects_w.game_length_min,
    projects_w.game_length_max,
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
	MIN(releases_w.published_at),
	releases_w.published_by
FROM packages_w
JOIN releases_w
ON packages_w.package_id = releases_w.package_id
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
    published_at,
    published_by
)
SELECT
    releases_w.release_id,
    releases_w.package_id,
    releases_w.version,
    releases_w.version_major,
    releases_w.version_minor,
    releases_w.version_patch,
    COALESCE(releases_w.version_pre, ""),
    COALESCE(releases_w.version_build, ""),
    releases_w.published_at,
    releases_w.published_by
FROM releases_w
            '''
        )

# SELECT files_w.*, releases_w.* FROM files_w JOIN releases_w ON files_w.package_id = releases_w.package_id AND files_w.version = releases_w.version;

        cur.execute('''
INSERT OR IGNORE INTO files (
    file_id,
    release_id,
    url,
    filename,
    size,
    sha256,
    requires,
    published_at,
    published_by
)
SELECT
    file_id,
    release_id,
    url,
    filename,
    size,
    sha256,
    compatibility,
    published_at,
    published_by
FROM files_w
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
INSERT INTO image_revisions (
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
FROM images
            '''
        )

        cur.execute('''
INSERT INTO galleries (
    project_id,
    filename,
    description,
    published_at,
    published_by,
    position
)
SELECT
    project_id,
    filename,
    description,
    published_at,
    published_by,
    position
FROM galleries_w
WHERE published_at IS NOT NULL
    AND published_by IS NOT NULL
        ''')

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

        # project modified time is the max of all timestamps associated with
        # the project
        cur.execute('''
UPDATE projects
SET modified_at = x.published_at
FROM (
    SELECT project_id, MAX(published_at) as published_at
    FROM (
        SELECT packages.project_id, releases.published_at
        FROM releases
        JOIN packages
        ON packages.package_id = releases.package_id
        UNION
        SELECT images.project_id, images.published_at
        FROM images
    )
    GROUP BY project_id
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
    game_players_min,
    game_players_max,
    game_length_min,
    game_length_max,
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
    game_players_min,
    game_players_max,
    game_length_min,
    game_length_max,
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

        cur.execute('''
INSERT INTO tags (
    project_id,
    tag
)
SELECT
    project_id,
    tag
FROM tags_w
            '''
        )


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


def add_or_get_release(conn, pkg_id, ver):
    c = conn.cursor()

    c.execute("SELECT release_id FROM releases_w WHERE package_id = ? AND version = ?", (pkg_id, ver))
    if r := c.fetchone():
        return r[0]

    c.execute("INSERT INTO releases_w (package_id, version) VALUES(?, ?) RETURNING release_id", (pkg_id, ver))
    return c.fetchone()[0]


def remove_accents(s):
    nfkd_form = unicodedata.normalize('NFKD', s)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def lookup_user(c, u):
    # lookup by email
    if u[0]:
        c.execute("SELECT user_id FROM users_w WHERE email = ? COLLATE NOCASE", (u[0],))
        if r := c.fetchone():
            return r[0]

    # lookup by username
    if u[1]:
        c.execute("SELECT user_id FROM users_w WHERE username = ? COLLATE NOCASE", (u[1].replace(' ', '_'),))
        if r := c.fetchone():
            return r[0]

    # lookup by name
    if u[1]:
        c.execute("SELECT user_id FROM users_w WHERE realname = ? COLLATE NOCASE", (u[1],))
        if r := c.fetchone():
            return r[0]

    return None


bad_username_re = re.compile('[^a-zA-Z0-9._-]')


email_map = {
    'dulgin@arcor.de': 'iberkenkamp-darnedde@arcor.de',
    'shadowagl@126.com': 'shadowbbs@126.com',
    'gaetbe@gmail.com': 'gaetbe@yahoo.fr',
    'rlee50@sc.rr.com': 'richz99ral@yahoo.com',
    'placeholder+monsieur_poulet@vassal.org': 'mbelanger@iname.com',
    'placeholder+dave_deitch@vassal.org': 'davenet@comcast.net',
}

user_map = {
    'Bugggg': 'mrbug',
    'Peter Dietrich': 'pdietrich2',
    'Pdietrich': 'pdietrich2',
    'Greg Amos': 'Teufelhunde',
    'Monsieur_Poulet': 'MonsieurPoulet',
    'Bruce Mansfield': 'bcmansfield',
    'Caesar78': 'alecrespi',
    'Giacomo': 'Giacomo_Rossi',
    'Novasuecia': 'Nicholas_Hjelmberg',
    'Cemoreno': 'CesarM',
    'Vance Strickland': 'barthheart',
    'David L. Jones': 'TheLockers',
    'Dave Jones': 'TheLockers',
    'Mathias Daval': 'cyberlp23',
    'rlee50': 'Richz99',
    'Jonathan Burdick': 'burdick.ip.research',
    'Tim Craire': 'easyalias',
    'bgg rattle': 'rattle',
    'Edgar Gallego': 'Edgar',
    'Jim Perkinson': 'LeLechuck',
    'John Edwards': 'jzedward',
    'Dave Deitch': 'Wolff589',
    'dave deitch': 'Wolff589',
    'Elliott Miles McKinley': 'eman1969',
    'Silvio Melo': 'Segmelo',
    'Phillip Weltsch': 'phil398',
}


def add_or_get_user(conn, u):
    if sub := email_map.get(u[0], None):
        u = (sub, u[1])

    if sub := user_map.get(u[1], None):
        u = (u[0], sub)

    c = conn.cursor()

    if uid := lookup_user(c, u):
        return uid

    if not u[0] and '@' in u[1]:
        # maybe the username is actually the email address; swap them
        u = (u[1], u[0])

        if uid := lookup_user(c, u):
            return uid

    if not u[1]:
        # create missing username from email address
        if u[0] and '@' in u[0]:
            u = (u[0], u[0].split('@')[0])

    email = u[0]
    username = u[1].replace(' ', '_') if u[1] else ''
    realname = u[1] or None

    # if username contains illegal chars
    if bad_username_re.search(username):
        if email and '@' in email:
            # use email account as username
            username = email.split('@')[0]
        else:
            # replace all the illegal chars
            username = remove_accents(username)
            username = bad_username_re.sub('', username)

    if email and '@' not in email:
        email = None

    # usernames must have length in [3,20]
    if len(username) < 3:
        username += '_1'
    elif len(username) > 20:
        username = username[0:20]

    # usernames must not have consecutive special chars
    username = re.sub('[._-]{2,}', '_', username)

    # usernames must end with a letter or number
    if not re.match('[A-Za-z0-9]', username[-1]):
        username = username[:-1]

    rec = {
        'email': email,
        'realname': realname,
        'username': username,
        'matched': False
    }

    cols, vals = make_cols_vals(rec)
    c.execute(f"INSERT INTO users_w ({cols}) VALUES({vals}) RETURNING user_id", rec)
    return c.fetchone()[0]


def normalize_filename(filename):
    filename = urllib.parse.unquote(filename)
    filename = filename.replace(' ', '_')
    return filename[0].capitalize() + filename[1:]


def fname_for_meta(filename):
    filename = urllib.parse.unquote(filename)
    filename = filename.replace('_', ' ')
    filename = filename[0].capitalize() + filename[1:]
    return f"File:{filename}"


def get_url(filename, file_meta):
    if meta := file_meta.get(fname_for_meta(filename)):
        return meta['url']
    return None


def get_publisher(filename, file_meta):
    if meta := file_meta.get(fname_for_meta(filename)):
        return meta['user']
    return None


image_prefix_re = re.compile(r'^(Image|File)\s*:\s*', flags=re.IGNORECASE)


def parse_screenshot_image(filename, file_meta, file_ctimes):
    irec = {}

    if filename:
        if filename.startswith("[[") and filename.endswith("]]"):
            filename = filename[2:-2]

        filename = filename.lstrip().split('|')[0]
        filename = urllib.parse.unquote(filename).rstrip()
        filename = image_prefix_re.sub('', filename)

        if filename:
            irec['filename'] = normalize_filename(filename)

            if url := get_url(filename, file_meta):
                irec['url'] = url

            if ctime := file_ctimes.get(ctime_key(filename)):
                irec['published_at'] = ctime

            if ipub := get_publisher(filename, file_meta):
                irec['published_by'] = ipub

    return irec


def title_sort_key(title):
    # Lowercase everything
    title = title.lower()

    # Strip accents
    title = remove_accents(title)

    # Articles go to end of sort key

    # TODO: Figure out what to do with Die, Der, Das, L', La, Le, Les, Una
    if title.startswith('a la'):
        # Spanish: A is not an article
        return title

    for art in ('the', 'a', 'an'):
        if title.startswith(art + ' '):
            return title[len(art) + 1:] + ', ' + art

    return title


def to_ts(d):
    return datetime.datetime.fromisoformat(d).timestamp() * (10**9)


def ctime_key(f):
    f = f.replace('_', ' ')
    return f[0].upper() + f[1:]


players_re = re.compile(r'(\d+)(?:\+|(?:\s*(?:-|to)\s*(\d+)))?', flags=re.I)


def split_players(pltag):
    if m := players_re.fullmatch(pltag):
        return m.group(1), m.group(2)
    else:
        return None, None


lsplit_re = re.compile(r'\s*(?:-|–|−|to|à)\s*', flags=re.I)
usplit_re = re.compile(r'(\d+(?:\.\d+)?)\+?\s*(\w*\.?)')


def parse_length(l):
    if m := usplit_re.fullmatch(l):
        val = m.group(1)
        unit = m.group(2)

        unit = unit.lower()
        if unit.startswith('m'):
            unit = 'm'
        elif unit.startswith('h'):
            unit = 'h'
        else:
            unit = None

    else:
        val = None
        unit = None

    return val, unit


def parse_length_tag(ltag):
    l = lval = lunit = r = rval = runit = None

    ltag = ltag.lower().replace('+', '').replace('~', '').replace('>', '').strip()

    if 'turns' not in ltag:
        s = lsplit_re.split(ltag, maxsplit=1)
        l = s[0]
        r = s[1] if len(s) == 2 else None

        if l.startswith('<'):
            r = l[1:].strip()
            l = None

        if l:
            lval, lunit = parse_length(l)

        if r:
            rval, runit = parse_length(r)

        if runit and lval and not lunit:
            lunit = runit

        if lval and not lunit:
            lunit = 'm'

        if rval and not runit:
            runit = 'm'

        if lval:
            if lunit == 'h':
                lval = int(float(lval) * 60)
            else:
                lval = int(lval)

        if rval:
            if runit == 'h':
                rval = int(float(rval) * 60)
            else:
                rval = int(rval)

    return lval, rval



def process_file_entry(file, release_id, file_meta, file_ctimes, conn):
    frec = {
        'release_id': release_id,
        'semver': -1
    }

    fmaints = file['maintainers']
    fcontribs = file['contributors']
    fpub = None

    if d := file.get('date'):
        frec['date'] = parse_date(d)

    for k, v in file.items():
        if v and k not in ('date', 'maintainers', 'contributors', 'size'):
            frec[k] = v

    if version := frec.pop('version', None):
        frec['version_raw'] = version

    if vp := frec.pop('version_parsed', None):
        frec['version_major'] = vp[0]
        frec['version_minor'] = vp[1]
        frec['version_patch'] = vp[2]
        frec['version_pre'] = vp[3]
        frec['version_build'] = vp[4]

    if compat := frec.pop('compatibility', None):
        frec['compatibility_raw'] = compat

    if filename := frec.get('filename'):
        ext = os.path.splitext(filename)[1]

        if ext:
            # strip the dot and lowercase
            ext = ext[1:].lower()
            frec['filetype'] = ext

        if url := get_url(filename, file_meta):
            frec['url'] = url

        if ctime := file_ctimes.get(ctime_key(filename)):
            frec['published_at'] = ctime

        fpub = get_publisher(filename, file_meta)

    if fpub:
        frec['published_by'] = add_or_get_user(conn, (None, fpub))

    fid = do_insert(conn, 'files_w', 'file_id', frec)

    for e in fmaints:
        do_insert_users(conn, 'file_maintainers_w', 'file_id', e, fid)

    for e in fcontribs:
        do_insert_users(conn, 'file_contributors_w', 'file_id', e, fid)

    return fpub, fmaints, fcontribs


def process_json(conn, file_meta, file_ctimes, filename, num):
    print(num)

    with open(filename, 'r') as f:
        p = json.load(f)

    num = str(num)

    title = p['title']

    images = []
    gallery = []
    for e in p['gallery']:
        irec = parse_screenshot_image(e['img'], file_meta, file_ctimes)
        if irec:
            images.append(irec)

            gdesc = pypandoc.convert_text(
                e['alt'], 'commonmark', format='mediawiki'
            ).strip()
            grec = { **irec, 'description': gdesc }
            grec.pop('url', None)

            gallery.append(grec)

    # convert the remaining wikitext to markdown
    readme = pypandoc.convert_text(
        p['readme'], 'commonmark+pipe_tables', format='mediawiki'
    )

    # remove HTML comments
    readme = readme.replace("""```{=html}
<!-- -->
```""", '')
    readme = readme.replace("<!-- -->\n", '')

    # replace strikethrough HTML with markdown
    readme = readme.replace('<s>', '~~').replace('</s>', '~~')
    readme = readme.replace('<strike>', '~~').replace('</strike>', '~~')

    # replace code HTML with markdown
    readme = readme.replace('<code>', '```\n').replace('</code>', '\n```')

    for i, img in enumerate(p['images']):
        irec = parse_screenshot_image(img[0], file_meta, file_ctimes)
        if irec:
            images.append(irec)

            img_norm = img[0].replace(' ', '_')
            if img[1]:
                readme = readme.replace(f"IMAGE_LINK_{i}", f"[![]({img_norm})]({img[1]})")
            else:
                readme = readme.replace(f"IMAGE_LINK_{i}", f"![]({img_norm})")

            if img[1]:
                if img[1].startswith('Module:'):
                    lname = img[1].removeprefix('Module:')
                    lrec = {
                        'project_id': num,
                        'link': lname
                    }
                    do_insert(conn, 'links_w', 'project_id', lrec)

    mrec = {
        'game_title': title,
        'game_title_sort_key': title_sort_key(title),
        'project_id': num,
        'created_at': to_ts(p['ctime']),
        'text': readme
    }

    for k, v in p['info'].items():
        mrec[f"game_{k}"] = v

    if num_players := mrec.get('game_players'):
        pmin, pmax = split_players(num_players)
        if pmin:
            mrec['game_players_min'] = pmin
        if pmax:
            mrec['game_players_max'] = pmax

    if length := mrec.get('game_length'):
        lmin, lmax = parse_length_tag(length)
        if lmin:
            mrec['game_length_min'] = lmin
        if lmax:
            mrec['game_length_max'] = lmax

    # convert game image url to game image name
    if imgname := mrec.get('game_image'):
        if imgname == 'nia.jpg':
            # "not available" image
            mrec['game_image'] = ''
        elif url := get_url(imgname, file_meta):
            mrec['game_image'] = normalize_filename(imgname)

            if irec := parse_screenshot_image(imgname, file_meta, file_ctimes):
                images.append(irec)

    do_insert(conn, 'projects_w', 'project_id', mrec)

    # make tags
    tags = []
    if era := mrec.get('game_era'):
        tags.append(f"era:{era}")

    if topic := mrec.get('game_topic'):
        tags.append(f"topic:{topic}")

    if scale := mrec.get('game_scale'):
        tags.append(f"scale:{scale}")

    if series := mrec.get('game_series'):
        tags.append(f"series:{series}")

    for t in tags:
        do_insert(conn, 'tags_w', 'project_id', {'project_id': num, 'tag': t})

    owners = p.get('maintainer', [])
    contribs = p.get('contributors', [])
    players = p.get('players', [])

    possible_owners = []
    possible_contribs = []
    file_publishers = []

    # process modules section
    for pkg, rels in p.get('modules', {}).items():
        pkg_id = add_or_get_package(conn, num, pkg)

        for rel, files in rels.items():
            rel_id = add_or_get_release(conn, pkg_id, rel)

            for file in files:
                fpub, fmaints, fcontribs =  process_file_entry(file, rel_id, file_meta, file_ctimes, conn)

                if fpub:
                    file_publishers.append((None, fpub))

                possible_owners += fmaints
                possible_contribs += fcontribs

    for e in players:
        do_insert_users(conn, 'players_w', 'project_id', e, num)

    # try to ensure we have somebody as an owner
    if not owners:
        owners = contribs
        if not owners:
            owners = possible_owners
            if not owners:
                owners = possible_contribs
                if not owners:
                    owners = file_publishers
                    if not owners:
                        owners = [('placeholder+nobody@vassal.org', 'nobody')]

    for e in owners:
        do_insert_users(conn, 'owners_w', 'project_id', e, num)

    for e in contribs:
        do_insert_users(conn, 'module_contributors_w', 'project_id', e, num)

    for e in images:
        e['project_id'] = num
        if ipub := e.get('published_by'):
            e['published_by'] = add_or_get_user(conn, (None, ipub))
        do_insert_or_ignore(conn, 'images_w', 'project_id', e)

    for i, e in enumerate(gallery):
        e['project_id'] = num
        e['position'] = i
        if ipub := e.get('published_by'):
            e['published_by'] = add_or_get_user(conn, (None, ipub))
        do_insert_or_ignore(conn, 'galleries_w', 'project_id', e)


async def process_json_async(conn, files, file_ctimes, filename, num):
    with conn as cur:
        try:
            process_json(cur, files, file_ctimes, filename, num)
        except Exception as e:
            raise RuntimeError(f"!!! {num}") from e


async def run():
    fpath = 'data/files_fixed.json'
    upath = 'data/users.json'
    vpath = 'data/file_meta_fixed.json'
    wpath = 'data/pagejson_fixed'
    f_ctime_path = 'data/file_ctimes.json'
    dbpath = 'projects.db'

    with open(fpath, 'r') as f:
        files = json.load(f)

    with open(f_ctime_path, 'r') as f:
        file_ctimes = json.load(f)

    file_ctimes = { k.removeprefix('File:'): to_ts(v) for k, v in file_ctimes.items() }

    with contextlib.closing(sqlite3.connect(dbpath)) as conn:
        create_db(conn)
        populate_users(conn, upath)

        async with asyncio.TaskGroup() as tg:
            for f in glob.glob(f"{wpath}/[0-9]*.json"):
                num = int(os.path.basename(f).removesuffix('.json'))
                tg.create_task(process_json_async(conn, files, file_ctimes, f, num))

        add_placeholder_user_emails(conn)
        populate_versions(conn, vpath)
        populate_compatibility(conn)
        rewrite_image_links(conn)
        apply_fixups(conn)
        convert_for_gls(conn)


if __name__ == '__main__':
    asyncio.run(run())
