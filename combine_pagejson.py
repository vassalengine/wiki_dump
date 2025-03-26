import asyncio
import datetime
import glob
import json
import shutil
import urllib.parse

import semver


def fname_for_files(filename):
    filename = urllib.parse.unquote(filename)
    filename = filename.replace('_', ' ')
    filename = filename[0].capitalize() + filename[1:]
    return f"File:{filename}"


def get_files_record(filename, files):
    return files.get(fname_for_files(filename))


def ctime_key(f):
    f = f.replace('_', ' ')
    return f[0].upper() + f[1:]


async def combine_page(path, files, ctimes, meta):
    print(path)

    with open(path, 'r') as f:
        p = json.load(f)

    pm = p['modules']
    for sec in [ sec for sec in pm if not sec ]:
        mods = pm.setdefault('Module', [])
        mods += pm.pop(sec)

    for sec, mods in pm.items():
        for m in mods:
            m.pop('date', None)

            if filename := m.get('filename'):
                if frec := get_files_record(filename, files):
                    url = frec['url']

                    m['url'] = url 
                    m['published_by'] = frec['user']

                    if mrec := meta.get(url):
                        m['size'] = mrec.get('size')
                        m['sha256'] = mrec.get('sha256')
                        if v := mrec.get('version_parsed'):
                            m['version_parsed'] = v
                            m['version'] = str(semver.Version(major=v[0], minor=v[1], patch=v[2], prerelease=v[3], build=v[4]))

                if ctime := ctimes.get(ctime_key(filename)):
                    m['published_at'] = ctime

    with open(path, 'w') as f:
        json.dump(p, f, indent=2)


async def run():
    fpath = 'data/files_fixed.json'
    mpath = 'data/file_meta_fixed.json'
    cpath = 'data/file_ctimes.json'

    ipath = 'data/pagejson'
    opath = 'data/pagejson_combined'

    shutil.copytree(ipath, opath, dirs_exist_ok=True)

    with open(fpath, 'r') as f:
        files = json.load(f)

    with open(cpath, 'r') as f:
        ctimes = json.load(f)

    ctimes = { k.removeprefix('File:'): v for k, v in ctimes.items() }

    with open(mpath, 'r') as f:
        meta = json.load(f)

    async with asyncio.TaskGroup() as tg:
        for f in glob.glob(f"{opath}/[0-9]*.json"):
            tg.create_task(combine_page(f, files, ctimes, meta))

    print('')


if __name__ == '__main__':
    asyncio.run(run())
