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


def x1914_glorys_end(p):
     p['modules'] = {
        "Glory's End": p['modules']["1.0 Glory's End"],
        'When Eagles Fight': p['modules']['1.0 When Eagles Fight']
    }


def apuren_el(p):
    p['title'] = '¡' + p['title']


def arriba_espana(p):
    p['title'] = '¡Arriba España!'


def assault_of_the_dead(p):
    p['modules']['Alternate Version'] = p['modules']['1.0 Alternate Version']
    del  p['modules']['1.0 Alternate Version']


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
    # 0-9
    '13 Dead End Drive': x13_dead_end_drive,
    '1914': collapse_pkgs,
    "1914: Glory's End / When Eagles Fight": x1914_glorys_end,
    '1936: Guerra Civil': collapse_pkgs,
    '1985: Under an Iron Sky': collapse_pkgs,
    '300: Earth & Water': collapse_pkgs, 

    # A
    'A las Barricadas! (2nd Edition)': collapse_pkgs,
    'Aces of Valor': collapse_pkgs,
    'Across Suez': collapse_pkgs,
    'Age of Dogfights: WW1': collapse_pkgs,
    'Age of Muskets Volume I: Tomb for an Empire': collapse_pkgs,
    'Aegean Strike': collapse_pkgs,
    'Air Superiority': collapse_pkgs,
    'Airborne in My Pocket': collapse_pkgs,
    'Alien Frontiers': collapse_pkgs,
    'All Things Zombie: The Boardgame': collapse_pkgs,
    'Ancient Civilizations of the Inner Sea': collapse_pkgs,
    'Andean Abyss': collapse_pkgs,
    'Apuren el corralito!: The 2nd Battle of Alihuatá, December 1933': apuren_el,
    'Arcole 1796': collapse_pkgs,
    'Ardennes II': collapse_pkgs,
    'The Ardennes Offensive: The Battle of the Bulge, December 1944': collapse_pkgs,
    'Arena: Roma II': collapse_pkgs,
    'Arracourt': collapse_pkgs,
    'Arriba Espana!': arriba_espana,
    'Ashes: Rise of the Phoenixborn': collapse_pkgs,
    'Assault of the Dead: Tactics': assault_of_the_dead,
    'Atlanta': collapse_pkgs,
    'Attack Sub': collapse_pkgs,
    'Austerlitz': collapse_pkgs,
    'Austerlitz 1805': collapse_pkgs,
    'Axis & Allies': collapse_pkgs,
    'Axis & Allies Naval Miniatures: War at Sea': collapse_pkgs,

    # B
    'Balkan Front': collapse_pkgs,
    'Band of Brothers': collapse_pkgs,
    'BAOR': collapse_pkgs,

    # U
    'UND1C1': collapse_pkgs,
    'Utopia Engine': collapse_pkgs,

    # V
    'Valor and Victory': collapse_pkgs,
    'Victory in Vietnam': collapse_pkgs,

    # W
    "Wacht am Rhein': The Battle of the Bulge, 16 Dec 44-2 Jan 45": wacht_am_rhein, 
    'War At Sea': collapse_pkgs,
    'The War At Sea (first edition)': collapse_pkgs,
    'WARLINE: Maneuver Strategy & Tactics': collapse_pkgs,

    # Y
    'Ye Gods!': collapse_pkgs,
    'Yggdrasil': yggdrasil,

    # Z
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
