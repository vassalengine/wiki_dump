import asyncio
import glob
import json
import shutil
import os


def collapse_pkgs(p):
    mods = p['modules']

    # map everything to one package
    d = []
    for v in mods.values():
        d += v

    p['modules'] = { p['title']: d }


def wacht_am_rhein(p):
    p['title'] = "'" + p['title']
    p['modules'] = {
        'North is up Orientation': [
            *p['modules']["1.0 North is up Orientation"],
            *p['modules']["1.1 North is up Orientation"]
        ],
        'East is up Orientation': [
            *p['modules']["1.42 East is up Orientation"],
            *p['modules']["1.3 East is up Orientation"]
        ]
    }


fixups = {
    '1914': collapse_pkgs,
    '1936: Guerra Civil': collapse_pkgs,
    '300: Earth & Water': collapse_pkgs, 
    'A las Barricadas! (2nd Edition)': collapse_pkgs,
    "Wacht am Rhein': The Battle of the Bulge, 16 Dec 44-2 Jan 45": wacht_am_rhein, 
    'War At Sea': collapse_pkgs
}

#            # map each package individually 
#            for k, v in pmap.items():
#                d = mods.setdefault(v, [])
#                d += mods.pop(k)


async def fixup_page(path):
    print(path)

    with open(path, 'r') as f:
        p = json.load(f)

    fixup = fixups.get(p['title'], None)
    if fixup is not None:
        fixup(p)

        with open(path, 'w') as f:
            json.dump(p, f, indent=2)


async def run():
    ipath = 'data/pagejson'
    opath = 'data/pagejson_fixed'

    shutil.copytree(ipath, opath, dirs_exist_ok=True) 

    async with asyncio.TaskGroup() as tg:
        for f in glob.glob(f"{opath}/[0-9]*.json"):
            tg.create_task(fixup_page(f))

    print('')


if __name__ == '__main__':
    asyncio.run(run())
