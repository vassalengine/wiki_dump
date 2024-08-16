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


def x13_dead_end_drive(p):
    p['modules'] = {
        'Spanish': [ m for v in p['modules'].values() for m in v ]
    }


def yggdrasil(p):
    p['modules']['Dark Eclipse'] += p['modules'].pop('Dark Eclipse v2.0')


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
    '13 Dead End Drive': x13_dead_end_drive,
    '1914': collapse_pkgs,
    '1936: Guerra Civil': collapse_pkgs,
    '300: Earth & Water': collapse_pkgs, 
    'A las Barricadas! (2nd Edition)': collapse_pkgs,
    'Aces of Valor': collapse_pkgs,
    'Across Suez': collapse_pkgs,
    'Age of Dogfights: WW1': collapse_pkgs,
    'Age of Muskets Volume I: Tomb for an Empire': collapse_pkgs,
    "Wacht am Rhein': The Battle of the Bulge, 16 Dec 44-2 Jan 45": wacht_am_rhein, 
    'War At Sea': collapse_pkgs,
    'The War At Sea (first edition)': collapse_pkgs,
    'WARLINE: Maneuver Strategy & Tactics': collapse_pkgs,
    'Ye Gods!': collapse_pkgs,
    'Yggdrasil': yggdrasil,
    'Zürich 1799': collapse_pkgs
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
