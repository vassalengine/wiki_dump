import asyncio
import glob
import json
import shutil
import os

from versions import try_parse_version


def no_box_image(p):
    p['info']['image'] = ''
    return False


def collapse_pkgs(p):
    mods = p['modules']

    # map everything to one package
    d = []
    for v in mods.values():
        d += v

    p['modules'] = { p['title']: d }
    return False


def x13_dead_end_drive(p):
    p['modules'] = {
        'Spanish': [ m for v in p['modules'].values() for m in v ]
    }
    return True


def x1914_glorys_end(p):
    p['modules'] = {
        "Glory's End": p['modules']["1.0 Glory's End"],
        'When Eagles Fight': p['modules']['1.0 When Eagles Fight']
    }
    return True


def a5a(p):
    p['modules'] = {
        'Gettysburg': [ m for v in p['modules'].values() for m in v if 'Gettysburg' in m['filename'] ],
        '1st Bull Run': [ m for v in p['modules'].values() for m in v if 'Bull' in m['filename'] ],
        'Shiloh': [ m for v in p['modules'].values() for m in v if 'Shiloh' in m['filename'] ],
        'Pea Ridge': [ m for v in p['modules'].values() for m in v if 'Pea' in m['filename'] ],
        'Bentonville': [ m for v in p['modules'].values() for m in v if 'Bentonville' in m['filename'] ],
        'Rules': [ m for v in p['modules'].values() for m in v if 'pdf' in m['filename'] ]
    }
    return True


def apuren_el(p):
    p['title'] = '¡' + p['title']
    return False


def ardennes_44(p):
    p['modules'] = {
        '3rd Edition': [ m for v in p['modules'].values() for m in v if '3rd' in m['filename'] ],
        '2nd Edition': [ m for v in p['modules'].values() for m in v if '2ed' in m['filename'] or '2nd' in m['filename'] ],
        '1st Edition': [ m for v in p['modules'].values() for m in v if '2ed' not in m['filename'] and '2nd' not in m['filename'] and '3rd' not in m['filename']]
    }
    return True


def arquebus(p):
    p['modules'] = {
        'Agnadello': [ m for v in p['modules'].values() for m in v if 'Agnadello' in m['filename'] ],
        'Bicocca': [ m for v in p['modules'].values() for m in v if 'Bicocca' in m['filename'] ],
        'Ceresole': [ m for v in p['modules'].values() for m in v if 'Ceresole' in m['filename'] ],
        'Cerignola': [ m for v in p['modules'].values() for m in v if 'Cerignola' in m['filename'] ],
        'Fornovo': [ m for v in p['modules'].values() for m in v if 'Fornovo' in m['filename'] ],
        'Ravenna': [ m for v in p['modules'].values() for m in v if 'Ravenna' in m['filename'] ],
        'Marignano': [ m for v in p['modules'].values() for m in v if 'Marignano' in m['filename'] ],
        'Pavia': [ m for v in p['modules'].values() for m in v if 'Pavia' in m['filename'] ]
    }
    return True


def arriba_espana(p):
    p['title'] = '¡Arriba España!'
    return False


def assault_of_the_dead(p):
    p['modules']['Alternate Version'] = p['modules']['1.0 Alternate Version']
    del p['modules']['1.0 Alternate Version']
    return True


def avec_infini_regret(p):
    p['modules'] = {
        'Battle of Coutras - October 20, 1587': [ m for v in p['modules'].values() for m in v if 'Coutras' in m['filename'] ],
        'Battle of Dreux - December 19th, 1562': [ m for v in p['modules'].values() for m in v if 'Dreux' in m['filename'] ],
        "Battle for La Roche-l' Abeille, 25th June 1569": [ m for v in p['modules'].values() for m in v if 'Roche' in m['filename'] ]
    }
    return True


def battles_for_the_shenandoah(p):
    p['modules'] = {
        '2nd Winchester': [ m for v in p['modules'].values() for m in v if 'Winchester' in m['filename'] ],
        'Cool Spring': [ m for v in p['modules'].values() for m in v if 'Cool' in m['filename'] ],
        'McDowell': [ m for v in p['modules'].values() for m in v if 'McDowell' in m['filename'] ],
        'Piedmont': [ m for v in p['modules'].values() for m in v if 'Piedmont' in m['filename'] ]
    }
    return True


def tbotb(p):
    p['modules'] = {
        '1st Edition': [ m for v in p['modules'].values() for m in v if '2nd' not in m['filename'] ],
        '2nd Edition': [ m for v in p['modules'].values() for m in v if '2nd' in m['filename'] ]
    }
    return True


def battle_of_monmouth(p):
    p['modules'] = {
        'SPI': [ m for v in p['modules'].values() for m in v if 'S&T' not in m['filename'] ],
        'S&T 90': [ m for v in p['modules'].values() for m in v if 'S&T' in m['filename'] ]
    }
    return True


def battle_hymn(p):
    p['modules'] = {
        'Battle Hymn': [ m for v in p['modules'].values() for m in v if 'Battle' in m['filename'] ],
        'Leatherneck': [ m for v in p['modules'].values() for m in v if 'Leatherneck' in m['filename'] ]
    }
    return True


def battle_hymn_vol_1(p):
    p['modules'] = {
        'Gettysburg': [ m for v in p['modules'].values() for m in v if 'Gettysburg' in m['filename'] ],
        'Pea Ridge': [ m for v in p['modules'].values() for m in v if 'Pea' in m['filename'] ]
    }
    return True


def battle_of_corinth(p):
    jatc = p['modules']['Jackson at the Crossroads, v 1.0']
    del p['modules']['Jackson at the Crossroads, v 1.0']

    p['modules'] = {
        'Jackson at the Crossroads': jatc,
        'Corinth': [ m for v in p['modules'].values() for m in v ]
    }
    return True


def blockade(p):
    p['modules'] = {
        'Blockade': [ m for v in p['modules'].values() for m in v if 'Duel' not in m['filename'] ],
        'Blockade Duel': [ m for v in p['modules'].values() for m in v if 'Duel' in m['filename'] ]
    }
    return True


def bloody_steppes(p):
    p['modules'] = {
        'Alma': [ m for v in p['modules'].values() for m in v if 'Alma' in m['filename'] ],
        'Balaclava': [ m for v in p['modules'].values() for m in v if 'Balaclava' in m['filename'] ],
        'Inkerman': [ m for v in p['modules'].values() for m in v if 'Inkerman' in m['filename'] ]
    }
    return True


def brandywine_germantown(p):
    p['modules'] = {
        'Brandywine': [ m for v in p['modules'].values() for m in v if 'Brandywine' in m['filename'] ],
        'Germantown': [ m for v in p['modules'].values() for m in v if 'Germantown' in m['filename'] ]
    }
    return True


def case_yellow(p):
    p['modules'] = {
        'Scenarios 1 and 2': [ m for v in p['modules'].values() for m in v if 'SC_1_2' in m['filename'] ],
        'Scenario 3': [ m for v in p['modules'].values() for m in v if 'SC_3' in m['filename'] ]
    }
    return True


def cobra(p):
    p['modules'] = {
        'Cobra from S&T #64': [ m for v in p['modules'].values() for m in v if 'v04' in m['filename'] ],
        'Cobra from S&T #251': [ m for v in p['modules'].values() for m in v if 'Cobra2' in m['filename'] ]
    }
    return True


def crimean_war_battles(p):
    p['modules'] = {
        'Alma': [ m for v in p['modules'].values() for m in v if 'Alma' in m['filename'] ],
        'Balaclava': [ m for v in p['modules'].values() for m in v if 'Balaclava' in m['filename'] ],
        'Inkerman': [ m for v in p['modules'].values() for m in v if 'Inkerman' in m['filename'] ],
        'Tchernaya River': [ m for v in p['modules'].values() for m in v if 'Tchernaya' in m['filename'] ]
    }
    return True


def dien_bien_phu_tfg(p):
    p['modules'] = {
        '2nd Edition': [ m for v in p['modules'].values() for m in v if '2ed' in m['filename'] ],
        '1st Edition': [ m for v in p['modules'].values() for m in v if '2ed' not in m['filename'] ]
    }
    return True


def epees_crois(p):
    p['modules'] = {
        'Ascalon': [ m for v in p['modules'].values() for m in v if 'Ascalon' in m['filename'] ],
        'Dorylee': [ m for v in p['modules'].values() for m in v if 'Dorylee' in m['filename'] ]
    }
    return True


def epees_norm(p):
    p['modules'] = {
        'Hastings': [ m for v in p['modules'].values() for m in v if 'Hastings' in m['filename'] ],
        'Vales Dunes': [ m for v in p['modules'].values() for m in v if 'ValesDunes' in m['filename'] ],
        'Varaville': [ m for v in p['modules'].values() for m in v if 'Varaville' in m['filename'] ]
    }
    return True


def epees_souv(p):
    p['modules'] = {
        'Bouvines': [ m for v in p['modules'].values() for m in v if 'Bouvines' in m['filename'] ],
        'Worrigen': [ m for v in p['modules'].values() for m in v if 'Worrigen' in m['filename'] ]
    }
    return True


def fighting_general_patton(p):
    p['modules'] = {
        "At Fascists' Foot": [ m for v in p['modules'].values() for m in v if 'AFF' in m['filename'] ],
        "Breakthrough Ironcurtain": [ m for v in p['modules'].values() for m in v if 'BI' in m['filename'] ],
        "Rush on Avranches": [ m for v in p['modules'].values() for m in v if 'RoA' in m['filename'] ],
        "Raise the Siege": [ m for v in p['modules'].values() for m in v if 'RtS' in m['filename'] ],
        "Files": [ m for v in p['modules'].values() for m in v if 'Notes' in m['filename'] ]
    }
    return True


def forgotten_legions(p):
    p['modules'] = {
        'Drive on Damascus': [ m for v in p['modules'].values() for m in v if 'Damascus' in m['filename'] ],
        'Bloody Keren': [ m for v in p['modules'].values() for m in v if 'Keren' in m['filename'] ]
    }
    return True


def four_battles_in_north_africa(p):
    p['modules'] = {
        'Cauldron': [ m for v in p['modules'].values() for m in v if 'Cauldron' in m['filename'] ],
        'Crusader': [ m for v in p['modules'].values() for m in v if 'Crusader' in m['filename'] ],
        'Kasserine': [ m for v in p['modules'].values() for m in v if 'Kasserine' in m['filename'] ],
        'Supercharge': [ m for v in p['modules'].values() for m in v if 'Supercharge' in m['filename'] ]
    }
    return True


def gospitch(p):
    p['modules'] = {
        'Gospitch': [ m for v in p['modules'].values() for m in v if 'Gospitch' in m['filename'] ],
        'Ocaña': [ m for v in p['modules'].values() for m in v if 'Ocana' in m['filename'] ]
    }
    return True


def highway_to_the_kremlin(p):
    p['readme'] = p['readme'].removeprefix("''' File for this module version are hosted at [http://www.limeyyankgames.co.uk/ Limey Yank Games]'''\n\n\n\n\n\n\n\n\n\n\n\n")
    return False


def a_house_divided(p):
    p['modules'] = {
        'GDW 1st Edition': [ m for v in p['modules'].values() for m in v if m['filename'].startswith('ahd_') ],
        'Phalanx': [ m for v in p['modules'].values() for m in v if m['filename'].startswith('AHD') ]
    }
    return True


def kaisers_pirates(p):
    p['modules'] = {
        'Module': [ m for v in p['modules'].values() for m in v if 'Solitaire' not in m['filename'] ],
        'Solitaire': [ m for v in p['modules'].values() for m in v if 'Solitaire' in m['filename'] ]
    }
    return True


def la_sombra(p):
    p['modules'] = {
        'Medellín': [ m for v in p['modules'].values() for m in v if 'MEDELLIN' in m['filename'] ],
        'Alcañíz':  [ m for v in p['modules'].values() for m in v if 'ALCANIZ' in m['filename'] ],
        'María de Huerva':  [ m for v in p['modules'].values() for m in v if 'MARIA' in m['filename'] ],
        'Tamames':  [ m for v in p['modules'].values() for m in v if 'TAMAMES' in m['filename'] ],
        'Castalla':  [ m for v in p['modules'].values() for m in v if 'CASTALLA' in m['filename'] ]
    }
    return True


def la_treve(p):
    p['modules'] = {
        'Blanquetaque': [ m for v in p['modules'].values() for m in v if 'Blanquetaque' in m['filename'] ],
        'Guinegatte':  [ m for v in p['modules'].values() for m in v if 'Guinegatte' in m['filename'] ]
    }
    return True


def le_dauphin(p):
    p['modules'] = {
        'Dieppe': [ m for v in p['modules'].values() for m in v if 'Dieppe' in m['filename'] ],
        'Saint-Jacques-sur-la-Brise':  [ m for v in p['modules'].values() for m in v if 'StJacques' in m['filename'] ],
        'Montlhéry': [ m for v in p['modules'].values() for m in v if 'Montlhery' in m['filename'] ]
    }
    return True


def le_lion_et_lepee(p):
    p['modules'] = {
        'Arsouf': [ m for v in p['modules'].values() for m in v if 'Arsouf' in m['filename'] ],
        'Tremithoussia': [ m for v in p['modules'].values() for m in v if 'Tremithoussia' in m['filename'] ]
    }
    return True


def nawfb(p):
    p['modules'] = {
        'Wagram': [ m for v in p['modules'].values() for m in v if 'Wagram' in m['filename'] ],
        'Jena-Auerstadt': [ m for v in p['modules'].values() for m in v if 'Jena' in m['filename'] ],
        'The Battle of Nations': [ m for v in p['modules'].values() for m in v if 'Nations' in m['filename'] ],
        'Marengo': [ m for v in p['modules'].values() for m in v if 'Marengo' in m['filename'] ]
    }
    return True


def ngbg(p):
    p['modules'] = {
        'Nyborg-Fehrbellin': [ m for v in p['modules'].values() for m in v if 'Nyborg' in m['filename'] ],
        'Halmstad-Warksow': [ m for v in p['modules'].values() for m in v if 'Halmstad' in m['filename'] ],
        'Lund': [ m for v in p['modules'].values() for m in v if 'Lund' in m['filename'] ],
        'Landskrona': [ m for v in p['modules'].values() for m in v if 'Landskrona' in m['filename'] ],
        'Malmoe': [ m for v in p['modules'].values() for m in v if 'Malmoe' in m['filename'] ]
    }
    return True


def next_war_korea(p):
    p['modules'] = {
        '2nd Edition': [ m for v in p['modules'].values() for m in v if '2nd' in m['filename'] ],
        '1st Edition': [ m for v in p['modules'].values() for m in v if '2nd' not in m['filename'] ]
    }
    return True


def par_le_feu(p):
    p['modules'] = {
        'Arques': [ m for v in p['modules'].values() for m in v if 'Arques' in m['filename'] ],
        'Coutras': [ m for v in p['modules'].values() for m in v if 'Coutras' in m['filename'] ],
        'Jarnac': [ m for v in p['modules'].values() for m in v if 'Jarnac' in m['filename'] ],
        "La Roche l'Abeiller": [ m for v in p['modules'].values() for m in v if 'Roche' in m['filename'] ],
        'Saint-Denis': [ m for v in p['modules'].values() for m in v if 'Saint' in m['filename'] ]
    }
    return True


def paris_vaut(p):
    p['modules'] = {
        'Dreux 1562': [ m for v in p['modules'].values() for m in v if 'Dreux' in m['filename'] ],
        'Ivry 1590': [ m for v in p['modules'].values() for m in v if 'Ivry' in m['filename'] ]
    }
    return True


def pericles(p):
    p['modules'] = {
        '2-4 Players with Bots': [ m for v in p['modules'].values() for m in v if 'Solitaire' not in m['filename'] ],
        'Solitaire only': [ m for v in p['modules'].values() for m in v if 'Solitaire' in m['filename'] ]
    }
    return True



def prussias_glory_ii(p):
    p['modules'] = {
        'Krefeld': [ m for v in p['modules'].values() for m in v if 'Krefeld' in m['filename'] ],
        'Prague': [ m for v in p['modules'].values() for m in v if 'Prague' in m['filename'] ]
    }
    return True


def quatre_batailles_en_espagne(p):
    p['modules'] = {
        'Ocana': p['modules']['1.0 Ocana'],
        'Salamanque': p['modules']['1.0 Salamanque'],
        'Vitoria': p['modules']['1.0 Vitoria'],
        'Sorauren': p['modules']['1.0 Sorauren']
    }
    return True


def raider_drop_zone(p):
    p['info']['length'] = '1-8 hours'
    return False


def return_to_the_rock(p):
    p['maintainer'] = [ [ None, "Airjudden" ] ]
    return False


def roads_to_l(p):
    p['modules'] = {
        'Staraya Russa Scenarios': [ m for v in p['modules'].values() for m in v if 'Staraya' in m['filename'] ],
        'Soltsy Scenarios':  [ m for v in p['modules'].values() for m in v if 'Soltsy' in m['filename'] ],
    }
    return True


def tacw(p):
    p['modules'] = {
        '2nd Newbury': [ m for v in p['modules'].values() for m in v if '2nd' in m['filename'] ],
        '1st Newbury': [ m for v in p['modules'].values() for m in v if '1st' in m['filename'] ],
        'Naseby': [ m for v in p['modules'].values() for m in v if 'Naseby' in m['filename'] ],
        'Edgehill': [ m for v in p['modules'].values() for m in v if 'Edgehill' in m['filename'] ],
        'Cheriton': [ m for v in p['modules'].values() for m in v if 'Cheriton' in m['filename'] ],
        'Marston Moor': [ m for v in p['modules'].values() for m in v if 'Marston' in m['filename'] ]
    }
    return True


def tdog1805(p):
    p['modules'] = {
        'Austerlitz': [ m for v in p['modules'].values() for m in v if 'Austerlitz' in m['filename'] ],
        'Elchingen': [ m for v in p['modules'].values() for m in v if 'Elchingen' in m['filename'] ],
        'Hollabrunn': [ m for v in p['modules'].values() for m in v if 'Hollabrunn' in m['filename'] ]
    }
    return True


def tywq(p):
    p['modules'] = {
        'Freiburg': [ m for v in p['modules'].values() for m in v if 'Freiburg' in m['filename'] ],
        'Lutzen': [ m for v in p['modules'].values() for m in v if 'Lutzen' in m['filename'] ],
        'Nordigen': [ m for v in p['modules'].values() for m in v if 'Nordigen' in m['filename'] ],
        'Rocroi': [ m for v in p['modules'].values() for m in v if 'Rocroi' in m['filename'] ],
        'Breitenfeld': [ m for v in p['modules'].values() for m in v if 'Breitenfeld' in m['filename'] ]
    }
    return True


def triumph_and_tragedy(p):
    p['modules'] = {
        'C&T': [ m for v in p['modules'].values() for m in v if 'Triumph' not in m['filename'] ],
        'T&T':[ m for v in p['modules'].values() for m in v if 'Triumph' in m['filename'] ]
    }
    return True


def twin_peaks(p):
    cm = [ m for v in p['modules'].values() for m in v if m['filename'].startswith('Cedar') ]
    sm = [ m for v in p['modules'].values() for m in v if m['filename'].startswith('South') ]

    p['modules'] = {
        'Cedar Mountain': cm,
        'South Mountain': sm
    }
    return True


def ukraine_43(p):
    two_ed1 = p['modules']['2nd Edition v1.01']
    two_ed2 = p['modules']['2nd Edition v1.02']
    del p['modules']['2nd Edition v1.01']
    del p['modules']['2nd Edition v1.02']

    p['modules']['2nd Edition'] = [ *two_ed1, *two_ed2 ]
    return True


def yggdrasil(p):
    p['modules']['Dark Eclipse'] += p['modules'].pop('Dark Eclipse v2.0')
    return True


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
    return True


def westpac_1978(p):
    p['modules'] = {
        'Westpac 1978':  [ m for v in p['modules'].values() for m in v if 'Westpac' in m['filename'] ],
        'Denmark Strait 1978':  [ m for v in p['modules'].values() for m in v if 'Denmark' in m['filename'] ]
    }
    return True


def westwall(p):
    p['modules'] = {
        'Combined': [ m for v in p['modules'].values() for m in v if 'Quad' in m['filename'] ],
        'Arnhem': [ m for v in p['modules'].values() for m in v if 'Arnhem' in m['filename'] ],
        'Bastogne': [ m for v in p['modules'].values() for m in v if 'Bastogne' in m['filename'] ],
        'Hurtgen Forest': [ m for v in p['modules'].values() for m in v if 'Hurtgen' in m['filename'] ],
        'Remagen': [ m for v in p['modules'].values() for m in v if 'Remagen' in m['filename'] ]
    }
    return True


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
    'Across 5 Aprils': a5a,
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
    "Ardennes '44": ardennes_44,
    'Arena: Roma II': collapse_pkgs,
    'Arquebus: Men of Iron Volume IV': arquebus,
    'Arracourt': collapse_pkgs,
    'Arriba Espana!': arriba_espana,
    'Ashes: Rise of the Phoenixborn': collapse_pkgs,
    'Assault of the Dead: Tactics': assault_of_the_dead,
    'Atlanta': collapse_pkgs,
    'Attack Sub': collapse_pkgs,
    'Austerlitz': collapse_pkgs,
    'Austerlitz 1805': collapse_pkgs,
    'Avec Infini Regret': avec_infini_regret,
    'Axis & Allies': collapse_pkgs,
    'Axis & Allies Naval Miniatures: War at Sea': collapse_pkgs,
    'Axis & Allies Pacific: 1940 Edition': collapse_pkgs,

    # B
    'Balkan Front': collapse_pkgs,
    'Band of Brothers': collapse_pkgs,
    'BAOR': collapse_pkgs,
    'The Battle of the Bulge': tbotb,
    'The Battle of Monmouth (1982)': battle_of_monmouth,
    'Battle Hymn': battle_hymn,
    'Battle Hymn Vol.1: Gettysburg and Pea Ridge': battle_hymn_vol_1,
    'The Battle of Corinth: Standoff at the Tennessee, October 3-4, 1862': battle_of_corinth,
    'Battles for the Shenadoah: A Death Valley Expansion': battles_for_the_shenandoah,
    'The Blitzkrieg Legend: The Battle for France, 1940': collapse_pkgs,
    'Blockade': blockade,
    'Bloody Steppes of Crimea: Alma - Balaclava - Inkerman 1854': bloody_steppes,
    'Brandywine & Germantown': brandywine_germantown,

    # C
    'Case Yellow, 1940: The German Blitzkrieg in the West': case_yellow,
    'The Caucasus Campaign: The Russo-German War in the Caucasus, 1942': collapse_pkgs,
    'Cobra: Game of the Normandy Breakout': cobra,
    'Crimean War Battles': crimean_war_battles,
    'Crossing the Line: Aachen 1944': collapse_pkgs,

    # D
    'Dien Bien Phu: The Final Gamble': dien_bien_phu_tfg,

    # E
    'Epées et croisades': epees_crois,
    'Epées Normandes': epees_norm,
    'Epées souveraines : Bouvines 1214 - Worringen 1288': epees_souv,
    'Eurydice & Orpheus': no_box_image,

    # F
    'Fields of Fire': collapse_pkgs,
    'The Fighting General Patton': fighting_general_patton,
    'Forgotten Legions': forgotten_legions,
    'Four Battles in North Africa': four_battles_in_north_africa,

    # G
    'Gospitch & Ocaña 1809': gospitch,

    # H
    'A House Divided': a_house_divided,
    'Highway to the Kremlin': highway_to_the_kremlin,

    # K
    "The Kaiser's Pirates": kaisers_pirates,

    # L
    'La sombra del aguila': la_sombra,
    "La Trêve ou l'Epée": la_treve,
    "Le Dauphin et l'Epée": le_dauphin,
    "Le Lion et l'Epée": le_lion_et_lepee,
    'The Lord of the Rings: The Card Game': collapse_pkgs,

    # M
    'Manassas': collapse_pkgs,

    # N
    'Napoleon at War:Four Battles': nawfb,
    'Neuroshima Hex!': collapse_pkgs,
    'Next War: Korea': next_war_korea,
    'Normandy, The Beginning of the End': collapse_pkgs,
    'Nothing Gained But Glory': ngbg,

    # O
    'Operation Theseus: Gazala 1942': collapse_pkgs,

    # P
    'Par le feu, le fer et la Foi': par_le_feu,
    'Paris vaut bien une messe !': paris_vaut,
    'Pericles: The Peloponnesian Wars': pericles,
    "Prussia's Glory II": prussias_glory_ii,

    # Q
    'Quatre Batailles en Espagne': quatre_batailles_en_espagne,

    # R
    'Raider Drop Zone': raider_drop_zone,
    'Return to the Rock: Corregidor, 1945': return_to_the_rock,
    'Roads to Leningrad: Battles of Soltsy and Staraya Russa, 1941': roads_to_l,
    'Rommel (2017)': no_box_image,
    'Ruse & Bruise': collapse_pkgs,
    'Russian Front': collapse_pkgs,

    # S
    'Small World Underground': collapse_pkgs,
    'Star Wars: Armada': collapse_pkgs,

    # T
    'TablaPeriodica': no_box_image,
    'Thirty Years War Quad': tywq,
    'This Accursed Civil War': tacw,
    'Three Days of Glory 1805': tdog1805,
    'Triumph & Tragedy': triumph_and_tragedy,
    'Twin Peaks': twin_peaks,

    # U
    "Ukraine '43": ukraine_43,
    'UND1C1': collapse_pkgs,
    'Universe Risk': collapse_pkgs,
    'Utopia Engine': collapse_pkgs,

    # V
    'Valor and Victory': collapse_pkgs,
    'Victory in Vietnam': collapse_pkgs,

    # W
    "Wacht am Rhein': The Battle of the Bulge, 16 Dec 44-2 Jan 45": wacht_am_rhein,
    'War At Sea': collapse_pkgs,
    'The War At Sea (first edition)': collapse_pkgs,
    'WARLINE: Maneuver Strategy & Tactics': collapse_pkgs,
    'Westpac 1978': westpac_1978,
    'Westwall: Four Battles to Germany': westwall,

    # Y
    'Ye Gods!': collapse_pkgs,
    'Yggdrasil': yggdrasil,

    # Z
    'Zeppelin Raider': collapse_pkgs,
    'Zürich 1799': collapse_pkgs
}


async def fixup_page(path):
    print(path)

    with open(path, 'r') as f:
        p = json.loads(f.read().replace('\\u200e', ''))

    title = p['title']

    # apply fixups
    fixup = fixups.get(title, None)
    if fixup is None or not fixup(p):
        # rewrite packages
        mods = p.get('modules', {})
        secs = list(mods.keys())
        for sec in secs:
            # if sec is a version, dump everything into the common package
            if sec == title or try_parse_version(sec) is not None:
                m = mods.setdefault('Module', [])
                m += mods[sec]
                del mods[sec]

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
