import contextlib
import re
import sqlite3

import semver


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

    v = try_semver(version)
    if v is not None:
        return v    

    version = ver_zero_fix_re.sub(r'\1\2', version)
    
    v = try_semver(version)
    if v is not None:
        return v

    return None



ext_re = re.compile(r'(?i)\.(v?(mod|mdx)|zip)$')
ver_re = re.compile(r'v?\d+([_.-]\d+)*$')


def try_extract_version(filename):
    filename = ext_re.sub('', filename)

    vu = ver_re.search(filename)
    if vu:
        vu = vu.group(0).replace('_', '.').replace('-', '.')
        return try_parse_version(vu)

    return None


def parse(conn):
    with conn as cur:
        rows = cur.execute('''
SELECT project_id, filename
FROM files_w
WHERE filename IS NOT NULL
ORDER BY project_id
            '''
        )

        proj_id = None
        for row in rows:
            filename = row[1]
            filename = ext_re.sub('', filename)
            vu = ver_re.search(filename)
            if vu:
                if row[0] != proj_id:
                    print("")
                    proj_id = row[0]

                print(filename[:vu.start(0)].rstrip(" _-"))



def run():
    dbpath = 'projects.db'

    with contextlib.closing(sqlite3.connect(dbpath)) as conn:
       parse(conn) 


if __name__ == '__main__':
    run()
