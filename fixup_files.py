import json


user_fixups = {
    "File:Machiavelli.vmod": 'Mycenae',
    "File:Manv1b.vmod": 'Mbeninger',
    "File:World Killer v1.0 09 24 10.vmod": 'Brian448',
    "File:MarcoPolo.vmod": 'Yuyu',
    "File:Marengo 0.3.vmod": 'Bsmith',
    "File:Maria User Guide.pdf": 'SteveBish',
    "File:LoanoVassal.vmod": 'Bubulle',
    "File:2-BAOR 1-1.vmdx": 'Rfdoane',
    "File:LMaps-3-BOAR.vmdx": 'Rfdoane',
    "File:LMaps-2-FRG.vmdx": 'Rfdoane',
    "File:MBT-IDF.vmod": 'Rfdoane',
    "File:British-USMC.vmdx": 'Rfdoane',
    "File:IDF.vmdx": 'Rfdoane',
    "File:IMPORTANT - readme.txt": 'Rfdoane',
    "File:Nadir DTP Pack.vmdx": 'Rfdoane',
    "File:Terrain Pack.vmdx": 'Rfdoane',
    "File:Turret MOD.vmdx": 'Richz99',
    "File:Version History.txt": 'Rfdoane',
    "File:Misterio.vmod": 'Yuyu',
    "File:Spanish-Eagles-Vassal-1.0.vmod": 'Kcoombs',
    "File:EV-1.01.vmod": 'TeTeT',
    "File:EV-1.0.vmod": 'TeTeT',
    "File:Espana1936v12.vmod": 'Norovirus',
    "File:Espana1936.vmod": 'Norovirus',
    "File:Espinosa v1.1.vmod": 'Taikunkikun',
    "File:EuroFront II v1.8.vmod": 'bennyb',
    "File:Naipe en la Ruta de la Selva.vmod": 'Packonn',
    "File:Not Go v1.2.vmod": 'Narfanator',
    "File:Pacific Victory v1 1 1.vmod": 'Fbedard24',
    "File:PaxRomana4.1.vmod": 'Kcoombs',
    "File:Playing Cards.vmod": 'Tadufre',
    "File:Pocketrockets.vmod": 'Gaetbe',
    "File:Khaki1.vmod": 'Dmart',
    "File:Price of Freedom v1.0.vmod": 'Kcoombs',
    "File:PTA Vassal Sept 17 2008.vmod": 'Brennenreece',
    "File:Princes of the Renaissance-0.2.vmod": 'Quicksabre',
    "File:PrussiasDefiantStand-v5.vmod": 'Shilinski',
    "File:Tpovs 2.0.1.vmod": 'Harm',
    "File:OCOWargamer41a.vmod": 'Mwilding',
    "File:Offrandes.vmod": 'Gaetbe',
    "File:Ogremanual.zip": 'Zass',
    "File:OGRE.vmod": 'Zass',
    "File:Op Felix.vmod": 'Jmlima',
    "File:OpM v1 0.vmod": 'Kishel',
    "File:Othello-Reversi.vmod": 'Aidendouglass',
    "File:Outlaws.vmod": 'Jerry_Tresman',
    "File:Quintet v1 0.vmod": 'Brian448',
    "File:Raceday.vmod": 'Deaneubanks',
    "File:Race for berlin 1.1.vmod": 'Francois_Xavier_Euze',
    "File:GBoH RAN.vmod": 'Grenadyer',
    "File:RedDragonInn v1 6.vmod": 'Neumannium',
    "File:Rommel-Desert-v6.vmod": 'shilinski',
    "File:Rommel-Desert-v7.vmod": 'shilinski',
    "File:RustleMania v0.2.1.vmod": 'Kcoombs',
    "File:Starmada.vmod": 'Jefferyschutt',
    "File:Starmada AE.vmod": 'MadSeason',
    "File:Starmada Vassal Playing Guide.pdf": 'MadSeason',
    "File:StormOverStalingrad v12.vmod": 'Brent_Easton',
    "File:SOS version history.zip": 'Brent_Easton',
    "File:StradaRomana.vmod": ' Gaetbe',
    "File:Strategos 0 1.vmod": 'IrishBouzouki',
    "File:Strategos 0 2.vmod": 'IrishBouzouki',
    "File:Succession Wars1.01.vmod": 'Skorpio',
    "File:BattleForNormandy 2.vmod": 'Joel_Toppen',
    "File:Multi.vmod": 'Thorndraco',
    "File:End of Empire v1 3.vmod": 'Tswider2',
    "File:Epic 0 2.vmod": 'Austerity',
    "File:Project Discovery.vmod": 'Srmansfield',
    "File:BSG Pyramid.vmod": 'Soft-bug',
    "File:OdiseaEspacial.vmod": 'Yuyu',
    "File:Dealer McDope 1.0 .vmod": 'burdick.ip.research',
    "File:Overthetop 0.12.vmod": 'Josh_Laverty',
    "File:Overthetop 0.11.zip": 'Josh_Laverty',
    "File:Over the top rules v011.pdf": 'Josh_Laverty',
    "File:Revolutionary Road B2C R1.01.vmod": 'Jardic',
    "File:The Rum Run-0.1.vmod": 'Alex_Coulombe',
    "File:Starvation Island Ver1.vmod": 'Mark_Evans',
    "File:Sticks and Stones.vmod": 'Xavier',
    "File:TarotGame.vmod": 'Tarotgames',
    "File:Carcassonne-2.0.vmod": 'ColtsFan76',
    "File:Carcassonne-Simple.vmod": 'Sultan',
}


def run():
    ipath = 'data/files.json'
    opath = 'data/files_fixed.json'

    with open(ipath, 'r') as f:
        p = json.load(f)

    for k, v in p.items():
        if fixup := user_fixups.get(k, None):
            v['user'] = fixup

    with open(opath, 'w') as f:
        json.dump(p, f, indent=2)


if __name__ == '__main__':
    run()
