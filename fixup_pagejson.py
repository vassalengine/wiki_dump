import asyncio
import glob
import json
import shutil
import os

import semver

import versions


def before_mod_count(p):
    return len([m for pkg in p['modules'].values() for m in pkg])


def after_mod_count(p):
    return len([m for pkg in p['modules'].values() for rel in pkg.values() for m in rel])


def ok(p):
    pass


def collapse_pkgs(p):
    mods = p['modules']

    if mods:
        # map everything to one package
        d = []
        for v in mods.values():
            d += v

        p['modules'] = { 'Module': d } if d else {}


def x1stAlamein(p):
    p['modules'] = {
        'Module': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def x1809_napoleons_danube_campaign(p):
    p['modules'] = {
        'Module': {
            '0.7.0': [ m for pn, pv in p['modules'].items() for m in pv if m.get('version') == '0.7.0' ],
            '0.5.0': [ m for pn, pv in p['modules'].items() for m in pv if m.get('version') == '0.5.0' ],
            '0.0.0': p['modules'].pop('1.0')
        }
    }


def x1812_the_campaign(p):
    p['modules'] = {
        'Hex': [ m for pn, pv in p['modules'].items() for m in pv if 'Hex' in m['filename'] ],
        'Area': [ m for pn, pv in p['modules'].items() for m in pv if 'Area' in m['filename'] ]
    }
    use_pkgs(p)


def x18xx(p):
    p['modules'] = {
        'Module': {
            '2.13.0': p['modules'].pop('2.13')
        },
        'Misc': {
            '0.0.0': p['modules'].pop('Misc')
        }
    }


def x1914_glorys_end(p):
    p['modules'] = {
        "Glory's End": p['modules']["1.0 Glory's End"],
        'When Eagles Fight': p['modules']['1.0 When Eagles Fight']
    }
    use_pkgs(p)


def x8thArmy(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules']['1.00']
        }
    }


def a_house_divided(p):
    p['modules'] = {
        "Phalanx Games (2nd Edition)": [ m for pn, pv in p['modules'].items() for m in pv if 'Phalanx' in pn ],
        'GDW (1st Edition)': [ m for pn, pv in p['modules'].items() for m in pv if 'GDW' in pn ]
    }
    use_pkgs(p)


def a_las_barricadas_2ed(p):
    p['modules']['2.51'].extend(p['modules'].pop('1.0'))
    version_to_release(p)


def a_splendid_little_war(p):
    p['modules']['1st Edition'] = p['modules'].pop('1')
    use_pkgs(p)


def a_time_for_trumpets(p):
    p['modules']['2.9'] += p['modules'].pop('v2.# Introductory Note and User Manual')
    version_to_release(p)


def across_5_aprils(p):
    ms = p['modules']['Module']
    p['modules'] = {
        'Module': {},
        'Rules': {
            '0.0.0': p['modules'].pop('Rules')
        }
    }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def aftershock(p):
    p['modules'] = {
        'Module': {
            '1.1.0': p['modules'].pop('1.1') + p['modules'].pop('1.1 - Facilitator ONLY')
        },
        'Rules': {
            '5.2.0': p['modules'].pop('Rules')
        }
    }


def air_assault_on_crete(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv if m.get('version') is not None ]
    misc =  [ m for pn, pv in p['modules'].items() for m in pv if m.get('version') is None ]
    p['modules'] = {
        'Module': {},
        'Misc': { '0.0.0': misc }
    }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def annihilator(p):
    p['modules'] = {
        'Annihilator': {
            '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'annih' in m['filename'] ]
        },
        'OneWorld': {
            '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'World' in m['filename'] ]
        }
    }


def ardennes_44(p):
    p['modules'] = {
        '3rd Edition': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if pn.startswith('3rd') },
        '2nd Edition': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if pn.startswith('2nd') },
        '1st Edition': { '1.2.0': [ m for pn, pv in p['modules'].items() for m in pv if pn in ('1.22', 'None') ] }
    }


def arkwright(p):
    p['modules'] = {
        'English': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'DE' not in m['filename'] },
        'German': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'DE' in m['filename'] }
    }


def arrakhars_wand(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules'].pop('Module')
        }
    }


def arquebus(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def assault_on_hoth(p):
    p['modules'] = {
        'English': {
            '0.0.0': p['modules'].pop('3.1 English')
        },
        'Spanish': {
            '1.0.0': p['modules'].pop('1.0 Spanish')
        }
    }


def atlantic_wall(p):
    pkgs = p['modules'].values()
    p['modules'] = { 'Module': {} }

    for pkg in pkgs:
        v = next(m['version'] for m in pkg if 'version' in m)
        for m in pkg:
            r = p['modules']['Module'].setdefault(v, [])
            r.append(m)


def attack_vector(p):
    p['modules'] = {
        'Module': {
            '0.9.0': p['modules'].pop('0.9')
        },
        'Misc': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def ahgc_trivia(p):
    p['modules'] = {
        'Module': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def axis_and_allies_bulge(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv if pn != 'Misc']
    misc = [ m for pn, pv in p['modules'].items() for m in pv if pn == 'Misc']
    p['modules'] = {
        'Module': {},
        'Misc': {
            '0.0.0': misc
        }
    }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


#def a_victory_lost(p):
#    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
#    p['modules'] = { 'Module': {} }
#    for m in ms:
#        r = p['modules']['Module'].setdefault(m['version'], [])
#        r.append(m)


def b17_qots(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv if pn != 'Extensions']
    ext = [ m for pn, pv in p['modules'].items() for m in pv if pn == 'Extensions']
    p['modules'] = {
        'Module': {},
        'Extensions': {
            '0.0.0': ext
        }
    }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def babylon_5_ccg(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv if pn != 'Misc']
    p['modules'] = {
        'Module': {},
        'Misc': {
            '0.0.0': p['modules'].pop('Misc')
        }
    }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def baltic_gap(p):
    fow = p['modules'].pop('FOW 4.26') + p['modules'].pop('FOW 4.25 + 13.7')

    p['modules'] = {
        'Standard': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv },
        'FOW': {  m['version']: [ m ] for m in fow }
    }


def band_of_brothers(p):
    ext30 = p['modules'].pop('Unofficial material for version 3.0')
    p['modules']['Module version 3.0'] += ext30
    version_to_release(p)


def battlelore(p):
    jp = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'BattleLorev32.vmod')
    p['modules']['3.2'].remove(jp)

    p['modules'] = {
        'English': {
            '3.2.0': p['modules'].pop('3.2'),
            '3.1.0': p['modules'].pop('3.1'),
            '3.0.0': p['modules'].pop('3.0'),
            '1.2.0': p['modules'].pop('1.2'),
            '1.0.0': p['modules'].pop('1.0')
        },
        'French': {
            '1.0.0-c': p['modules'].pop('???')
        },
        'Japanese': {
            '3.2.0': [ jp ]
        }
    }


def battle_cry(p):
    p['modules'] = {
        'English': {
            '3.2.0': p['modules'].pop('3.2')
        },
        'German': {
            '3.2.0': p['modules'].pop('3.2 German Language')
        }
    }


def battle_cry_150(p):
    p['modules'] = {
        'Standard': {
            '2.1.0': p['modules'].pop('2.1 Standard'),
            '1.1.0': p['modules'].pop('1.1 Standard')
        },
        'Epic': {
            '1.3.0': p['modules'].pop('1.3 Epic')
        }
    }


def battle_for_moscow_ii(p):
    p['modules']['Version 1.0'] += p['modules'].pop('Vlog Combat Demo')
    version_to_release(p)


def battletech(p):
    p['modules'] = {
        'QuickStrike Rules': {
            '0.4.0': p['modules'].pop('QuickStrike Rules')
        },
        'Miniatures Rules': {
            '0.2.0': p['modules'].pop('Miniatures Rules')
        },
        'Classic Rules': {
            '2.1.1': [ m for pn, pv in p['modules'].items() for m in pv if 'version' not in m or m['version'] != '2.1.0' ],
            '2.1.0': [ m for pn, pv in p['modules'].items() for m in pv if m.get('version') == '2.1.0' ]
        }
    }


def beyond_the_rhine(p):
    fow = p['modules'].pop('1.05') + p['modules'].pop('1.04') + p['modules'].pop('1.03')

    p['modules'] = {
        'Standard': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv },
        'FOW': {  m['version']: [ m ] for m in fow }
    }


def bios_megafauna(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Extension': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmdx') }
    }


def belter(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Misc': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv if not m['filename'].endswith('.vmod') ]
        }
    }


def blockade(p):
    p['modules'] = {
        'Standard': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Duel' not in m['filename'] },
        'Duel': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Duel' in m['filename'] },
    }


def blood_and_roses(p):
    tp = [ m for pn, pv in p['modules'].items() for m in pv if 'Tri' in pn ]
    one = p['modules'].pop('1.1')

    p['modules'] = {
        "Men of Iron Tri-Pack": {},
        '1st Edition': { '1.1.0': one }
    }

    for m in tp:
        r = p['modules']['Men of Iron Tri-Pack'].setdefault(m['version'], [])
        r.append(m)


def bloody_steppes(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def blue_and_gray(p):
    comp = p['modules'].pop('1.0')
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]

    p['modules'] = {
        'Complete': { '1.0.0': comp },
        'Individual Modules': {}
    }

    for m in ms:
        r = p['modules']['Individual Modules'].setdefault(m['version'], [])
        r.append(m)


def blue_and_gray_ii(p):
    comp = p['modules'].pop('1.0')
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]

    p['modules'] = {
        'Complete': { '1.0.0': comp },
        'Individual Modules': {}
    }

    for m in ms:
        r = p['modules']['Individual Modules'].setdefault(m['version'], [])
        r.append(m)


def bobby_lee(p):
    p['modules']['5.0.0-b2'] = [ m for m in p['modules']['5.0'] if m['version'] == '5.0.0-b2' ]
    p['modules']['5.0.0'] = [ m for m in p['modules']['5.0'] if m['version'] == '5.0.0' ] +  p['modules'].pop('None')
    version_to_release(p)


def breaking_the_chains(p):
    p['modules'] = {
        "2nd Edition": p['modules'].pop('1.1, 2ndEdition'),
        '1st Edition': p['modules'].pop('4.2.2')
    }
    use_pkgs(p)


def britannia(p):
    p['modules'] = {
        "FFG": { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'FFG' in pn },
        "AH": { '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'FFG' not in pn ] }
    }


def brothers_at_war(p):
    p['modules'] = {
        'Module': [ m for pn, pv in p['modules'].items() for m in pv if '1862' in pn ],
        'Glorieta Pass Add-On': [ m for pn, pv in p['modules'].items() for m in pv if 'Glorieta' in pn ]
    }
    use_pkgs(p)


def bull_run(p):
    misc = p['modules'].pop('None')
    p['modules'] = {
        'Original Graphics': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Original' in pn },
        'ADC2 Conversion': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Original' not in pn },
        'Misc': {
            '0.0.0': misc
        }
    }


def canadian_crucible(p):
    p['modules'] = {
        'MMP Version': [ m for pn, pv in p['modules'].items() for m in pv if 'MMP' in pn ],
        'DriverG Version': [ m for pn, pv in p['modules'].items() for m in pv if 'DriverG' in pn ]
    }
    use_pkgs(p)


def cards_against_humanity(p):
    ov = p['modules'].pop('Offical Versions')

    p['modules'] = {
        'Offical Versions': {
            '1.0.0': [ m for m in ov if m.get('version') == '1.0.0' ],
            '1.2.0': [ m for m in ov if m.get('version') == '1.2.0' ],
            '1.2.1': [ m for m in ov if m.get('version') in ('1.2.1', None) ]
        },
        'Custom Cards': {
            '1.0.0': p['modules'].pop('Custom Cards')
        }
    }


def case_blue_gbii(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'HQ Extension': {
            '0.2.0': p['modules'].pop('HQ Extension .02')
        }
    }


def castaways(p):
     p['modules'] = {
        'Module': {
            '1.2.0': p['modules'].pop('1.2')
        },
        'Reglas del juego': {
            '0.0.0': p['modules'].pop('Reglas del juego')
        }
    }


def cataclysm(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv if 'Unofficial' not in pn ]
    p['modules'] = {
        'Module': {},
        'Unofficial WW1 Usermod': {
            '1.2.0': p['modules'].pop('Unofficial WW1 Usermod')
        }
    }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def cataphract(p):
    p['modules'] = {
        'Module': {
            '3.0.0': p['modules'].pop('3.0'),
            '2.1.0': p['modules'].pop('2.1')
        },
        'Cataphract Saved Games': {
            '0.0.0': p['modules'].pop('Cataphract Saved Games')
        },
        'Attila Saved Games': {
            '0.0.0': p['modules'].pop('Attila Saved Games')
        }
    }


def central_front_series(p):
    rules = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Central_Front_Unified_Rules_210104.pdf')
    p['modules'] = {
        'Red Thrust 5-Map Grand Campaign': {
            m['version']: [ m ] for m in p['modules'].pop('1.xx Red Thrust 5-Map Grand Campaign') if 'version' in m
        },
        'Mittelland Thrust 3-Map Campaign': {
            '1.0.0': p['modules'].pop('1.xx Mittelland Thrust 3-Map Campaign')
        },
        'Standard': {
            '0.1.0': p['modules'].pop('0.1 Standard')
        },
        'Blind': {
            '0.1.0': p['modules'].pop('0.1 Blind')
        }
    }

    p['modules']['Red Thrust 5-Map Grand Campaign']['1.0.0'].append(rules)


def champs_de_bataille(p):
    p['modules'] = {
        'Module': {
            '0.0.0': p['modules']['Module']
        }
    }


def citadels(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def civil_war(p):
    p['modules'] = {
        'Module': {
            m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m
        },
        'Misc': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def clash_of_giants_ii(p):
    p['modules'] = {
        'Ypres': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Ypres' in pn },
        'Galicia': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Galicia' in pn }
    }


def clixers(p):
    p['modules'] = {
        'Module': {
            '0.0.0': p['modules']['Module']
        }
    }


def combat_commander_europe(p):
    x260 = next(m for m in p['modules']['2.6 (older extensions)'] if m['filename'] == 'CombatCommanderEurope-2.6.vmod')
    p['modules']['2.6 (older extensions)'].remove(x260)

    items = list(p['modules'].items())
    p['modules'] = { 'Module': {} }
    for pn, pv in items:
        ver = next(m['version'] for m in pv if 'version' in m)
        p['modules']['Module'][ver] = pv

    p['modules']['Module']['2.6.0'] = [ x260 ]


def combat_vol_2(p):
    p['modules'] = {
        'Combat!2 Base Module': {
            '3.1.0': p['modules'].pop('Combat!2 Base Module version 3.1')
        },
        'Combat!2 Extension Add-on version 1.2': {
            '1.2.0': p['modules'].pop('Combat!2 Extension Add-on version 1.2')
        },
        'Combat!2 Campaign Module': {
            '1.3.0': p['modules'].pop('Combat!2 Campaign Module version 1.3')
        },
        'Combat_Experienced Add-on': {
            '0.0.0': p['modules'].pop('Combat_Experienced Add-on')
        }
    }


def cc_ancients(p):
    p['modules'] = {
        'Full Game (Standard and Epic) 4.x (English; Italian from v4.3.17)': {
            '4.3.24':  p['modules'].pop('4.3'),
            '4.2.6': p['modules'].pop('4.2'),
            '4.1.1': p['modules'].pop('4.1f1'),
            '4.1.0': p['modules'].pop('4.1'),
            '4.0.0': p['modules'].pop('4.0'),
        },
        'Standard Game (English)': {
            '3.3.0': p['modules'].pop('3.3') + [ m for pn, pv in p['modules'].items() for m in pv if m['filename'] in ('CCA Expansion1.vmdx', 'CCA Expansion2.vmdx', 'CCA Expansion3.vmdx', 'CCA Expansion4.vmdx', 'CCA Expansion6.vmdx', 'CCA C3iScenarios.vmdx', 'ScenarioX.vmdx', 'ScenarioX_ArmyList.vmdx', 'CCA RandomScenario.vmdx', 'UserMaps_ACxx.vmdx', 'UserMaps_DCxx.vmdx', 'UserMaps_GBxx.vmdx', 'UserMaps_JDxx.vmdx', 'UserMaps_MMxx.vmdx', 'UserMaps_TTxx.vmdx') ],
            '3.2.0': [ next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'C&CAncientsv3.vmod') ],
            '1.0.0': p['modules'].pop('d10')
        },
        'Epic Game (English)': {
            '1.1.0':  p['modules'].pop('1.1') + [ m for pn, pv in p['modules'].items() for m in pv if m['filename'] in ('Epic01_PunicWars.vmdx', 'Epic02_JuliusCaesar.vmdx', 'Epic03_Exp1.vmdx') ]
        },
        'Standard Game (Italian)': {
            '3.2.0': [ next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'C&CAncientsv3_ITA.vmod') ] + [ m for pn, pv in p['modules'].items() for m in pv if m['filename'] in ('IT Expansion1.vmdx', 'IT Expansion2.vmdx', 'IT RandomScenario.vmdx', 'IT ScenarioX.vmdx') ]
        },
        'Epic Game (Italian)': {
            '1.0.0': p['modules'].pop('1.0')
        }
    }


def cc_napoleonics(p):
    p['modules'] = {
        'Module': {
            '5.1.0-beta11': p['modules'].pop('v5.1 beta11 - not backward compatible, see comments section!'),
            '5.0.0-beta9': p['modules'].pop('v5.0 beta9 - superceded by 5.1. Not recommended for new games!'),
            '4.1.16': p['modules'].pop('v4.1'),
            '4.0.6': p['modules'].pop('v4.0'),
            '3.43.0': p['modules'].pop('v3.43'),
            '3.42.0': p['modules'].pop('v3.42'),
            '3.41.0': p['modules'].pop('v3.41'),
            '2.55.0': p['modules'].pop('v2.55'),
            '1.42.0': p['modules'].pop('v1.42')
        },
        'Epic': {
            '2.2.0': p['modules'].pop('Epic v2.2'),
            '1.21.0': p['modules'].pop('Epic v1.21 (Unofficial)')
        }
    }


def conflict_of_heroes_atb(p):
    p['modules'] = {
        'English': { next(m['version'] for m in pv if 'version' in m): pv for pn, pv in p['modules'].items() if 'French' not in pn },
        'French': {
            '1.41.0': p['modules'].pop('1.41 (French)'),
            '1.42.0': p['modules'].pop('1.42 (French)')
        }
    }


def conflict_of_heroes_sos(p):
    p['modules'] = {
        'Module': {
            '1.3.1': p['modules'].pop('1.3')
        },
        'Storms of Steel Firefights': {
            '0.0.0':  p['modules'].pop('Storms of Steel Firefights')
        }
    }


def conquest_and_consequences(p):
    p['modules'] = {
        'Module': [ m for pn, pv in p['modules'].items() for m in pv if 'C&T' not in m['filename'] ],
        'Combined C&C/T&T': [ m for pn, pv in p['modules'].items() for m in pv if 'C&T' in m['filename'] ]
    }
    use_pkgs(p)


def crimean_war_battles(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Individual Modules': {} }
    for m in ms:
        r = p['modules']['Individual Modules'].setdefault(m['version'], [])
        r.append(m)


def crusade_and_revolution(p):
    p['modules'] = {
        'English': { next(m['version'] for m in pv if 'version' in m): pv for pn, pv in p['modules'].items() if 'ESP' not in pn },
        'Spanish': { next(m['version'] for m in pv if 'version' in m): pv for pn, pv in p['modules'].items() if 'ESP' in pn }
    }


def cry_havoc(p):
    p['modules'] = {
        'Module': {
            '1.1.0': p['modules'].pop('1.1'),
            '1.0.0': p['modules'].pop('1.0')
        },
        'Misc - Unofficial Extensions': {
            '0.0.0':  p['modules'].pop('Misc - Unofficial Extensions')
        }
    }


def d_day_dice(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def dak2(p):
    fow = p['modules'].pop('FOW 4.28') + p['modules'].pop('FOW 4.27') + p['modules'].pop('FOW 4.25+13.7')

    p['modules'] = {
        'Standard': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv },
        'FOW': {  m['version']: [ m ] for m in fow }
    }


def dien_bien_phu_tfg(p):
    p['modules'] = {
        '2nd Edition': [ m for pn, pv in p['modules'].items() for m in pv if '2nd' in pn ],
        '1st Edition': [ m for pn, pv in p['modules'].items() for m in pv if 'English' in pn ]
    }
    use_pkgs(p)


def dominant_species(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def dominion(p):
    p['modules'] = {
        'Module': {
            '1.9.0': [ m for pn, pv in p['modules'].items() for m in pv if m.get('version') == '1.9.0' ],
            '1.8.0': [ m for pn, pv in p['modules'].items() for m in pv if m.get('version') in ('1.8.0', None) ]
        }
    }


def dse_motorcade_showdown(p):
    p['modules'] = {
        'Module': {
            '0.2.9': p['modules'].pop('2.9')
        },
        'Rules': {
            '0.0.0': p['modules'].pop('Rules')
        }
    }


def dse_hell_over(p):
    p['modules'] = {
        'Module': {
            '1.3.0': p['modules'].pop('0.4')
        },
        'Rules': {
            '1.0.0': p['modules'].pop('Rules')
        }
    }


def dse_quebec_1759(p):
    p['modules'] = {
        'Module': {
            '0.4.0': p['modules'].pop('0.4')
        },
        'Thesis/Rules': {
            '0.0.0': p['modules'].pop('Thesis/Rules')
        }
    }


def dse_kazhdyy_gorod(p):
    p['modules'] = {
        'Module': {
            '0.6.0': p['modules'].pop('0.4')
        },
        "Facilitator's Guide": {
            '0.0.0': p['modules'].pop("Facilitator's Guide")
        }
    }


def dragon_pass(p):
    st = next(m for pn, pv in p['modules'].items() for m in pv if m.get('filename') == 'Dragon_Pass_Stemming_the_Tide.vmdx')
    ht = next(m for pn, pv in p['modules'].items() for m in pv if m.get('filename') == 'Dragon_Pass_High_Tide.vmdx')

    p['modules'] = {
        'Module': { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Stemming the Tide': { '1.0.0': [ st ] },
        'High Tide': { '1.0.0': [ ht ] }
    }


def dune_wfa(p):
    p['modules'] = {
        'Module': {
            '1.1.0': p['modules'].pop('1.01')
        },
        "Scripted Setup": { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if 'Scripted' in pn }
    }


def eldritch_horror(p):
    p['modules']['1.9.2'] = [ m for m in p['modules']['1.9'] if m.get('version') == '1.9.2' ]
    p['modules']['1.9.1'] = [ m for m in p['modules']['1.9'] if m.get('version') == '1.9.1' ]
    p['modules']['1.9.0'] = [ m for m in p['modules']['1.9'] if 'version' not in m or m['version'] == '1.9.0' ]
    p['modules'].pop('1.9')
    version_to_release(p)


def elfball(p):
    p['modules'] = {
        'Module': { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Misc': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def enemy_action_kharkov(p):
    p['modules']['2-Player'] = p['modules'].pop('2-Player 1.31')
    p['modules']['German Solo'] = p['modules'].pop('German Solo 1.6')
    p['modules']['Soviet Solo'] = p['modules'].pop('Soviet Solo 1.2')
    use_pkgs(p)


def europa_full_map(p):
    scen = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'scenarios.zip')

    p['modules'] = {
        'Module': { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') }
    }
    p['modules']['Module']['0.88.0'].append(scen)


def exile_sun(p):
    p['modules'] = {
        'Module': {
            '1.2.0': p['modules'].pop('1.0'),
            '2.0.1': p['modules'].pop('2.0')
        }
    }


def fall_blau_ags(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def feilong(p):
    p['modules'] = {
        'Module': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def feudal(p):
    p['modules'] = {
        'Module': { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Rules': {
            '0.0.0': p['modules'].pop('Rules')
        }
    }


def first_victories(p):
    p['modules']['Rolica'] = p['modules'].pop('2.1 Rolica')
    p['modules']['Vimero'] = p['modules'].pop('2.0 Vimero')
    use_pkgs(p)


def firepower(p):
    p['modules'] = {
        'Module': { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Misc': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def flat_top(p):
    p['modules'] = {
        'Module': { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') and 'Blind' not in pn },
        'Blind Version': {
            '0.1.0': p['modules'].pop('Blind Version 0.1')
        },
        'Misc': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def flight_leader(p):
    p['modules'] = {
        'Module': { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') and pn == '2.2' } | { '1.1.0':  p['modules'].pop('1.1') },
        'Blind': {
            '1.1.0': p['modules'].pop('Blind 1.1')
        }
    }


def formula_de(p):
    exts = [ m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('vmdx') ]

    p['modules'] = {
        'English': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'English' in pn and 'version' in m },
        'Italian': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Italian' in pn }
    }

    p['modules']['English']['2.1.0'] += exts


def fortress_berlin(p):
    p['modules'] = {
        'Module': { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Misc': {
            '0.0.0': p['modules'].pop('None') + p['modules'].pop('2.0')
        }
    }


def freedom_in_the_galaxy(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def friedrich(p):
    p['modules'] = {
        'Module': { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Rules': {
            '0.0.0': p['modules'].pop('Rules')
        }
    }


def gd42(p):
    p['modules'] = {
        'Module': {
            '1.5.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def galactic_adventures(p):
    p['modules'] = {
        'French': {
            '1.1.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def gi_joe_tcg(p):
    p['modules'] = {
        'Module': {
            '1.5.1': p['modules'].pop('1.5.1'),
        },
        'Other Files': {
            '0.0.0': p['modules'].pop('Other Files')
        }
    }


#def gmt_efs_ii(p):
#    p['modules'] = {
#        'Module': { m['version'] : [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
#        'Misc': {
#            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv if not m['filename'].endswith('.vmod') ]
#        }
#    }


def gandhi(p):
    p['modules'] = {
        'Modules': {
            '1.1.0': [ m for pn, pv in p['modules'].items() for m in pv if m['version'] == '1.1.0' ],
            '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv if m['version'] != '1.1.0' ]
        }
    }


def germania_drusus(p):
    p['modules']['1.0.0'] = [ m for m in p['modules']['1.1'] if m.get('version') == '1.0.0' ]
    p['modules']['1.1.0'] = [ m for m in p['modules']['1.1'] if m.get('version') != '1.0.0' ]
    p['modules'].pop('1.1')
    version_to_release(p)


def gettysburg_badges_of_courage(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Misc': {
            '0.0.0': [ m  for pn, pv in p['modules'].items() for m in pv if not m['filename'].endswith('.vmod') ]
        }
    }


def global_war(p):
    sav = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vsav'))
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') }
    }
    p['modules']['Module']['0.1.0'].append(sav)


def gloomhaven(p):
    x310 = [ m for m in p['modules']['3.1'] if m.get('version') not in ('3.1.1', '3.1.2') ]
    x311 = [ m for m in p['modules']['3.1'] if m.get('version') == '3.1.1' ]
    x312 = [ m for m in p['modules']['3.1'] if m.get('version') == '3.1.2' ]

    x4_notes = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Gloomhaven_V4.0_Change_Notes.txt')
    x4_retire = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Gloomhaven_5Player_How to retire V4.0.pdf')
    retire = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Gloomhaven_5Player_How_to_retire.pdf')

    x31_4p = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Gloomhaven_Scenarios_4P_3.1.vmdx')

    x100 = [ m for m in p['modules']['1.0'] if m['filename'].endswith(('.vmod', '.vmdx')) ]

    p['modules'] = {
        'Module': {
            '4.0.0': p['modules'].pop('4.0') + [ x4_notes, x4_retire ],
            '3.2.0': p['modules'].pop('3.2') + [ retire ],
            '3.1.2': x312,
            '3.1.1': x311,
            '3.1.0': x310 + [ x31_4p ],
            '3.0.0': p['modules'].pop('3.0'),
            '2.3.0': p['modules'].pop('2.3'),
            '2.2.0': p['modules'].pop('2.2'),
            '2.1.0': p['modules'].pop('2.1'),
            '2.0.0': p['modules'].pop('2.0'),
            '1.5.0': p['modules'].pop('1.5'),
            '1.4.0': p['modules'].pop('1.4'),
            '1.3.0': p['modules'].pop('1.3'),
            '1.2.0': p['modules'].pop('1.2'),
            '1.1.0': p['modules'].pop('1.1'),
            '1.0.0': x100
        }
    }


def gosix(p):
    p['modules'] = {
        'English': {
            '1.0.0': p['modules'].pop('1.0 English')
        },
        'French': {
            '1.0.0': p['modules'].pop('1.0 French')
        }
    }


def grand_fleet(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Misc': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv if not m['filename'].endswith('.vmod') ]
        }
    }


def great_medieval_battles(p):
    full = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Great Medieval Battles.vmod')
    for pn in p['modules']:
        p['modules'][pn] = [ m for m in p['modules'][pn] if m['filename'] != 'Great Medieval Battles.vmod' ]
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]

    p['modules'] = {
        'Full Game': { '1.0.0': [ full ] },
        'Individual Battles': {}
    }

    for m in ms:
        r = p['modules']['Individual Battles'].setdefault(m['version'], [])
        r.append(m)


def guadalcanal(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules'].pop('1.0')
        },
        'Misc': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def gunslinger(p):
    sp = p['modules'].pop('1.3.2 Spanish Edition')

    p['modules'] = {
        'English Edition': { next(m['version'] for m in pv if 'version' in m): pv for pn, pv in p['modules'].items() if any('Reloaded' not in m['filename'] for m in pv) },
        'Gunslinger Reloaded Spanish-English': { next(m['version'] for m in pv if 'version' in m): pv for pn, pv in p['modules'].items() if any('Reloaded' in m['filename'] for m in pv) },
        'Spanish Edition': { '1.3.2': sp }
    }


def gustav_adolf(p):
    p['modules'] = {
        'Complete Module': {
            '0.3.0': p['modules'].pop('0.3')
        },
        'Individual Battle Modules': {
            '1.0.0': p['modules'].pop('1.0')
        }
    }


def hands_in_the_sea(p):
    p['modules'] = {
        'LIVE': [ m for pn, pv in p['modules'].items() for m in pv if 'LIVE' in pn ],
        'No automation': [ m for pn, pv in p['modules'].items() for m in pv if 'LIVE' not in pn ]
    }
    use_pkgs(p)


def high_frontier(p):
    p['modules'] = {
        'Module': {
            '2.7.0': p['modules'].pop('2.7.0'),
            '2.6.1': p['modules'].pop('2.6.1') + p['modules'].pop('2.6.0') + p['modules'].pop('4.0.2') + p['modules'].pop('0.5'),
            '1.7.0': p['modules'].pop('1.07') + p['modules'].pop('1.06') + p['modules'].pop('1.04') + p['modules'].pop('0.0')
        }
    }


def hitlers_war(p):
    p['modules'] = {
        "Hitler's War": {
            '1.0.0':  p['modules'].pop('1.0'),
            '2.0.0':  p['modules'].pop('2.0.0')
        },
        "Hitler's Global War": {
            '0.2.0': p['modules'].pop('0.2'),
            '0.4.0': p['modules'].pop('0.4')
        },
        'Documents': {
            '0.0.0': p['modules'].pop('Documents')
        }
    }


def imperial_struggle(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def infidel(p):
    tp = [ m for pn, pv in p['modules'].items() for m in pv if 'Tri' in pn ]
    nontp = [ m for pn, pv in p['modules'].items() for m in pv if 'Tri' not in pn ]

    p['modules'] = {
        "Men of Iron Tri-Pack": {},
        '1st Edition': {}
    }

    for m in tp:
        r = p['modules']['Men of Iron Tri-Pack'].setdefault(m['version'], [])
        r.append(m)

    for m in nontp:
        r = p['modules']['1st Edition'].setdefault(m['version'], [])
        r.append(m)


def invasion_america(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def invasion_malta(p):
    p['modules'] = {
        '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv ]
    }
    version_to_release(p)


def island_war(p):
    ms = p['modules']['Module']
    p['modules'] = {
        'Module': {},
        'Game Rules': {
            '0.0.0': p['modules'].pop('Game Rules')
        },
        'Errata': {
            '0.0.0': p['modules'].pop('Errata')
        }
    }

    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def julius_caesar(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def kahmate(p):
    p['modules'] = {
        'Module': {
            '3.2.0': p['modules'].pop('1.0')
        }
    }


def kolejka(p):
    p['modules'] = {
        'Module': {
            '0.1.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def korea_tfw(p):
    fow = p['modules'].pop('FOW 5.02') + p['modules'].pop('FOW 5.01') + p['modules'].pop('FOW 4.25+13.7')
    old = p['modules'].pop('Non FOW 1.8') + p['modules'].pop('Non FOW 1.6')

    p['modules'] = {
        'Standard': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv },
        'FOW': { m['version']: [ m ] for m in fow },
        'Old': { m['version']: [ m ] for m in old }
    }


def kremlin(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Rules': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def la_bat_austerlitz(p):
    notes = next(m for pn, pv in p['modules'].items() for m in pv if 'Notes' in m['filename'])

    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m }
    }

    p['modules']['Module']['1.1.0'].append(notes)


def labyrinth(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def leader_1(p):
    p['modules'] = {
        'Main Module': {
            '2.23.0': p['modules'].pop('Main Module')
        },
        'Stage Generator': {
            '1.1.0': p['modules'].pop('Stage Generator')
        },
        'Extensions': {
            '0.0.0': p['modules'].pop('Extensions')
        }
    }


def leaving_earth(p):
    for pn in p['modules'].keys():
        ms = p['modules'][pn]
        p['modules'][pn] = {}
        for m in ms:
            r = p['modules'][pn].setdefault(m['version'], [])
            r.append(m)


def legendary(p):
    p['modules'] = {
        'Module': {
            '5.2.1': p['modules'].pop('5.2.1'),
            '5.1.0': p['modules'].pop('5.1.0'),
            '5.0.0': p['modules'].pop('5.0'),
            '4.1.0': p['modules'].pop('4.1'),
            '2.51.0': p['modules'].pop('2.51'),
        },
        'Fan': {
            '1.0.0': p['modules'].pop('Fan 1.0')
        }
    }


def les_rois_francs(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules'].pop('1.0')
        },
        'Lyndanise 1219, Vae Victis 118': {
            '1.0.0': p['modules'].pop('Lyndanise 1219, Vae Victis 118')
        },
        'Roncevaux, Vae Victis 120': {
            '1.0.0': p['modules'].pop('Roncevaux, Vae Victis 120')
        }
    }


def liberte(p):
    p['modules'] = {
        'Module': {
            '1.1.2': p['modules']['v1.1'],
            '1.0.12': p['modules']['v1.0']
        }
    }


def mbt(p):
    p['modules'] = {
        'Base Game': {
            '1.1.6': p['modules'].pop('Base Game')
        },
        'Expansions': {
            '0.0.0': p['modules'].pop('Expansions')
        },
        'Oversize Map Files': {
            '0.0.0': p['modules'].pop('Oversize Map Files')
        }
    }


def mbt_idf(p):
   p['modules'] = {
        'Base Game': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Extensions': {
            '0.0.0': p['modules'].pop('Extensions')
        },
        'Misc': {
            '0.0.0': p['modules'].pop('Misc')
        }
    }


def machi_koro(p):
    p['modules'] = {
        'Deluxe': {
            '1.0.2': p['modules'].pop('Deluxe 1.0')
        },
        'Basic': {
            '1.1.7': p['modules'].pop('1.1.7')
        }
    }



def manassas(p):
    p['modules'] = {
        'Module': {
            '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv if m.get('version') != '2.0.0' ],
            '2.0.0': [ m for pn, pv in p['modules'].items() for m in pv if m.get('version') == '2.0.0' ]
        }
    }


def mechwar4(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules'].pop('1.0')
        },
        'Rules': {
            '7.2.0': p['modules'].pop('7.2')
        }
    }


def melee_wizard(p):
    dt = p['modules'].pop('Death Test 1.0')

    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv },
        'Death Test': {
            '1.0.0': dt
        }
    }


def memoir_44(p):
    p['modules'] = {
        'Module': {
            '10.16.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def men_of_iron(p):
    tp = [ m for pn, pv in p['modules'].items() for m in pv if 'Tri' in pn ]
    one = [ m for pn, pv in p['modules'].items() for m in pv if 'Tri' not in pn ]

    p['modules'] = {
        "Men of Iron Tri-Pack": {},
        '1st Edition': {}
    }

    for m in tp:
        r = p['modules']['Men of Iron Tri-Pack'].setdefault(m['version'], [])
        r.append(m)

    for m in one:
        r = p['modules']['1st Edition'].setdefault(m['version'], [])
        r.append(m)


def merchants_and_marauders(p):
    es = p['modules'].pop('1.0')
    wind = p['modules'].pop('1.00')

    ms = [ m for pn, pv in p['modules'].items() for m in pv ]

    p['modules'] = {
        'English': {},
        'Spanish': { '1.0.0': es }
    }

    for m in ms:
        r = p['modules']['English'].setdefault(m['version'], [])
        r.append(m)

    p['modules']['English']['1.7.0'] += wind


def middle_east_strike(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') ]

    p['modules'] = {
        'Module': {},
        'Additional Files': {
            '0.0.0': p['modules'].pop('Additional Files')
        }
    }

    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def midway(p):
    p['modules'] = {
       'Double Blind': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Double' in pn },
        'Standard': {
            '1.3.0': p['modules']['1.3']
        }
    }


def napoleon_at_bay(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Misc': {
            '0.0.0': p['modules'].pop('2011_0621')
        }
    }


def napoleons_last_battles(p):
    p['modules'] = {
        'Campaign Game': p['modules'].pop('Module'),
        'Individual Battle Modules': p['modules'].pop('Individual Battle Modules') + p['modules'].pop('Individual Battle Modules Version 2.1')
    }

    for pn, pv in p['modules'].items():
        p['modules'][pn] = {}
        for m in pv:
            r = p['modules'][pn].setdefault(m['version'], [])
            r.append(m)


def napoleon_the_waterloo(p):
    p['modules'] = {
        'Avalon Hill': {
            '1.0.0': p['modules'].pop('4')
        },
        'Columbia Games 4th Edition': {
            '1.0.0': p['modules'].pop('1')
        },
        'Columbia Games 3rd Edition': {
            '3.0.0': p['modules'].pop('3')
        }
    }


def nations_at_war_wsr(p):
    p['modules'] = {
        'English (2nd Edition)': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if '2nd' in pn },
        'English (1st Edition)': {
            '2.1.0': [ m for m in p['modules']['2.1 1st Edition'] if 'DE' not in m['filename'] ]
        },
        'German (Spielworxx)': {
            '2.1.0': [ m for m in p['modules']['2.1 1st Edition'] if 'DE' in m['filename'] ]
        }
    }


def neanderthal(p):
    p['modules'] = {
        "2nd Edition": p['modules']['2nd Edition'],
        '1st Edition': p['modules']['1st Edition']
    }
    use_pkgs(p)


def neuroshima_hex(p):
    del p['modules']['OLDER VERSIONS']
    version_to_release(p)


def next_war_korea(p):
    p['modules'] = {
        "2nd Edition": { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if '2nd Edition' in pn },
        '1st Edition': {
            '1.2.0':  p['modules']['1.2'],
            '1.1.0':  p['modules']['1.1'],
            '1.0.0':  p['modules']['1.0']
        }
    }


def next_war_taiwan(p):
    p['modules'] = {
        "Revised": { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Revised' in pn },
        '1st Edition': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Revised' not in pn }
    }


def no_better_place_to_die(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Misc': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def no_retreat_the_russian_front(p):
    p['modules'] = {
        'English': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Spanish' not in pn },
        'Spanish': {
            '1.4.0': p['modules'].pop('1.4 Spanish Edition'),
            '1.3.0': p['modules'].pop('1.3 Spanish Edition')
        }
    }


def normandy_44(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def nothing_gained_but_glory(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def on_to_richmond_ii(p):
    p['modules'] = {
        'On To Richmond II': p['modules'].pop('On To Richmond II v3'),
        'Grant Takes Command II': p['modules'].pop('Grant Takes Command II v3'),
        'The Petersburg Campaign': p['modules'].pop('The Petersburg Campaign v3')
    }
    use_pkgs(p)


def ogre(p):
    p['modules'] = {
        'Module I': {
            '1.0.0': p['modules'].pop('Module I')
        },
        'Module III': { next(m['version'] for m in pv if 'version' in m): pv for pn, pv in p['modules'].items() if '1' in pn },
        'OGRE Rules 2nd Edition': {
            '0.0.0': p['modules'].pop('OGRE Rules 2nd Edition')
        }
    }


def operation_grenade(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Rules': {
            '0.0.0': p['modules'].pop('Rules')
        }
    }


def operation_mercury(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Player Aids': {
            '0.0.0': p['modules'].pop('Player Aids')
        }
    }


def origins_how(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Extension': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmdx') }
    }


def pacific_war(p):
    misc = p['modules'].pop('None')
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv },
        'Misc': {
            '0.0.0': misc
        }
    }


def pandemic(p):
    p['modules'] = {
        'Pandemic + All 3 Expansions': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if '3' in pn },
        'In the Lab': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Lab' in pn },
        'On the Brink': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Brink' in pn },
    }


def panzer(p):
    p['modules'] = {
        'Base Game': {
            '1.6.8': p['modules'].pop('Base Game')
        },
        'Expansions': { m['version']: [ m ] for m in p['modules']['Expansions'] },
        'Oversize Map Files': {
            '0.0.0': p['modules'].pop('Oversize Map Files')
        }
    }


def panzer_command(p):
    p['modules'] = {
        'Module': {
            '2.2.0': p['modules'].pop('2.2'),
            '1.0.1': p['modules'].pop('1.0.1'),
            '1.0.0': p['modules'].pop('1.0')
        },
        'Misc': {
            '0.0.0': p['modules'].pop('Misc')
        }
    }


def panzer_north_africa(p):
    p['modules'] = {
        'Base Game': {
            '1.1.0': p['modules'].pop('Base Game')
        },
        'Oversize Map Files': {
            '0.0.0': p['modules'].pop('Oversize Map Files')
        }
    }


def panzerblitz(p):
    p['modules'] = {
        'PanzerBlitz Deluxe': {
            '1.4.0': p['modules'].pop('Panzer Blitz Deluxe V1.04')
        },
        'PanzerBlitz': {
            '3.4.4': p['modules'].pop('3.4.4'),
            '3.5.2': p['modules'].pop('3.5b'),
            '3.5.26': p['modules'].pop('3.5z'),
            '3.6.0': p['modules'].pop('3.6'),
            '3.7.0': p['modules'].pop('3.7'),
        },
        'Misc': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def paris_vaut(p):
    p['modules'] = {
        'Dreux 1562': {
            '1.0.0': p['modules'].pop('Dreux 1562 version 1.0')
        },
        'Ivry 1590': {
            '1.0.0': p['modules'].pop('Ivry 1590 version 1.0')
        }
    }


def paths_of_glory(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def pattons_3rd_army(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Rules': {
            '0.0.0': p['modules'].pop('Rules')
        }
    }


def pattons_best(p):
    p['modules'] = {
        'Module': {
            '1.3.1': [ m for m in p['modules']['1.3'] if m['version'] == '1.3.1' ],
            '1.3.0': [ m for m in p['modules']['1.3'] if m['version'] == '1.3.0' ],
            '0.97.2': p['modules']['0.97b'],
            '0.97.0':  p['modules']['0.97']
        }
    }


def pente(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def pericles(p):
    p['modules'] = {
        '2-4 players with Bots': [ m for pn, pv in p['modules'].items() for m in pv if 'Bots' in pn ],
        'Solitaire only': [ m for pn, pv in p['modules'].items() for m in pv if 'Bots' not in pn ]
    }
    use_pkgs(p)


def pirates_of_the_spanish_main(p):
    p['modules'] = {
        'English (Wizkids Version)': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'English' in pn },
        'French': {
            '1.5.0': p['modules'].pop('1.5 French')
        }
    }


def prussias_glory_ii(p):
    raise RuntimeError()


def quatre_batailles(p):
    p['modules'] = { k.removeprefix('1.0 '): v for k, v in p['modules'].items() }
    use_pkgs(p)


def race_for_the_galaxy(p):
    p['modules'] = {
        'French Language': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv }
    }


def race_formula_90(p):
    p['modules'] = {
        '2ed': {
            '0.1.0': p['modules'].pop('2ed 0.1')
        },
        '1ed': {
            '6.1.0': p['modules'].pop('6.1'),
            '6.0.0': p['modules'].pop('6'),
            '5.0.0': p['modules'].pop('5'),
            '4.0.0': p['modules'].pop('4'),
            '3.0.0': p['modules'].pop('3')
        },
        'Benetton': {
            '1.0.0': p['modules'].pop('Benetton 1.0')
        }
    }


def rallyman(p):
    p['modules'] = {
        'English Language': {
            '4.0.1': p['modules'].pop('4.0.1 English Language'),
            '3.1.0': p['modules'].pop('3.1 English Language'),
        },
        'French Language': {
            '2.0.0': p['modules'].pop('2.0 French Language')
        }
    }


def red_badge_of_courage(p):
    br1 = p['modules'].pop('1.1')
    br2 = [ m for pn, pv in p['modules'].items() for m in pv if 'BR' in m['filename'] ]

    ms = [ m for pn, pv in p['modules'].items() for m in pv if 'BR' not in m['filename'] ]
    p['modules'] = {
        'Complete': {},
        'First Bull Run': {
            '1.1.0': br1
        },
        'Second Bull Run': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in br2 },
    }
    for m in ms:
        r = p['modules']['Complete'].setdefault(m['version'], [])
        r.append(m)


def reluctant_enemies(p):
    fow = p['modules'].pop('4.28') + p['modules'].pop('4.27') + p['modules'].pop('4.25+13.7')
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]

    p['modules'] = {
        'Standard': {},
        'FOW': { m['version']: [ m ] for m in fow }
    }

    for m in ms:
        r = p['modules']['Standard'].setdefault(m['version'], [])
        r.append(m)


def roads_to_leningrad(p):
    p['modules'] = {
        'Staraya Russa Scenarios': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Staraya' in m['filename'] },
        'Soltsy Scenarios': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Soltsy' in m['filename'] }
    }


def roborally(p):
    p['modules']['2.0'].extend(p['modules'].pop('2.0 Extension'))
    version_to_release(p)


def russian_front(p):
    misc = p['modules'].pop('Misc')
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]

    p['modules'] = {
        'Module': {},
        'Misc': {
            '0.0.0': misc
        }
    }

    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def samurai_battles(p):
     p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Genpei War': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmdx') }
    }


def samurai_blades_and_map(p):
    p['modules'] = {
        'Module': { '13.0.0': p['modules'].pop('Module') }
    }


def samurai_blades_campaign(p):
    p['modules'] = {
        'Module': { '0.0.0': p['modules'].pop('Module') }
    }


def sauron(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def semper_fi(p):
     p['modules'] = {
        'Module': {
            '1.1.0': [ m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') ],
            '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv if not m['filename'].endswith('.vmod') ]
        }
    }


def sicily_ii(p):
    fow = p['modules'].pop('1.01 FOW')
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]

    p['modules'] = {
        'Standard': {},
        'FOW': { m['version']: [ m ] for m in fow }
    }

    for m in ms:
        r = p['modules']['Standard'].setdefault(m['version'], [])
        r.append(m)


def sicily_the_race(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Rules': {
            '0.0.0': p['modules'].pop('Rules')
        }
    }


def silent_war(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'IJN Extension': {
            '1.0.0': p['modules'].pop('1.0'),
            '1.1.1': p['modules'].pop('1.1')
        }
    }


def smolensk_barbarossa(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def soe_lysander(p):
    p['modules'] = {
        'Module': {
            '1.5.0-a': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def space_alert(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Extension': {
            '0.30.0': p['modules'].pop('0.30')
        }
    }


def space_opera(p):
    rules = next(m for pn, pv in p['modules'].items() for m in pv if 'Rulebook' in m['filename'])

    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m }
    }

    p['modules']['Module']['1.1.0'].append(rules)


def spacecorp(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Ventures' not in m['filename'] },
        'Ventures': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Ventures' in m['filename'] }
    }


def squad_leader(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for m in p['modules']['Module Files'] },
        'Extension Files': {
            '0.0.0': p['modules'].pop('Extension Files')
        },
        'Scenario Start Files': {
            '0.0.0': p['modules'].pop('Scenario Start Files')
        },
        'Boards, Version 5 SK with LOS installed (EXC: Desert boards #25-31)': {
            '0.0.0': p['modules'].pop('Boards, Version 5 SK with LOS installed (EXC: Desert boards #25-31)!!')
        },
        'Overlays': {
            '0.0.0': p['modules'].pop('Overlays')
        },
        'Customized and special boards': {
            '0.0.0': p['modules'].pop('Customized and special boards')
        },
        'Miscellaneous Module Files': {
            '0.0.0': p['modules'].pop('Miscellaneous Module Files')
        },
        'Help and Version History Files': {
            '0.0.0': p['modules'].pop('Help and Version History Files')
        }
    }


def star_wars_armada(p):
    del p['modules']['HISTORICAL VERSIONS']
    version_to_release(p)


def star_wars_epic_duels(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Misc': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def star_wars_miniatures(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Extensions': {
            '0.0.0': p['modules'].pop('Extensions')
        }
    }


def starfire(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def starmada_tae(p):
    p['modules'] = {
        'Module': {
            '1.2.0': p['modules']['1.02']
        }
    }


def star_trek_the_game(p):
    p['modules'] = {
        'Module': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def star_trek_iii(p):
    p['modules'] = {
        'Kobayashi Maru Game': {
            '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'Maru' in m['filename']]
        },
        'Sherwood Syndrome Game': {
            '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'Sherwood' in m['filename']]
        },
        'Free Enterprise Game': {
            '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'Free' in m['filename']]
        },
    }


def star_wars_tactics(p):
    p['modules'] = {
        'Module': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def steel_wolves(p):
    instr = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.pdf'))
    p['modules'] = {
        'English': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m and 'DE' not in m.get('filename', '') },
        'German - Das Boot (Spielworxx)': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'DE' in m.get('filename', '') }
    }

    p['modules']['English']['1.1.0'].append(instr)


def stonewall_jacksons_way_ii(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def storm_over_arnhem(p):
    p['modules'] = {
        'English': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'English' in pn },
        'Japanese': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'English' not in pn and m['filename'].endswith('.vmod') },
        'Rules': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'English' not in pn and m['filename'].endswith('.pdf') ]
        }
    }


def struggle_of_empires(p):
    p['modules'] = {
        'Deluxe': {
            '1.1.0': p['modules'].pop('Deluxe 1.1')
        },
        'Module': {
            '1.3.0': p['modules'].pop('1.3')
        }
    }


def successors_2ed(p):
    p['modules'] = {
        'Deluxe version': {
            '0.1.0': p['modules'].pop('0.0.1 Deluxe version')
        },
        'Module': {
            '1.2.0': p['modules'].pop('1.02')
        }
    }


def suez73(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules']['1.00']
        }
    }


def summoner_wars(p):
    base3x = next(m for m in p['modules']['3.x'] if 'Base' in m['filename'])
    p['modules']['3.1.0'] = [ m for m in p['modules']['3.x'] if m.get('version') == '3.1.0' ] + [ base3x ]
    p['modules']['3.1.2'] = [ m for m in p['modules']['3.x'] if m.get('version') == '3.1.2' ]
    p['modules']['3.1.4'] = [ m for m in p['modules']['3.x'] if m.get('version') == '3.1.4' ]
    p['modules'].pop('3.x')

    base4x = next(m for m in p['modules']['4.x'] if 'Base' in m['filename'])
    p['modules']['4.0.0'] = [ m for m in p['modules']['4.x'] if m.get('version') == '4.0.0' ] + [ base4x ]
    p['modules']['4.1.0'] = [ m for m in p['modules']['4.x'] if m.get('version') == '4.1.0' ]
    p['modules']['4.2.0'] = [ m for m in p['modules']['4.x'] if m.get('version') == '4.2.0' ]
    p['modules'].pop('4.x')
    version_to_release(p)


def sweden_fights_on(p):
    p['modules'] = {
        'Complete Module': {
            '1.1.0': p['modules'].pop('1.1')
        },
        'Individual Battle Modules': {
            '1.0.0': p['modules'].pop('1.0')
        }
    }


def tactics_25(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules'].pop('Module')
        }
    }


def tannenberg_1914(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Player Aids': {
            '0.0.0': p['modules'].pop('Player Aids')
        }
    }


def target_arnhem(p):
    setup = next(m for pn, pv in p['modules'].items() for m in pv if 'setup' in m['filename'])

    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m }
    }

    p['modules']['Module']['1.0.0'].append(setup)


def tarot(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def tenkatoitsu(p):
    instr = p['modules'].pop('Instructions')
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]

    p['modules'] = {
        'Module': {},
        'Instructions': {
            '0.0.0': instr
        }
    }

    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def tet_offensive(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules'].pop('Module')
        }
    }


def the_alamo_victory_in_death(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Misc': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def the_balkan_wars(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Rules': {
            '0.0.0': p['modules'].pop('Rules')
        }
    }


def the_battle_of_corinth(p):
    p['modules'] = {
        'Corinth': [ m for pn, pv in p['modules'].items() for m in pv if 'Corinth' in pn ],
        'Jackson at the Crossroads': [ m for pn, pv in p['modules'].items() for m in pv if 'Corinth' not in pn ]
    }
    use_pkgs(p)


def the_battle_of_the_bulge(p):
    p['modules'] = {
        "2nd Edition": [ m for pn, pv in p['modules'].items() for m in pv if pn.startswith('2nd Edition') ],
        '1st Edition': p['modules']['1.05']
    }
    use_pkgs(p)


def the_battle_of_monmouth_1982(p):
    st = [ m for pn, pv in p['modules'].items() for m in pv if '90' in m['filename'] ]
    ms = [ m for pn, pv in p['modules'].items() for m in pv if '90' not in m['filename'] ]
    p['modules'] = {
        'SPI': {},
        'S&T 90': { '1.0.0': st },
    }
    for m in ms:
        r = p['modules']['SPI'].setdefault(m['version'], [])
        r.append(m)


def the_campaign_for_north_africa(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Operation Brevity scenario files': {
            '0.0.0': p['modules'].pop('Operation Brevity scenario files')
        }
    }


def the_creature_that_ate_sheboygan(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Misc': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'version' not in m ]
        }
    }


def the_desert_fox(p):
    p['modules'] = {
        'SPI': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'SPI' in m['filename'] },
        'Hay Archive': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'SPI' not in m['filename'] }
    }


def the_fast_carriers(p):
    p['modules'] = {
        'Module': {
            '1.1.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def the_fighting_general_patton(p):
    p['modules'] = {
        'Module': {
            '1.0.0': [ m for pn, pv in p['modules'].items() for m in pv ]
        }
    }


def the_grunwald_swords(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def the_kaisers_pirates(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def the_mighty_endeavor(p):
    log = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.txt'))

    p['modules'] = {
        '2nd Edition': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'TME2' in m['filename'] },
        '1st Edition': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'TME2' not in m['filename'] and m['filename'].endswith('.vmod') }
    }

    p['modules']['1st Edition']['1.7.0'].append(log)


def the_longest_day(p):
    hist = p['modules'].pop('Current Itemized Version History')
    vmdx = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmdx'))

    ms = [ m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') ]
    p['modules'] = {
        'Module': {},
        'Current Itemized Version History': {
            '0.0.0': hist
        }
    }

    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)

    p['modules']['Module']['0.8.0'].append(vmdx)


def the_other_side(p):
    p['modules'] = {
        'Beyond the Other Side': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Beyond' in pn },
        'The Other Side': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Beyond' not in pn }
    }


def the_sword_and_the_stars(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Misc': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'version' not in m ]
        }
    }


def through_the_breach(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Misc': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'version' not in m ]
        }
    }


def title_bout(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Rules': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'version' not in m ]
        }
    }


def tomb_raider(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Extensions': {
            '0.0.0': [ m for pn, pv in p['modules'].items() for m in pv if 'version' not in m ]
        }
    }


def tonnage_war_solitaire(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Rules': {
            '0.0.0': p['modules'].pop('None')
        }
    }


def torgau(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules']['1.00']
        }
    }


def totaler_krieg_2e(p):
    ds_sav = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vsav') and pn == '8.56')
    ae_sav = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vsav') and pn == '7.13')

    ms = [ m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)

    p['modules']['Module']['8.56.0'].append(ds_sav)
    p['modules']['Module']['7.13.0'].append(ae_sav)


def trafalgar(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules']['1.00']
        }
    }


def triple_topper(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def turkenkrieg(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Heirs of the Golden Horde Extensions': {
            '0.0.0': p['modules'].pop('Heirs of the Golden Horde Extensions')
        }
    }


def twilight_struggle(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv if 'Deluxe' in pn or pn.startswith('3.') ]

    p['modules'] = {
        'Deluxe': {},
        '2nd Edition': {
            '1.3.0': p['modules'].pop('2nd Edition - 1.3')
        },
        '1st Edition': {
            '2.5.0': p['modules'].pop('1st Edition - 2.5')
        },
        'Play By E-Mail with ACTS': {
            '1.2.4': p['modules'].pop('Play By E-Mail with ACTS - 1.2')
        },
        'No Rule Enforcement': {
            '1.0.2': p['modules'].pop('No Rule Enforcement 1.0.2')
        }
    }

    for m in ms:
        r = p['modules']['Deluxe'].setdefault(m['version'], [])
        r.append(m)


def ukraine43(p):
    p['modules'] = {
        "2nd Edition": [ m for pn, pv in p['modules'].items() for m in pv if pn.startswith('2nd Edition') ],
        '1st Edition': p['modules']['1.1']
    }
    use_pkgs(p)


def use_100(p):
    p['modules']['Module'] = {
        '1.0.0': p['modules']['Module']
    }


def under_the_lily_banners(p):
    p['modules'] = {
        'Complete Module': {
            '2.4.0': p['modules'].pop('2.4'),
            '2.3.0': p['modules'].pop('2.3'),
            '2.1.0': p['modules'].pop('2.1'),
        },
        'Individual Battle Modules': {
            '1.2.0': p['modules'].pop('1.2')
        }
    }


def use_pkgs(p):
    mods = p['modules']

    for pn, pc in mods.items():
        mods[pn] = { e['version']: [ e ] for e in pc }


def verdun(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Player Aids': {
            '0.0.0': p['modules'].pop('Player Aids')
        }
    }


def version_to_release(p):
    pkgs = list(p['modules'].values())
    rels = {}
    p['modules'] = { 'Module': rels }

    for pc in pkgs:
        ver = next(x['version'] for x in pc if x['filename'].endswith('.vmod'))
        rels[ver] = pc


def victory_in_the_pacific(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Version History': {
            '0.0.0': p['modules'].pop('Version History')
        },
        'Misc': {
            '0.0.0': p['modules'].pop('Misc')
        },
    }


def voyage_of_the_bsm_pandora(p):
    p['modules'] = {
        'Voyage of the B.S.M Pandora': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Voyage' in m['filename'] },
        'Wreck of the B.S.M Pandora': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Voyage' not in m['filename'] }
    }


def wacht_am_rhein(p):
    p['modules'] = {
        'East is up Orientation': [ m for pn, pv in p['modules'].items() for m in pv if 'East' in pn ],
        'North is up Orientation': [ m for pn, pv in p['modules'].items() for m in pv if 'North' in pn ]
    }
    use_pkgs(p)


def warpwar(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def washingtons_war(p):
    vlog = next(m for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vlog'))

    p['modules'] = {
        'English': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'English' in pn and 'version' in m },
        'German': {
            '1.2.0': p['modules'].pop('1.2 German')
        }
    }

    p['modules']['English']['1.3.0'].append(vlog)


def waterloo(p):
    p['modules'] = {
        'Waterloo with artwork by Imaginative Strategist': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Strategist' in pn },
        'Waterloo with artwork by John Cooper': {
            '2.2.0': p['modules'].pop('Waterloo with artwork by John Cooper')
        },
        'Waterloo with original artwork by Avalon Hill': {
            '2.2.0': p['modules'].pop('Waterloo with original artwork by Avalon Hill')
        },
        'Rules': {
            '0.0.0': p['modules'].pop('Rules')
        }
    }

def weimar(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv ]
    p['modules'] = { 'Module': {} }
    for m in ms:
        r = p['modules']['Module'].setdefault(m['version'], [])
        r.append(m)


def westwall(p):
    ms = [ m for pn, pv in p['modules'].items() for m in pv if pn != '1.0' ]

    p['modules'] = {
        'Complete Module': {
            '1.0.0': p['modules'].pop('1.0')
        },
        'Individual Modules': {}
    }

    for m in ms:
        r = p['modules']['Individual Modules'].setdefault(m['version'], [])
        r.append(m)


def wing_commander_armada(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Rules': {
            '0.0.0': p['modules'].pop('0.7.1')
        }
    }


def wing_leader(p):
    p['modules'] = {
        'Module': {
            '5.0.0': p['modules'].pop('v5.00') + p['modules'].pop('v2.00') + p['modules'].pop('v1.00') + p['modules'].pop('v1.1'),
            '4.2.0': p['modules'].pop('Legacy 4.02') + [
                next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'WL Blitz v2.vmdx'),
                next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'WL Eagles v1.vmdx'),
                next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'WL Victories 2e v1.vmdx'),
                next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'WL Origins v1.vmdx')
            ],
            '4.1.0': p['modules'].pop('Legacy 4.01'),
            '3.0.0': p['modules'].pop('Legacy 3.00') + [
                next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Wing Leader Blitz v1.vmdx'),
                next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Wing Leader C3i-29 v1.vmdx'),
                next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Wing Leader C3i-30 v1.vmdx'),
                next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Wing Leader Fandom v102.vmdx'),
                next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Wing Leader Fandom v101.vmdx'),
                next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Wing Leader Fandom v1.vmdx')
            ],
            '2.0.0': [ next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Wing Leader v2.vmod') ],
            '1.0.0': [ next(m for pn, pv in p['modules'].items() for m in pv if m['filename'] == 'Wing Leader v1.vmod') ]
        }
    }


def winter_war(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules']['1.00'],
            '1.1.0': p['modules']['1.10']
        }
    }


def wizard_kings(p):
    p['modules'] = {
        '2nd Edition': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if '2nd' in pn },
        '?? Edition': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if '2nd' not in pn }
    }


def world_at_war(p):
    p['modules'] = {
        'Eisenbach Gap': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if m['filename'].endswith('.vmod') },
        'Blood and Bridges': {
            '1.3.0': p['modules'].pop('1.3 Blood and Bridges'),
            '2.0.0': [ m for m in p['modules']['2.0'] if 'Blood' in m['filename'] ]
        },
        'Death of the 1st Panzer': {
            '1.3.0': p['modules'].pop('1.3 Death of the 1st Panzer'),
            '2.0.0': [ m for m in p['modules']['2.0'] if 'Death' in m['filename'] ]
        },
        'Battles within Battles': {
            '1.0.0': p['modules'].pop('1.0 Battles within Battles'),
            '2.0.0': [ m for m in p['modules']['2.0'] if 'Battles' in m['filename'] ]
        },
        'Baltic Fury': {
            '1.0.0': p['modules'].pop('1.0')
        },
        '4th CMBG': {
            '1.2.0': p['modules'].pop('1.2 4th CMBG')
        },
        'Line of Fire 1-6': {
            '1.3.0': p['modules'].pop('1.3 Line of Fire 1-6')
        },
        'Line of Fire 7+': {
            '1.2.0': p['modules'].pop('1.2 Line of Fire 7+')
        }
    }


def yggdrasil(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Dark' not in pn },
        'Dark Eclipse': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'Dark' in pn }
    }


def z_g_resurgence(p):
    p['modules'] = {
        'Module': { m['version']: [ m ] for pn, pv in p['modules'].items() for m in pv if 'version' in m },
        'Help Files': {
            '0.0.0': p['modules'].pop('Help Files')
        }
    }


def zulu(p):
    p['modules'] = {
        'Module': {
            '1.0.0': p['modules']['1.00']
        }
    }


collapses = {
    "\"The Aragón Front\"": None,
    "'65: Squad-Level Combat in the Jungles of Vietnam": collapse_pkgs,
    "'CA' Tactical Naval Warfare in the Pacific, 1941-45": None,
    "(Your Name Here) and the Argonauts": collapse_pkgs,
    "11 de Setembre Setge 1714": collapse_pkgs,
    "12 Hours at Maleme": collapse_pkgs,
    "12 Patrols": collapse_pkgs,
    "13 Days: The Cuban Missile Crisis": collapse_pkgs,
    "13 Dead End Drive": None,
    "13: The Colonies in Revolt": collapse_pkgs,
    "1631 Un Empire En Flammes": collapse_pkgs,
    "1714: The Case of the Catalans": None,
    "1775: Rebellion": collapse_pkgs,
    "1776": None,
    "1792: La Patrie en Danger": collapse_pkgs,
    "1805: Sea of Glory": collapse_pkgs,
    "1807: The Eagles Turn East": None,
    "1809: Napoleons Danube Campaign": None,
    "1812!: War on the Great Lakes Frontier": collapse_pkgs,
    "1812: Napoleon's Fateful March": None,
    "1812: The Campaign of Napoleon in Russia": None,
    "1812: The Invasion of Canada": collapse_pkgs,
    "1813: Napoleon's Nemesis": collapse_pkgs,
    "1866: The Struggle for Supremacy in Germany": collapse_pkgs,
    "18xx": None,
    "1914": collapse_pkgs,
    "1914: Fureur à l'Est": collapse_pkgs,
    "1914: Germany at War": collapse_pkgs,
    "1914: Glory's End / When Eagles Fight": None,
    "1914: Nach Paris": collapse_pkgs,
    "1914: Offensive à outrance": collapse_pkgs,
    "1914: Serbien Muss Sterbien": collapse_pkgs,
    "1914: Twilight in the East": collapse_pkgs,
    "1918/1919: Storm in the West": collapse_pkgs,
    "1918: Brother against Brother": collapse_pkgs,
    "1918: Operation Michel": collapse_pkgs,
    "1936: Guerra Civil": None,
    "1942": collapse_pkgs,
    "1944: D-Day to the Rhine": collapse_pkgs,
    "1960: The Making of the President": collapse_pkgs,
    "1972: The Lost Phantom": collapse_pkgs,
    "1979: Revolution in Iran": collapse_pkgs,
    "1985: Under an Iron Sky": collapse_pkgs,
    "1989: Dawn of Freedom": collapse_pkgs,
    "1st Alamein": None,
    "2 Minutes to Midnight": collapse_pkgs,
    "2024-An Olympic Undertaking": collapse_pkgs,
    "2040: An American Insurgency": collapse_pkgs,
    "22 pommes": collapse_pkgs,
    "278th Squadron \"the same 4 cats\": SM79 Damned Hunchback": collapse_pkgs,
    "2nd Fleet": None,
    "300: Earth & Water": collapse_pkgs,
    "3rd Fleet": collapse_pkgs,
    "40th Panzer Korps": collapse_pkgs,
    "57th Panzer Korps": collapse_pkgs,
    "5th Fleet": None,
    "7 Ages": None,
    "7th Fleet": collapse_pkgs,
    "8th Army: Operation Crusader": None,
    "A Call to Arms: Babylon 5 Space Combat": collapse_pkgs,
    "A Chat Module": collapse_pkgs,
    "A Distant Plain": collapse_pkgs,
    "A Fearful Slaughter: The Battle of Shiloh": collapse_pkgs,
    "A Few Acres of Snow": collapse_pkgs,
    "A Frozen Hell": collapse_pkgs,
    "A Game of Thrones: The Board Game (Second Edition)": None,
    "A Gate of Hell: The Campaign for Charleston, July-September 1863": collapse_pkgs,
    "A Gest of Robin Hood": collapse_pkgs,
    "A Gleam of Bayonets: The Battle of Antietam": collapse_pkgs,
    "A Glorious Chance: The Naval Struggle for Lake Ontario in the War of 1812": collapse_pkgs,
    "A House Divided": None,
    "A Master Stroke: The Battle for Meiktila, March 5-14, 1945": None,
    "A Mighty Fortress": None,
    "A Modest Inclination Towards Speed": collapse_pkgs,
    "A Most Dangerous Time": collapse_pkgs,
    "A Most Fearful Sacrifice: The Three Days of Gettysburg": collapse_pkgs,
    "A Pragmatic War: The War of the Austrian Succession 1741 – 1748": collapse_pkgs,
    "A Raging Storm": collapse_pkgs,
    "A Splendid Little War: The 1898 Santiago Campaign": None,
    "A Study in Emerald": None,
    "A Thunder Upon the Land: The Battles of Narva and Poltava": None,
    "A Time for Trumpets: The Battle of the Bulge, December 1944": None,
    "A Victory Awaits: Operation Barbarossa 1941": collapse_pkgs,
    "A Victory Denied": collapse_pkgs,
    "A Victory Lost": None,
    "A Winter War": collapse_pkgs,
    "A World at War": collapse_pkgs,
    "A la charge: Normands et Byzantins": collapse_pkgs,
    "A la guerre...": collapse_pkgs,
    "A las Barricadas!": None,
    "A las Barricadas! (2nd Edition)": None,
    "AFTERSHOCK: A Humanitarian Crisis Game": None,
    "APBA American Saddle Racing Game": collapse_pkgs,
    "Abaddon": collapse_pkgs,
    "Absolute Victory: World Conflict 1939-1945": collapse_pkgs,
    "Absolute War! The Russian Front 1941-45": collapse_pkgs,
    "Acadians": collapse_pkgs,
    "Aces High": collapse_pkgs,
    "Aces of Valor": collapse_pkgs,
    "Acquire": collapse_pkgs,
    "Across 5 Aprils": None,
    "Across Four Oceans": collapse_pkgs,
    "Across Suez": None,
    "Across the Bug River: Volodymyr-Volynskyi 1941": collapse_pkgs,
    "Across the Pacific": collapse_pkgs,
    "Across the Potomac": collapse_pkgs,
    "Admiralty": collapse_pkgs,
    "Adowa": collapse_pkgs,
    "Advanced Civilization": None,
    "Advanced Delve Dice": collapse_pkgs,
    "Advanced Pacific Theater of Operations": None,
    "Advanced Squad Leader": collapse_pkgs,
    "Advanced Tobruk System": collapse_pkgs,
    "Aegean Strike": collapse_pkgs,
    "Aether Captains": collapse_pkgs,
    "Afrika (2nd Edition)": collapse_pkgs,
    "Afrika Korps": None,
    "Afrika: The Northern African Campaign, 1940-1942": collapse_pkgs,
    "Against the Reich": collapse_pkgs,
    "Age Of Steam": None,
    "Age of Aces": collapse_pkgs,
    "Age of Bismarck: The Unifications of Italy and Germany 1859-1871": None,
    "Age of Dogfights: WW1": collapse_pkgs,
    "Age of Empires III: The Age of Discovery": collapse_pkgs,
    "Age of Muskets Volume I: Tomb for an Empire": collapse_pkgs,
    "Age of Napoleon": collapse_pkgs,
    "Age of Sail": None,
    "Agordat 1893": collapse_pkgs,
    "Agricola, Master of Britain": collapse_pkgs,
    "Air & Armor": collapse_pkgs,
    "Air & Armor: Würzburg, Tactical Armored Warfare in Europe – Designer Signature Edition": collapse_pkgs,
    "Air Assault on Crete": None,
    "Air Force": None,
    "Air Scarmush: Tactical Flight Contest": collapse_pkgs,
    "Air Strike": collapse_pkgs,
    "Air Superiority": collapse_pkgs,
    "Airborne in My Pocket": collapse_pkgs,
    "Alamo": collapse_pkgs,
    "Albion 20": collapse_pkgs,
    "Albion: Land of Faerie": collapse_pkgs,
    "Alchelemental": None,
    "Alchemists": collapse_pkgs,
    "Alea Iacta Est": collapse_pkgs,
    "Alexander The Great": collapse_pkgs,
    "Alexander at Tyre": None,
    "Alexandros and I Am Spartacus!": collapse_pkgs,
    "Algeria: The war of Independence 1954-1962": collapse_pkgs,
    "Alhambra: Big Box": None,
    "Alien Frontiers": collapse_pkgs,
    "Aliens": collapse_pkgs,
    "All Bridges Burning": collapse_pkgs,
    "All Things Zombie": None,
    "All Things Zombie: The Boardgame": collapse_pkgs,
    "All hands on deck": collapse_pkgs,
    "All is lost save Honour": collapse_pkgs,
    "All or Nothing": collapse_pkgs,
    "All-Star Baseball": None,
    "Allen's Dirt The Game": None,
    "Alma 1854": collapse_pkgs,
    "Almeida et Bussaco 1810": collapse_pkgs,
    "Almoravid": collapse_pkgs,
    "Almost a Miracle! The Revolutionary War in the North": collapse_pkgs,
    "Amateurs to Arms!": collapse_pkgs,
    "Ambon: Burning Sun & Little Seagulls": collapse_pkgs,
    "Ambush": None,
    "America Falling: The Coming Civil War": collapse_pkgs,
    "American Megafauna": collapse_pkgs,
    "American Tank Ace: 1944-1945": collapse_pkgs,
    "Amerika Bomber: Evil Queen of the Skies": collapse_pkgs,
    "Ameritrash": collapse_pkgs,
    "Amigos and Insurrectos: The Philippine Insurrection 1899-1902": collapse_pkgs,
    "Amoeba Wars": collapse_pkgs,
    "Amphipolis: 424/422 av. J.-C.": collapse_pkgs,
    "An Attrition of Souls": collapse_pkgs,
    "An Infamous Traffic": collapse_pkgs,
    "Ancient Battles Deluxe": collapse_pkgs,
    "Ancient Civilizations of the Inner Sea": collapse_pkgs,
    "Ancient Civilizations of the Middle East": collapse_pkgs,
    "Ancients": None,
    "Andartes": collapse_pkgs,
    "Andean Abyss": collapse_pkgs,
    "Android: Mainframe": collapse_pkgs,
    "Android: Netrunner": None,
    "Angola": collapse_pkgs,
    "Anima Tactics": collapse_pkgs,
    "Annihilator / OneWorld": None,
    "Antietam 1862": collapse_pkgs,
    "Antipalos": collapse_pkgs,
    "Antiquity": collapse_pkgs,
    "Anvil-Dragoon: The Second D-Day": collapse_pkgs,
    "Anzio": collapse_pkgs,
    "Anzio Beachhead": collapse_pkgs,
    "Anzio/Cassino": collapse_pkgs,
    "Apocalypse Road": collapse_pkgs,
    "Apocalypse in the East: The Rise of the First Caliphate 646-656 A.D.": collapse_pkgs,
    "Apocalypse of Steel": collapse_pkgs,
    "Apocalypse: World War II in Europe": collapse_pkgs,
    "Apples to Apples": collapse_pkgs,
    "April's Harvest: The Battle of Shiloh, April 6 & 7, 1862": collapse_pkgs,
    "Apuren el corralito!: The 2nd Battle of Alihuatá, December 1933": collapse_pkgs,
    "Aqua Romana": collapse_pkgs,
    "Aquileia": collapse_pkgs,
    "Arboretum": collapse_pkgs,
    "Archipelago": collapse_pkgs,
    "Arcole 1796": collapse_pkgs,
    "Arctic Disaster: The Destruction of Convoy PQ-17": collapse_pkgs,
    "Arctic Storm: The Russo-Finnish Winter War 1939-40": collapse_pkgs,
    "Arden": collapse_pkgs,
    "Ardennes": collapse_pkgs,
    "Ardennes '44": None,
    "Ardennes II": collapse_pkgs,
    "Ardennes Petite: A Battle of the Bulge, Ardennes 1944, Minigame": collapse_pkgs,
    "Arena: Roma II": collapse_pkgs,
    "Argent: The Consortium": collapse_pkgs,
    "Argon Battlefront": None,
    "Ariete: The Battle of Bir el Gubi, Libya November 1941": collapse_pkgs,
    "Arimaa": None,
    "Aristeia!": collapse_pkgs,
    "Arkham Horror": None,
    "Arkham Horror Unlimited": collapse_pkgs,
    "Arkham Horror: Curse of the Dark Pharaoh Expansion": collapse_pkgs,
    "Arkham Horror: Dunwich Horror Expansion": collapse_pkgs,
    "Arkham Horror: Innsmouth Horror Expansion": collapse_pkgs,
    "Arkham Horror: Kingsport Horror Expansion": collapse_pkgs,
    "Arkham Horror: Miskatonic Horror Expansion": collapse_pkgs,
    "Arkham Horror: The Black Goat of the Woods Expansion": collapse_pkgs,
    "Arkham Horror: The King in Yellow Expansion": collapse_pkgs,
    "Arkham Horror: The Lurker at the Threshold Expansion": collapse_pkgs,
    "Arkwright": None,
    "Armada: The War With Spain 1585-1604": collapse_pkgs,
    "Armageddon War": collapse_pkgs,
    "Armies of Arcana": collapse_pkgs,
    "Armored Knights North Africa - Operation Crusader": collapse_pkgs,
    "Army of Frogs": collapse_pkgs,
    "Arquebus: Men of Iron Volume IV": None,
    "Arracourt": collapse_pkgs,
    "Arrakhar's Wand": None,
    "Arriala: Canal de Garonne": collapse_pkgs,
    "Arriba Espana!": None,
    "Ars Victor": collapse_pkgs,
    "Artifact": None,
    "Ascari": None,
    "Ascension: Chronicle of the Godslayer": None,
    "Ascension: Return of the Fallen": collapse_pkgs,
    "Ascension: Storm of Souls": collapse_pkgs,
    "Asesinato en el Orient Express": collapse_pkgs,
    "Ashes: Rise of the Phoenixborn": collapse_pkgs,
    "Ashes: Rise of the Phoenixborn – The Children of Blackcloud": collapse_pkgs,
    "Ashes: Rise of the Phoenixborn – The Frostdale Giants": collapse_pkgs,
    "Asia Engulfed": collapse_pkgs,
    "Aspern-Essling": collapse_pkgs,
    "Aspern-Essling 1809": collapse_pkgs,
    "Assault": None,
    "Assault Red Horizon 41": collapse_pkgs,
    "Assault of the Dead: Tactics": None,
    "Assault on Doomrock": collapse_pkgs,
    "Assault on Hoth: The Empire Strikes Back": None,
    "Assault on Mt Everest": None,
    "Assault on Sevastopol": collapse_pkgs,
    "Assault on Tobruk: Rommel Triumphant": collapse_pkgs,
    "Assaut sur Suez": collapse_pkgs,
    "Asteroid": None,
    "Astra Titanus": collapse_pkgs,
    "At Any Cost: Metz 1870": collapse_pkgs,
    "At the Gates of Loyang": collapse_pkgs,
    "Athens & Sparta": collapse_pkgs,
    "Atlanta": collapse_pkgs,
    "Atlanta Is Ours": collapse_pkgs,
    "Atlanta: Civil War Campaign Game": None,
    "Atlantic Chase": collapse_pkgs,
    "Atlantic Sentinels: North Atlantic Convoy Escort, 1942-43": collapse_pkgs,
    "Atlantic Wall: The Invasion of Europe": None,
    "Atlantis Rising": collapse_pkgs,
    "Attack Sub": None,
    "Attack Vector: Tactical": None,
    "Attack in the Ardennes": collapse_pkgs,
    "Attack of the 50 Foot Colossi!": collapse_pkgs,
    "Attack of the Mutants!": None,
    "Au fil de l'epee": None,
    "Aurelian: Restorer of the World": collapse_pkgs,
    "Auspicious Beginning": collapse_pkgs,
    "Austerlitz": collapse_pkgs,
    "Austerlitz 1805": collapse_pkgs,
    "Austerlitz 1805: Rising Eagles": collapse_pkgs,
    "Austerlitz 20": collapse_pkgs,
    "Austerlitz: The Battle of Three Emperors, 2 December 1805": collapse_pkgs,
    "Autumn For Barbarossa": collapse_pkgs,
    "Autumn Of Glory": collapse_pkgs,
    "Avalon Hill Game Company's Game of Trivia": None,
    "Ave Roma": collapse_pkgs,
    "Avec Honneur et Panache: Volume 1 – Turenne": collapse_pkgs,
    "Avec Infini Regret": None,
    "Avec Infini Regret II": collapse_pkgs,
    "Avec Infini Regret III: Moncontour 1569": collapse_pkgs,
    "Aventuras de Naipe": collapse_pkgs,
    "Awesome Little Green Men": None,
    "Axis & Allies": None,
    "Axis & Allies Europe 1940": None,
    "Axis & Allies Miniatures": None,
    "Axis & Allies Naval Miniatures: War at Sea": collapse_pkgs,
    "Axis & Allies Pacific: 1940 Edition": None,
    "Axis & Allies: Battle of the Bulge": None,
    "Axis & Allies: Guadalcanal": None,
    "Azhanti High Lightning": collapse_pkgs,
    "B-17 Queen of the Skies": None,
    "B-25 Prince of the Skies": collapse_pkgs,
    "B-29 Super Fortress": collapse_pkgs,
    "B.C.M. Brigada Criminal Movil (Spanish edition)": collapse_pkgs,
    "BANG!": None,
    "BAOR": collapse_pkgs,
    "Babel": collapse_pkgs,
    "Babylon 5 Collectible Card Game": None,
    "Babylonia": collapse_pkgs,
    "Back to the Future 2&3 Board Game": collapse_pkgs,
    "Backgammon": collapse_pkgs,
    "Bagh Chal": collapse_pkgs,
    "Balance of Powers": collapse_pkgs,
    "Bali": None,
    "Balkan Front": collapse_pkgs,
    "Ball's Bluff": collapse_pkgs,
    "Baltic Gap": None,
    "Bananagrams": collapse_pkgs,
    "Band of Brothers": None,
    "Band of Brothers: Ghost Panzer": collapse_pkgs,
    "Band of Brothers: Texas Arrows": collapse_pkgs,
    "Banditen!": collapse_pkgs,
    "Bang! The Duel": None,
    "Banish the Snakes: A Game of St. Patrick in Ireland": collapse_pkgs,
    "Banzai": collapse_pkgs,
    "Baptism at Bull Run": collapse_pkgs,
    "Baptism by Fire: The Battle of Kasserine": collapse_pkgs,
    "Bar-Lev: The 1973 Arab-Israeli War, Deluxe Edition": collapse_pkgs,
    "Bar-Lev: The Yom-Kippur War of 1973": collapse_pkgs,
    "Baraja Española": collapse_pkgs,
    "Barbarian Kings": collapse_pkgs,
    "Barbarian Prince": None,
    "Barbarian, Kingdom & Empire": collapse_pkgs,
    "Barbarians at the Gates: The Decline and Fall of the Western Roman Empire 337 - 476": collapse_pkgs,
    "Barbarossa: Army Group Center, 1941": collapse_pkgs,
    "Barbarossa: Army Group North, 1941": collapse_pkgs,
    "Barbarossa: Army Group South, 1941": collapse_pkgs,
    "Barbarossa: Crimea": collapse_pkgs,
    "Barbarossa: Game of the Russo-German War 1941-45": None,
    "Barbarossa: Kiev to Rostov, 1941": collapse_pkgs,
    "Barbarossa: The Russo-German War 1941-45": collapse_pkgs,
    "Barefoot to Glory!: Estigarribia's Western Chaco Campaign in 1934": collapse_pkgs,
    "Barren Victory": collapse_pkgs,
    "Barrocco": collapse_pkgs,
    "Basileus": collapse_pkgs,
    "Basileus II": collapse_pkgs,
    "Basilica": collapse_pkgs,
    "Bastogne": collapse_pkgs,
    "Bastogne of Somnium": collapse_pkgs,
    "Bastogne: Screaming Eagles Under Siege": collapse_pkgs,
    "Bataan!": collapse_pkgs,
    "Bataille de Neville's Cross - 1346": collapse_pkgs,
    "Bataille de la Marne 1914": collapse_pkgs,
    "Battle Above the Clouds": collapse_pkgs,
    "Battle Bots": None,
    "Battle Card: Market Garden": collapse_pkgs,
    "Battle Cry": None,
    "Battle Cry!": collapse_pkgs,
    "Battle Cry: 150th Civil War Anniversary Edition": None,
    "Battle For Germany": None,
    "Battle Hymn": None,
    "Battle Hymn Vol.1: Gettysburg and Pea Ridge": None,
    "Battle Line": collapse_pkgs,
    "Battle Masters": None,
    "Battle Platform Antilles": None,
    "Battle Sheep": None,
    "Battle for Biternia": None,
    "Battle for Fallujah: April 2004": None,
    "Battle for Galicia, 1914": collapse_pkgs,
    "Battle for Kursk: The Tigers Are Burning, 1943": collapse_pkgs,
    "Battle for Moscow": None,
    "Battle for Moscow II": None,
    "Battle for Stalingrad": collapse_pkgs,
    "Battle of Honey Springs": None,
    "Battle of Thermopylae": None,
    "Battle of White Plains": collapse_pkgs,
    "Battle of the Bulge": None,
    "Battle of the Bulge - Smithsonian Edition": collapse_pkgs,
    "Battle of the Little Bighorn": collapse_pkgs,
    "Battle of the Ring": None,
    "Battle of the Rosebud": collapse_pkgs,
    "Battle: The Game of Generals": None,
    "BattleCON": None,
    "BattleLore": None,
    "BattleLore (Second Edition)": None,
    "BattleTech": None,
    "BattleTech: Alpha Strike": collapse_pkgs,
    "BattleTech: Domination": None,
    "Battlefields of Olympus": None,
    "Battlefleet Gothic": collapse_pkgs,
    "Battlefleet Mars: Space Combat in the 21st Century": collapse_pkgs,
    "Battleground: Fantasy Warfare": collapse_pkgs,
    "Battles for Prydain: Heroic Combat in Dark Age Britain 450-650 AD": collapse_pkgs,
    "Battles for the Ardennes": None,
    "Battles for the Shenadoah: A Death Valley Expansion": None,
    "Battles in the East 2: Uman Pocket and Guderian's Final Blitzkrieg": collapse_pkgs,
    "Battles of Napoleon: Volume I – EYLAU 1807": collapse_pkgs,
    "Battles of Trenton and Princeton": None,
    "Battles of Westeros": None,
    "Battles of the Ancient World Volume III": None,
    "Battles of the Bulge: Celles": collapse_pkgs,
    "Battles of the Warrior Queen": collapse_pkgs,
    "Battles on the Ice": collapse_pkgs,
    "Battles with the Gringos, Mexico 1846-62": collapse_pkgs,
    "Battles: Medieval": collapse_pkgs,
    "Battles: Western Europe": collapse_pkgs,
    "Battleship / Salvo": None,
    "Battlestar Galactica": None,
    "Battlestar Galactica: Daybreak Expansion": collapse_pkgs,
    "Battlestar Galactica: Exodus Expansion": collapse_pkgs,
    "Battlestar Galactica: Pegasus Expansion": collapse_pkgs,
    "Battlestar Galactica: The Board Game": None,
    "Battlestations": None,
    "Bautzen 1813": collapse_pkgs,
    "Bautzen 1945": collapse_pkgs,
    "Bayonets & Tomahawks": collapse_pkgs,
    "Beda Fomm": collapse_pkgs,
    "Beda Fomm (1979)": collapse_pkgs,
    "BelTrain": None,
    "Belleau Wood": collapse_pkgs,
    "Bellum Gallicum II": collapse_pkgs,
    "Belter: Mining the Asteroids, 2076": None,
    "Beneath the Med: Regia Marina at Sea 1940-1943": collapse_pkgs,
    "Benedict Arnold and the Northern Theater": collapse_pkgs,
    "Berestechko 1651": collapse_pkgs,
    "Berezina 20": collapse_pkgs,
    "Berlin '85: The Enemy at the Gates": collapse_pkgs,
    "Betrayal At House On The Hill": None,
    "Beyond Waterloo": collapse_pkgs,
    "Beyond the Rhine": None,
    "Big Queen": None,
    "Big*Bang": None,
    "Bios: Genesis": collapse_pkgs,
    "Bios: Megafauna": None,
    "Bios: Megafauna (second edition)": collapse_pkgs,
    "Bios: Origins (Second Edition)": collapse_pkgs,
    "Birth of a Legend": collapse_pkgs,
    "Bismarck": None,
    "Bismarck: The Last Battle": collapse_pkgs,
    "Bitter End: Attack to Budapest, 1945": collapse_pkgs,
    "Bitter Woods (4th Edition)": None,
    "Black Death": collapse_pkgs,
    "Black Hole": None,
    "Black Orchestra": collapse_pkgs,
    "Black Sea Black Death": None,
    "Black Swan": collapse_pkgs,
    "Black Wednesday": collapse_pkgs,
    "Blackbeard": collapse_pkgs,
    "Blackbeard: The Golden Age of Piracy": collapse_pkgs,
    "Blackhorse": collapse_pkgs,
    "Blade Runner: Rep-Detect": collapse_pkgs,
    "Blitz! A World in Conflict": None,
    "BlitzKrieg (2ème Edition)": collapse_pkgs,
    "Blitzkrieg": None,
    "Blitzkrieg General (2nd Edition)": None,
    "Blitzkrieg!: World War Two in 20 Minutes": collapse_pkgs,
    "Blockade": None,
    "Blocks in the East": collapse_pkgs,
    "Blood & Roses": None,
    "Blood & Steel": collapse_pkgs,
    "Blood Bowl": collapse_pkgs,
    "Blood Bowl: Team Manager - The Card Game": None,
    "Blood of Noble Men: The Alamo": None,
    "Blood on the Ohio": collapse_pkgs,
    "Bloodstones": collapse_pkgs,
    "Bloody 110": None,
    "Bloody April, 1917: Air War Over Arras, France": collapse_pkgs,
    "Bloody April: The Battle of Shiloh, 1862": collapse_pkgs,
    "Bloody Monday": collapse_pkgs,
    "Bloody Ridge": collapse_pkgs,
    "Bloody Steppes of Crimea: Alma - Balaclava - Inkerman 1854": None,
    "Bloody Tarara (TCS)": collapse_pkgs,
    "Bloqueo": collapse_pkgs,
    "Blox": collapse_pkgs,
    "Blue & Gray II": None,
    "Blue & Gray: Four American Civil War Battles": None,
    "Blue Cross, White Ensign": collapse_pkgs,
    "Blue Max": collapse_pkgs,
    "Blue Moon City": collapse_pkgs,
    "Blue Water Navy": collapse_pkgs,
    "Blue vs. Gray": collapse_pkgs,
    "Board Dominoes": collapse_pkgs,
    "Bobby Lee": None,
    "Bolt Action": None,
    "Bomber": collapse_pkgs,
    "Bomber Boys": collapse_pkgs,
    "Bomber Command": collapse_pkgs,
    "Bonaparte at Marengo": None,
    "Bonaparte in Italy": None,
    "Boom-O": collapse_pkgs,
    "Boots & Saddles": collapse_pkgs,
    "Border Reivers: Anglo-Scottish Border Raids, 1513-1603": collapse_pkgs,
    "Borderlands": collapse_pkgs,
    "Borkowo 1806": collapse_pkgs,
    "Borodino 1812": None,
    "Borodino 20": collapse_pkgs,
    "Borodino: Battle of the Moskova, 1812": collapse_pkgs,
    "Boss Monster: The Dungeon Building Card Game": None,
    "Botifarra": collapse_pkgs,
    "Bowl Bound": collapse_pkgs,
    "Bowl and Score": None,
    "Box of Golf: A Classic Golf Board Game": None,
    "Braccio da Montone": collapse_pkgs,
    "Bradley's D-Day and Monty's D-Day": None,
    "Brandywine": collapse_pkgs,
    "Brandywine & Germantown": None,
    "Brass: Birmingham": None,
    "Brave Little Belgium": collapse_pkgs,
    "Bravery In the Sand": collapse_pkgs,
    "Brazen Chariots: Battles for Tobruk, 1941": collapse_pkgs,
    "Breaking the Chains: War in the South China Sea": None,
    "Breakout & Pursuit: The Battle for France, 1944": collapse_pkgs,
    "Breakout Normandy": None,
    "Breakthrough: Cambrai": collapse_pkgs,
    "Breakthru": None,
    "Breitenfeld": collapse_pkgs,
    "Brezhnev's War: NATO vs. the Warsaw Pact in Germany, 1980": collapse_pkgs,
    "Bridge/Hearts": collapse_pkgs,
    "Brief Border Wars": collapse_pkgs,
    "Brikwars": collapse_pkgs,
    "Briscola": collapse_pkgs,
    "Britain Stands Alone": collapse_pkgs,
    "Britannia": None,
    "Brotherhood & Unity": collapse_pkgs,
    "Brothers at War: 1862": None,
    "Buck Rogers: Battle for the 25th Century": collapse_pkgs,
    "Bug-Eyed Monsters": None,
    "Bulge 20": collapse_pkgs,
    "Bulge: The Battle for the Ardennes 16 Dec. '44-2 Jan. '45": collapse_pkgs,
    "Bull Run": None,
    "Bull Run 1861": collapse_pkgs,
    "Bullet♥︎": collapse_pkgs,
    "Bundeswehr, An Assault Series Module": collapse_pkgs,
    "Bundeswehr: Northern Germany, late 1970's": collapse_pkgs,
    "Burgle Bros.": collapse_pkgs,
    "Burma": None,
    "Burncylce": collapse_pkgs,
    "Burning Banners": collapse_pkgs,
    "Burning Mountains": collapse_pkgs,
    "Burning Suns": collapse_pkgs,
    "Burnside Takes Command": None,
    "Bussaco 20": collapse_pkgs,
    "By Iron and Blood": collapse_pkgs,
    "Byzantium": collapse_pkgs,
    "C.V.: A game of the Battle of Midway": collapse_pkgs,
    "CEP: Combate en el Espacio Profundo": collapse_pkgs,
    "CLAG": collapse_pkgs,
    "Cacao": None,
    "Caeris": collapse_pkgs,
    "Caesar Imperator: Britannia": collapse_pkgs,
    "Caesar XL": collapse_pkgs,
    "Caesar in Alexandria": None,
    "Caesar's Gallic War": collapse_pkgs,
    "Caesar's Legions": collapse_pkgs,
    "Caesar: Conquest of Gaul": None,
    "Caesar: Epic Battle of Alesia": None,
    "Caesar: Rome vs Gaul": collapse_pkgs,
    "Camelot": None,
    "Campaign Commander Volume I: Roads to Stalingrad": collapse_pkgs,
    "Campaign Commander Volume II: Coral Sea": collapse_pkgs,
    "Campaign Commander Volume III: Punic Island": collapse_pkgs,
    "Campaign of Nations": collapse_pkgs,
    "Campaign to Stalingrad: Southern Russia 1942": None,
    "Canadian Civil War: La Guerre de la Sécession du Canada": collapse_pkgs,
    "Canadian Crucible: Brigade Fortress at Norrey": None,
    "Candidate": collapse_pkgs,
    "Cannonball Colony": None,
    "Canope 1801": collapse_pkgs,
    "Capone Says": collapse_pkgs,
    "Captain Park's Imaginary Polar Expedition": collapse_pkgs,
    "Captain's Sea": collapse_pkgs,
    "Car Wars": collapse_pkgs,
    "Car Wars Compendium": collapse_pkgs,
    "Car Wars Deluxe Edition": None,
    "Carcassonne": None,
    "Carcassonne: Hunters and Gatherers": None,
    "Carcassonne: The Castle": None,
    "Carcassonne: The Discovery": None,
    "Cards Against Humanity": None,
    "Caricat!": collapse_pkgs,
    "Carolingi": collapse_pkgs,
    "Carrier": collapse_pkgs,
    "Carrier Battle: Philippine Sea": collapse_pkgs,
    "Carson City": collapse_pkgs,
    "Carthage: The First Punic War": collapse_pkgs,
    "Cartographers: A Roll Player Tale": collapse_pkgs,
    "Case Blue / Guderian's Blitzkrieg II": None,
    "Case Geld: The Axis Invasion of North America, 1945-46": collapse_pkgs,
    "Case Yellow, 1940: The German Blitzkrieg in the West": None,
    "Cassino 1944": collapse_pkgs,
    "Cassino 44": collapse_pkgs,
    "Castaways": None,
    "Castle Panic": collapse_pkgs,
    "Cataclysm: A Second World War": None,
    "Cataphract / Attila": None,
    "Cave Evil": collapse_pkgs,
    "Caza-Tesoros": collapse_pkgs,
    "Cedar Creek 1864": collapse_pkgs,
    "Cedar Mountain 1862": collapse_pkgs,
    "Cedar Mountain: The Prelude to Bull Run, August 9, 1862": collapse_pkgs,
    "Central America": collapse_pkgs,
    "Central Front Series": None,
    "Cerebria: The Inside World": None,
    "Chabyrinthe": collapse_pkgs,
    "Chaco": None,
    "Chainsaw Warrior": collapse_pkgs,
    "Champion Hill": collapse_pkgs,
    "Championship Formula Racing": collapse_pkgs,
    "Champs de Bataille": None,
    "Chancellorsville (Second Edition)": collapse_pkgs,
    "Chancellorsville: Bloody May, 1863": collapse_pkgs,
    "Chandragupta": collapse_pkgs,
    "Chaos in the Old World": collapse_pkgs,
    "Chaostle": None,
    "Charioteer": collapse_pkgs,
    "Chariots of Fire": collapse_pkgs,
    "Charlemagne, Master of Europe": collapse_pkgs,
    "Cheese Chasers": collapse_pkgs,
    "Cherburg of Somnium": collapse_pkgs,
    "Chess 'n' Checkers": None,
    "Chesscalation": None,
    "Chicago Express": collapse_pkgs,
    "Chicago, Chicago!": collapse_pkgs,
    "Chickamauga: Bloody September, 1863": collapse_pkgs,
    "Chickamauga: The Confederacy's Last Hope": collapse_pkgs,
    "Chickasaw Bayou: The Battle of Walnut Hills, December 26-29, 1862": collapse_pkgs,
    "Chieftain, An Assault Series Module": collapse_pkgs,
    "Chinese Farm: Egyptian-Israeli Combat in the '73 War": collapse_pkgs,
    "Chitin: I": None,
    "Chocolatl": collapse_pkgs,
    "Chronicles of Frost": collapse_pkgs,
    "Chrononauts": collapse_pkgs,
    "Chu Shogi": collapse_pkgs,
    "Chunky Fighters": collapse_pkgs,
    "Churchill": collapse_pkgs,
    "Circadians: Chaos Order": collapse_pkgs,
    "Circle of Fire: The Siege of Cholm, 1942": collapse_pkgs,
    "Circus Maximus": None,
    "Citadel of Blood": None,
    "Citadel: The Battle of Dien Bien Phu": None,
    "Citadels": None,
    "City of Guilds": collapse_pkgs,
    "Cityfight: Modern Combat in the Urban Environment": collapse_pkgs,
    "Cité": collapse_pkgs,
    "Civil War": None,
    "Civil War Game 1863": collapse_pkgs,
    "Civilization: A New Dawn": collapse_pkgs,
    "Clash for a Continent": None,
    "Clash of Carriers": collapse_pkgs,
    "Clash of Cultures": collapse_pkgs,
    "Clash of Giants II": None,
    "Clash of Giants: Campaigns of Tannenberg and the Marne, 1914": collapse_pkgs,
    "Clash of Giants: Civil War": collapse_pkgs,
    "Clash of Monarchs": collapse_pkgs,
    "Clash of Sovereigns: The War of the Austrian Succession, 1740-48": None,
    "Clash of Wills: Shiloh 1862": collapse_pkgs,
    "Claustrophobia": collapse_pkgs,
    "Climate change – the board game": collapse_pkgs,
    "Clixers": None,
    "Clontarf": collapse_pkgs,
    "Close Action": None,
    "Close Assault": None,
    "Cloudspire": collapse_pkgs,
    "Cluedo": None,
    "Coalition: The Napoleonic Wars, 1805-1815": collapse_pkgs,
    "Cobra: Game of the Normandy Breakout": None,
    "Codenames": collapse_pkgs,
    "Codeword Cromwell: The German Invasion of England, 8 June 1940": collapse_pkgs,
    "Codex: Card-Time Strategy": None,
    "Cold War Naval Battles": None,
    "Colmar 1945": collapse_pkgs,
    "Colonial Diplomacy": collapse_pkgs,
    "Colonial Space Wars": collapse_pkgs,
    "Colonial Twilight: The French-Algerian War, 1954-62": collapse_pkgs,
    "Color Warz:Paint Brawl": collapse_pkgs,
    "Comancheria": collapse_pkgs,
    "Combat Command": None,
    "Combat Commander Tournament Battle Pack": collapse_pkgs,
    "Combat Commander: Battle Pack 1 - Paratroopers": collapse_pkgs,
    "Combat Commander: Battle Pack 2 - Stalingrad": collapse_pkgs,
    "Combat Commander: Battle Pack 3 - Normandy": collapse_pkgs,
    "Combat Commander: Battle Pack 4 - New Guinea": collapse_pkgs,
    "Combat Commander: Battle Pack 5 - The Fall of the West": collapse_pkgs,
    "Combat Commander: Battle Pack 6 - Operation Sea Lion": collapse_pkgs,
    "Combat Commander: Europe": None,
    "Combat Commander: Mediterranean": collapse_pkgs,
    "Combat Commander: Pacific": None,
    "Combat Commander: Resistance": collapse_pkgs,
    "Combat Infantry": None,
    "Combat Leader: East Front '41": collapse_pkgs,
    "Combat!": None,
    "Combat! Volume 2: An Expansion for Combat!": None,
    "Commando 4 en action : Dieppe 1942": collapse_pkgs,
    "Commands & Colors Ancients": None,
    "Commands & Colors Tricorne: Jacobite Rising": collapse_pkgs,
    "Commands & Colors Tricorne: The American Revolution": collapse_pkgs,
    "Commands & Colors: Medieval": None,
    "Commands & Colors: Napoleonics": None,
    "Commands & Colors: Napoleonics Exp 6: EPIC Napoleonics": collapse_pkgs,
    "Commands & Colors: Samurai Battles": None,
    "Commodore": collapse_pkgs,
    "Conan": collapse_pkgs,
    "Condottiere": None,
    "Confederate Rails: Railroading in the American Civil War 1861-1865": collapse_pkgs,
    "Conflict": collapse_pkgs,
    "Conflict of Heroes: Awakening the Bear! Russia 1941-1942": None,
    "Conflict of Heroes: Storms of Steel! Kursk 1943": None,
    "Congo Merc: The Congo, 1964": collapse_pkgs,
    "Conquerors": collapse_pkgs,
    "Conquest": collapse_pkgs,
    "Conquest & Consequences": None,
    "Conquest of Paradise": collapse_pkgs,
    "Conquest of the Empire": None,
    "Conquest of the Empire: Imperator": collapse_pkgs,
    "Conquistador": collapse_pkgs,
    "Conquistador: The Age of Exploration": collapse_pkgs,
    "Consequential": collapse_pkgs,
    "Container": collapse_pkgs,
    "Contractors": None,
    "Corbach 1760": collapse_pkgs,
    "Core": collapse_pkgs,
    "Core Worlds": collapse_pkgs,
    "Corps Command: Dawn's Early Light": collapse_pkgs,
    "Corps Command: Totensonntag": collapse_pkgs,
    "Corsairs and Hellcats": collapse_pkgs,
    "Cortes et la conquête du Mexique 1519-1521": collapse_pkgs,
    "Cortes: Conquest of the Aztec Empire": collapse_pkgs,
    "Corvette Command": collapse_pkgs,
    "Corée 1950": collapse_pkgs,
    "Cosmic Encounter": collapse_pkgs,
    "Cosmic Encounter (2008)": collapse_pkgs,
    "Cosmic frog": collapse_pkgs,
    "Counter-Attack! Arras": collapse_pkgs,
    "Counter-Attack: The Battle of Arras, 1940": collapse_pkgs,
    "Coup": collapse_pkgs,
    "Cradle of Civilization": collapse_pkgs,
    "Crash Tackle": None,
    "Credo": collapse_pkgs,
    "Crescendo of Doom": collapse_pkgs,
    "Crescent City Cargo": collapse_pkgs,
    "Crimea: Conquest & Liberation": collapse_pkgs,
    "Crimean War Battles": None,
    "Cripmaquion": None,
    "Crisis 2020": collapse_pkgs,
    "Crisis: Sinai 1973": collapse_pkgs,
    "Critical Collapse": collapse_pkgs,
    "Cromwell": collapse_pkgs,
    "Cross of Iron": collapse_pkgs,
    "Crossbows and Cannon": None,
    "Crosshairs": collapse_pkgs,
    "Crossing the Line: Aachen 1944": collapse_pkgs,
    "Crowbar! The Rangers at Pointe du Hoc, June 6th 1944": collapse_pkgs,
    "Crown of Roses": collapse_pkgs,
    "Crusade and Revolution: The Spanish Civil War, 1936-1939": None,
    "Crusader": collapse_pkgs,
    "Crusader Kingdoms: The War for the Holy Land": collapse_pkgs,
    "Crusader Rex": collapse_pkgs,
    "Cry Havoc": None,
    "Cthulhu Dice": collapse_pkgs,
    "Cthulhu Wars": collapse_pkgs,
    "Cuba Libre": collapse_pkgs,
    "Cudgel Duel: Franco's first counterstrikes at the Ebro, Aug-Sep 1938": collapse_pkgs,
    "D'Overlord à Berlin": collapse_pkgs,
    "D-Day": None,
    "D-Day - Smithsonian Edition": None,
    "D-Day Dice": None,
    "D-Day and Beyond": collapse_pkgs,
    "D-Day at Omaha Beach": None,
    "DAK2": None,
    "DC Comics Dice Masters: Justice League": collapse_pkgs,
    "DC Comics Dice Masters: War of Light": collapse_pkgs,
    "DLG Napoleonic": collapse_pkgs,
    "DMZ: The Battle for South Korea, late 1970s": collapse_pkgs,
    "DNPS": collapse_pkgs,
    "DSE - Decisive Operations": collapse_pkgs,
    "DSE - Force on Force": collapse_pkgs,
    "DSE - Lines & Webs": collapse_pkgs,
    "DSE - Motorcade Showdown": None,
    "DSE-Death Can Wait": collapse_pkgs,
    "DSE-Hell Over the Horizon": None,
    "DSE-Quebec 1759": None,
    "DSE:Kazhdyy Gorod": None,
    "Damocles Mission": None,
    "Dante's Inferno": None,
    "Dark Cults": collapse_pkgs,
    "Dark Emperor": None,
    "Dark Moon": collapse_pkgs,
    "Dark Nebula": collapse_pkgs,
    "Das Boot: Der deutsche U-Bootkrieg, 1939-1943": collapse_pkgs,
    "Das Phantom": collapse_pkgs,
    "Dauntless": collapse_pkgs,
    "Dawn Patrol: Role Playing Game of WW I Air Combat": None,
    "Dawn of Empire: The Spanish American Naval War in the Atlantic, 1898": collapse_pkgs,
    "Dawn of the Dead": collapse_pkgs,
    "Dawn of the Zeds (Third edition)": collapse_pkgs,
    "Dawn's Early Light: The War of 1812": collapse_pkgs,
    "Day of Days: The Invasion of Normandy 1944": collapse_pkgs,
    "De Bellis Magistrorum Militum": collapse_pkgs,
    "De Bellis Vassalus": collapse_pkgs,
    "De Sang & de Tourbe": collapse_pkgs,
    "Dead of Night": collapse_pkgs,
    "Dead of Winter": collapse_pkgs,
    "Dead of Winter: A Crossroads Game": collapse_pkgs,
    "Deadlands:Doomtown": collapse_pkgs,
    "Death Ride - Hafid Ridge": None,
    "Death Ride Kursk: 11th Panzer": collapse_pkgs,
    "Death Ride Kursk: Gross Deutschland": None,
    "Death Ride Kursk: Totenkopf": collapse_pkgs,
    "Death Ride Normandy: Point du Hoc": collapse_pkgs,
    "Death Ride Salerno: 16th Panzer": collapse_pkgs,
    "Death Ride: Arras": collapse_pkgs,
    "Death Valley: Battles for the Shenandoah": None,
    "Death in the Trenches: The Great War 1914-1918 (Second Edition)": collapse_pkgs,
    "Death in the Trenches: The Great War, 1914-1918": collapse_pkgs,
    "Death of an Army: Ypres 1914": collapse_pkgs,
    "DeathMaze": None,
    "Debrecen 1944: Orages à l'Est 2 Hongrie": collapse_pkgs,
    "Decision at Kasserine: Rommel's Last Chance – Designer Signature Edition": collapse_pkgs,
    "Decision in France": collapse_pkgs,
    "Decisive Victory 1918: Volume One – Soissons": collapse_pkgs,
    "Decktet-Dectana-Gnostica": collapse_pkgs,
    "Deep Space D-6": collapse_pkgs,
    "Defending America: Intercepting the Amerika Bombers, 1947-48": collapse_pkgs,
    "Defiant Russia: Operation Barbarossa, 1941": collapse_pkgs,
    "Dejarik": None,
    "Delve the Card Game": collapse_pkgs,
    "Delve: The Dice Game": collapse_pkgs,
    "Demon's Run": None,
    "Demonlord": collapse_pkgs,
    "Demons": None,
    "Demyansk Shield: the Frozen Fortress, February-May 1942": collapse_pkgs,
    "Dennewitz 20": collapse_pkgs,
    "Derelicts of Sin: Heresy": collapse_pkgs,
    "Descent on Crete: May 1941": collapse_pkgs,
    "Desert Fox Deluxe": collapse_pkgs,
    "Desert Rats": None,
    "Desert Victory: North Africa, 1940-1942": collapse_pkgs,
    "Desert War": collapse_pkgs,
    "Desert War: Tactical Warfare in North Africa": collapse_pkgs,
    "Destruction of Army Group Center: The Soviet Summer Offensive": collapse_pkgs,
    "Devil Boats: PT Boats in the Solomons": collapse_pkgs,
    "Devil's Horsemen": None,
    "Dice Masters Draft": collapse_pkgs,
    "DiceWar: Light of Dragons": collapse_pkgs,
    "Die Macher": collapse_pkgs,
    "Dien Bien Phu: The Final Gamble": None,
    "Dig": None,
    "Dig Down Dwarf": collapse_pkgs,
    "Dimension Demons": None,
    "Dinosaurs of the Lost World": collapse_pkgs,
    "Diplomacy": collapse_pkgs,
    "Dire Heroes: Gas Attack at Ypres": collapse_pkgs,
    "District Commander Binh Dinh": collapse_pkgs,
    "District Commander Kandahar": collapse_pkgs,
    "District Commander Maracas: Virtualia 2019": collapse_pkgs,
    "District Commander: ZNO": collapse_pkgs,
    "Divided America: The Next Civil war": collapse_pkgs,
    "Divine Right": None,
    "Dix-huit lapins": collapse_pkgs,
    "Dixie: The Second War Between the States": collapse_pkgs,
    "Dixit": None,
    "Dogfight": collapse_pkgs,
    "Dogfight Deluxe": collapse_pkgs,
    "Dominant Species": None,
    "Dominant Species: Marine": collapse_pkgs,
    "Dominion": None,
    "Dominion: Alchemy": collapse_pkgs,
    "Dominion: Intrigue": collapse_pkgs,
    "Dominion: Prosperity": collapse_pkgs,
    "Dominion: Seaside": collapse_pkgs,
    "Dominoes": collapse_pkgs,
    "Donau Front": collapse_pkgs,
    "Donnerschlag: Escape from Stalingrad": collapse_pkgs,
    "Door2Door": None,
    "Double-Play Baseball": None,
    "Downfall of Empires": collapse_pkgs,
    "Downfall of the Third Reich": collapse_pkgs,
    "Downfall: Conquest of the Third Reich, 1942-1945": collapse_pkgs,
    "Downtown: Air War Over Hanoi, 1965 - 1972": None,
    "Dragon Dice": None,
    "Dragon Pass": None,
    "Dragonlance": collapse_pkgs,
    "Dragonriders of Pern": collapse_pkgs,
    "Dragons of Glory": collapse_pkgs,
    "Drang Nach Osten!": collapse_pkgs,
    "DreadBall (Second Edition)": collapse_pkgs,
    "Dreadball": collapse_pkgs,
    "Dreadnought: Surface Combat in the Battleship Era, 1906-45": collapse_pkgs,
    "Dreamblade": None,
    "Dresden 20": collapse_pkgs,
    "Drive on Kursk: July 1943": collapse_pkgs,
    "Drive on Paris": collapse_pkgs,
    "Drive on Stalingrad: Battle for Southern Russia Game": collapse_pkgs,
    "Drive on Washington: The Battle of Monocacy Junction, July 9, 1864": None,
    "Dropfleet Commander": collapse_pkgs,
    "Druid: Boudicca's Rebellion, 61 A.D.": collapse_pkgs,
    "Duel for Kharkov": collapse_pkgs,
    "Duel in the Desert": None,
    "Duel of Ages II": collapse_pkgs,
    "Dune": None,
    "Dune Adventure Game": None,
    "Dune Express": collapse_pkgs,
    "Dune: War for Arrakis": None,
    "Dungeon": None,
    "Dungeon Alliance": collapse_pkgs,
    "Dungeon Command": collapse_pkgs,
    "Dungeon Command: Blood of Gruumsh": collapse_pkgs,
    "Dungeon Command: Curse of Undeath": collapse_pkgs,
    "Dungeon Command: Heart of Cormyr": collapse_pkgs,
    "Dungeon Command: Sting of Lolth": collapse_pkgs,
    "Dungeon Command: Tyranny of Goblins": collapse_pkgs,
    "Dungeon Crawler": None,
    "Dungeon Plungin'": None,
    "Dungeon Run": None,
    "Dungeon Twister": collapse_pkgs,
    "Dungeon Universalis": None,
    "Dungeoneer: Tomb of the Lich Lord": None,
    "Dungeonquest": collapse_pkgs,
    "Dungeons & Dragons Dice Masters: Battle for Faerûn": collapse_pkgs,
    "Dungeons & Dragons Miniatures": None,
    "Dungeons & Dragons: Attack Wing": collapse_pkgs,
    "Dungeons & Dragons: The Fantasy Adventure Board Game": collapse_pkgs,
    "Dunkerque: 1940": None,
    "Durchbruch: The Austro-German attack at Caporetto": collapse_pkgs,
    "Durrenstein & Schongraben 1805": collapse_pkgs,
    "Dust Halo": None,
    "Dynamo: Dunkirk, 1940": collapse_pkgs,
    "Dynasty": collapse_pkgs,
    "Débâcle": collapse_pkgs,
    "Déluges": collapse_pkgs,
    "EOKA": collapse_pkgs,
    "Eagles of the Empire: Spanish Eagles": collapse_pkgs,
    "Earth Reborn": collapse_pkgs,
    "East Prussian Carnage": collapse_pkgs,
    "EastFront: The War in Russia, 1941-45": collapse_pkgs,
    "Eastern Front Solitaire": None,
    "Eastern Front Tank Leader": collapse_pkgs,
    "Ebb & Flow: The Final Communist Offensive in Korea, 22 April-10 June 1951": collapse_pkgs,
    "Eclipse": None,
    "Edelweiss: The Struggle in the Caucasus July - November 1942": collapse_pkgs,
    "Eighth Air Force": collapse_pkgs,
    "Ekö": collapse_pkgs,
    "El Alamein of Somnium": collapse_pkgs,
    "El Alamein: Battles in North Africa, 1942": None,
    "El Grande": collapse_pkgs,
    "Elder Sign": None,
    "Eldritch Horror": None,
    "Element:Silver": collapse_pkgs,
    "Elemental Clash": None,
    "Elfball": None,
    "Elo Darkness": collapse_pkgs,
    "Elric: Battle at the End of Time": collapse_pkgs,
    "Elusive Victory": collapse_pkgs,
    "Embrace An Angry Wind": collapse_pkgs,
    "Eminent Domain": None,
    "Emperor of China": collapse_pkgs,
    "Empire at Sunrise": collapse_pkgs,
    "Empire of the Rising Sun": collapse_pkgs,
    "Empire of the Sun": None,
    "Empires & Alliances": collapse_pkgs,
    "Empires in Arms": None,
    "Empires of the Middle Ages": None,
    "Empires of the void": collapse_pkgs,
    "Empires: Rise and Fall": None,
    "En Busca Del Imperio Cobra": collapse_pkgs,
    "En Garde": collapse_pkgs,
    "En Pointe Toujours!": None,
    "End of Empire: 1744-1782": collapse_pkgs,
    "End of the Iron Dream": None,
    "Endangered": collapse_pkgs,
    "Enemy Action: Kharkov": None,
    "Enemy Action:Ardennes": collapse_pkgs,
    "Enemy Coast Ahead: The Dambuster Raid": collapse_pkgs,
    "Enemy Coast Ahead: The Doolittle Raid": None,
    "Enemy at the Gates": None,
    "Enigma Machine I": collapse_pkgs,
    "Epaminondas": None,
    "Epic": collapse_pkgs,
    "Epic (Unpublished)": None,
    "Epic of the Peloponnesian War": collapse_pkgs,
    "Epées Normandes": None,
    "Epées Royales": collapse_pkgs,
    "Epées et Hallebardes 1315-1476": None,
    "Epées et croisades": None,
    "Epées souveraines : Bouvines 1214 - Worringen 1288": None,
    "Equatorial Clash": collapse_pkgs,
    "Eriantys": collapse_pkgs,
    "Escape From Colditz": None,
    "Escape from Altassar": collapse_pkgs,
    "Escape from Hades": collapse_pkgs,
    "España 1936": collapse_pkgs,
    "Espinosa": None,
    "EuroFront II": collapse_pkgs,
    "Europa Austria 38": collapse_pkgs,
    "Europa Czech 38": collapse_pkgs,
    "Europe Engulfed": collapse_pkgs,
    "Europe in Turmoil II: The Interbellum Years 1920-1939": collapse_pkgs,
    "Europe in Turmoil: Prelude to the Great War": collapse_pkgs,
    "Eurydice & Orpheus": collapse_pkgs,
    "Euthia: Torment of Resurrection": collapse_pkgs,
    "Everything vs. Everything": collapse_pkgs,
    "Exago": collapse_pkgs,
    "Excalibur": collapse_pkgs,
    "Excalibur (NAC)": None,
    "Executive Decision": collapse_pkgs,
    "Exile Sun": None,
    "Explorers & Exploiters": collapse_pkgs,
    "Explorers of the Lost World": collapse_pkgs,
    "Eylau 1807": collapse_pkgs,
    "FAB: Golan '73": collapse_pkgs,
    "FAB: Sicily": collapse_pkgs,
    "FAB: The Bulge": collapse_pkgs,
    "FNG": collapse_pkgs,
    "Fair Catch": None,
    "Fall Blau: Army Group South, June-December 1942": None,
    "Fall Of The Third Reich": collapse_pkgs,
    "Fall of Lumen": collapse_pkgs,
    "Falling Sky: The Gallic Revolt Against Caesar": collapse_pkgs,
    "Fallschirmjaeger": collapse_pkgs,
    "Family Business": None,
    "Fatal Alliances III Dreadnoughts in Flames": None,
    "Fatal Alliances: The Great War": collapse_pkgs,
    "Federation & Empire": collapse_pkgs,
    "Federation Space": collapse_pkgs,
    "Feilong": None,
    "Feldgrau": collapse_pkgs,
    "Festung Europa: The Campaign for Western Europe, 1943-1945": collapse_pkgs,
    "Feudal": None,
    "Feudal Lord": collapse_pkgs,
    "Feudum": collapse_pkgs,
    "Field Commander: Alexander": collapse_pkgs,
    "Field Commander: Rommel": collapse_pkgs,
    "Fields of Despair: France 1914-1918": collapse_pkgs,
    "Fields of Fire": collapse_pkgs,
    "Fifth Corps": collapse_pkgs,
    "Fifth Frontier War": collapse_pkgs,
    "Fighter Duel": collapse_pkgs,
    "Fighter Duel Lite": collapse_pkgs,
    "Fighters of the Pacific": None,
    "Fighting Formations: Grossdeutschland Motorized Infantry Division": None,
    "Fighting Sail": None,
    "Fighting Wings": collapse_pkgs,
    "Fire & Stone: Siege of Vienna 1683": collapse_pkgs,
    "Fire As She Bears!: Rules for Naval Combat in the Age of FIghting Sail (Second Edition)": collapse_pkgs,
    "Fire In The Lake": collapse_pkgs,
    "Fire In The Sky": collapse_pkgs,
    "Fire in the East": None,
    "Fire on the Mountain: Battle of South Mountain September 14, 1862": collapse_pkgs,
    "Fireball Forward!": None,
    "Fireball Island": collapse_pkgs,
    "Firebirds: Gunship (UH-1C)": collapse_pkgs,
    "Firebirds: Huey": collapse_pkgs,
    "Firebirds: Huey (OH-6A)": collapse_pkgs,
    "Firefight": collapse_pkgs,
    "Firefight: Modern U.S. and Soviet Small Unit Tactics": collapse_pkgs,
    "Firepower": None,
    "First Blood: The Guadalcanal Campaign": None,
    "First Bull Run: 150th Anniversary Edition": collapse_pkgs,
    "First Team: Vietnam": None,
    "First Victories: Wellington versus Napoleon": None,
    "First to Fight": collapse_pkgs,
    "Fitna: The Global War in the Middle East": collapse_pkgs,
    "Five Tribes": collapse_pkgs,
    "Flashpoint South China Sea": collapse_pkgs,
    "Flashpoint: Golan": collapse_pkgs,
    "Flashpoint: Venezuela": collapse_pkgs,
    "Flat Top": None,
    "Fleet 2025: East China Sea": collapse_pkgs,
    "Fleurus 1794": collapse_pkgs,
    "Flight Leader": None,
    "Flight of the Intruder": collapse_pkgs,
    "Flintlock: Black Powder, Cold Steel - Volume I: Carolina Rebels": collapse_pkgs,
    "Flying Circus: Tactical Aerial Combat, 1915-1918": collapse_pkgs,
    "Flying Colors": None,
    "Folklore Board Game": collapse_pkgs,
    "Food Fight": None,
    "For Honor and Glory: War of 1812 Land and Naval Battles": None,
    "For King and Parliament": collapse_pkgs,
    "For Whom the Bell Tolls": collapse_pkgs,
    "For the People": collapse_pkgs,
    "For the Win": collapse_pkgs,
    "Forbidden Stars": None,
    "Forged in Fire": collapse_pkgs,
    "Forgotten Legions": None,
    "Formula 1": collapse_pkgs,
    "Formula De": None,
    "Fort Sumter: The Secession Crisis, 1860-61": collapse_pkgs,
    "Fortress America": collapse_pkgs,
    "Fortress Berlin": None,
    "Fortress Europa": None,
    "Fortress Rhodesia": collapse_pkgs,
    "Fou Fou Fou": collapse_pkgs,
    "Four Battles in North Africa": None,
    "Four Battles of Army Group South": None,
    "Four Lost Battles": collapse_pkgs,
    "France '40": collapse_pkgs,
    "France '40: 2nd Edition": collapse_pkgs,
    "France 1940": None,
    "France 1944: The Allied Crusade in Europe": collapse_pkgs,
    "France 1944: The Allied Crusade in Europe – Designer Signature Edition": collapse_pkgs,
    "Frederick the Great": None,
    "Frederick's Gamble: The Seven Years War": None,
    "Free At Last": collapse_pkgs,
    "Free at Last": collapse_pkgs,
    "Free at Last Draft Rules Version 2022": None,
    "Freedom in The Galaxy": None,
    "Friday": collapse_pkgs,
    "Friedland 1807": collapse_pkgs,
    "Friedrich": None,
    "Frigate: Sea War in the Age of Sail": collapse_pkgs,
    "From One War To Another": collapse_pkgs,
    "From Salerno to Rome: World War II – The Italian Campaign, 1943-1944": collapse_pkgs,
    "Frondeurs et Frondeuses": collapse_pkgs,
    "Front Toward Enemy": collapse_pkgs,
    "Frontier Wars": collapse_pkgs,
    "Frosthaven": None,
    "Fuentes de Onoro 1811": collapse_pkgs,
    "Fulda Gap: The First Battle of the Next War": collapse_pkgs,
    "Full Metal Planete": collapse_pkgs,
    "Full Thrust": collapse_pkgs,
    "Furor Barbarus": collapse_pkgs,
    "Fury in the East": collapse_pkgs,
    "Fury in the West": collapse_pkgs,
    "Futbol Extraño": collapse_pkgs,
    "Féodalité": None,
    "G.I. Joe TCG": None,
    "GBoH Interactive Map": collapse_pkgs,
    "GD '40": collapse_pkgs,
    "GD '41": collapse_pkgs,
    "GD '42": None,
    "GI: Anvil of Victory": collapse_pkgs,
    "GMT East Front Series Volume I": None,
    "GMT East Front Series Volume II": None,
    "GTS: The Greatest Day": collapse_pkgs,
    "Gaines Mill": collapse_pkgs,
    "Galactic Adventures": None,
    "Galactic Emperor": None,
    "Galaxy of D": collapse_pkgs,
    "Galleys & Galleons": collapse_pkgs,
    "Gallipoli": None,
    "Gallipoli, 1915: Churchill's Greatest Gamble": collapse_pkgs,
    "GameTable15": None,
    "Game of Drones": collapse_pkgs,
    "Gandhi: The Decolonization of British India, 1917 – 1947": None,
    "Gangsters": collapse_pkgs,
    "Gaslands: Post-Apocalyptic Vehicular Combat": collapse_pkgs,
    "Gathering Storm": collapse_pkgs,
    "Gazala": collapse_pkgs,
    "Gazala of Somnium": collapse_pkgs,
    "Gazala: The Cauldron": collapse_pkgs,
    "Gears of War: The Board Game": None,
    "Genesis: The Bronze Age": collapse_pkgs,
    "Gentes": collapse_pkgs,
    "Geocronos": None,
    "Gergovie": collapse_pkgs,
    "German Fleet Boats": collapse_pkgs,
    "Germania": collapse_pkgs,
    "Germania: Drusus' Campaigns 12-9 BC": None,
    "Germantown 1777": collapse_pkgs,
    "Get to the Chopper!!!": None,
    "Gettysburg": collapse_pkgs,
    "Gettysburg (1977 Edition)": None,
    "Gettysburg (2010)": collapse_pkgs,
    "Gettysburg (2018)": collapse_pkgs,
    "Gettysburg 150": collapse_pkgs,
    "Gettysburg 1863": collapse_pkgs,
    "Gettysburg: 125th Anniversary Edition": None,
    "Gettysburg: A Time for Heroes": collapse_pkgs,
    "Gettysburg: Badges of Courage": None,
    "Gettysburg: Bloody July, 1863": collapse_pkgs,
    "Gettysburg: Lee's Greatest Gamble": collapse_pkgs,
    "Ghost Stories": collapse_pkgs,
    "Ghost Stories: B-Rice Lee": collapse_pkgs,
    "Ghost Stories: Chuck No-Rice": collapse_pkgs,
    "Ghost Stories: Jean-Claude Van Rice": collapse_pkgs,
    "Ghost Stories: The Guardhouse Expansion": collapse_pkgs,
    "Ghost Stories: The Village People Expansion": collapse_pkgs,
    "Ghost Stories: White Moon": collapse_pkgs,
    "Ginkgopolis": collapse_pkgs,
    "Give Us Victories": collapse_pkgs,
    "Gizmology": collapse_pkgs,
    "Gladiator": None,
    "Glider-Pit Gladiators": None,
    "Global War": None,
    "Global War: The War Against Germany and Japan, 1939-45": collapse_pkgs,
    "Gloomhaven": None,
    "Gloomhaven: Jaws of the Lion": None,
    "Gloomholdin'": collapse_pkgs,
    "Glory": collapse_pkgs,
    "Glory II: Across the Rappahannock": collapse_pkgs,
    "Glory III": collapse_pkgs,
    "Glory Recalled: Hong Kong 1941": collapse_pkgs,
    "Glory to Rome": collapse_pkgs,
    "Gnadenlos!": collapse_pkgs,
    "Go": collapse_pkgs,
    "Go For The Green": None,
    "Goblin": collapse_pkgs,
    "God's Playground": collapse_pkgs,
    "Godtear": collapse_pkgs,
    "Golan: Syrian-Israeli Combat in the '73 War": collapse_pkgs,
    "Goose Green": collapse_pkgs,
    "Gorizia 1916: La sesta battaglia dell'Isonzo": collapse_pkgs,
    "Gosix": None,
    "Gospitch & Ocaña 1809": None,
    "Gosu": collapse_pkgs,
    "Gothic Invasion": collapse_pkgs,
    "Granada: Last Stand of the Moors – 1482-1492": collapse_pkgs,
    "Grand Conquest": collapse_pkgs,
    "Grand Fleet": None,
    "Grand Prix": collapse_pkgs,
    "Grand Siécle": collapse_pkgs,
    "Grant Takes Command": None,
    "Grant's Gamble": collapse_pkgs,
    "Grav Armor": None,
    "Great Battles of Alexander: Deluxe Edition": None,
    "Great Battles of Julius Caesar: Deluxe Edition": None,
    "Great Battles of Julius Caesar: The Civil Wars 48-45 B.C.": collapse_pkgs,
    "Great Medieval Battles: Four Battles from the Middle Ages": None,
    "Great War Commander": collapse_pkgs,
    "Greek Dark Age": None,
    "Greenland": None,
    "Grenadier: Tactical Warfare 1680-1850": collapse_pkgs,
    "Gringo!": None,
    "Grossbeeren 20": collapse_pkgs,
    "Growling Tigers : The Battle for Changde, 1943": collapse_pkgs,
    "Grunwald 1410": collapse_pkgs,
    "Guadalajara": collapse_pkgs,
    "Guadalcanal": None,
    "Guadalcanal of Somnium": collapse_pkgs,
    "Guam: Return to Glory": collapse_pkgs,
    "Guardians": collapse_pkgs,
    "Guderian's Blitzkrieg II": collapse_pkgs,
    "Guelphs and Ghibellines": collapse_pkgs,
    "Guerilla": collapse_pkgs,
    "Guerrilla Checkers": collapse_pkgs,
    "Guild Ball": None,
    "Guilford": collapse_pkgs,
    "Gulf Strike": collapse_pkgs,
    "Guns of August": collapse_pkgs,
    "Gunslinger": None,
    "Gustav Adolf the Great: With God and Victorious Arms": None,
    "Görlitz 20": collapse_pkgs,
    "H&S": None,
    "Hackopoly": None,
    "Hadrian's Line": collapse_pkgs,
    "Halebarde & Gonfanon": None,
    "Hamburger Hill": collapse_pkgs,
    "Hammer of the Scots": collapse_pkgs,
    "Hammer's Slammers": collapse_pkgs,
    "Hanau 1813": collapse_pkgs,
    "Hands in the Sea": None,
    "Hannibal: Rome vs. Carthage": None,
    "Hannibal: The Italian Campaign": collapse_pkgs,
    "Hansa Teutonica: Big Box": collapse_pkgs,
    "Harpoon: Captain's Edition": None,
    "Harvest": collapse_pkgs,
    "Hastenbeck 1757": collapse_pkgs,
    "Havannah": collapse_pkgs,
    "Healthy Heart Hospital": collapse_pkgs,
    "Heart of Darkness: An Adventure Game of African Exploration": collapse_pkgs,
    "Hearts and Minds: Vietnam 1965-1975": collapse_pkgs,
    "Hearts and Minds: Vietnam 1965-1975 (Third Edition)": collapse_pkgs,
    "Heights of Courage": collapse_pkgs,
    "Heirs of the Golden Horde": collapse_pkgs,
    "Helden in het Veld": collapse_pkgs,
    "Hell Before Night: The Battle of Shiloh": collapse_pkgs,
    "Hell's Highway": collapse_pkgs,
    "Hellenes: Campaigns of the Peloponnesian War": collapse_pkgs,
    "Hellenica: Story of Greece": collapse_pkgs,
    "Hellespont (411/410 AV. J.-C.)": collapse_pkgs,
    "Hellfire Pass": collapse_pkgs,
    "Helltank": collapse_pkgs,
    "Helltank Destroyer": collapse_pkgs,
    "Help Arrives": collapse_pkgs,
    "Hera and Zeus": collapse_pkgs,
    "Heralds of Defeat": collapse_pkgs,
    "Here Come the Rebels": collapse_pkgs,
    "Here I Stand": collapse_pkgs,
    "HeroClix": collapse_pkgs,
    "HeroQuest": None,
    "Heroes of Feonora": None,
    "Heroes of New Phlan": None,
    "Heroes of Normandie": collapse_pkgs,
    "Heroes of Terrinoth": collapse_pkgs,
    "Hexabrae": collapse_pkgs,
    "Hexagony": collapse_pkgs,
    "Hexemonia": collapse_pkgs,
    "Hey! That's My Fish!": None,
    "Hibernia": collapse_pkgs,
    "High Frontier": None,
    "High Frontier (3rd edition)": None,
    "High Frontier 4 All": collapse_pkgs,
    "High Trader (Pbem / Forum tool only)": collapse_pkgs,
    "Highway to the Kremlin": collapse_pkgs,
    "Highway to the Reich: Operation Market-Garden 17-26 September 1944 – 2nd Edition": collapse_pkgs,
    "Hill of Doves: The First Anglo-Boer War": collapse_pkgs,
    "Hippos & Crocodiles": collapse_pkgs,
    "History of Civilizations": collapse_pkgs,
    "History of the World": collapse_pkgs,
    "History of the World (2018)": collapse_pkgs,
    "Hit The Beach": None,
    "Hitler's Reich": collapse_pkgs,
    "Hitler's War": None,
    "Hive": collapse_pkgs,
    "Hnefatafl": None,
    "Hoa-Binh 1951-1952: The Battle of the Black River": collapse_pkgs,
    "Hof Gap": collapse_pkgs,
    "Hold the Line": collapse_pkgs,
    "Hold the Line: Bella Gerant Alii": collapse_pkgs,
    "Hold the Line: Frederick's War": collapse_pkgs,
    "Hold the Line: Philipp's War": collapse_pkgs,
    "HoldFast: Korea 1950-1951": collapse_pkgs,
    "HoldFast: Russia 1941-1942": collapse_pkgs,
    "Holdfast: Tunisia 1942-43": collapse_pkgs,
    "Holland '44: Operation Market-Garden": collapse_pkgs,
    "Homestead": collapse_pkgs,
    "Hood Strikes North": collapse_pkgs,
    "Hoplite": collapse_pkgs,
    "Hoppers": None,
    "Horse & Musket: Annual Number 1": collapse_pkgs,
    "Horse & Musket: Crucible of War": collapse_pkgs,
    "Horse & Musket: Dawn of an Era": collapse_pkgs,
    "Horse & Musket: Sport of Kings": collapse_pkgs,
    "Horseless Carriage": collapse_pkgs,
    "Hot Spot": None,
    "Hougoumont": collapse_pkgs,
    "House Of Normandy": collapse_pkgs,
    "Hube's Pocket": None,
    "Hungarian Rhapsody: The Eastern Front in Hungary – October 1944-February 1945": collapse_pkgs,
    "Hunters from the Sky": collapse_pkgs,
    "Hunting Party": collapse_pkgs,
    "Hurtgen of Somnium": collapse_pkgs,
    "Huuue!": None,
    "Huzzah! Four Battles of the American Civil War Vol. 1": collapse_pkgs,
    "Hyle": None,
    "HypoWar": collapse_pkgs,
    "I Will Fight No More... Forever": collapse_pkgs,
    "IJN": collapse_pkgs,
    "ITACS": None,
    "Iberos": collapse_pkgs,
    "Ici, c'est la France! The Algerian War of Independence 1954-62": collapse_pkgs,
    "Iconoclasm": collapse_pkgs,
    "Ides of March: The End of the Roman Republic 44BC - 30BC": collapse_pkgs,
    "Iena 1806": collapse_pkgs,
    "Ikusa": collapse_pkgs,
    "Iliad": collapse_pkgs,
    "Illuminati": collapse_pkgs,
    "Illuminati Endgame 2012": collapse_pkgs,
    "Illuminati: Deluxe Edition": None,
    "Illusions Of Glory": collapse_pkgs,
    "Impact Naval Game": None,
    "Imperator": collapse_pkgs,
    "Imperial Struggle": None,
    "Imperial Tide: The Great War 1914-1918": collapse_pkgs,
    "Imperialism: Road To Domination": collapse_pkgs,
    "Imperium": None,
    "Imperium Romanum II": collapse_pkgs,
    "Imperius": collapse_pkgs,
    "Impulse": collapse_pkgs,
    "In Their Quiet Fields II": None,
    "Inception": collapse_pkgs,
    "Inception - Solo card game": collapse_pkgs,
    "Incredible Courage at Austerlitz - Telnitz": collapse_pkgs,
    "India Pakistan Nuclear Crisis": collapse_pkgs,
    "Indian Ocean Region: South China Sea – Vol. II": collapse_pkgs,
    "Infection Express": collapse_pkgs,
    "Inferno": collapse_pkgs,
    "Inferno sugli Altipiani, 1916": collapse_pkgs,
    "Infidel": None,
    "Infinity: A Skirmish Game": collapse_pkgs,
    "Inhabit the Earth": collapse_pkgs,
    "Inkermann 1854": collapse_pkgs,
    "Interceptor Ace: Daylight Air Defense Over Germany, 1943-44": collapse_pkgs,
    "Interceptor Ace: Volume 2 – Last Days of the Luftwaffe, 1944-45": collapse_pkgs,
    "Into a Bear Trap: The Battle for Grozny, January 1995": collapse_pkgs,
    "Into the Bastards": collapse_pkgs,
    "Into the Woods: The Battle of Shiloh": collapse_pkgs,
    "Intruder": collapse_pkgs,
    "Invaders From Dimension X!": collapse_pkgs,
    "Invasion 1066: The Battle of Hastings": collapse_pkgs,
    "Invasion of Malta: 1942": None,
    "Invasion of the Air-Eaters": collapse_pkgs,
    "Invasion: America – Death Throes of the Superpower": None,
    "Invasion: Malta": None,
    "Invasion: Norway": None,
    "Invasions: Volume 1 – 350-650 AD": collapse_pkgs,
    "Iran Israel Nuclear Crisis": collapse_pkgs,
    "Iron Curtain": collapse_pkgs,
    "Iron Tide: Panzers in the Ardennes": collapse_pkgs,
    "Iron and Oak": collapse_pkgs,
    "Ironwood": collapse_pkgs,
    "Island Emergency": collapse_pkgs,
    "Island Of D 2: The Shadow of Dawn": collapse_pkgs,
    "Island War: Four Pacific Battles": None,
    "Island of D": None,
    "It Never Snows": collapse_pkgs,
    "Italia": collapse_pkgs,
    "Italia '44": collapse_pkgs,
    "Italia 1917-1918: A Farewell to Arms": collapse_pkgs,
    "Ivanhoe": collapse_pkgs,
    "Iwanna's Theme Park": collapse_pkgs,
    "Iwo Jima - Rage Against the Marines": None,
    "IwoJima": collapse_pkgs,
    "Jackson & Sheridan": collapse_pkgs,
    "Jackson in the Valley": collapse_pkgs,
    "Jambo": collapse_pkgs,
    "Jambo +1st/2nd expansions": collapse_pkgs,
    "Jambo Expansion": collapse_pkgs,
    "Jambo Expansion 2": collapse_pkgs,
    "James Bond 007 Assault! Game": collapse_pkgs,
    "Jasper and Zot": None,
    "Jati": collapse_pkgs,
    "Java": collapse_pkgs,
    "Jena 20": collapse_pkgs,
    "John Carter: Warlord of Mars": collapse_pkgs,
    "John Prados' Third Reich": collapse_pkgs,
    "Jugger TTG:Dogskull Heroes": collapse_pkgs,
    "Julius Caesar": collapse_pkgs,
    "Julius Caesar: Game of the Gallic Wars": collapse_pkgs,
    "Justinian": collapse_pkgs,
    "Kabinettskrieg": None,
    "Kahmaté": None,
    "Kampfpanzer: Armored Combat, 1937-40": collapse_pkgs,
    "Kaosball: The Fantasy Sport of Total Domination": collapse_pkgs,
    "Karelia '44": collapse_pkgs,
    "Kassala": collapse_pkgs,
    "Kasserine": None,
    "Kasserine Pass": None,
    "Katana: Samurai Action Card Game": collapse_pkgs,
    "Katzbach 20": collapse_pkgs,
    "Kawaguchi's Gamble: Edson's Ridge": collapse_pkgs,
    "Kawanakajima 1561": collapse_pkgs,
    "Kazaam": collapse_pkgs,
    "Kellogg's Major League Baseball Game": None,
    "Kerbal Card Program": None,
    "Kestenga: Another Fight to the Finnish": None,
    "Kharkov Battles: Before & After Fall Blau": collapse_pkgs,
    "Kharkov: The Soviet Spring Offensive": collapse_pkgs,
    "Khartoum: Sudan, 1883 to 1885": None,
    "Khas": None,
    "Khet: The Laser Game": None,
    "Khronos": collapse_pkgs,
    "Khyber Rifles: Britannia in Afghanistan": None,
    "Kido Butai: Japan's Carriers at Midway": collapse_pkgs,
    "Kiev 1943: Orages à l'est 3 Ukraine": collapse_pkgs,
    "Kill Doctor Lucky": collapse_pkgs,
    "King Philip's War": collapse_pkgs,
    "King of New York": collapse_pkgs,
    "King of Tokyo": collapse_pkgs,
    "King's Table": None,
    "Kingdom of Heaven: The Crusader States 1097-1291": collapse_pkgs,
    "Kingmaker": None,
    "Kingmaker (2023)": None,
    "Kircholm 1605": collapse_pkgs,
    "Kircholm 1605 (2014)": collapse_pkgs,
    "Kirovograd": None,
    "Klin Zha": collapse_pkgs,
    "Knight Hawks": collapse_pkgs,
    "Knights of the Air": collapse_pkgs,
    "Knights of the Dinner Table: Orcs at the Gates": None,
    "Kock 1939": collapse_pkgs,
    "Kolejka": None,
    "Kolin: Frederick's First Defeat – June 18, 1757": collapse_pkgs,
    "Kon-tiki": None,
    "Korea: Fire and Ice": collapse_pkgs,
    "Korea: The Forgotten War": None,
    "Korea: The Mobile War 1950-51": collapse_pkgs,
    "Korsun Pocket": None,
    "Korsun Pocket 2: Little Stalingrad on the Dnepr": collapse_pkgs,
    "Krazy Wordz": collapse_pkgs,
    "Kremlin": None,
    "Kreta 1941": collapse_pkgs,
    "Kriegbot": collapse_pkgs,
    "Kriegspiel (1970)": collapse_pkgs,
    "Krosmaster: Arena": collapse_pkgs,
    "Kursk: History's Greatest Tank Battle, July 1943": collapse_pkgs,
    "Kursk: Operation Zitadelle, 4 July 1943": collapse_pkgs,
    "L Bataille Novi": collapse_pkgs,
    "L'Art de la Guerre": None,
    "L'Été des Boxers": collapse_pkgs,
    "La Bataille d'Auerstædt": collapse_pkgs,
    "La Bataille d'Austerlitz": None,
    "La Bataille d'Espagnol: Talavera": collapse_pkgs,
    "La Bataille de Corunna-Espagnol": collapse_pkgs,
    "La Bataille de Dresde": collapse_pkgs,
    "La Bataille de France, 1940": collapse_pkgs,
    "La Bataille de Friedland 1807 et le siège de Danzig 1807": collapse_pkgs,
    "La Bataille de Hanau": collapse_pkgs,
    "La Bataille de Leipzig 1813": collapse_pkgs,
    "La Bataille de Ligny": collapse_pkgs,
    "La Bataille de Mont St Jean": collapse_pkgs,
    "La Bataille de Neerwinden": collapse_pkgs,
    "La Bataille de Paris 1814": collapse_pkgs,
    "La Bataille de Raszyn 1809": collapse_pkgs,
    "La Bataille de Wavre": collapse_pkgs,
    "La Bataille de la Moscowa": collapse_pkgs,
    "La Bataille de la Moscowa (third edition)": collapse_pkgs,
    "La Bataille des Quatre Bras": collapse_pkgs,
    "La Bérézina 1812": collapse_pkgs,
    "La Casa de los Fantasmas": collapse_pkgs,
    "La Città": collapse_pkgs,
    "La Fuga de Coldit": collapse_pkgs,
    "La Garde avance!": collapse_pkgs,
    "La Grande Armée: The Campaigns of Napoleon in Central Europe": collapse_pkgs,
    "La Grande Guerre 14-18": collapse_pkgs,
    "La Granja": None,
    "La Guerra de Africa 1859-60": collapse_pkgs,
    "La Guerre de 1870: La chute de Napoléon III (juillet-août 1870)": collapse_pkgs,
    "La Guerre de Troie": None,
    "La Guerre de l'Empereur": collapse_pkgs,
    "La Patrie en Danger 1814": collapse_pkgs,
    "La Trêve ou l'Epée": None,
    "La Vallée des Mammouths": collapse_pkgs,
    "La bataille d'Hondschoote": collapse_pkgs,
    "La bataille de Jemmapes": collapse_pkgs,
    "La bataille des Downs 1639": collapse_pkgs,
    "La guerre d'indépendance de Bretagne (1487-1491)": collapse_pkgs,
    "La guerre du Bien public 1465": collapse_pkgs,
    "La sombra del aguila": None,
    "Labyrinth: The War on Terror": None,
    "Land and Freedom: The Spanish Revolution and Civil War": collapse_pkgs,
    "Las Navas de Tolosa, 1212": collapse_pkgs,
    "Last Battle: Ie Shima, 1945": collapse_pkgs,
    "Last Blitzkrieg: Wacht am Rhein, The Battle of the Bulge": collapse_pkgs,
    "Last Chance for Victory": collapse_pkgs,
    "Last Frontier: The Vesuvius Incident": collapse_pkgs,
    "Last Full Measure: The Battle of Brandy Station": collapse_pkgs,
    "Last Full Measure: The Battle of Cedar Mountain": collapse_pkgs,
    "Last Full Measure: The Battle of Gettysburg": collapse_pkgs,
    "Last Full Measure: The Battle of Gettysburg (Second Edition)": collapse_pkgs,
    "Last Full Measure: The Battle of Hanover": collapse_pkgs,
    "Last Full Measure: The Battle of Second Manassas": collapse_pkgs,
    "Last Full Measure: The Battle of Shiloh": collapse_pkgs,
    "Last Full Measure: The Battles of Aldie, Middleburg, and Upperville": collapse_pkgs,
    "Last Full Measure: The Battles of Cross Keys and Port Republic": collapse_pkgs,
    "Last Full Measure: The Battles of Kernstown": collapse_pkgs,
    "Last Full Measure: The Battles of South Mountain": collapse_pkgs,
    "Last Full Measure: The Maryland Campaign": collapse_pkgs,
    "Last Night on Earth: The Zombie Game": collapse_pkgs,
    "Last Stand: The Battle for Moscow 1941-42": collapse_pkgs,
    "Last full measure: The Battle of Trevilians Station": collapse_pkgs,
    "Launch Fighters!": collapse_pkgs,
    "Le Dauphin et l'Epée": None,
    "Le Grand Empire": collapse_pkgs,
    "Le Lion et l'Epée": None,
    "Le Marché de Samarkand": collapse_pkgs,
    "Le Retour de l'Empereur": collapse_pkgs,
    "Le Temps des As II": collapse_pkgs,
    "Le Vol de l'Aigle (Game Aid Only)": None,
    "Leader 1": None,
    "Leader 1: Hell of the North": None,
    "Leaping Lemmings": collapse_pkgs,
    "Leaving Earth": None,
    "Lebensraum: The War For Europe, 1941-1945": collapse_pkgs,
    "Lee Moves North: The Confederate Summer Offensive, 1862 & 1863": collapse_pkgs,
    "Lee Takes Command": collapse_pkgs,
    "Lee at Gettysburg: July 1st 1863": collapse_pkgs,
    "Lee vs Grant": None,
    "Lee's Invincibles": collapse_pkgs,
    "Lee's Last Offensive": collapse_pkgs,
    "Legendary Endeavors CCG Nightmare Set": collapse_pkgs,
    "Legendary: A Marvel Deck Building Game": None,
    "Legends of Lanasia": None,
    "Legends of Void": collapse_pkgs,
    "Legends of the Three Kingdoms": collapse_pkgs,
    "Legion": collapse_pkgs,
    "Legions of Darkness": collapse_pkgs,
    "Legions of Steel": collapse_pkgs,
    "Leipzig 1813": collapse_pkgs,
    "Leipzig: The Battle of Nations – Napoleon vs. Europe": collapse_pkgs,
    "Lembitu": collapse_pkgs,
    "Leningrad": collapse_pkgs,
    "Leningrad '41": collapse_pkgs,
    "Lepanto": collapse_pkgs,
    "Lepanto 1571: A Sea Turned Red by Blood": collapse_pkgs,
    "Leros": collapse_pkgs,
    "Les Faiseurs d'Univers - Makers of Univers": None,
    "Les Guerres de Bourgogne": collapse_pkgs,
    "Les Guerres du Roi Soleil 1667-1713": collapse_pkgs,
    "Les Maréchaux : Junot 1808 - Soult 1809": collapse_pkgs,
    "Les Maréchaux II: Dupont 1808 – Victor 1811 – Suchet 1813": collapse_pkgs,
    "Les Maréchaux III: Augereau 1814 et Eugene 1814": collapse_pkgs,
    "Les Maréchaux IV: Joseph 1809": collapse_pkgs,
    "Les Maréchaux V: Moreau 1800": collapse_pkgs,
    "Les Quatre-Bras & Waterloo 1815: The Empire's Final Blows": collapse_pkgs,
    "Les Rois Francs": None,
    "Les batailles de St Albans": collapse_pkgs,
    "Les cent-heures de Waterloo, la campagne de Belgique de 1815": collapse_pkgs,
    "Les victoires du Maréchal de Saxe : Fontenoy 1745 - Lauffeld 1747": collapse_pkgs,
    "Letters from Whitechapel": None,
    "Lettow-Vorbeck: East Africa 1914-18": None,
    "Leuthen: Drums and Muskets Vol. 1": collapse_pkgs,
    "Leuthen: Frederick's Greatest Victory": collapse_pkgs,
    "Level Six": collapse_pkgs,
    "Leviathan 3000: Space Warfare": collapse_pkgs,
    "Liberty Roads": None,
    "Liberty or Death: The American Insurrection": collapse_pkgs,
    "Liberty: The American Revolution 1775-83": collapse_pkgs,
    "Liberté": None,
    "Light Division": collapse_pkgs,
    "Lightning War": collapse_pkgs,
    "Ligny 1815: Last Eagles": collapse_pkgs,
    "Like Lions They Fought": collapse_pkgs,
    "Lilliburlero: The Battle of the Boyne, July 1690": collapse_pkgs,
    "Lincoln's War": None,
    "Lion of Ethiopia": collapse_pkgs,
    "Lion of Judah: The War for Ethiopia, 1935-1941": collapse_pkgs,
    "Lion of the North": None,
    "Little Big Horn": collapse_pkgs,
    "Littoral Commander: Indo-Pacific": collapse_pkgs,
    "Live Free or Die: Three Battles for America": collapse_pkgs,
    "Lobositz: First Battle of the Seven Years War": collapse_pkgs,
    "Lock 'n Load Tactical: Bear and the Jackal": collapse_pkgs,
    "Lock 'n Load Tactical: Dark July 43": collapse_pkgs,
    "Lock 'n Load Tactical: Day of Heroes": collapse_pkgs,
    "Lock 'n Load Tactical: Days of Villainy": collapse_pkgs,
    "Lock 'n Load Tactical: Hell Frozen Over": collapse_pkgs,
    "Lock 'n Load Tactical: Heroes Against the Red Star": None,
    "Lock 'n Load Tactical: Heroes in Defiance": collapse_pkgs,
    "Lock 'n Load Tactical: Heroes of Normandy": None,
    "Lock 'n Load Tactical: Heroes of North Africa": None,
    "Lock 'n Load Tactical: Heroes of the Bitter Harvest": collapse_pkgs,
    "Lock 'n Load Tactical: Heroes of the Falklands": collapse_pkgs,
    "Lock 'n Load Tactical: Heroes of the Motherland": None,
    "Lock 'n Load Tactical: Heroes of the Nam": collapse_pkgs,
    "Lock 'n Load Tactical: Heroes of the Pacific": None,
    "Lock 'n Load Tactical: Starter Kit": collapse_pkgs,
    "Lock 'n Load: A Day of Heroes": collapse_pkgs,
    "Lock 'n Load: Heroes of the Gap": collapse_pkgs,
    "Lock 'n Load: Heroes of the Pacific": collapse_pkgs,
    "Lock 'n Load: World Championship": collapse_pkgs,
    "Lock n' Load: Band of Heroes": collapse_pkgs,
    "London's Burning": collapse_pkgs,
    "Long Road to Getttysburg (GCACW)": None,
    "Long Roads to Gettysburg II": collapse_pkgs,
    "Lord of the Dead": None,
    "Lord of the Rings Battlegame": None,
    "Lord of the Rings: Combat Hex Tradeable Miniatures Game": collapse_pkgs,
    "Lord of the Rings: The Confrontation": collapse_pkgs,
    "Lord of the Rings: The Confrontation (Deluxe Edition)": collapse_pkgs,
    "Lordes e Reis": collapse_pkgs,
    "Lords of the Sierra Madre (second edition)": collapse_pkgs,
    "Lords of the Spanish Main": collapse_pkgs,
    "Los Amos del Horizonte": collapse_pkgs,
    "Lost Battles: Operational Combat in Russia": collapse_pkgs,
    "Lost Cities": collapse_pkgs,
    "Lost Ruins of Arnak": collapse_pkgs,
    "Loups gris en Atlantique": collapse_pkgs,
    "Love Live! School Idol Festival": collapse_pkgs,
    "Ludo": collapse_pkgs,
    "Ludus Gladiatorius": collapse_pkgs,
    "Luftwaffe": None,
    "Luna Mare: Mineralis & Dominatio": None,
    "Luzon: Race for Bataan": collapse_pkgs,
    "Lyngk": collapse_pkgs,
    "MAG-23 Guadalcanal": collapse_pkgs,
    "MBT": None,
    "MBT / IDF": None,
    "MOCKBA": collapse_pkgs,
    "Mabinogion": collapse_pkgs,
    "MacGowan & Lombardy's The Great War": collapse_pkgs,
    "Machi Koro": None,
    "Machiavelli": collapse_pkgs,
    "Mad steel arena": collapse_pkgs,
    "Mafia": None,
    "Mage Knight Board Game": collapse_pkgs,
    "Mage Wars": None,
    "Magenta 1859": collapse_pkgs,
    "Magestorm": collapse_pkgs,
    "Magic Hat": collapse_pkgs,
    "Magic Realm": collapse_pkgs,
    "Magnifico": collapse_pkgs,
    "Maharaja": collapse_pkgs,
    "Malaya & Burma": None,
    "Malifaux": None,
    "Malvern Hill": collapse_pkgs,
    "Man of War": collapse_pkgs,
    "Management": None,
    "Manassas": None,
    "Maneuver": None,
    "Manifest Destiny": collapse_pkgs,
    "Manoeuvre": collapse_pkgs,
    "Mansions of Madness": None,
    "Maori Wars: The New Zealand Land Wars, 1845-1872": collapse_pkgs,
    "Maori:Warriors of the Long White Cloud – Clan Warfare in New Zealand": collapse_pkgs,
    "Maquis": collapse_pkgs,
    "March Madness": None,
    "March of the Ants": collapse_pkgs,
    "Marching Through Georgia": collapse_pkgs,
    "Marco Polo": collapse_pkgs,
    "Marengo": collapse_pkgs,
    "Marengo 1800": collapse_pkgs,
    "Margin Of Error: A Presidential Election Game": collapse_pkgs,
    "Maria": None,
    "Marine Fighter Squadron: A Solitaire Game of Aerial Combat in the Solomons (1942-1945)": None,
    "Mario Kart Racing": collapse_pkgs,
    "Marita-Merkur: The Campaign in the Balkans, 1940-41": collapse_pkgs,
    "Marne 1918: Friedensturm": collapse_pkgs,
    "Marston Moor": collapse_pkgs,
    "Martian Dice": collapse_pkgs,
    "Marval Heroes": collapse_pkgs,
    "Marvel Dice Masters: Age of Ultron": collapse_pkgs,
    "Marvel Dice Masters: Avengers vs. X-Men": collapse_pkgs,
    "Marvel Dice Masters: Uncanny X-Men": collapse_pkgs,
    "Masques": collapse_pkgs,
    "Masséna at Loano": collapse_pkgs,
    "Master of Orion: The Board Game": collapse_pkgs,
    "Matanikau": collapse_pkgs,
    "Math Wars": collapse_pkgs,
    "Mayday": collapse_pkgs,
    "Maze of the Red Mage: A Solitaire Dungeon Adventure!": None,
    "MechWar '77: Tactical Armored Combat in the 1970's": None,
    "MechWar 2": collapse_pkgs,
    "MechWar 4": None,
    "Mechwarrior: Dark Age (2002)": collapse_pkgs,
    "Medapolis": collapse_pkgs,
    "Medapolis Lite": collapse_pkgs,
    "Medina de Rioseco 1808": collapse_pkgs,
    "Medwar Sicily": collapse_pkgs,
    "Melee - Wizard": None,
    "Meltwater: A Game of Tactical Starvation": collapse_pkgs,
    "Memoir '44": None,
    "Men of Iron, Volume I: The Rebirth of Infantry": None,
    "Mentis": collapse_pkgs,
    "Merchant of Venus": None,
    "Merchants & Marauders": None,
    "Mercury/Market Garden": collapse_pkgs,
    "Mesopotamia: Birth of Civilization": collapse_pkgs,
    "Mexica": collapse_pkgs,
    "Micro Space Empire": collapse_pkgs,
    "MicroClix 1.4": collapse_pkgs,
    "Middle East Strike": None,
    "Middle-Earth Quest": collapse_pkgs,
    "Midway": None,
    "Mighty Empires: Warhammer Expansion": collapse_pkgs,
    "Mighty Morphin Rainbow Rangers": collapse_pkgs,
    "Milky Way": collapse_pkgs,
    "Mille Bornes": collapse_pkgs,
    "Mind Game": None,
    "Minden 1759": None,
    "Mini Rogue": collapse_pkgs,
    "MiniCore": collapse_pkgs,
    "Minuteman: The Second American Revolution": collapse_pkgs,
    "Mississippi Banzai": collapse_pkgs,
    "Mississippi Fortress": collapse_pkgs,
    "Misterio": collapse_pkgs,
    "Mistfall": collapse_pkgs,
    "Mistral: the Western Med 1740-48": collapse_pkgs,
    "Mistsmall: Mistfall in Your Pocket": collapse_pkgs,
    "Mizuage": collapse_pkgs,
    "Mobile Suit Gundam: Fortress": collapse_pkgs,
    "Modern Battles: Four Contemporary Conflicts": collapse_pkgs,
    "Mohawk": collapse_pkgs,
    "Monmouth": collapse_pkgs,
    "Monopanem": collapse_pkgs,
    "Monopoly": None,
    "Monopoly Deal Card Game": collapse_pkgs,
    "Monsterpocalypse": None,
    "Monsterpocalypse - Voltron: Defender of the Universe Battle Game": collapse_pkgs,
    "Montcalm & Wolfe": collapse_pkgs,
    "Montebello": None,
    "Montebello 1800": collapse_pkgs,
    "Montenotte 1796": collapse_pkgs,
    "Montmirail and Vauchamps 1814": collapse_pkgs,
    "Monty's Gamble: Market Garden": collapse_pkgs,
    "Montélimar: The Anvil of Fate": collapse_pkgs,
    "Moon": collapse_pkgs,
    "Moonbase Alpha": collapse_pkgs,
    "Moorea": collapse_pkgs,
    "Moravian Sun": collapse_pkgs,
    "Mordheim: City of the Damned": collapse_pkgs,
    "More Aggressive Attitudes: The 1862 Virginia Campaign": collapse_pkgs,
    "Morgan's A'Comin'!": collapse_pkgs,
    "Morituri te Salutamus": collapse_pkgs,
    "Mosby's Raiders": collapse_pkgs,
    "Moscow '41": collapse_pkgs,
    "Moscow Embattled, 1941: the Minigame": collapse_pkgs,
    "Mountains Aflame!": collapse_pkgs,
    "Mr President": collapse_pkgs,
    "Mr. Jack": None,
    "Mr. Lincoln's War: Army of the Potomac": None,
    "Mr. Madison's War": collapse_pkgs,
    "Mr. President": collapse_pkgs,
    "Mukden: Sino-Soviet Combat in the '70's": collapse_pkgs,
    "Multi Board": collapse_pkgs,
    "Muse: A Storytelling Game": collapse_pkgs,
    "Muses": collapse_pkgs,
    "Musket & Pike Dual Pack": collapse_pkgs,
    "Musket & Pike: Tactical Combat, 1550-1680": collapse_pkgs,
    "Mustangs": collapse_pkgs,
    "Mutant Chronicles Collectible Miniatures Game": collapse_pkgs,
    "Mutant Chronicles: Siege of the Citadel": collapse_pkgs,
    "Mythic Battles": collapse_pkgs,
    "Mythic Mischief": collapse_pkgs,
    "Mâamut": collapse_pkgs,
    "NATO Division Commander": collapse_pkgs,
    "NATO, Nukes, & Nazis": None,
    "NATO: Operational Combat in Europe in the 1970's": collapse_pkgs,
    "NATO: The Cold War Goes Hot": collapse_pkgs,
    "NATO: The Next War in Europe": collapse_pkgs,
    "NFL Strategy": None,
    "Nachod and Skalitz 1866": collapse_pkgs,
    "Naipe en la Ruta de la Selva": collapse_pkgs,
    "Naipe en las Carreras": collapse_pkgs,
    "Naipe y la Ballena Blanca v.1.0": collapse_pkgs,
    "Napoleon 1807": collapse_pkgs,
    "Napoleon Against Russia": collapse_pkgs,
    "Napoleon At Bay: Defend the Gates of Paris": None,
    "Napoleon Returns 1815": collapse_pkgs,
    "Napoleon against Europe": collapse_pkgs,
    "Napoleon and his Marshals": None,
    "Napoleon and the Archduke Charles: The Battle of Abensberg": collapse_pkgs,
    "Napoleon at War:Four Battles": None,
    "Napoleon at Waterloo": None,
    "Napoleon at the Crossroads": collapse_pkgs,
    "Napoleon in Europe": collapse_pkgs,
    "Napoleon's Art of War: Eylau & Dresden": collapse_pkgs,
    "Napoleon's Eagles 2: The Hundred Days – The Waterloo Campaign": collapse_pkgs,
    "Napoleon's Eagles: Storm in the East – The Battles of Borodino and Leipzig": collapse_pkgs,
    "Napoleon's Last Battles": None,
    "Napoleon's Leipzig Campaign": collapse_pkgs,
    "Napoleon's Triumph": None,
    "Napoleon's War II: The Gates of Moscow": collapse_pkgs,
    "Napoleon's War: The 100 Days": collapse_pkgs,
    "Napoleon: The Waterloo Campaign, 1815": None,
    "Napoleonic 20 Expansion Kit": collapse_pkgs,
    "Napoleon’s Imperium": collapse_pkgs,
    "Napoléon 1806": collapse_pkgs,
    "Napoléon 1815": collapse_pkgs,
    "Napoléon's Conquests": collapse_pkgs,
    "Narvik": collapse_pkgs,
    "Nation Building": collapse_pkgs,
    "Nations": collapse_pkgs,
    "Nations at War: Desert Heat": collapse_pkgs,
    "Nations at War: Stalin's Triumph": collapse_pkgs,
    "Nations at War: White Star Rising": None,
    "Nations in Arms: Valmy to Waterloo": collapse_pkgs,
    "Navajo Wars": collapse_pkgs,
    "Naval Warfare Mediterranean": collapse_pkgs,
    "Naval Warfare Northern Europe": collapse_pkgs,
    "Navia Dratp": None,
    "Neanderthal": None,
    "Neck and Neck": None,
    "Necromancer": collapse_pkgs,
    "Necromunda": collapse_pkgs,
    "Nemesis: Burma 1944": collapse_pkgs,
    "Nemo's War (Second Edition)": collapse_pkgs,
    "Netrunner": None,
    "Neuroshima Hex!": None,
    "Nevsky": collapse_pkgs,
    "New Frontiers": collapse_pkgs,
    "New York 1776": None,
    "Newtown": collapse_pkgs,
    "Next War: India-Pakistan": collapse_pkgs,
    "Next War: Iran": collapse_pkgs,
    "Next War: Korea": None,
    "Next War: Poland": collapse_pkgs,
    "Next War: Taiwan": None,
    "Next War: Vietnam": collapse_pkgs,
    "Ney vs. Wellington: The Battle of Quatre Bras": collapse_pkgs,
    "Nieuchess": None,
    "Nieuport 1600": collapse_pkgs,
    "Night Drop 2: Pegasus Bridge": collapse_pkgs,
    "Nightfall": collapse_pkgs,
    "Nightfighter": None,
    "Nightfighter Ace": collapse_pkgs,
    "Nine Men's Morris": collapse_pkgs,
    "Nine Years: The War of the Grand Alliance 1688-1697": collapse_pkgs,
    "No Better Place To Die": None,
    "No Motherland Without: North Korea in Crisis and Cold War": collapse_pkgs,
    "No Peace Without Honor!: The Dutch War 1672-1678": collapse_pkgs,
    "No Peace Without Spain!": collapse_pkgs,
    "No Question of Surrender": None,
    "No Retreat 2": collapse_pkgs,
    "No Retreat 4! Italian Front: 1943-45": collapse_pkgs,
    "No Retreat!": None,
    "No Retreat! The North African Front": None,
    "No Retreat! The Russian Front": None,
    "No Retreat!: Polish & French Fronts": collapse_pkgs,
    "No Such Mercy": None,
    "Nomad Gods": collapse_pkgs,
    "Nomonhan Khalkin Gol 1939": collapse_pkgs,
    "None But Heroes": collapse_pkgs,
    "Nordwind 1945": collapse_pkgs,
    "Norman Conquests: Conflicts of the Normans and their successors 1053 - 1265": None,
    "Normandie 1944": collapse_pkgs,
    "Normandy '44": None,
    "Normandy of Somnium": collapse_pkgs,
    "Normandy, The Beginning of the End": collapse_pkgs,
    "Normandy: The Invasion of Europe 1944": collapse_pkgs,
    "North Africa '41": collapse_pkgs,
    "North Africa:Afrika Korps vs Desert Rats, 1940-42": collapse_pkgs,
    "North German Plain": collapse_pkgs,
    "North Korea Nuclear Crisis": collapse_pkgs,
    "Not Go": None,
    "Not War But Murder": collapse_pkgs,
    "Nothing Gained But Glory": None,
    "Nothing Left To Bomb": collapse_pkgs,
    "Nova": collapse_pkgs,
    "Novi 1799": collapse_pkgs,
    "Nuklear Winter '68": collapse_pkgs,
    "O'Connor's Offensive": collapse_pkgs,
    "Oath: Chronicles of Empire and Exile": collapse_pkgs,
    "Obbedisco!": collapse_pkgs,
    "Objective Moscow: The Death of Soviet Communism": collapse_pkgs,
    "Objective: Kiev": collapse_pkgs,
    "Objective: Schmidt": collapse_pkgs,
    "Oceans of Fire": collapse_pkgs,
    "Oceanía": collapse_pkgs,
    "October War: Doctrine and Tactics in the Yom Kippur Conflict": None,
    "Odin's Ravens (Second Edition)": collapse_pkgs,
    "Odisea Espacial": collapse_pkgs,
    "Officer Class beta": collapse_pkgs,
    "Offrandes": collapse_pkgs,
    "Ogre": None,
    "Oil War: American Intervention in the Persian Gulf": collapse_pkgs,
    "Okko: Era of the Asagiri": collapse_pkgs,
    "Old School Tactical": collapse_pkgs,
    "Old School Tactical: Volume 2 – West Front 1944/45": collapse_pkgs,
    "Old West Shootout": collapse_pkgs,
    "Olympica": collapse_pkgs,
    "Omaha Beachhead: Battle for the Bocage": collapse_pkgs,
    "Omaha: The Bloody Beach": collapse_pkgs,
    "On To Paris!": collapse_pkgs,
    "On the Bounce": collapse_pkgs,
    "On to Richmond II: The Union Strikes South": None,
    "On to Richmond!": None,
    "Once We Moved Like the Wind: The Apache Wars, 1861-1886": collapse_pkgs,
    "Onslaught": None,
    "Open Fire: Solitaire Tank Combat in WWII": collapse_pkgs,
    "Operation Battleaxe: Wavell vs. Rommel, 1941": collapse_pkgs,
    "Operation Dauntless: The Battles for Fontenay and Rauray, France, June 1944": collapse_pkgs,
    "Operation Diadem of Somnium": collapse_pkgs,
    "Operation Felix": collapse_pkgs,
    "Operation Grenade: The Battle for the Rhineland 23 Feb. - 5 Mar. '45": None,
    "Operation Ichi-Go: Japan's Massive 1944 Offensive Across China": None,
    "Operation Jubilee": collapse_pkgs,
    "Operation Mercury: The German Airborne Assault on Crete, 1941": None,
    "Operation Mercury: The Invasion of Crete": None,
    "Operation Michael": collapse_pkgs,
    "Operation Olympic": None,
    "Operation Pegasus": collapse_pkgs,
    "Operation Skorpion: Rommel's First Strike – Halfaya Pass, May 1941": collapse_pkgs,
    "Operation Theseus: Gazala 1942": collapse_pkgs,
    "Operation Typhoon: The German Assault on Moscow, 1941": collapse_pkgs,
    "Operation Veritable": collapse_pkgs,
    "Optimates et Populares": collapse_pkgs,
    "Optio": collapse_pkgs,
    "Opération Husky, Sicile 1943": collapse_pkgs,
    "Orages à l'Est": collapse_pkgs,
    "Orbit War": None,
    "Orbital": None,
    "Orchard: A 9 card solitaire game": collapse_pkgs,
    "Order and Chaos": None,
    "Orient Express": None,
    "Origins of World War I": collapse_pkgs,
    "Origins of World War II": collapse_pkgs,
    "Origins: How We Became Human": None,
    "Ostkrieg: WWII Eastern Front": collapse_pkgs,
    "Othello": collapse_pkgs,
    "Otterburn 1388": collapse_pkgs,
    "Our Place in the Sun": None,
    "Outdoor Survival": collapse_pkgs,
    "Outlaws: Adventures in the Old West": collapse_pkgs,
    "Outpost Gamma": collapse_pkgs,
    "Outreach: The Conquest of the Galaxy, 3000AD": collapse_pkgs,
    "Over the top: The Dogs of War": None,
    "Overflight!": collapse_pkgs,
    "Overlord": None,
    "Ozymandia": None,
    "PQ-17: Arctic Naval Operations 1941-43": collapse_pkgs,
    "PRESTAGS Master-Pack": None,
    "Pacific Fleet": collapse_pkgs,
    "Pacific Islands Campaign - Iwo Jima": collapse_pkgs,
    "Pacific Tide: The United States Versus Japan, 1941-45": collapse_pkgs,
    "Pacific Victory": None,
    "Pacific Victory: Pacific Theater of WW2 – Second Edition": collapse_pkgs,
    "Pacific War": None,
    "Pandemic": None,
    "Pandemic: Fall of Rome": None,
    "Pandemic: In the Lab": collapse_pkgs,
    "Pandemic: On the Brink": collapse_pkgs,
    "Pandemic: State of Emergency": collapse_pkgs,
    "Panzer": None,
    "Panzer '44: Tactical Armored Combat, Europe, 1944-45": collapse_pkgs,
    "Panzer Armee Afrika": collapse_pkgs,
    "Panzer Battles: 11th Panzer on the Chir River": collapse_pkgs,
    "Panzer Clash": None,
    "Panzer Command": None,
    "Panzer Leader": collapse_pkgs,
    "Panzer North Africa": None,
    "PanzerArmee Afrika: Rommel in the Desert, April 1941 - November 1942": None,
    "PanzerBlitz": None,
    "PanzerBlitz: Hill of Death": collapse_pkgs,
    "Panzergruppe Guderian": collapse_pkgs,
    "Panzerkrieg": collapse_pkgs,
    "Panzers !": collapse_pkgs,
    "Panzers Last Stand: Battles for Budapest, 1945": collapse_pkgs,
    "Par le feu, le fer et la Foi": None,
    "Paratroop": collapse_pkgs,
    "Parcel O' Rogues": collapse_pkgs,
    "Parchis": collapse_pkgs,
    "Paris vaut bien une messe !": None,
    "Pas de Calais": collapse_pkgs,
    "Pathogen": collapse_pkgs,
    "Paths To Hell": collapse_pkgs,
    "Paths of Glory": None,
    "Patton's 3rd Army: The Lorraine Campaign": None,
    "Patton's Best": None,
    "Patton's Vanguard": collapse_pkgs,
    "Paul Koenig's Fortress Europe": collapse_pkgs,
    "Paul Koenig's The Bulge: 6th Panzer Army": collapse_pkgs,
    "Pavlov's House": collapse_pkgs,
    "Pax Baltica": collapse_pkgs,
    "Pax Emancipation": collapse_pkgs,
    "Pax Illuminaten": collapse_pkgs,
    "Pax Pamir": collapse_pkgs,
    "Pax Pamir (Second Edition)": None,
    "Pax Porfiriana": collapse_pkgs,
    "Pax Renaissance": None,
    "Pax Renaissance: 2nd Edition": collapse_pkgs,
    "Pax Romana": collapse_pkgs,
    "Pax Transhumanity": collapse_pkgs,
    "Pax Viking": collapse_pkgs,
    "Pay Dirt": collapse_pkgs,
    "Paydirt": None,
    "Pea Ridge: The Gettysburg of the West March 7-8 1862": collapse_pkgs,
    "Pearl Harbor": collapse_pkgs,
    "Pegasus Bridge": collapse_pkgs,
    "Pegasus Bridge: The Beginning of D-Day - June 6, 1944": None,
    "Peloponnesian War": collapse_pkgs,
    "Peloton": collapse_pkgs,
    "Pendragon": collapse_pkgs,
    "Pensacola, 1781": collapse_pkgs,
    "Pente": None,
    "Perdition's Mouth: Abyssal Rift": None,
    "Perfidia": collapse_pkgs,
    "Pericles: The Peloponnesian Wars": None,
    "Perilous Tales": collapse_pkgs,
    "Perryville": None,
    "Petrichor": collapse_pkgs,
    "Phalanx: Tactical Warfare 500-100 BC": collapse_pkgs,
    "Phobos Rising!": collapse_pkgs,
    "Picket Duty: Kamikaze Attacks against U.S. Destroyers – Okinawa, 1945": collapse_pkgs,
    "Piecepack": collapse_pkgs,
    "Pioneers": collapse_pkgs,
    "Pirates by RedDeBlu": collapse_pkgs,
    "Pirates of the Spanish Main": None,
    "PitLane": None,
    "Pitt's War": collapse_pkgs,
    "Pixel Tactics": collapse_pkgs,
    "Pizza Box Baseball": collapse_pkgs,
    "Pizza Box Football": collapse_pkgs,
    "Pizza World": collapse_pkgs,
    "Plains Indian Wars": collapse_pkgs,
    "Plan Orange: Pacific War 1930 - 1935": collapse_pkgs,
    "Planet Busters": collapse_pkgs,
    "Plantagenet: Cousins' War for England, 1459 - 1485": collapse_pkgs,
    "Platoon Commander Deluxe: The Battle of Kursk": None,
    "Playing Cards": collapse_pkgs,
    "Pleasant Hill: The Red River Campaign": collapse_pkgs,
    "Ploy": collapse_pkgs,
    "Pocket Battles Series": collapse_pkgs,
    "Pocket Battles: Celts vs. Romans": collapse_pkgs,
    "Pocket Battles: Confederacy vs Union": collapse_pkgs,
    "Pocket Battles: Elves vs. Orcs": collapse_pkgs,
    "Pocket Battles: Lord of the Rings": collapse_pkgs,
    "Pocket Battles: Macedonians vs. Persians": collapse_pkgs,
    "Pocket Civ": collapse_pkgs,
    "Pocket Pro Golf": collapse_pkgs,
    "Pocket Rockets": collapse_pkgs,
    "Pod People from Another Planet!": collapse_pkgs,
    "Point Blank: V is for Victory": collapse_pkgs,
    "Poland of Somnium": collapse_pkgs,
    "Polis: Fight for the Hegemony": None,
    "Politburo, Lucha de Poder": collapse_pkgs,
    "Polygoons": None,
    "Poor Bloody Infantry": collapse_pkgs,
    "Popular Front": collapse_pkgs,
    "Port Stanley: Battle for the Falklands": collapse_pkgs,
    "Post-Heist": collapse_pkgs,
    "Postcard from the Revolution": collapse_pkgs,
    "Power Grid": None,
    "Power Plants": collapse_pkgs,
    "Practice": None,
    "Prague: The Empty Triumph": collapse_pkgs,
    "Prairie Aflame! The Northwest Rebellion of 1885": collapse_pkgs,
    "Prelude to Disaster: The Soviet Spring Offensive – May 1942": collapse_pkgs,
    "Prelude to Rebellion": collapse_pkgs,
    "Prelude to Revolution: Russia's Descent into Anarchy 1905 - 1917": collapse_pkgs,
    "Price of Freedom": collapse_pkgs,
    "Prime Minister": collapse_pkgs,
    "Primetime Adventures": collapse_pkgs,
    "Princes of the Renaissance": collapse_pkgs,
    "Pro Tennis": None,
    "Progress: Evolution of Technology": collapse_pkgs,
    "Project discovery": collapse_pkgs,
    "Proliferation!": collapse_pkgs,
    "Prussia's Defiant Stand": collapse_pkgs,
    "Prussia's Glory II": None,
    "Pub Battles: Monmouth": collapse_pkgs,
    "Puerto Rico": collapse_pkgs,
    "Puppet Wars Unstitched": collapse_pkgs,
    "Pursuit of Glory": collapse_pkgs,
    "Pyramid (Battlestar Galactica)": collapse_pkgs,
    "Quarriors!": collapse_pkgs,
    "Quartermaster General": collapse_pkgs,
    "Quatre Batailles en Espagne": None,
    "Quatre Bras 1815: Last Eagles": collapse_pkgs,
    "Quebec 1759": None,
    "Queens' Gambit: The War in Italy, 1742-1748": collapse_pkgs,
    "Quintet": None,
    "Quinto": None,
    "RAF": None,
    "RAF Coastal Command (Hudson)": collapse_pkgs,
    "RAF Coastal Command (Sunderland)": collapse_pkgs,
    "RAF: The Battle of Britain 1940": None,
    "RAN": collapse_pkgs,
    "RR": collapse_pkgs,
    "RRR": None,
    "Race Day": collapse_pkgs,
    "Race For Tunis": collapse_pkgs,
    "Race for Bastogne": collapse_pkgs,
    "Race for Berlin: The Final Struggle": collapse_pkgs,
    "Race for the Galaxy": None,
    "Race to Berlin": collapse_pkgs,
    "Race to Tokyo": collapse_pkgs,
    "Race to the Sea 1914": collapse_pkgs,
    "Race! Formula 90": None,
    "Race! Formula 90: 2nd Edition": collapse_pkgs,
    "Radetzky's March: The Hundred Hours Campaign": collapse_pkgs,
    "Radlands": collapse_pkgs,
    "Ragnarök": collapse_pkgs,
    "Raid On St. Nazaire": None,
    "Raid and Riposte": collapse_pkgs,
    "Raid on Bananama: The Bad Boys Game": None,
    "Raid on Iran": collapse_pkgs,
    "Raid on the Bunker": None,
    "Raid sur Bruneval 1942": collapse_pkgs,
    "Raid! Commando Operations, in the 20th Century": collapse_pkgs,
    "Raider 16 - Atlantis": collapse_pkgs,
    "Raider 33: Pinguin": collapse_pkgs,
    "Raider Drop Zone": collapse_pkgs,
    "Raiders of the Deep: U-boats of the Great War, 1914-18": collapse_pkgs,
    "Rail Baron": None,
    "Raj": collapse_pkgs,
    "Rallyman": None,
    "Rallyman: GT": collapse_pkgs,
    "Rattenkrieg": collapse_pkgs,
    "Rebel Fury": collapse_pkgs,
    "Rebel Raiders on the High Seas": collapse_pkgs,
    "Rebel Sabers: Civil War Cavalry Battles": collapse_pkgs,
    "Rebel Yell": collapse_pkgs,
    "Rebels in the White House": None,
    "Red Alert: Space Fleet Warfare": collapse_pkgs,
    "Red Badge of Courage": None,
    "Red Dragon, Blue Dragon: The Huaihai, 1948-49": collapse_pkgs,
    "Red Flag Over Paris": collapse_pkgs,
    "Red Poppies Campaigns: The Battles for Ypres": collapse_pkgs,
    "Red Poppies Campaigns: Volume 2 – Last Laurels At Limanowa": collapse_pkgs,
    "Red Poppies Campaigns: Volume 3 – Assault Artillery: La Malmaison": collapse_pkgs,
    "Red Poppies: WWI Tactics": collapse_pkgs,
    "Red Star Rising: The War in Russia, 1941-1944": collapse_pkgs,
    "Red Star/White Eagle: The Russo-Polish War, 1920": collapse_pkgs,
    "Red Star/White Eagle: The Russo-Polish War, 1920 – Designer Signature Edition": collapse_pkgs,
    "Red Star/White Star '78": collapse_pkgs,
    "Red Storm over the Reich": collapse_pkgs,
    "Red Storm: Baltic Approaches": collapse_pkgs,
    "Red Storm: The Air War Over Central Germany, 1987": None,
    "Red Strike": collapse_pkgs,
    "Red Sun Rising: The Russo-Japanese War 1904-05": collapse_pkgs,
    "Red Vengeance": collapse_pkgs,
    "Red Winter": collapse_pkgs,
    "Reds! - The Russian Civil War": None,
    "Redvers' Reverse: The Battle of Colenso, 1899": collapse_pkgs,
    "Reef Encounter": collapse_pkgs,
    "Regatta": collapse_pkgs,
    "Reichshoffen 1870": collapse_pkgs,
    "Reinforcements, An Assault Series Module": collapse_pkgs,
    "Reluctant Enemies: Operation Exporter – The Commonwealth Invasion of Lebanon & Syria, June-July, 1941": None,
    "Remagen Bridge": None,
    "Remember Limerick! The War of the Two Kings: Ireland, 1689-1691": collapse_pkgs,
    "Renaissance of Infantry: Tactical Warfare, 1250 A.D-1550 A.D": collapse_pkgs,
    "Renature": collapse_pkgs,
    "Renegade": collapse_pkgs,
    "Renegade Legion: Centurion – Blood & Steel": collapse_pkgs,
    "Renegade Legion: Interceptor": collapse_pkgs,
    "Renegade Legion: Leviathan": collapse_pkgs,
    "Renegade Legion: Prefect": collapse_pkgs,
    "Return to the Rock: Corregidor, 1945": collapse_pkgs,
    "Revolt in the East: Warsaw Pact Rebellion in the 1970's": collapse_pkgs,
    "Revolt on Antares": collapse_pkgs,
    "Revolution Road": collapse_pkgs,
    "Revolution!": collapse_pkgs,
    "Revolution: The Dutch Revolt 1568-1648": collapse_pkgs,
    "Rhode Island": collapse_pkgs,
    "Richard III: The Wars of the Roses": collapse_pkgs,
    "Richthofen's War": None,
    "Rifle & Saber: Tactical Combat 1850-1900": collapse_pkgs,
    "Rifles in the Ardennes": collapse_pkgs,
    "Rifles in the Darkness": None,
    "Rifles in the Pacific": collapse_pkgs,
    "Rifles in the Peninsula": collapse_pkgs,
    "Ringside": None,
    "Rise and Decline of the Third Reich": None,
    "Rise of Augustus": collapse_pkgs,
    "Rise of the Luftwaffe": None,
    "Risk": None,
    "Risk 2210 A.D.": collapse_pkgs,
    "Risk: Europe": collapse_pkgs,
    "River Rats: SEAL Team": collapse_pkgs,
    "River of Death: Battle of Chickamauga, September 19-20, 1863": collapse_pkgs,
    "Rivets": None,
    "Rivoli 1797": collapse_pkgs,
    "Road Rage": collapse_pkgs,
    "Road to Washington": None,
    "Road to the Rhine": collapse_pkgs,
    "Roads & Boats": collapse_pkgs,
    "Roads to Gettysburg": collapse_pkgs,
    "Roads to Gettysburg II: Lee Strikes North": None,
    "Roads to Leningrad: Battles of Soltsy and Staraya Russa, 1941": None,
    "Roads to Moscow: Battles of Mozhaysk and Mtsensk, 1941": collapse_pkgs,
    "Robin Hood": collapse_pkgs,
    "Robinson Crusoe: Adventure on the Cursed Island": collapse_pkgs,
    "RoboRally": None,
    "Robotech: Cyclone Run": collapse_pkgs,
    "Robots!": None,
    "Rock of the Marne": collapse_pkgs,
    "Rolica et Vimeiro 1808": None,
    "Roma": collapse_pkgs,
    "Roma aeterna": collapse_pkgs,
    "Rommel": collapse_pkgs,
    "Rommel (2017)": None,
    "Rommel in the Desert": None,
    "Rommel's War": collapse_pkgs,
    "Room 25": collapse_pkgs,
    "Root": collapse_pkgs,
    "Rosenkönig": collapse_pkgs,
    "Rossyïa 1917": collapse_pkgs,
    "Rostov '41: Race to the Don": collapse_pkgs,
    "Royal Tank Corps": collapse_pkgs,
    "Ruhr of Somnium": collapse_pkgs,
    "Run, Fight, or Die!": None,
    "Runebound (Third Edition) (2015)": collapse_pkgs,
    "Runewars": collapse_pkgs,
    "Runewars Miniatures Game": None,
    "Ruse & Bruise": collapse_pkgs,
    "Russia Besieged": None,
    "Russia Besieged: Deluxe Edition": collapse_pkgs,
    "Russian Civil War 1918-1922": None,
    "Russian Civil War 1918-1922 (Second Edition)": None,
    "Russian Front": None,
    "RustleMania": collapse_pkgs,
    "S.P.Q.R. Deluxe": None,
    "SOE: Lysander": None,
    "Sa Battalla": collapse_pkgs,
    "Sack Armies": None,
    "Saga": collapse_pkgs,
    "Saga (2015)": collapse_pkgs,
    "Sagrajas 1086": collapse_pkgs,
    "Sagunto: The Battle for Valencia": None,
    "Saigon 75": collapse_pkgs,
    "Saints in Armor": None,
    "Saipan & Tinian: Island War Series, Volume I": collapse_pkgs,
    "Saipan: The Bloody Rock": collapse_pkgs,
    "Salerno '43": collapse_pkgs,
    "Salla 1941: A Fight to the Finnish": None,
    "Sam Grant": None,
    "Samurai": collapse_pkgs,
    "Samurai (AH)": collapse_pkgs,
    "Samurai (RK)": collapse_pkgs,
    "Samurai Battles": None,
    "Samurai Blades Campaign": None,
    "Samurai Blades and Map Builder": None,
    "Samurai Knight Fever": None,
    "San Marco": collapse_pkgs,
    "Sanctum": collapse_pkgs,
    "Santa Claus vs. The Easter Bunny": collapse_pkgs,
    "Santa Cruz 1797": collapse_pkgs,
    "Santander '37": collapse_pkgs,
    "Santiago Campaign 1898": collapse_pkgs,
    "Saratoga": collapse_pkgs,
    "Sauron": None,
    "Savage Streets": collapse_pkgs,
    "Savannah": collapse_pkgs,
    "Schleiz, Saalfeld, Auerstaedt 1806": collapse_pkgs,
    "Schnell Boats: Scourge of the English Channel": collapse_pkgs,
    "Schutztruppe": None,
    "Schutztruppe: Heia Safari 1914-1918": collapse_pkgs,
    "Scorched Earth": None,
    "Scotland Yard": collapse_pkgs,
    "Scrabble": collapse_pkgs,
    "Scratch One Flat Top!": None,
    "ScratchDTL": None,
    "Screaming Eagles in Holland": None,
    "Scum Cards": collapse_pkgs,
    "Sea Rogue": collapse_pkgs,
    "Search & Destroy: Tactical Combat Vietnam – 1965-1966": collapse_pkgs,
    "Search for the Emperor's Treasure": collapse_pkgs,
    "Seas of Thunder: Global Naval Warfare, 1939-45": collapse_pkgs,
    "Second Bull Run 1862": collapse_pkgs,
    "Second Fallujah": collapse_pkgs,
    "Second Front": collapse_pkgs,
    "Secret Hitler": collapse_pkgs,
    "Sector 41": collapse_pkgs,
    "Seelöwe: The German Invasion of Britain, 1940": collapse_pkgs,
    "Sekigahara 1600": collapse_pkgs,
    "Sekigahara: Unification of Japan": None,
    "Semper Fi": None,
    "Semper Victor": collapse_pkgs,
    "Senet": collapse_pkgs,
    "Sengoku Main": None,
    "Sentinels of the Multiverse": collapse_pkgs,
    "Seofan": collapse_pkgs,
    "Serpents of the Seas": collapse_pkgs,
    "Set a Watch": collapse_pkgs,
    "Seven Card Samurai": collapse_pkgs,
    "Seven Pines": collapse_pkgs,
    "Seven Pines; or, Fair Oaks": collapse_pkgs,
    "Shadows Upon Lassadar": collapse_pkgs,
    "Shadows in the Weald": collapse_pkgs,
    "Shadows over Camelot": collapse_pkgs,
    "Shadows over Normandie": collapse_pkgs,
    "Shell Shock!": collapse_pkgs,
    "Shenandoah: Jackson's Valley Campaign": collapse_pkgs,
    "ShengJi": collapse_pkgs,
    "Sheridan in the Valley": collapse_pkgs,
    "Shifting Sands": None,
    "Shiloh: April 1862": collapse_pkgs,
    "Shining Path: The Struggle for Peru": collapse_pkgs,
    "Ship of the Line": collapse_pkgs,
    "Shklinc": collapse_pkgs,
    "Shogi": None,
    "Showtime Hanoi": collapse_pkgs,
    "Sicilia '43": collapse_pkgs,
    "Sicilian Tarot": None,
    "Sicily - Operation Husky": None,
    "Sicily II": None,
    "Sicily: The Race for Messina": None,
    "Sicily: Triumph and Folly": collapse_pkgs,
    "Sid Meier's Civilization: The Board Game": collapse_pkgs,
    "Siege at Peking": collapse_pkgs,
    "Sigismundus Augustus: Dei gratia rex Poloniae": collapse_pkgs,
    "Silent Death": collapse_pkgs,
    "Silent Death Annex: Operation – Dry Dock": collapse_pkgs,
    "Silent Victory: U.S. Submarines in the Pacific, 1941-45": collapse_pkgs,
    "Silent War": None,
    "Silent War + IJN (Second Edition)": None,
    "Silver Bayonet: The First Team in Vietnam, 1965": collapse_pkgs,
    "Silverton": None,
    "Simple Soccer": None,
    "Sinai: The Arab-Israeli Wars – '56, '67 and '73": collapse_pkgs,
    "Sixth Fleet": None,
    "Sixth Fleet: US/Soviet Naval Operations in the Mediterranean in the 1970's": collapse_pkgs,
    "Skies Above Britain": collapse_pkgs,
    "Skies Above the Reich": None,
    "Skirmish Wars: Advance Tactics": collapse_pkgs,
    "Sky Galleons of Mars": collapse_pkgs,
    "Skyhawk: Rolling Thunder, 1966": collapse_pkgs,
    "Skytear": collapse_pkgs,
    "Skytear Horde": collapse_pkgs,
    "Sleeping Gods: Primeval Peril": collapse_pkgs,
    "Sleuth": None,
    "Slouch Hats & Eggshells": collapse_pkgs,
    "Slurp Trek": collapse_pkgs,
    "Small World": collapse_pkgs,
    "Small World Underground": collapse_pkgs,
    "Smess: The Ninny's Chess": None,
    "Smithereens: The End of World War II in Europe": collapse_pkgs,
    "Smokejumpers": collapse_pkgs,
    "Smolensk 20": collapse_pkgs,
    "Smolensk: Barbarossa Derailed": None,
    "Snapshot": None,
    "Sneaking Mission: Solo": None,
    "Sniper Kill Confirmed": collapse_pkgs,
    "Sniper!": collapse_pkgs,
    "Snit's Revenge": collapse_pkgs,
    "Soldier King": collapse_pkgs,
    "Soldiers: Tactical Combat in 1914-15": collapse_pkgs,
    "Solferino 1859": collapse_pkgs,
    "Solitaire Caesar": collapse_pkgs,
    "Solitaire Chess": None,
    "Solomons Campaign: Air, Land, and Sea Warfare, Pacific 1942": collapse_pkgs,
    "Somaliland 1940": collapse_pkgs,
    "Somme 1918": collapse_pkgs,
    "Song of Blades and Heroes": collapse_pkgs,
    "Sorcerer": None,
    "Sorry!": None,
    "Soulgivers": collapse_pkgs,
    "Source of the Nile": None,
    "South China Sea": collapse_pkgs,
    "South Mountain": collapse_pkgs,
    "South Mountain (1984)": collapse_pkgs,
    "South Pacific: Breaking the Bismarck Barrier 1942-1943": collapse_pkgs,
    "Sovereign Of The Seas": collapse_pkgs,
    "Space Alert": None,
    "Space Crusade": collapse_pkgs,
    "Space Empires": collapse_pkgs,
    "Space Empires: 4X": collapse_pkgs,
    "Space Hulk: Death Angel - The Card Game": collapse_pkgs,
    "Space Infantry": collapse_pkgs,
    "Space Nazis from Hell": None,
    "Space Opera": None,
    "Space hulk": collapse_pkgs,
    "SpaceCorp": None,
    "Spanish Civil War Battles: Jarama, Brunete, Penarroya and Guadalajara": collapse_pkgs,
    "Spartacus Imperator": collapse_pkgs,
    "Spartacvs: Crisis in the Roman Republic, 80-71 BC": collapse_pkgs,
    "Speed Circuit": collapse_pkgs,
    "Sphactérie -425": None,
    "Spies!": collapse_pkgs,
    "Spirit island": collapse_pkgs,
    "Spitfire: Tactical Aerial Combat in Europe 1939-42": collapse_pkgs,
    "Splatball: Suburban Legend": None,
    "Sport of Kings: Germany 1740-45": collapse_pkgs,
    "Sports Illustrated Baseball": None,
    "Squad Leader": None,
    "Squaring Circleville": collapse_pkgs,
    "St-Lô": collapse_pkgs,
    "Stalin's War": collapse_pkgs,
    "Stalin's World War III": collapse_pkgs,
    "Stalingrad": None,
    "Stalingrad '42": collapse_pkgs,
    "Stalingrad Inferno on the Volga": collapse_pkgs,
    "Stalingrad Pocket (2nd Edition)": collapse_pkgs,
    "Stalingrad Roads: Battle on the Edge of the Abyss": None,
    "Stalingrad: Verdun on the Volga": collapse_pkgs,
    "Stand at Mortain": collapse_pkgs,
    "Star Fleet Battle Force": collapse_pkgs,
    "Star Fleet Battles Cadet Training Manual": collapse_pkgs,
    "Star Realms": collapse_pkgs,
    "Star Saga: One – Beyond The Boundary": collapse_pkgs,
    "Star Smuggler": collapse_pkgs,
    "Star Trader": collapse_pkgs,
    "Star Traders": None,
    "Star Trek III": None,
    "Star Trek: Ascendancy": collapse_pkgs,
    "Star Trek: Attack Wing": collapse_pkgs,
    "Star Trek: Catan": collapse_pkgs,
    "Star Trek: Expeditions": None,
    "Star Trek: Fleet Captains": None,
    "Star Trek: Starship Tactical Combat Simulator": None,
    "Star Trek: The Dice Game": collapse_pkgs,
    "Star Trek: The Game": None,
    "Star Viking": collapse_pkgs,
    "Star Wars Assorted Card Games": collapse_pkgs,
    "Star Wars Batalles espacials": collapse_pkgs,
    "Star Wars Episode I: Customizable Card Game": collapse_pkgs,
    "Star Wars Miniatures": None,
    "Star Wars Miniatures Starship Battles": None,
    "Star Wars PocketModel TCG": None,
    "Star Wars Silent Death": None,
    "Star Wars Tactics": None,
    "Star Wars: Armada": None,
    "Star Wars: Battle for Endor": None,
    "Star Wars: Epic Duels": None,
    "Star Wars: Imperial Assault": None,
    "Star Wars: Star Warriors": collapse_pkgs,
    "Star Wars: Top Trumps Tournament": collapse_pkgs,
    "Star Wars: X-Wing Miniatures Game": None,
    "StarCraft: The Board Game": None,
    "StarForce 'Alpha Centauri': Interstellar Conflict in the 25th Century": collapse_pkgs,
    "Starfire": None,
    "Stargate": None,
    "Starmada": collapse_pkgs,
    "Starmada: The Admiralty Edition": None,
    "Starship Troopers": None,
    "Starship Wars": collapse_pkgs,
    "Starship: Panic": None,
    "Starvation Island": collapse_pkgs,
    "Stationfall": collapse_pkgs,
    "Statis Pro Baseball": None,
    "Statis Pro Football": None,
    "Steam Power": collapse_pkgs,
    "Steampunk Rally": collapse_pkgs,
    "Steamroller: Tannenberg 1914": collapse_pkgs,
    "Steel Wolves: The German Submarine Campaign Against Allied Shipping - Vol 1": None,
    "Stellar Conquest": None,
    "Stellar Horizons": collapse_pkgs,
    "Sticks and Stones": collapse_pkgs,
    "Stilicho: Last of the Romans": collapse_pkgs,
    "Stock Market Guru": collapse_pkgs,
    "Stone's River": None,
    "Stones River 1862": collapse_pkgs,
    "Stonewall Jackson's Way": collapse_pkgs,
    "Stonewall Jackson's Way II": None,
    "Stonewall in the Valley": collapse_pkgs,
    "Stonewall's Last Battle": collapse_pkgs,
    "Stonewall: The Battle of Kernstown": collapse_pkgs,
    "Storm Above the Reich": collapse_pkgs,
    "Storm Over Arnhem": None,
    "Storm Over Asia": collapse_pkgs,
    "Storm Over Dien Bien Phu": collapse_pkgs,
    "Storm Over Jerusalem: The Roman Siege": collapse_pkgs,
    "Storm Over Madrid 1936: \"Miracle of November\"": collapse_pkgs,
    "Storm Over Normandy": collapse_pkgs,
    "Storm Over Stalingrad": None,
    "Storm of Steel: Ju-87 Stuka – Eastern Front": collapse_pkgs,
    "Storm over Scandinavia": collapse_pkgs,
    "Storming the Reich": collapse_pkgs,
    "Strada Romana": collapse_pkgs,
    "Strafexpedition 1916": collapse_pkgs,
    "Stratego": collapse_pkgs,
    "Strategos": collapse_pkgs,
    "Strategy I: Strategic Warfare 350BC to 1984": collapse_pkgs,
    "Strategy of War": collapse_pkgs,
    "Streets Of Stalingrad (3rd Edition)": None,
    "Strike Force One: The Cold War Heats Up – 1975": collapse_pkgs,
    "Strike Them a Blow: 1864 North Anna River": collapse_pkgs,
    "Strike of the Eagle": collapse_pkgs,
    "Strike: Counter Strike – 4th Armored Division vs Panzer Lehr along the Saar": collapse_pkgs,
    "Striking the Anvil: Operation Anvil Dragoon": collapse_pkgs,
    "Stronghold": None,
    "Struggle for Europe": collapse_pkgs,
    "Struggle of Empires": None,
    "Subatomic: An Atom Building Game": collapse_pkgs,
    "Submarine": collapse_pkgs,
    "Successors (2nd Edition)": None,
    "Successors (3rd Edition)": collapse_pkgs,
    "Suez '73": None,
    "Suffragetto": None,
    "Sumeria": collapse_pkgs,
    "Summer Storm: The Battle of Gettysburg": None,
    "Summoner Wars": None,
    "Summoner Wars (Second Edition)": collapse_pkgs,
    "Sun Orchid Elixir Sale": collapse_pkgs,
    "Sunburst City Transport": collapse_pkgs,
    "Super Dungeon Explore": None,
    "Super Fantasy Brawl": collapse_pkgs,
    "Super Quest": collapse_pkgs,
    "Supermarina": collapse_pkgs,
    "Supply Lines of the American Revolution: The Southern Strategy": collapse_pkgs,
    "Supply Lines of the American Revolution: the Northern Theatre, 1775-1777": collapse_pkgs,
    "Supremacy": collapse_pkgs,
    "Survive: Escape from Atlantis!": None,
    "Swashbuckler!": None,
    "Sweden Fights On": None,
    "Switchboard": None,
    "Sword and Sail": collapse_pkgs,
    "Sword of Rome": collapse_pkgs,
    "Swordplay!": None,
    "Swords & Sorcery: Quest and Conquest in the Age of Magic": collapse_pkgs,
    "Swords around the Throne": collapse_pkgs,
    "Syracuse (415/413 av. J.-C.)": collapse_pkgs,
    "T.I.M.E Stories": collapse_pkgs,
    "TAC AIR": collapse_pkgs,
    "TF22": collapse_pkgs,
    "TF22: LOAD!": collapse_pkgs,
    "TINYforming Mars": None,
    "TablaPeriodica": None,
    "Table Battles": None,
    "Tactics": None,
    "Tactics (25th Anniversary Edition)": None,
    "Tactics II": collapse_pkgs,
    "Tactiques Napoleon - Auerstadt": collapse_pkgs,
    "Tactiques Napoleon - Battle of Eckmuhl, April 21st 1809": None,
    "Tactiques Napoleon - Raszyn": None,
    "Tactiques Napoleon - Tamames": None,
    "Tactiques Napoleon - Teugn-Hausen": None,
    "Taifa: Intriga y guerra en la Hispania Medieval": collapse_pkgs,
    "Talavera & Vimeiro": collapse_pkgs,
    "Talisman": collapse_pkgs,
    "Talisman (3rd Edition)": collapse_pkgs,
    "Talon": None,
    "Talvisota 1939-1940: The Soviet-Finnish Winter War": collapse_pkgs,
    "Tammany Hall": collapse_pkgs,
    "Tank Commander: North Africa": collapse_pkgs,
    "Tank Commander: North Africa (Crusader Mk II)": collapse_pkgs,
    "Tank Commander: North Africa (Humber Mk II)": collapse_pkgs,
    "Tank Commander: North Africa (M3A1 Stewart)": collapse_pkgs,
    "Tank Commander: The Ardennes": collapse_pkgs,
    "Tank Duel: Enemy in the Crosshairs": collapse_pkgs,
    "Tank on Tank": collapse_pkgs,
    "Tank on Tank: East Front": collapse_pkgs,
    "Tank on Tank: West Front": collapse_pkgs,
    "Tanktics: Computer Game of Armored Combat on the Eastern Front": collapse_pkgs,
    "Tannenberg 1914": collapse_pkgs,
    "Tannenberg 1914 (1990)": None,
    "Tannenberg: Eagles in the East / Galicia: The Forgotten Cauldron": collapse_pkgs,
    "Tannhauser": collapse_pkgs,
    "Tarawa 1943": collapse_pkgs,
    "Tarawa Red Beach One": collapse_pkgs,
    "Target Arnhem, Across Six Bridges": None,
    "Target for Today": collapse_pkgs,
    "Target for Tonight: Britain's Strategic Air Campaign Over Europe, 1942-1945": collapse_pkgs,
    "Target: Leningrad": collapse_pkgs,
    "Targui": collapse_pkgs,
    "Tarot, Tarock & Tarocchi Games": None,
    "Tash-Kalar: Arena of Legends": collapse_pkgs,
    "Task Force: Carrier Battles in the Pacific": collapse_pkgs,
    "TaskForce: Naval Tactics and Operations in the 1980's": collapse_pkgs,
    "Tatchanka: Ukraine, 1919-21": None,
    "Team Yankee": collapse_pkgs,
    "Techno Bowl: Arcade Football Unplugged": collapse_pkgs,
    "Temporum": collapse_pkgs,
    "Tempête sur Dixmude 1914": collapse_pkgs,
    "Tenka: Shogun Edition": collapse_pkgs,
    "Tenkatoitsu": None,
    "Tennis": None,
    "Terraforming Mars": None,
    "Terrible Swift Sword: Battle of Gettysburg Game": collapse_pkgs,
    "Test of Faith: The Arab-Israeli War of 1973": collapse_pkgs,
    "Test of Fire: Bull Run 1861": collapse_pkgs,
    "Tet Offensive": None,
    "Tetrarchia": collapse_pkgs,
    "Teutons!: Assaults on the West, 1870-1940": collapse_pkgs,
    "Texas Glory": collapse_pkgs,
    "Texas Revolution": None,
    "The 6 Days of Glory": collapse_pkgs,
    "The 7th Continent": collapse_pkgs,
    "The African Campaign": collapse_pkgs,
    "The African Campaign: Designer Signature Edition": collapse_pkgs,
    "The Air-Eaters Strike Back!": collapse_pkgs,
    "The Alamo": collapse_pkgs,
    "The Alamo: Victory in Death": None,
    "The American Civil War": collapse_pkgs,
    "The American Revolution 1775-1783": collapse_pkgs,
    "The American Revolution: Decision in North America": collapse_pkgs,
    "The Arab-Israeli Wars": None,
    "The Ardennes Offensive: The Battle of the Bulge, December 1944": collapse_pkgs,
    "The Arduous Beginning": collapse_pkgs,
    "The Ark of the Covenant": None,
    "The Army of the Heartland: The Army of Tennessee's Campaigns, 1861-1863": collapse_pkgs,
    "The Art of Siege": None,
    "The Awful Green Things From Outer Space": collapse_pkgs,
    "The Balkan Wars: Prelude to Disaster, 1912-1913": None,
    "The Barracks Emperors": collapse_pkgs,
    "The Baton Races of Yaz": None,
    "The Battle for Iwo Jima": collapse_pkgs,
    "The Battle for Jerusalem 1967": collapse_pkgs,
    "The Battle for Normandy": collapse_pkgs,
    "The Battle of Adobe Walls": collapse_pkgs,
    "The Battle of Agincourt": None,
    "The Battle of Armageddon: Deluxe Edition": collapse_pkgs,
    "The Battle of Austerlitz, December 2, 1805": collapse_pkgs,
    "The Battle of Blenheim, 1704": collapse_pkgs,
    "The Battle of Borodino: Napoleon in Russia 1812": collapse_pkgs,
    "The Battle of Brandywine": None,
    "The Battle of Camden, S.C.": None,
    "The Battle of Corinth: Standoff at the Tennessee, October 3-4, 1862": None,
    "The Battle of Fontenoy, 11 May, 1745": collapse_pkgs,
    "The Battle of Guilford Courthouse": None,
    "The Battle of Lobositz": None,
    "The Battle of Monmouth": collapse_pkgs,
    "The Battle of Monmouth (1982)": None,
    "The Battle of Moscow : The German Drive on Moscow, 1941": collapse_pkgs,
    "The Battle of Prague": None,
    "The Battle of Raphia": None,
    "The Battle of Saratoga": None,
    "The Battle of Tanga 1914": collapse_pkgs,
    "The Battle of Wakefield": collapse_pkgs,
    "The Battle of the Alma": None,
    "The Battle of the Bulge": None,
    "The Battles of Bull Run: Manassas – June 1861 and August 1862": collapse_pkgs,
    "The Battles of Mollwitz 1741 and Chotusitz 1742": collapse_pkgs,
    "The Battles of the Seven Days": collapse_pkgs,
    "The Bells Toll for Madrid: Franco´s Offensive against Madrid, Oct-Nov 1936": collapse_pkgs,
    "The Big Push: The Battle of the Somme": collapse_pkgs,
    "The Blitzkrieg Legend: The Battle for France, 1940": collapse_pkgs,
    "The Boss": collapse_pkgs,
    "The British Way: Counterinsurgency at the End of Empire": collapse_pkgs,
    "The Burning Blue": None,
    "The Campaign for North Africa: The Desert War 1940-43": None,
    "The Campaigns of King David": collapse_pkgs,
    "The Campaigns of Robert E. Lee": collapse_pkgs,
    "The Castles of Burgundy: The Card Game": collapse_pkgs,
    "The Caucasus Campaign: The Russo-German War in the Caucasus, 1942": collapse_pkgs,
    "The Chaco War": collapse_pkgs,
    "The China War: Sino-Soviet Conflict in the 1980s": collapse_pkgs,
    "The City of Kings": collapse_pkgs,
    "The Civil War": None,
    "The Company War": collapse_pkgs,
    "The Conquerors: Alexander the Great": collapse_pkgs,
    "The Conquistadors: The Spanish Conquest of the Americas 1518-1548": collapse_pkgs,
    "The Cost": collapse_pkgs,
    "The Creature That Ate Sheboygan": None,
    "The Crusades: Western Invasions of the Holy Land": None,
    "The Damned Die Hard: Philippines '41": collapse_pkgs,
    "The Dark Sands": collapse_pkgs,
    "The Dark Summer: Normandy 1944": collapse_pkgs,
    "The Dark Valley": None,
    "The Deadly Woods: The Battle of the Bulge": collapse_pkgs,
    "The Desert Fox: Rommel's Campaign for North Africa April 1941-December 1942": None,
    "The Devil's Cauldron": None,
    "The Devil's To Pay": None,
    "The Devil's To Pay! The First Day at Gettysburg": collapse_pkgs,
    "The Doomsday Project: Episode 1 – The Battle for Germany": collapse_pkgs,
    "The Doomsday Project: Episode 2 – The Battle for the Balkans": collapse_pkgs,
    "The Downfall of Pompeii": collapse_pkgs,
    "The Draugr": None,
    "The Drive on Metz, 1944": None,
    "The Drive on Metz, 1944 (Second Edition)": collapse_pkgs,
    "The Dungeon of D": collapse_pkgs,
    "The East is Red: The Sino Soviet War": collapse_pkgs,
    "The Emperor Returns": collapse_pkgs,
    "The End of the Triumvirate": collapse_pkgs,
    "The Everlasting Glory: Chinese War of Resistance 1937-1945": collapse_pkgs,
    "The Fall of France": collapse_pkgs,
    "The Fall of Rome": collapse_pkgs,
    "The Fall of Tobruk: Rommel's Greatest Victory": collapse_pkgs,
    "The Fast Carriers: Air-Sea Operations, 1941-77": None,
    "The Fellowship of the Ring": collapse_pkgs,
    "The Fighting General Patton": None,
    "The Fires of Midway": collapse_pkgs,
    "The First World War": collapse_pkgs,
    "The Flight of the Goeben": collapse_pkgs,
    "The Fog of War": None,
    "The Forgotten Battles: The Battle For Belorussia": collapse_pkgs,
    "The Franco-Prussian War": collapse_pkgs,
    "The Franco-Prussian War: August 1 to September 2, 1870": collapse_pkgs,
    "The Fulda Gap: The Battle for the Center": collapse_pkgs,
    "The Game of Shakespeare": None,
    "The Grand Campaign": collapse_pkgs,
    "The Grand Trunk Journey": collapse_pkgs,
    "The Great Crisis of Frederick II": collapse_pkgs,
    "The Great Game": collapse_pkgs,
    "The Great Heathen Army": collapse_pkgs,
    "The Great Invasion: The Gettysburg Campaign June 24 – July 3, 1863": collapse_pkgs,
    "The Great War": collapse_pkgs,
    "The Great War in Europe: Deluxe Edition": collapse_pkgs,
    "The Great War in the East: Four World War 1 Battles": None,
    "The Greatest Day: Sword, Juno, and Gold Beaches": None,
    "The Grunwald Swords": None,
    "The Guns of August": None,
    "The Guns of Gettysburg": collapse_pkgs,
    "The Halls of Montezuma": collapse_pkgs,
    "The Hell of Stalingrad": collapse_pkgs,
    "The Hellgame": collapse_pkgs,
    "The High Crusade": None,
    "The Hunted: Twilight of the U-Boats, 1943-45": collapse_pkgs,
    "The Hunters: German U-Boats at War, 1939-43": None,
    "The Invasion of Russia (1812)": collapse_pkgs,
    "The Invincible Armada 1588 AD": collapse_pkgs,
    "The Jaws of Victory: Battle of Korsun-Cherkassy Pocket – January/February 1944": collapse_pkgs,
    "The Kaiser's Pirates": None,
    "The Killing Ground": collapse_pkgs,
    "The Korean War": None,
    "The Korean War: June 1950 - May 1951": collapse_pkgs,
    "The Lamps Are Going Out": collapse_pkgs,
    "The Last Gamble: The Ardennes Offensive, December 1944 – Designer Signature Edition": collapse_pkgs,
    "The Last Hundred Yards": collapse_pkgs,
    "The Last Hundred Yards Mission Pack 1": collapse_pkgs,
    "The Last Hundred Yards Volume 2: Airborne Over Europe": collapse_pkgs,
    "The Last Hundred Yards Volume 3: The Solomon Islands": collapse_pkgs,
    "The Last Hundred Yards: Volume 4 – The Russian Front": collapse_pkgs,
    "The Last Success: Napoleon's March to Vienna, 1809": collapse_pkgs,
    "The Last Victory": collapse_pkgs,
    "The Late Unpleasantness: Two Campaigns to take Richmond": None,
    "The Legend Begins": collapse_pkgs,
    "The Legend of Robin Hood": collapse_pkgs,
    "The Legend of Zelda": collapse_pkgs,
    "The Legend of Zelda: Epic Duels": collapse_pkgs,
    "The Little Land: The Battle for Novorossiysk": collapse_pkgs,
    "The Little Prince: Make Me a Planet": collapse_pkgs,
    "The Long Road": collapse_pkgs,
    "The Longest Day": None,
    "The Lord of the Rings: The Card Game": None,
    "The Lords of Underearth": None,
    "The March on India, 1944": collapse_pkgs,
    "The Marne: Home Before the Leaves Fall": collapse_pkgs,
    "The Measure of the Earth": collapse_pkgs,
    "The Mighty Endeavor": None,
    "The Moscow Campaign: Strike and Counterstrike Russia": collapse_pkgs,
    "The Napoleonic Wars": None,
    "The Napoleonic Wars (Second Edition)": collapse_pkgs,
    "The New Era": collapse_pkgs,
    "The Next War": None,
    "The Next War: Modern Conflict in Europe": collapse_pkgs,
    "The Official Dealer McDope Dealing Game": collapse_pkgs,
    "The Oregon Trail Card Game": None,
    "The Other Side": None,
    "The Peiper Dream": collapse_pkgs,
    "The Peloponnesian War, 431-404 BC": None,
    "The Picrocholine Wars": collapse_pkgs,
    "The Plot to Assassinate Hitler": collapse_pkgs,
    "The Plum Island Horror": collapse_pkgs,
    "The Polls are Closed!": collapse_pkgs,
    "The Punic Wars: Rome vs Carthage, 264-146 B.C.": collapse_pkgs,
    "The Pursuit of von Spee": collapse_pkgs,
    "The Razor's Edge": collapse_pkgs,
    "The Red Dragon Inn": collapse_pkgs,
    "The Republic of Rome": None,
    "The Resistance": collapse_pkgs,
    "The Return of the Stainless Steel Rat": None,
    "The Rise of the Roman Republic: The Ancient World, Vol. 1": collapse_pkgs,
    "The Road to Cheren": collapse_pkgs,
    "The Royal Navy": collapse_pkgs,
    "The Rum Run": collapse_pkgs,
    "The Russian Campaign": None,
    "The Sands of War": collapse_pkgs,
    "The Scheldt Campaign": collapse_pkgs,
    "The Second World War": collapse_pkgs,
    "The Seven Days of 1809": collapse_pkgs,
    "The Shores of Tripoli": collapse_pkgs,
    "The Siege of Alesia": collapse_pkgs,
    "The Siege of Barad-Dur 3430": None,
    "The Siege of Jerusalem": None,
    "The Siege of Leningrad": collapse_pkgs,
    "The Siege of Orgun": collapse_pkgs,
    "The Soo Line": collapse_pkgs,
    "The Spanish Civil War": collapse_pkgs,
    "The Spanish Civil War 1936-1939": collapse_pkgs,
    "The Speed of Heat": collapse_pkgs,
    "The Stock Market Game": collapse_pkgs,
    "The Struggle of Nations": None,
    "The Succession Wars": None,
    "The Sun of Austerlitz": collapse_pkgs,
    "The Supreme Commander": collapse_pkgs,
    "The Sword and the Stars": None,
    "The Third Winter: The Battle for the Ukraine September 1943-April 1944": collapse_pkgs,
    "The Third World War": None,
    "The Third World War: Designer Signature Edition": collapse_pkgs,
    "The Three Days of Gettysburg (third edition)": None,
    "The Tide at Sunrise: The Russo-Japanese War 1904-1905": collapse_pkgs,
    "The Twelve Doctors: Doctor Who Card Game": collapse_pkgs,
    "The U.S. Civil War": collapse_pkgs,
    "The War At Sea (first edition)": collapse_pkgs,
    "The War for the Union": collapse_pkgs,
    "The War of Jenkins' Ear": None,
    "The War: The Pacific 1941-45": collapse_pkgs,
    "The Warlord Game": None,
    "The Warriors of Batak": collapse_pkgs,
    "The Way of the Warrior (Second Edition)": None,
    "The Wilderness Campaign: Lee vs. Grant, 1864": collapse_pkgs,
    "The Wolves": collapse_pkgs,
    "The World at War: Europe": collapse_pkgs,
    "The Wreck of the B.S.M. Pandora": collapse_pkgs,
    "The d6 Shooters": collapse_pkgs,
    "Their Finest Hour": collapse_pkgs,
    "Theseus: The Dark Orbit": collapse_pkgs,
    "Thirty Years War": collapse_pkgs,
    "Thirty Years War Quad": None,
    "Thirty Years War: Europe in Agony, 1618 - 1648": collapse_pkgs,
    "This Accursed Civil War": None,
    "This Guilty Land": collapse_pkgs,
    "This Hallowed Ground": collapse_pkgs,
    "This Terrible Sound": collapse_pkgs,
    "This War Without an Enemy": collapse_pkgs,
    "Thoughtwave": None,
    "Three Battles of Manassas": collapse_pkgs,
    "Three Days of Glory 1805": None,
    "Throne of Allegoria": collapse_pkgs,
    "Through the Ages: A Story of Civilization": collapse_pkgs,
    "Through the Breach": None,
    "Thud Ridge: A Solitaire Game of the Air War over North Vietnam": collapse_pkgs,
    "Thud and Blunder": collapse_pkgs,
    "Thunder Alley": collapse_pkgs,
    "Thunder Road: Vendetta": collapse_pkgs,
    "Thunder at Cassino": None,
    "Thunder at the Crossroads (2nd Edition)": None,
    "Thunder on the Mississippi: Grant's Vicksburg Campaign": collapse_pkgs,
    "Thunderbolt / Apache Leader": collapse_pkgs,
    "Thunderstone": collapse_pkgs,
    "Tic Tac Chec": collapse_pkgs,
    "Tic-Tac-Toe": None,
    "Ticket to Ride Map Collection: Volume 3 – The Heart of Africa": collapse_pkgs,
    "Ticket to Ride: Europe": collapse_pkgs,
    "Tide Of Iron": None,
    "Tigers In The Mist": collapse_pkgs,
    "Tigris & Euphrates": None,
    "Tiles and Figs": collapse_pkgs,
    "Time of Crisis": collapse_pkgs,
    "Timetripper": collapse_pkgs,
    "Tinian: The Forgotten Battle": collapse_pkgs,
    "Tiny Epic Galaxies": collapse_pkgs,
    "Titan": collapse_pkgs,
    "Titan Strike!": None,
    "Title Bout": None,
    "To Be King": collapse_pkgs,
    "To Take Washington: Jubal Early's Summer 1864 Campaign": collapse_pkgs,
    "To The Far Shore": collapse_pkgs,
    "To The Last Man": collapse_pkgs,
    "To the Green Fields Beyond: The Battle of Cambrai, 1917": collapse_pkgs,
    "Tobruk: Tank Battles in North Africa 1942": collapse_pkgs,
    "Tokyo Express": collapse_pkgs,
    "Tomb Raider": None,
    "Tomorrow the World": collapse_pkgs,
    "Tonkin: The Indochina war 1950-54 (2nd edition)": collapse_pkgs,
    "Tonnage War Solitaire": None,
    "Too many Bones": collapse_pkgs,
    "Torch": collapse_pkgs,
    "Torgau": None,
    "Torgau 1760": collapse_pkgs,
    "Total War": collapse_pkgs,
    "Totaler Krieg!": None,
    "Totaler Krieg! (2nd Edition) / Dai Senso": None,
    "Toulon, 1793": collapse_pkgs,
    "Tourcoing 1794": collapse_pkgs,
    "Traces of Hubris": collapse_pkgs,
    "Traces of War": collapse_pkgs,
    "Trader": collapse_pkgs,
    "Trafalgar": None,
    "Trailblazer Starmap": collapse_pkgs,
    "Trajan: Ancient Wars Series Expansion Kit": collapse_pkgs,
    "Transformers Trading Card Game": collapse_pkgs,
    "Trenches of Valor": collapse_pkgs,
    "Trenton 1776": collapse_pkgs,
    "Triomphe á Marengo": collapse_pkgs,
    "Triple Topper": None,
    "Trippples": collapse_pkgs,
    "Trireme: Tactical Game of Ancient Naval Warfare 494 BC-370 AD": collapse_pkgs,
    "Triumph & Glory: Battles of the Napoleonic Wars 1796-1809": collapse_pkgs,
    "Triumph & Tragedy": collapse_pkgs,
    "Triumph of Chaos": None,
    "Triumph of Chaos v.2 (Deluxe Edition)": None,
    "Triumph of the Will": collapse_pkgs,
    "Trivial Wars": collapse_pkgs,
    "Trollland": collapse_pkgs,
    "Tsukuyumi:Full Moon Down": collapse_pkgs,
    "Tsuro": collapse_pkgs,
    "Tuf": None,
    "Tuf-abet": None,
    "TuiShou7": collapse_pkgs,
    "Tunisia": collapse_pkgs,
    "Tunisia II": collapse_pkgs,
    "Tupamaro": collapse_pkgs,
    "Turncoats": collapse_pkgs,
    "Turning Point": collapse_pkgs,
    "Turning Point Stalingrad": collapse_pkgs,
    "Turning Point: The Battle of Stalingrad": collapse_pkgs,
    "Twilight Imperium (third Edition)": collapse_pkgs,
    "Twilight Imperium (third Edition): Shards of the Throne": collapse_pkgs,
    "Twilight Imperium (third Edition): Shattered Empire": collapse_pkgs,
    "Twilight Imperium: Fourth Edition": collapse_pkgs,
    "Twilight Sparkle's Secret Shipfic Folder": None,
    "Twilight Struggle": None,
    "Twin Peaks": collapse_pkgs,
    "Twixt": None,
    "Two Deck Siege": collapse_pkgs,
    "Typhoon!": collapse_pkgs,
    "Tyros": None,
    "Türkenkrieg (1737-1739)": None,
    "U-Boat": None,
    "U.E.F.A.": collapse_pkgs,
    "U.S.N.: The Game of War in the Pacific, 1941-43": None,
    "UND1C1": collapse_pkgs,
    "USN Deluxe": None,
    "Ubi": collapse_pkgs,
    "Ukraine '43": None,
    "Ukraine '44": collapse_pkgs,
    "Ukrainian Crisis": collapse_pkgs,
    "Ukrainian Crisis & The Little War": collapse_pkgs,
    "Ultima Ratio Regis": collapse_pkgs,
    "Una Vittoria Impossibile: Le Barricate di Parma del 1922": collapse_pkgs,
    "Una Vittoria Inutile, Goito 1848": collapse_pkgs,
    "Unbroken": collapse_pkgs,
    "Uncharted: The Board Game": collapse_pkgs,
    "Unconditional Surrender! Case Blue": collapse_pkgs,
    "Unconditional Surrender! World War 2 in Europe": None,
    "Undaunted: Normandy": collapse_pkgs,
    "Under the Lily Banners": None,
    "Under the Southern Cross: The South American Republics in the Age of the Fighting Sail": collapse_pkgs,
    "Une décennie dans les tranchées: Guerre Iran-Irak 1980-1988": None,
    "Unhappy King Charles": collapse_pkgs,
    "Universe": collapse_pkgs,
    "Universe Risk": collapse_pkgs,
    "Unmatched: Battle of Legends, Volume One": collapse_pkgs,
    "Unternehmen Rösselsprung: Caccia a Tito": collapse_pkgs,
    "Unterseeboot: U-Boat Solitaire": collapse_pkgs,
    "Up Front": None,
    "Up Front Nam": None,
    "Up Scope! Tactical Submarine Warfare in the 20th Century": collapse_pkgs,
    "Upon A Salty Ocean": collapse_pkgs,
    "Upwords": None,
    "Ur": collapse_pkgs,
    "Urban Operations": collapse_pkgs,
    "Urban Sprawl": collapse_pkgs,
    "Urban War": collapse_pkgs,
    "Urbino": collapse_pkgs,
    "Urrah!": collapse_pkgs,
    "Utopia Engine": collapse_pkgs,
    "V-Commandos": None,
    "VCS Salerno": collapse_pkgs,
    "VI Caesars": collapse_pkgs,
    "Vae Victis": collapse_pkgs,
    "Valley of Tears: The Yom Kippur War, 1973": collapse_pkgs,
    "Valor and Victory": None,
    "Vampire the Masquerade: Redmoon River": collapse_pkgs,
    "Vampires' Dance": collapse_pkgs,
    "Vampyre": collapse_pkgs,
    "Vast: The Crystal Caverns": collapse_pkgs,
    "Vector 3": None,
    "Veracruz: U.S. Invasion of Mexico 1847": collapse_pkgs,
    "Verdun 1916: Steel Inferno": collapse_pkgs,
    "Verdun, The Game of Attrition": collapse_pkgs,
    "Verdun: A Generation Lost": None,
    "Versailles 1919": collapse_pkgs,
    "Victoria Cross": None,
    "Victory Roads": collapse_pkgs,
    "Victory at Midway": collapse_pkgs,
    "Victory at Sea": collapse_pkgs,
    "Victory in Europe": None,
    "Victory in Normandy": collapse_pkgs,
    "Victory in Vietnam": collapse_pkgs,
    "Victory in the Pacific": None,
    "Victory: The Blocks of War": None,
    "Vietnam 1965-1975": None,
    "Vietnam: Rumor of War": collapse_pkgs,
    "Vijayanagara The Deccan Empires of Medieval India 1290-1398": collapse_pkgs,
    "Village Builder": collapse_pkgs,
    "Vinci": collapse_pkgs,
    "Vinegar Joe's War: CBI": None,
    "Vino": collapse_pkgs,
    "Virgin Queen": collapse_pkgs,
    "Virtual Valhalla": None,
    "Vittoria 20": collapse_pkgs,
    "Viva Zapata!": collapse_pkgs,
    "Vive L'Empereur!": collapse_pkgs,
    "Vive l'Empereur Advance": collapse_pkgs,
    "Volition CCG": collapse_pkgs,
    "Volteface": collapse_pkgs,
    "Von Manstein's Backhand Blow": collapse_pkgs,
    "Voyage of the B.S.M. Pandora": None,
    "WARLINE: Maneuver Strategy & Tactics": collapse_pkgs,
    "WTF1940 - The Breakthrough at Dinant": collapse_pkgs,
    "WW2 Skirmish": collapse_pkgs,
    "WWII Commander: Volume One – Battle Of The Bulge": collapse_pkgs,
    "WWII: Barbarossa to Berlin": collapse_pkgs,
    "Wabash Cannonball": collapse_pkgs,
    "Wacht am Rhein': The Battle of the Bulge, 16 Dec 44-2 Jan 45": None,
    "Wagon Wheel Chess": None,
    "Walcheren 1809": collapse_pkgs,
    "Walcheren of Somnium": collapse_pkgs,
    "War At Sea": None,
    "War Between The States 1861-1865": collapse_pkgs,
    "War Chest": collapse_pkgs,
    "War Galley": collapse_pkgs,
    "War In The East: The Russo-German Conflict, 1941-45 (Second Edition)": collapse_pkgs,
    "War and Peace": None,
    "War for America: The American Revolution, 1775-1782": collapse_pkgs,
    "War in Europe": collapse_pkgs,
    "War in the Desert": collapse_pkgs,
    "War in the Ice: The Battle for the Seventh Continent": collapse_pkgs,
    "War in the Outposts - The Europa Magazine": None,
    "War in the Pacific: The Campaign Against Imperial Japan, 1941-45": None,
    "War in the Pampas": collapse_pkgs,
    "War in the Wind: The Battle of Attu Island, 1943": None,
    "War of 1812": collapse_pkgs,
    "War of Resistance": collapse_pkgs,
    "War of the Lance": None,
    "War of the Ring": collapse_pkgs,
    "War of the Ring (1977)": collapse_pkgs,
    "War of the Suns": collapse_pkgs,
    "War to the Death": collapse_pkgs,
    "Warage": None,
    "Warburg 1760": collapse_pkgs,
    "Warchestra (Classic)": None,
    "Warhammer 40,000": collapse_pkgs,
    "Warhammer Skirmish": collapse_pkgs,
    "Warhammer: Age Of Sigmar": collapse_pkgs,
    "Warhammer: Diskwars": collapse_pkgs,
    "Warmachine": collapse_pkgs,
    "WarpWar": None,
    "Warplan: Dropshot II - The Turbulent '60s": None,
    "Warplan: Dropshot III - Endgames": None,
    "Warrior Knights": None,
    "Warriors of God": collapse_pkgs,
    "Wars of Marcus Aurelius: Rome 170-180CE": collapse_pkgs,
    "Wars of Religion, France 1562-1598": collapse_pkgs,
    "Washington's Crossing": collapse_pkgs,
    "Washington's War": None,
    "Watergate": collapse_pkgs,
    "Waterloo": None,
    "Waterloo (2009)": collapse_pkgs,
    "Waterloo (by International Team)": collapse_pkgs,
    "Waterloo 1815 : Fallen Eagles": collapse_pkgs,
    "Waterloo 1815: Fallen Eagles II": collapse_pkgs,
    "Waterloo 20": collapse_pkgs,
    "Waterloo 200": collapse_pkgs,
    "Waterloo Campaign 1815": collapse_pkgs,
    "Waterloo: l'ultima battaglia di Napoleone": collapse_pkgs,
    "Wave of Terror: Battle of the Bulge": collapse_pkgs,
    "Wavell's War": None,
    "Way of the Ninja: Capture the Shoguns Enemies!": collapse_pkgs,
    "We The People": collapse_pkgs,
    "We the People, 1787": collapse_pkgs,
    "Web and Starship": collapse_pkgs,
    "Weimar The Fight For Democracy": None,
    "Wellington": None,
    "Wellington's Victory: Battle of Waterloo Game – June 18th, 1815": collapse_pkgs,
    "Wellington's War: The Peninsular Campaign 1809-1814": collapse_pkgs,
    "Western Desert": None,
    "Western Front Ace: The Great Air War 1916-1918": None,
    "Western Legends": collapse_pkgs,
    "Western Town": collapse_pkgs,
    "Westpac 1978": collapse_pkgs,
    "Westphalia": None,
    "Westwall: Four Battles to Germany": None,
    "What Price Glory?": collapse_pkgs,
    "Wheels of Time": collapse_pkgs,
    "Where Eagles Dare": collapse_pkgs,
    "Where There is Discord": collapse_pkgs,
    "White Eagle Defiant: Poland 1939": collapse_pkgs,
    "White Star Rising: Airborne": collapse_pkgs,
    "White Star Rising: Operation Cobra": collapse_pkgs,
    "Whitehall Mystery": collapse_pkgs,
    "Why": collapse_pkgs,
    "Wild Blue Yonder": collapse_pkgs,
    "Wilderness Empires": collapse_pkgs,
    "Wilderness War": collapse_pkgs,
    "Wilson's Creek: The West's First Fight, August 10, 1861": collapse_pkgs,
    "Win Place & Show": None,
    "Wing Commander": None,
    "Wing Commander Armada PNP": None,
    "Wing Leader": None,
    "Wings": collapse_pkgs,
    "Wingspan": collapse_pkgs,
    "Winter Storm": collapse_pkgs,
    "Winter Storm: 57th Pz Korps Attempt to Relieve Stalingrad": collapse_pkgs,
    "Winter War": None,
    "Winter's Victory: The Battle of Preussisch-Eylau, 7-8 February 1807": collapse_pkgs,
    "Wir sind das Volk!": collapse_pkgs,
    "Wir sind das Volk! 2+2": collapse_pkgs,
    "Wise Bayonets": collapse_pkgs,
    "Wissembourg et Spicheren 1870: Premiers combats en Alsace-Lorraine": collapse_pkgs,
    "With It Or On It": collapse_pkgs,
    "Wizard Kings": None,
    "Wizard's Quest": None,
    "Wizards": None,
    "Wizna 1939": collapse_pkgs,
    "Wolf": collapse_pkgs,
    "Wolfpack: Submarine Warfare in the North Atlantic 1942-44": collapse_pkgs,
    "Wolfpack: The North Atlantic Convoy Struggles October 1941-March 1943": collapse_pkgs,
    "Won by the Sword": collapse_pkgs,
    "Wongar": collapse_pkgs,
    "Wooden Ships & Iron Men": None,
    "Word War - Competitive Crossword Game": None,
    "World At War 85: Starter Kit": collapse_pkgs,
    "World At War 85: Storming the Gap": None,
    "World At War 85: Storming the Gap – Storm and Steel Second Wave": collapse_pkgs,
    "World Killer": collapse_pkgs,
    "World War 3: 1976-1984": collapse_pkgs,
    "World War I": None,
    "World War II: European Theater of Operations": None,
    "World War II: European Theater of Operations, 1939-45": collapse_pkgs,
    "World War II: Pacific Theater of Operations": None,
    "World at War": None,
    "World at War 85: Storming the Gap – The Defense of Frankfurt": collapse_pkgs,
    "World in Flames": None,
    "World of Warcraft Miniatures Game": None,
    "World of Warcraft the Boardgame": collapse_pkgs,
    "Worlds Of Legend": collapse_pkgs,
    "Wrasslin'": None,
    "Wreckage": None,
    "Wu Wei: Journey of the Changing Path": collapse_pkgs,
    "Wurzburg: Soviet-American Combat in the '70's": collapse_pkgs,
    "X-Men: Mutant Insurrection": collapse_pkgs,
    "Xiang Qi": collapse_pkgs,
    "YINSH": None,
    "Yahtzee": None,
    "Yalu (2nd edition)": collapse_pkgs,
    "Yamatai": collapse_pkgs,
    "Yardmaster Express": None,
    "Yavalath": collapse_pkgs,
    "Ye Gods!": collapse_pkgs,
    "Year of the Rat: Vietnam, 1972": collapse_pkgs,
    "Yellowstone": None,
    "Yggdrasil": None,
    "Yom Kippur": collapse_pkgs,
    "Yom Kippur (1983)": collapse_pkgs,
    "York Town": collapse_pkgs,
    "Yu-Gi-Oh! Dice Masters": collapse_pkgs,
    "Yu-Gi-Oh! DungeonDice Monsters": None,
    "Yugoslavia: The Battles for Zagreb, 1979": collapse_pkgs,
    "Yuyu-Manji": None,
    "Z-G Resurgence": None,
    "Zama": collapse_pkgs,
    "Zeppelin Raider": collapse_pkgs,
    "Zero!": collapse_pkgs,
    "Zero-Sum": None,
    "Zombie Dice": collapse_pkgs,
    "Zombie In My Pocket": None,
    "Zombie Plague": collapse_pkgs,
    "Zombies!!!": collapse_pkgs,
    "Zorndorf": collapse_pkgs,
    "ZotzBrothers Chess War Level One": None,
    "Zulu Attack": None,
    "Zulu: Isandhlwana": None,
    "Zulu: Naka": None,
    "Zulu: Rorke's Drift": None,
    "Zulu: Ulundi": None,
    "Zulus on the Ramparts!: The Battle of Rorke's Drift – Second Edition": collapse_pkgs,
    "Zürich 1799": collapse_pkgs,
}


release_fixups = {
    "'CA' Tactical Naval Warfare in the Pacific, 1941-45": version_to_release,
    "13 Dead End Drive": version_to_release,
    "1776": use_pkgs,
    "1809: Napoleons Danube Campaign": x1809_napoleons_danube_campaign,
    "1812: The Campaign of Napoleon in Russia": x1812_the_campaign,
    "18xx": x18xx,
    "1914: Glory's End / When Eagles Fight": x1914_glorys_end,
    "1936: Guerra Civil": version_to_release,
    "1st Alamein": x1stAlamein,
    "7 Ages": version_to_release,
    "8th Army: Operation Crusader": x8thArmy,
    "A House Divided": a_house_divided,
    "A Splendid Little War: The 1898 Santiago Campaign": a_splendid_little_war,
    "A Thunder Upon the Land: The Battles of Narva and Poltava": version_to_release,
    "A Time for Trumpets: The Battle of the Bulge, December 1944": a_time_for_trumpets,
    "A las Barricadas! (2nd Edition)": a_las_barricadas_2ed,
    "Across Suez": version_to_release,
    "Advanced Pacific Theater of Operations": version_to_release,
    "AFTERSHOCK: A Humanitarian Crisis Game": aftershock,
    "Across 5 Aprils": across_5_aprils,
    "Age Of Steam": version_to_release,
    "Air Assault on Crete": air_assault_on_crete,
    "All-Star Baseball": version_to_release,
    "Annihilator / OneWorld": annihilator,
    "Ardennes '44": ardennes_44,
    "Arkwright": arkwright,
    "Arrakhar's Wand": arrakhars_wand,
    "Arquebus: Men of Iron Volume IV": arquebus,
    "Assault on Hoth: The Empire Strikes Back": assault_on_hoth,
    "Assault on Mt Everest": version_to_release,
    "Atlanta: Civil War Campaign Game": version_to_release,
    "Atlantic Wall: The Invasion of Europe": atlantic_wall,
    "Attack Vector: Tactical": attack_vector,
    "Avalon Hill Game Company's Game of Trivia": ahgc_trivia,
    "Avec Infini Regret": use_pkgs,
    "Awesome Little Green Men": version_to_release,
    "Axis & Allies: Battle of the Bulge": axis_and_allies_bulge,
    "Axis & Allies Europe 1940": version_to_release,
    "Axis & Allies Pacific: 1940 Edition": version_to_release,
    "B-17 Queen of the Skies": b17_qots,
    "Babylon 5 Collectible Card Game": babylon_5_ccg,
    "Bali": version_to_release,
    "Baltic Gap": baltic_gap,
    "Band of Brothers": band_of_brothers,
    "Barbarossa: Game of the Russo-German War 1941-45": version_to_release,
    "BattleLore": battlelore,
    "Battle Cry": battle_cry,
    "Battle Cry: 150th Civil War Anniversary Edition": battle_cry_150,
    "Battle Platform Antilles": version_to_release,
    "Battle Sheep": version_to_release,
    "Battle for Fallujah: April 2004": version_to_release,
    "Battle For Germany": use_pkgs,
    "Battle for Moscow II": battle_for_moscow_ii,
    "Battle of Thermopylae": version_to_release,
    "Battle of the Bulge": version_to_release,
    "Battle of the Ring": version_to_release,
    "Battles for the Shenadoah: A Death Valley Expansion": use_pkgs,
    "Battles of Trenton and Princeton": version_to_release,
    "Battlestations": version_to_release,
    "BattleTech": battletech,
    "BattleTech: Domination": version_to_release,
    "Belter: Mining the Asteroids, 2076": belter,
    "Beyond the Rhine": beyond_the_rhine,
    "Big Queen": version_to_release,
    "Bios: Megafauna": bios_megafauna,
    "Black Sea Black Death": version_to_release,
    "Blitz! A World in Conflict": version_to_release,
    "Blockade": blockade,
    "Blood & Roses": blood_and_roses,
    "Blood Bowl: Team Manager - The Card Game": version_to_release,
    "Bloody Steppes of Crimea: Alma - Balaclava - Inkerman 1854": bloody_steppes,
    "Blue & Gray: Four American Civil War Battles": blue_and_gray,
    "Blue & Gray II": blue_and_gray_ii,
    "Bobby Lee": bobby_lee,
    "Bowl and Score": version_to_release,
    "Brandywine & Germantown": version_to_release,
    "Breaking the Chains: War in the South China Sea": breaking_the_chains,
    "Britannia": britannia,
    "Brothers at War: 1862": brothers_at_war,
    "Bull Run": bull_run,
    "Camelot": version_to_release,
    "Campaign to Stalingrad: Southern Russia 1942": version_to_release,
    "Canadian Crucible: Brigade Fortress at Norrey": canadian_crucible,
    "Carcassonne": version_to_release,
    "Cards Against Humanity": cards_against_humanity,
    "Case Blue / Guderian's Blitzkrieg II": case_blue_gbii,
    "Case Yellow, 1940: The German Blitzkrieg in the West": use_pkgs,
    "Castaways": castaways,
    "Cataclysm: A Second World War": cataclysm,
    "Cataphract / Attila": cataphract,
    "Central Front Series": central_front_series,
    "Cerebria: The Inside World": version_to_release,
    "Champs de Bataille": champs_de_bataille,
    "Chesscalation": version_to_release,
    "Citadel of Blood": version_to_release,
    "Citadel: The Battle of Dien Bien Phu": version_to_release,
    "Citadels": citadels,
    "Civil War": civil_war,
    "Clash of Giants II": clash_of_giants_ii,
    "Clash of Sovereigns: The War of the Austrian Succession, 1740-48": version_to_release,
    "Clixers": clixers,
    "Cobra: Game of the Normandy Breakout": use_pkgs,
    "Combat! Volume 2: An Expansion for Combat!": combat_vol_2,
    "Combat Commander: Europe": combat_commander_europe,
    "Combat Commander: Pacific": version_to_release,
    "Commands & Colors Ancients": cc_ancients,
    "Commands & Colors: Napoleonics": cc_napoleonics,
    "Conflict of Heroes: Awakening the Bear! Russia 1941-1942": conflict_of_heroes_atb,
    "Conflict of Heroes: Storms of Steel! Kursk 1943": conflict_of_heroes_sos,
    "Conquest & Consequences": conquest_and_consequences,
    "Contractors": version_to_release,
    "Crash Tackle": version_to_release,
    "Crimean War Battles": crimean_war_battles,
    "Crusade and Revolution: The Spanish Civil War, 1936-1939": crusade_and_revolution,
    "Cry Havoc": cry_havoc,
    "D-Day - Smithsonian Edition": version_to_release,
    "D-Day Dice": d_day_dice,
    "DAK2": dak2,
    "Damocles Mission": version_to_release,
    "Dante's Inferno": version_to_release,
    "Dark Emperor": version_to_release,
    "DeathMaze": version_to_release,
    "Dejarik": version_to_release,
    "Demons": version_to_release,
    "Dien Bien Phu: The Final Gamble": dien_bien_phu_tfg,
    "Dig": version_to_release,
    "Divine Right": version_to_release,
    "Dixit": use_pkgs,
    "Dog Boats: Battle of the Narrow Seas": version_to_release,
    "Dominant Species": dominant_species,
    "Dominion": dominion,
    "Double-Play Baseball": version_to_release,
    "DSE - Motorcade Showdown": dse_motorcade_showdown,
    "DSE-Hell Over the Horizon": dse_hell_over,
    "DSE-Quebec 1759": dse_quebec_1759,
    "DSE:Kazhdyy Gorod": dse_kazhdyy_gorod,
    "Dune: War for Arrakis": dune_wfa,
    "Dungeon Plungin'": version_to_release,
    "Dungeon Run": version_to_release,
    "Dunkerque: 1940": version_to_release,
    "Dragon Pass": dragon_pass,
    "Eclipse": version_to_release,
    "El Gran Capitán: Campaigns of the Italian Wars 1494-1530 – Vol.2": version_to_release,
    "Eldritch Horror": eldritch_horror,
    "Elfball": elfball,
    "En Pointe Toujours!": version_to_release,
    "Enemy Action: Kharkov": enemy_action_kharkov,
    "Epées et Hallebardes 1315-1476": version_to_release,
    "Europa Full Map": europa_full_map,
    "Exile Sun": exile_sun,
    "Fall Blau: Army Group South, June-December 1942": fall_blau_ags,
    "Fatal Alliances III Dreadnoughts in Flames": version_to_release,
    "Feilong": feilong,
    "Feudal": feudal,
    "Fighting Formations: Grossdeutschland Motorized Infantry Division": version_to_release,
    "Firepower": firepower,
    "First Blood: The Guadalcanal Campaign": use_pkgs,
    "First Victories: Wellington versus Napoleon": first_victories,
    "Flat Top": flat_top,
    "Flight Leader": flight_leader,
    "Food Fight": version_to_release,
    "Formula De": formula_de,
    "Fortress Berlin": fortress_berlin,
    "Four Battles in North Africa": version_to_release,
    "Four Battles of Army Group South": version_to_release,
    "France 1940": version_to_release,
    "Freedom in The Galaxy": freedom_in_the_galaxy,
    "Friedrich": friedrich,
    "G.I. Joe TCG": gi_joe_tcg,
    "GD '42": gd42,
    "Galactic Adventures": galactic_adventures,
    "Gallipoli": version_to_release,
    "Gandhi: The Decolonization of British India, 1917 – 1947": gandhi,
    "Germania: Drusus' Campaigns 12-9 BC": germania_drusus,
    "Get to the Chopper!!!": version_to_release,
    "Gettysburg: Badges of Courage": gettysburg_badges_of_courage,
    "GMT East Front Series Volume I": version_to_release,
#    "GMT East Front Series Volume II": gmt_efs_ii,
    "Glider-Pit Gladiators": version_to_release,
    "Global War": global_war,
    "Gloomhaven": gloomhaven,
    "Gosix": gosix,
    "Grand Fleet": grand_fleet,
    "Greenland": use_pkgs,
    "Great Medieval Battles: Four Battles from the Middle Ages": great_medieval_battles,
    "Guadalcanal": guadalcanal,
    "Guild Ball": version_to_release,
    "Gunslinger": gunslinger,
    "Gustav Adolf the Great: With God and Victorious Arms": gustav_adolf,
    "H&S": version_to_release,
    "Hands in the Sea": hands_in_the_sea,
    "Heroes of Feonora": version_to_release,
    "Heroes of New Phlan": version_to_release,
    "High Frontier": high_frontier,
    "Hitler's War": hitlers_war,
    "Hot Spot": version_to_release,
    "Hyle": version_to_release,
    "Impact Naval Game": version_to_release,
    "Imperial Struggle": imperial_struggle,
    "Infidel": infidel,
    "Invasion: America – Death Throes of the Superpower": invasion_america,
    "Invasion: Malta": invasion_malta,
    "Island of D": version_to_release,
    "Island War: Four Pacific Battles": island_war,
    "Jasper and Zot": version_to_release,
    "Julius Caesar": julius_caesar,
    "Kabinettskrieg": version_to_release,
    "Kasserine": use_pkgs,
    "Kasserine Pass": version_to_release,
    "Kellogg's Major League Baseball Game": version_to_release,
    "Kestenga: Another Fight to the Finnish": version_to_release,
    "Kahmaté": kahmate,
    "King's Table": version_to_release,
    "Knights of the Dinner Table: Orcs at the Gates": version_to_release,
    "Kolejka": kolejka,
    "Korea: The Forgotten War": korea_tfw,
    "Korsun Pocket": version_to_release,
    "Kremlin": kremlin,
    "Kunersdorf 1759": version_to_release,
    "La Bataille d'Austerlitz": la_bat_austerlitz,
    "Labyrinth: The War on Terror": labyrinth,
    "Leader 1": leader_1,
    "Leaving Earth": leaving_earth,
    "Lee vs Grant": version_to_release,
    "Legendary: A Marvel Deck Building Game": legendary,
    "Les Rois Francs": les_rois_francs,
    "Letters from Whitechapel": version_to_release,
    "Liberté": liberte,
    "Limits of Glory: Bonaparte's Eastern empire": version_to_release,
    "Lincoln's War": version_to_release,
    "Luftwaffe": version_to_release,
    "Luna Mare: Mineralis & Dominatio": version_to_release,
    "MBT": mbt,
    "MBT / IDF": mbt_idf,
    "Machi Koro": machi_koro,
    "Management": version_to_release,
    "Manassas": manassas,
    "Maneuver": version_to_release,
    "Mansions of Madness": version_to_release,
    "March Madness": version_to_release,
    "Maze of the Red Mage: A Solitaire Dungeon Adventure!": version_to_release,
    "MechWar 4": mechwar4,
    "Melee - Wizard": melee_wizard,
    "Memoir '44": memoir_44,
    "Men of Iron, Volume I: The Rebirth of Infantry": men_of_iron,
    "Merchants & Marauders": merchants_and_marauders,
    "Middle East Strike": middle_east_strike,
    "Midway": midway,
    "Minden 1759": version_to_release,
    "Monsterpocalypse": version_to_release,
    "NATO, Nukes, & Nazis": version_to_release,
    "Napoleon At Bay: Defend the Gates of Paris": napoleon_at_bay,
    "Napoleon: The Waterloo Campaign, 1815": napoleon_the_waterloo,
    "Napoleon's Last Battles": napoleons_last_battles,
    "Nations at War: White Star Rising": nations_at_war_wsr,
    "Neanderthal": neanderthal,
    "Neck and Neck": version_to_release,
    "Neuroshima Hex!": neuroshima_hex,
    "Next War: Korea": next_war_korea,
    "Next War: Taiwan": next_war_taiwan,
    "Nieuchess": version_to_release,
    "No Better Place To Die": no_better_place_to_die,
    "No Retreat! The North African Front": use_pkgs,
    "No Retreat! The Russian Front": no_retreat_the_russian_front,
    "Normandy '44": normandy_44,
    "Nothing Gained But Glory": nothing_gained_but_glory,
    "On to Richmond II: The Union Strikes South": on_to_richmond_ii,
    "Ogre": ogre,
    "Operation Grenade: The Battle for the Rhineland 23 Feb. - 5 Mar. '45": operation_grenade,
    "Operation Mercury: The German Airborne Assault on Crete, 1941": operation_mercury,
    "Operation Olympic": version_to_release,
    "Orbit War": version_to_release,
    "Orbital": version_to_release,
    "Order and Chaos": version_to_release,
    "Origins: How We Became Human": origins_how,
    "Our Place in the Sun": version_to_release,
    "Overlord": version_to_release,
    "Ozymandia": version_to_release,
    "Pacific War": pacific_war,
    "Pandemic": pandemic,
    "Panzer": panzer,
    "PanzerBlitz": panzerblitz,
    "Panzer Command": panzer_command,
    "Panzer North Africa": panzer_north_africa,
    "Paris vaut bien une messe !": paris_vaut,
    "Paths of Glory": paths_of_glory,
    "Patton's 3rd Army: The Lorraine Campaign": pattons_3rd_army,
    "Patton's Best": pattons_best,
    "Pax Renaissance": version_to_release,
    "Pegasus Bridge: The Beginning of D-Day - June 6, 1944": version_to_release,
    "Pente": pente,
    "Perdition's Mouth: Abyssal Rift": version_to_release,
    "Pericles: The Peloponnesian Wars": pericles,
    "Pirates of the Spanish Main": pirates_of_the_spanish_main,
    "Polis: Fight for the Hegemony": version_to_release,
    "Polygoons": use_pkgs,
    "Pro Tennis": version_to_release,
    "Quatre Batailles en Espagne": quatre_batailles,
    "Quinto": version_to_release,
    "RAF": version_to_release,
    "Race! Formula 90": race_formula_90,
    "Race for the Galaxy": race_for_the_galaxy,
    "Raid On St. Nazaire": version_to_release,
    "Raid on Bananama: The Bad Boys Game": version_to_release,
    "Raid on the Bunker": version_to_release,
    "Rallyman": rallyman,
    "Red Badge of Courage": red_badge_of_courage,
    "Reluctant Enemies: Operation Exporter – The Commonwealth Invasion of Lebanon & Syria, June-July, 1941": reluctant_enemies,
    "Ringside": version_to_release,
    "Road to Washington": version_to_release,
    "Roads to Gettysburg II: Lee Strikes North": use_pkgs,
    "Roads to Leningrad: Battles of Soltsy and Staraya Russa, 1941": roads_to_leningrad,
    "RoboRally": roborally,
    "Rolica et Vimeiro 1808": version_to_release,
    "Russian Front": russian_front,
    "Sack Armies": version_to_release,
    "Saints in Armor": use_pkgs,
    "Salla 1941: A Fight to the Finnish": version_to_release,
    "Samurai Battles": samurai_battles,
    "Samurai Blades and Map Builder": samurai_blades_and_map,
    "Samurai Blades Campaign": samurai_blades_campaign,
    "Sauron": sauron,
    "Schutztruppe": version_to_release,
    "Semper Fi": semper_fi,
    "Skies Above the Reich": use_pkgs,
    "Sicily: The Race for Messina": sicily_the_race,
    "Sicily II": sicily_ii,
    "Silent War": silent_war,
    "Simple Soccer": version_to_release,
    "Smess: The Ninny's Chess": version_to_release,
    "Smolensk: Barbarossa Derailed": smolensk_barbarossa,
    "Sneaking Mission: Solo": version_to_release,
    "Solitaire Chess": version_to_release,
    "Sorcerer": version_to_release,
    "Sorry!": version_to_release,
    "SOE: Lysander": soe_lysander,
    "Space Alert": space_alert,
    "Space Nazis from Hell": version_to_release,
    "Space Opera": space_opera,
    "SpaceCorp": spacecorp,
    "Sports Illustrated Baseball": version_to_release,
    "Squad Leader": squad_leader,
    "Star Trek: Expeditions": version_to_release,
    "Star Trek: Fleet Captains": version_to_release,
    "Star Trek: The Game": star_trek_the_game,
    "Star Trek III": star_trek_iii,
    "Star Wars: Armada": star_wars_armada,
    "Star Wars: Battle for Endor": version_to_release,
    "Star Wars Miniatures": star_wars_miniatures,
    "Star Wars Tactics": star_wars_tactics,
    "Starfire": starfire,
    "Stargate": version_to_release,
    "Starmada: The Admiralty Edition": starmada_tae,
    "Starship: Panic": version_to_release,
    "Star Wars: Epic Duels": star_wars_epic_duels,
    "Statis Pro Football": version_to_release,
    "Steel Wolves: The German Submarine Campaign Against Allied Shipping - Vol 1": steel_wolves,
    "Stonewall Jackson's Way II": stonewall_jacksons_way_ii,
    "Storm Over Arnhem": storm_over_arnhem,
    "Struggle of Empires": struggle_of_empires,
    "Summer Storm: The Battle of Gettysburg": version_to_release,
    "Super Dungeon Explore": version_to_release,
    "Suez '73":  suez73,
    "Successors (2nd Edition)": successors_2ed,
    "Suffragetto": version_to_release,
    "Summoner Wars": summoner_wars,
    "Sweden Fights On": sweden_fights_on,
    "Switchboard": version_to_release,
    "Tactics": version_to_release,
    "Tactics (25th Anniversary Edition)": tactics_25,
    "Tannenberg 1914 (1990)": tannenberg_1914,
    "Target Arnhem, Across Six Bridges": target_arnhem,
    "Tarot, Tarock & Tarocchi Games": tarot,
    "Tatchanka: Ukraine, 1919-21": version_to_release,
    "Tenkatoitsu": tenkatoitsu,
    "Tennis": version_to_release,
    "Tet Offensive": tet_offensive,
    "The Alamo: Victory in Death": the_alamo_victory_in_death,
    "The Art of Siege": use_pkgs,
    "The Balkan Wars: Prelude to Disaster, 1912-1913": the_balkan_wars,
    "The Baton Races of Yaz": version_to_release,
    "The Battle of Agincourt": version_to_release,
    "The Battle of Brandywine": version_to_release,
    "The Battle of Camden, S.C.": version_to_release,
    "The Battle of Corinth: Standoff at the Tennessee, October 3-4, 1862": the_battle_of_corinth,
    "The Battle of Guilford Courthouse": version_to_release,
    "The Battle of Lobositz": version_to_release,
    "The Battle of Monmouth (1982)": the_battle_of_monmouth_1982,
    "The Battle of Prague": version_to_release,
    "The Battle of Raphia": version_to_release,
    "The Battle of Saratoga": version_to_release,
    "The Battle of the Alma": version_to_release,
    "The Battle of the Bulge": the_battle_of_the_bulge,
    "The Campaign for North Africa: The Desert War 1940-43": the_campaign_for_north_africa,
    "The Creature That Ate Sheboygan": the_creature_that_ate_sheboygan,
    "The Dark Valley": version_to_release,
    "The Desert Fox: Rommel's Campaign for North Africa April 1941-December 1942": the_desert_fox,
    "The Devil's To Pay": version_to_release,
    "The Draugr": version_to_release,
    "The Fast Carriers: Air-Sea Operations, 1941-77": the_fast_carriers,
    "The Fighting General Patton": the_fighting_general_patton,
    "The Game of Shakespeare": version_to_release,
    "The Great War in the East: Four World War 1 Battles": use_pkgs,
    "The Grunwald Swords": the_grunwald_swords,
    "The High Crusade": version_to_release,
    "The Hunters: German U-Boats at War, 1939-43": version_to_release,
    "The Kaiser's Pirates": the_kaisers_pirates,
    "The Korean War": version_to_release,
    "The Longest Day": the_longest_day,
    "The Lord of the Rings: The Card Game": version_to_release,
    "The Lords of Underearth": version_to_release,
    "The Mighty Endeavor": the_mighty_endeavor,
    "The Napoleonic Wars": version_to_release,
    "The Other Side": the_other_side,
    "The Return of the Stainless Steel Rat": version_to_release,
    "The Siege of Barad-Dur 3430": version_to_release,
    "The Siege of Jerusalem": version_to_release,
    "The Sword and the Stars": the_sword_and_the_stars,
    "The Three Days of Gettysburg (third edition)": version_to_release,
    "The Warlord Game": version_to_release,
    "Thirty Years War Quad": version_to_release,
    "Through the Breach": through_the_breach,
    "Tide Of Iron": version_to_release,
    "Titan Strike!": version_to_release,
    "Title Bout": title_bout,
    "Tolling of the Bell": version_to_release,
    "Tomb Raider": tomb_raider,
    "Tonnage War Solitaire": tonnage_war_solitaire,
    "Totaler Krieg! (2nd Edition) / Dai Senso": totaler_krieg_2e,
    "Torgau": torgau,
    "Trafalgar": trafalgar,
    "Triple Topper": triple_topper,
    "Tuf": version_to_release,
    "Tuf-abet": version_to_release,
    "Türkenkrieg (1737-1739)": turkenkrieg,
    "Twilight Struggle": twilight_struggle,
    "Twixt": version_to_release,
    "U-Boat": version_to_release,
    "U.S.N.: The Game of War in the Pacific, 1941-43": version_to_release,
    "Ukraine '43": ukraine43,
    "Upwords": use_100,
    "Unconditional Surrender! World War 2 in Europe": version_to_release,
    "Under the Lily Banners": under_the_lily_banners,
    "Une décennie dans les tranchées: Guerre Iran-Irak 1980-1988": version_to_release,
    "Valor and Victory": version_to_release,
    "Vector 3": use_100,
    "Verdun: A Generation Lost": verdun,
    "Victory in the Pacific": victory_in_the_pacific,
    "Voyage of the B.S.M. Pandora": voyage_of_the_bsm_pandora,
    "Wagon Wheel Chess": use_100,
    "Wacht am Rhein': The Battle of the Bulge, 16 Dec 44-2 Jan 45": wacht_am_rhein,
    "War At Sea": version_to_release,
    "Warchestra (Classic)": version_to_release,
    "WarpWar": warpwar,
    "Washington's War": washingtons_war,
    "Waterloo": waterloo,
    "Weimar The Fight For Democracy": weimar,
    "Westwall: Four Battles to Germany": westwall,
    "Wing Commander Armada PNP": wing_commander_armada,
    "Wing Leader": wing_leader,
    "Winter War": winter_war,
    "Wizard's Quest": use_100,
    "Wizards": use_100,
    "Wizard Kings": wizard_kings,
    "Word War - Competitive Crossword Game": use_100,
    "World At War 85: Storming the Gap": version_to_release,
    "World at War": world_at_war,
    "World War I": use_100,
    "World War II: European Theater of Operations": use_pkgs,
    "World War II: Pacific Theater of Operations": use_pkgs,
    "Wrasslin'": use_100,
    "Wreckage": use_100,
    "YINSH": use_100,
    "Yahtzee": use_100,
    "Yellowstone": use_100,
    "Yggdrasil": yggdrasil,
    "Yu-Gi-Oh! DungeonDice Monsters": use_100,
    "Z-G Resurgence": z_g_resurgence,
    "Zulu Attack": zulu,
    "Zulu: Isandhlwana": zulu,
    "Zulu: Naka": zulu,
    "Zulu: Rorke's Drift": zulu,
    "Zulu: Ulundi": zulu
}


fixups = {
    # owner can sort it
    "World in Flames": None,
    "Dungeons & Dragons Miniatures": None,
    "Twilight Sparkle's Secret Shipfic Folder": None,
    "A Game of Thrones: The Board Game (Second Edition)": None,
    "Malifaux": None,
    "Napoleon's Last Battles": None,

    # split
    "Afrika Korps": None,
    "Age of Sail": None,
    "Arkham Horror": None,
    "Assault of the Dead: Tactics": None,
    "Au fil de l'epee": None,
    "Battle for Moscow": None,
    "BattleLore (Second Edition)": None,
    "Battles for the Ardennes": None,
    "Battle: The Game of Generals": None,
    "Betrayal At House On The Hill": None,
    "Bitter Woods (4th Edition)": None,
    "Blitzkrieg": None,
    "Breakout Normandy": None,
    "Caesar: Epic Battle of Alesia": None,
    "Caesar in Alexandria": None,
    "Codex: Card-Time Strategy": None,
    "Combat!": None,
    "D-Day": None,
    "Downtown: Air War Over Hanoi, 1965 - 1972": None,
    "Dreamblade": None,
    "Drive on Washington: The Battle of Monocacy Junction, July 9, 1864": None,
    "Dune": None,
    "El Alamein: Battles in North Africa, 1942": None,
    "Empires of the Middle Ages": None,
    "Fighting Sail": None,
    "Fortress Europa": None,
    "Gettysburg: 125th Anniversary Edition": None,
    "Great Battles of Alexander: Deluxe Edition": None,
    "Hannibal: Rome vs. Carthage": None,
    "Imperium": None,
    "Kingmaker": None,
    "L'Art de la Guerre": None,
    "Marine Fighter Squadron: A Solitaire Game of Aerial Combat in the Solomons (1942-1945)": None,
    "MechWar 'Gloomhaven_Scenarios_4P_3.1.vmdx77: Tactical Armored Combat in the 1970's": None,
    "Napoleon at Waterloo": None,
    "NFL Strategy": None,
    "No Retreat!": None,
    "PanzerArmee Afrika: Rommel in the Desert, April 1941 - November 1942": None,
    "Platoon Commander Deluxe: The Battle of Kursk": None,
    "Red Storm: The Air War Over Central Germany, 1987": None,
    "Richthofen's War": None,
    "Rise and Decline of the Third Reich": None,
    "Rommel (2017)": None,
    "Russia Besieged": None,
    "Scorched Earth": None,
    "Silent War + IJN (Second Edition)": None,
    "Sleuth": None,
    "Snapshot": None,
    "Source of the Nile": None,
    "Sphactérie -425": None,
    "S.P.Q.R. Deluxe": None,
    "Stalingrad": None,
    "Starship Troopers": None,
    "Star Wars: Imperial Assault": None,
    "Statis Pro Baseball": None,
    "Stellar Conquest": None,
    "Terraforming Mars": None,
    "The Arab-Israeli Wars": None,
    "The Civil War": None,
    "The Drive on Metz, 1944": None,
    "The Guns of August": None,
    "The Republic of Rome": None,
    "The Russian Campaign": None,
    "The Succession Wars": None,
    "Up Front": None,
    "Vietnam 1965-1975": None,
    "War and Peace": None,
    "Western Front Ace: The Great Air War 1916-1918": None,
}

# TODO: add description field to files?


async def fixup_page(path):
    try:
        do_fixup_page(path)
    except Exception as e:
        raise RuntimeError(path) from e


def do_fixup_page(path):
#    print(path)

    with open(path, 'r') as f:
        p = json.loads(f.read().replace('\\u200e', ''))

    title = p['title']

    before_count = before_mod_count(p)

    # apply collapse
    if collapse := collapses.get(title):
        collapse(p)

    # insert releases between packages and files
    ms = p['modules']
    if len(ms) == 1 and 'Module' in ms and ms['Module'] and all('version' in e for e in ms['Module']):

        mods = ms.pop('Module')
        p['modules']['Module'] = {}
        for m in mods:
            r = p['modules']['Module'].setdefault(m['version'], [])
            r.append(m)

    elif release_fixup := release_fixups.get(title):
        release_fixup(p)

    elif ms:
        if all(versions.try_semver(pn) for pn in ms):
            mpkg = [ (str(versions.try_semver(pn)), pc) for pn, pc in ms.items() ]
            ms.clear()
            ms['Module'] = {}

            for v, pc in mpkg:
                ms['Module'].setdefault(v, []).extend(pc)

        else:
            for pn, pc in ms.items():
                ms[pn] = { pn: ms[pn] }

    # apply fixup
    if fixup := fixups.get(title):
        fixup(p)

    after_count = after_mod_count(p)

    if before_count != after_count:
        print(path, before_count, after_count)

    with open(path, 'w') as f:
        json.dump(p, f, indent=2)


async def run():
    ipath = 'data/pagejson_combined'
    opath = 'data/pagejson_fixed'

    shutil.copytree(ipath, opath, dirs_exist_ok=True)

    async with asyncio.TaskGroup() as tg:
        for f in glob.glob(f"{opath}/[0-9]*.json"):
            tg.create_task(fixup_page(f))

    print('')


if __name__ == '__main__':
    asyncio.run(run())
