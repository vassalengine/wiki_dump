import json

# echo -e '.mode tab \n SELECT fileurl, filename, version_raw, version, version_major, version_minor, version_patch, version_pre, version_build, semver FROM files_w ORDER BY filename;' | sqlite3 projects.db >after.3
# diff --color=always -U 0 before after.3

# comm -13 b a3 | cut -f1,5-8 | sed -e 's/^.*\/images\///' | awk '{ printf "'%s': (%s, %s, %s, %s, None),\n", $1, $2, $3, $4, $5 }'

version_fixups = {
    '0/00/Acta_2e_v1.3release.vmod': (1, 3, 0, None, None),
    '0/00/Battle_of_the_Bulge_v1.2.vmod': (1, 2, 0, None, None),
    '0/00/BWN_v1.1_rev.vmod': (1, 1, 0, None, None),
    '0/00/Enemy_Action-Kharkov_2-Player_Version_1.31.vmod': (1, 31, 0, None, None),
#    '0/00/Launch_Fighters_1.1.vmod': (0, 6, 0, b, None),
    '0/01/Starfire_2.1_retro.vmod': (2, 1, 0, None, None),
    '0/03/Flying_Colors_vol4_1-0-2.vmdx': (1, 0, 2, None, None),
#    '0/04/Central_America_3.2.1.vmod': (3, 2, 1, None, None),
    '0/04/Pacific_Victory_v2.0f.vmod': (2, 0, 0, 'f', None),
    '0/07/Battles_of_Bull_Run.vmod': (1, 0, 0, None, None),
    '0/07/Pea_Ridge_SPI_v2.1.vmod': (2, 1, 0, None, None),
    '0/08/DoE_1.2.vmod': (1, 2, 0, None, None),
#    '0/09/AfrikaKorps-2.0-ch-oldschool.vmod': (1, 1, 0, OS, None),
    '0/09/Aww-v10.vmod': (1, 0, 0, None, None),
    '0/09/Raceday.vmod': (1, 3, 0, None, None),
    '0/0b/Stonewall_ST_V072.VMOD': (0, 72, 0, None, None),
    '0/0c/Caesar2.vmod': (0, 1, 0, None, None),
    '0/0c/War_of_the_suns_v06.vmod': (0, 6, 0, None, None),
    '0/0f/Alamo114.vmod': (1, 14, 0, None, None),
    '1/10/GBACW-Cedar-Mountain_v2.vmod.vmod': (2, 0, 0, None, None),
#    '1/10/TSSSF_1-0-5_rus.vmod': (1, 0, 5, rus, None),
    '1/11/ABimP_V1.03.vmod': (1, 3, 0, None, None),
    '1/12/AVC_v0_01.vmod': (0, 1, 0, None, None),
    '1/12/Carrier_v013.vmod': (0, 13, 0, None, None),
#    '1/12/Pericles_V_1-0_Solitaire.vmod': (1, 0, 0, Solitaire, None),
    '1/13/Germania.vmod': (1, 5, 0, None, None),
    '1/13/GMT_Vietnam_2_24.vmod': (2, 24, 0, None, None),
#    '1/14/Marine_Fighter_Squadron_1_1alt.vmod': (1, 1, 0, alt, None),
    '1/14/NBPTD27.vmod': (2, 7, 0, None, None),
    '1/15/B-17_QotS-v098.vmod': (0, 98, 0, None, None),
    '1/15/FD_Lite.vmod': (1, 0, 0, None, None),
    '1/16/CarrierV2.vmod': (2, 0, 0, None, None),
    '1/18/Bayonets_N_Tomahawks_1.0.vmod': (1, 0, 0, None, None),
    '1/18/GuadMaster.vmod': (1, 0, 0, None, None),
#    '1/18/Napoleons_Triumph_v0.84-no-teams.vmod': (0, 84, 0, noteams, None),
    '1/19/CasaFantasmas.vmod': (1, 0, 0, None, None),
    '1/19/Kremlin_v3.1.vmod': (3, 1, 0, None, None),
    '1/1a/Bomber_v095.vmod': (0, 95, 0, None, None),
    '1/1b/TheOtherSide1.1.vmod': (1, 1, 0, None, None),
#    '1/1c/PW2_v101.vmod': (2, 1, 0, , None),
    '1/1d/DigDownDwarf-v1-2.vmod': (1, 2, 0, None, None),
    '1/1d/Playing_Cards.vmod': (1, 0, 0, None, None),
    '1/1d/On_the_Bounce_-_TR_1.vmod': (1, 0, 0, None, None),
    '1/1e/FullMetalPlanet-v2.0.vmod': (2, 0, 0, None, None),
#    '1/1e/SPQR_Deluxe_v2.3.vmod': (2, 3, 0, c, None),
    '1/1f/Eastern_Front_Solitaire.vmod': (0, 95, 0, None, None),
#    '1/1f/PW2_v100.vmod': (2, 1, 0, , None),
    '1/1f/Saipan_v100.Vmod': (1, 0, 0, None, None),
    '2/20/Combat_3_1.vmod': (3, 1, 0, None, None),
    '2/20/GMT_Vietnam_2_25.vmod': (2, 25, 0, None, None),
    '2/21/AVA-v1_22.vmod': (1, 2, 2, None, None),
    '2/22/Enemy_Action_Kharkov-German_Solo_Version_1.6.vmod': (1, 6, 0, None, None),
    '2/22/Stellar_Conquest_K14.vmod': (14, 0, 0, None, None),
    '2/23/Close_Assault.vmod': (0, 95, 0, None, None),
    '2/24/Struggle_for_Europe_v2.1.vmod': (2, 1, 0, None, None),
    '2/25/CaseBlue_GBII_v510.vmod': (5, 10, 0, None, None),
#    '2/25/M3E-Malifaux_GG3-v3a.vmod': (3, 0, 0, eMalifauxGG3V3a, None),
    '2/25/War_of_the_suns_v05.vmod': (0, 5, 0, None, None),
    '2/26/Race_formula90_v6.vmod': (6, 0, 0, None, None),
    '2/27/Acta_2e_v1.36release.vmod': (1, 36, 0, None, None),
#    '2/29/PW2_v102.vmod': (2, 1, 2, , None),
    '2/29/Sword-of-rome.vmod': (4, 0, 0, None, None),
    '2/2b/Battlefleet_Mars_V2.0.vmod': (2, 0, 0, None, None),
    '2/2c/Silent_War.vmod': (0, 97, 0, None, None),
    '2/2d/Devils2PayR3a.vmod': (3, 0, 0, 'a', None),
    '2/2d/Klinzha.vmod': (0, 11, 0, None, None),
    '2/2d/RSWE_v1.3.vmod': (1, 3, 0, None, None),
    '2/2d/TPStalingrad.vmod': (1, 0, 0, None, None),
    '2/2e/Guam_v090.Vmod': (0, 90, 0, None, None),
    '2/2e/Santa_Cruz_1797_v1.04.vmod': (1, 4, 0, None, None),
#    '3/30/AFK-2.3.vmod': (0, 2, 3, , None),
    '3/30/AlienFrontier12.vmod': (1, 2, 0, None, None),
#    '3/30/Napoleons_Triumph_v0.86-no-teams.vmod': (0, 86, 0, noteams, None),
    '3/32/3W_BattleCry%21.vmod': (1, 0, 0, None, None),
    '3/32/GBACW-Cedar-Mt.vmod': (1, 0, 0, None, None),
    '3/34/Case_Blue_1.1.1.vmod': (1, 1, 1, None, None),
    '3/34/TheOtherSide1.3.1.vmod': (1, 3, 1, None, None),
    '3/34/VIPv34p01.vmod': (3, 4, 0, 'p01', None),
    '3/34/WHDW_2X43.vmod': (2, 43, 0, None, None),
    '3/35/FoF_All_Volumes_v3.3.03_X_PUBLIC.vmod': (3, 3, 3, None, None),
    '3/36/Hitlers_Reich_1.4.vmod': (1 ,4, 0, None, None),
    '3/37/Halebarde%26gonfanon.vmod': (1, 0, 0, None, None),
#    '3/37/Iran_Irak_V1.2_En.vmod': (1, 2, 0, b, None),
#    '3/37/M3E-Malifaux-v1i.vmod': (3, 0, 0, ev1i, None),
    '3/37/Mr_Lincolns_War.vmod': (1, 0, 0, None, None),
    '3/38/1863_Civil_War_Game.vmod': (1, 0, 0, None, None),
    '3/38/FallingSky_v2.01.vmod': (2, 0, 1, None, None),
    '3/39/RSBDE-v1.0b02.vmod': (1, 0, 0, 'b02', None),
    '3/3a/DRUID.vmod': (1, 0, 0, None, None),
    '3/3b/Saipan_v101.Vmod': (1, 1, 0, None, None),
    '3/3c/Db_FrenchGivorsClub_3_1_0.vmod': (3, 1, 0, None, None),
    '3/3c/Unterseeboot.vmod': (0, 7, 0, None, None),
    '3/3d/FightingFormations%28GD%29final_v1.09.vmod': (1, 0, 9, None, None),
#    '3/3d/M3E-Malifaux_MoM-v4e.vmod': (0, 0, 0, v4e, None),
    '3/3e/Attack_Sub_v095.vmod': (0, 95, 0, None, None),
    '3/3e/TheOtherSide2.0_BTOS.vmod': (2, 0, 0, None, None),
    '4/40/Cudgel_duel_1.02.vmod': (1, 2, 0, None, None),
#    '4/40/La_Granja_v1.1DE.vmod': (1, 1, 0, DE, None),
    '4/40/NWIP_1.61.vmod': (1, 6, 0, 'Beta', None),
    '4/40/Spartacus-v1.0.vmod': (1, 0, 0, None, None),
    '4/41/Battle_of_the_Bulge_v1.1.vmod': (1, 1, 0, None, None),
    '4/41/Leaving_Earth_No_OP_v1.2a.vmod': (1, 2, 0, 'a', None),
    '4/45/Hoplite101.vmod': (1, 0, 1, None, None),
    '4/45/Queens%27Gambitv1.5.vmod': (1, 5, 0, None, None),
    '4/45/The_Late_Unpleasantness_IITASv3.vmod': (3, 0, 0, None, None),
    '4/46/VMidway.vmod': (2, 0, 0, None, None),
    '4/47/Waterloo-A-1_0.vmod': (1, 0, 0, None, None),
    '4/48/Enemy_Action_Kharkov-Soviet_Solo_Version_1.2.vmod': (1, 2, 0, None, None),
    '4/48/Salvo.vmod': (0, 1, 0, None, None),
    '4/49/Central_America_v.2.12.vmod': (2, 1, 2, None, None),
#    '4/4a/CivilWar17b01.vmod': (1, 7, 0, b01, None),
    '4/4a/Fitsb11.vmod': (1, 1, 0, None, None),
    '4/4a/Nemesis_v2_3a.vmod': (2, 3, 0, 'a', None),
    '4/4a/Starmada.vmod': (1, 0, 0, None, None),
#    '4/4b/M3E-Malifaux-v1d.vmod': (3, 0, 0, ev1d, None),
    '4/4b/Star_Fleet_Battle_Force_v.1.1_safe.vmod': (1, 1, 0, None, None),
    '4/4c/Novi_1799_ver1.1.vmod': (1, 1, 0, None, None),
    '4/4c/Roads-to-Stalingrad_-_v_1-01.vmod': (1, 1, 0, None, None),
    '4/4c/Skies_above_the_Reich_v097.vmod': (0, 97, 0, 'BETA', None),
    '4/4d/BAR-Germantown_v101.vmod': (1, 0, 1, None, None),
    '4/4d/Paths_of_Glory_7.2.2.1.vmod': (7, 2, 2, '1', None),
    '4/4d/The_Dark_Valley_G01.vmod': (1, 1, 0, None, None),
#    '4/4e/M3E-Malifaux-v1c.vmod': (3, 0, 0, ev1c, None),
    '4/4e/Napoleons_Triumph_v0.89.vmod': (0, 89, 0, None, None),
#    '4/4e/Queens%27_Gambitv16a.vmod': (1, 6, 0, MapFixed, None),
    '5/51/Aces.vmod': (1, 0, 0, None, None),
    '5/51/First_Team_11a.vmod': (1, 1, 0, None, None),
    '5/51/Quarriors-v03j.vmod': (0, 3, 0, 'j', None),
    '5/52/Caesar_in_Gaul_1.1.vmod': (1, 1, 0, None, None),
    '5/52/RSBDE-v1.2.vmod': (1, 2, 0, None, None),
#    '5/52/TAHGC-Scenario-2000-Operation_Hubertus-Maps-1-7-8-20-21-22.zip': (1, 7, 8, 202122, None),
#    '5/53/CardsAgainstHumanity1_0%2BCustom.vmod': (1, 0, 0, Custom, None),
    '5/53/Gunslinger_v_1.9.4DC.vmod': (1, 9, 4, None, None),
#    '5/53/Last_Battle_Ie_Shima-1-3.vmod': (1, 2, 0, JV, None),
#    '5/54/AFK-2.3.1.vmod': (0, 2, 3, , None),
#    '5/56/Iran_Irak_V1.2_Fr.vmod': (1, 2, 0, a, None),
    '5/56/Targui.vmod': (1, 0, 0, None, None),
    '5/57/Case_Blue_1.1.vmod': (1, 1, 0, None, None),
    '5/57/TK2_2_00.vmod': (2, 0, 0, None, None),
    '5/58/Db_FrenchGivorsClub_3_0_1.vmod': (3, 0, 1, None, None),
#    '5/59/Arkwright_v1.0.3DE.vmod': (1, 0, 3, DE, None),
    '5/59/WSS-NBE-3.02.vmod': (3, 0, 2, None, None),
#    '5/5a/M3E-Malifaux_Burns-v3.vmod': (3, 0, 0, eMalifauxBurnsV3, None),
    '5/5b/Briscola_v10.vmod': (0, 2, 0, None, None),
    '5/5b/Gettysburg150-Ver-1-1.vmod': (1, 1, 0, None, None),
#    '5/5b/Korea_V5_01.vmod': (5, 1, 0, JEPMod8, None),
    '5/5b/PanzerExp2_1-2-2.vmdx': (1, 2, 2, None, None),
    '5/5b/TurningPoint-1-01.vmod': (1, 1, 0, None, None),
#    '5/5b/RE-3-2.vmod': (4, 25, 0, build1, None),
#    '5/5c/A3R_Rev1702_AWAW.vmod': (1, 7, 0, 2, None),
    '5/5c/AtBR-v1b.vmod': (1, 0, 0, 'b', None),
    '5/5c/NATO_DSE_v1-4.vmod': (1, 4, 0, None, None),
#    '5/5c/PW2_v103.vmod': (2, 1, 3, , None),
    '5/5d/Conflict.vmod': (1, 0, 0, None, None),
    '5/5d/SecretHitler05.vmod': (0, 5, 0, None, None),
    '5/5d/TankDuel_v1-06.vmod': (1, 0, 6, None, None),
    '5/5d/TheOtherSide1.3.2.vmod': (1, 3, 2, None, None),
#    '5/5e/M3E-Explorers-v2c.vmod': (3, 0, 0, eExplorersV2c, None),
    '5/5f/Europe_Engulfed_v3.2.0_Release.vmod': (3, 2, 0, None, None),
#    '5/5f/RFTv222_E-v1.0.vmod': (2, 2, 2, E.1.0, None),
    '5/5f/WHDW_2X44.vmod': (2, 44, 0, None, None),
    '6/61/Counter-Attack_Arras.vmod': (1, 0, 0, None, None),
    '6/61/TAC_v1.5.vmod': (1, 5, 0, None, None),
#    '6/62/M3E-Malifaux_MoM-v4a.vmod': (0, 0, 0, v4a, None),
    '6/63/Napoleons_Triumph_v0.88.vmod': (0, 88, 0, None, None),
    '6/64/RSBDE-v1.1.1-p02.vmod': (1, 1, 1, 'b02', None),
#    '6/65/Gandhi_1.1_shorter_map.vmod': (1, 1, 0, shortermap, None),
    '6/66/Alchemists_-_0.90.vmod': (0, 90, 0, None, None),
#    '6/66/M3E-Explorers-v2.vmod': (3, 0, 0, eExplorersV2, None),
    '6/66/Bridge.vmod': (1, 0, 0, None, None),
#    '6/67/Malifaux_3_Ed_3_4_10.vmod': (3, 4, 10, , None),
    '6/68/AirPower.vmod': (0, 6, 0, None, None),
#    '6/68/Korea_v4_25_rc4.vmod': (4, 25, 0, JEPa, None),
    '6/68/Risk2210.vmod': (1, 5, 0, None, None),
    '6/68/Tic-tac_chec.vmod': (1, 0, 0, None, None),
    '6/6a/ASLW_2nd_Ed.vmod': (2, 0, 0, None, None),
#    '6/6a/EAA-German-Solo-1_1a.vmod': (1, 0, 0, a, None),
    '6/6b/GBACW-Corinth.vmod': (1, 0, 0, None, None),
    '6/6b/Iberos.vmod': (1, 1, 0, None, None),
    '6/6c/Heroclix-02.vmod': (0, 2, 0, None, None), 
    '6/6d/CoH_v1_3.vmod': (1, 31, 0, None, None),
    '6/6e/Emperor_of_China.vmod': (1, 0, 0, None, None),
    '6/6f/Havannah.vmod': (1, 0, 0, None, None),
    '7/70/HFP_Wargamer_39b.vmod': (2, 0, 0, None, None),
    '7/70/NacMafia.vmod': (1, 0, 0, None, None),
    '7/71/Vmbb.vmod': (1, 0, 0, None, None),
#    '7/71/Tokyo_express_v.096.vmod': (0, 9, 0, Beta, None),
    '7/72/DitT_1.0.vmod': (1, 0, 0, None, None),
    '7/74/LOTRC_BY_D0NK1J0T3_1.1.vmod': (1, 1, 0, None, None),
#    '7/74/Terraforming_Mars_307_fr.vmod': (3, 0, 7, fr, None),
#    '7/75/DDay-1.0-ch-oldschool.vmod': (1, 0, 0, OS, None),
    '7/75/Europe_Engulfed_v3.0.1_Release.vmod': (3, 0, 1, None, None),
    '7/75/Illuminati04.vmod': (0, 4, 0, None, None),
#    '7/75/RFTv2210_E-v1.0.vmod': (2, 2, 1, E.1.0, None),
    '7/76/RSBDE-v1.1.vmod': (1, 1, 0, None, None),
    '7/76/RSWE_v1.01.vmod': (1, 0, 1, None, None),
#    '7/77/AxisEmpires_9.0.7-perso.vmod': (9, 0, 0, boka, None),
    '7/79/Aireaters006.vmod': (0, 0, 6, None, None),
    '7/79/AlienFrontier.vmod': (1, 5, 1, None, None),
    '7/79/Central_America_v.1.12.vmod': (1, 1, 2, None, None),
    '7/79/EOTID.vmod': (1, 2, 0, None, None),
    '7/79/Nie11.vmod': (1, 1, 0, None, None),
    '7/79/Raj.vmod': (1, 1, 0, None, None),
#    '7/7a/M3E-Malifaux_GG3-v3d.vmod': (3, 0, 0, eMalifauxGG3V3d, None),
#    '7/7a/NWTaiwan1_3_Revised.vmod': (1, 3, 0, Revised, None),
    '7/7b/GMT_Vietnam_2_21.vmod': (2, 21, 0, None, None),
    '7/7b/World_War_3_ver2.vmod': (2, 0, 0, None, None),
    '7/7d/Dungeon_Alliance_1.1.vmod': (1, 1, 0, None, None),
    '7/7d/RBS-12p14.vmod': (1, 2, 0, 'p14', None),
#    '7/7e/FitG-v2_05-Solitaire.vmod': (2, 5, 0, Solitaire, None),
#    '7/7e/TLD-0.8.0.vmod': (0, 8, 0, b080d, None),
    '7/7f/ECA_Doolittle_Raid%281%29.Vmod': (1, 0, 0, None, None),
#    '8/80/Escape_from_Colditz_V3.0.vmod': (0, 2, 0, , None),
    '8/80/Spartacus1.2.vmod': (1, 2, 0, None, None),
    '8/80/STGD-31b06-wga.vmod': (3, 1, 0, 'b06', None),
    '8/81/Feudal11.vmod': (1, 1, 0, None, None),
    '8/81/TA6B.vmod': (1, 0, 0, None, None),
    '8/81/Trojanwar.vmod': (1, 0, 0, None, None),
#    '8/82/East-is-red-v03.vmod': (0, 2, 0, DRAFT, None),
#    '8/82/Malifaux_3_Ed_3_3_8.vmod': (0, 0, 0, v3.3.8, None),
#    '8/83/1775_Rebellion_Module_Fixed_1.00.vmod': (0, 90, 0, , None),
    '8/83/Acta_2e_v1.2.vmod': (1, 2, 0, None, None),
#    '8/85/PW2_v104.vmod': (2, 1, 4, , None),
    '8/85/Trader.vmod': (1, 0, 0, None, None),
    '8/86/FP_CA171.vmod': (1, 7, 1, None, None),
    '8/86/Pax_Porfiriana.vmod': (1, 0, 2, None, None),
    '8/87/Aireaters002.vmod': (0, 0, 2, None, None),
    '8/87/Chancellorsville_1.2.vmod': (1, 2, 0, None, None),
    '8/87/TheOtherSide2.1_BTOS.vmod': (2, 1, 0, None, None),
#    '8/88/NWTaiwan1_0_Revised.vmod': (1, 0, 0, Revised, None),
    '8/89/Napoleons_Triumph_v0.81-no-teams.vmod': (0, 81, 0, None, None),
    '8/8b/Novi_1799.1.0.vmod': (1, 0, 0, None, None),
#    '8/8b/WSR_v2.1DE.vmod': (2, 1, 0, DE, None),
    '8/8c/BoltAction2.vmod': (1, 0, 0, None, None),
    '8/8d/FoF_All_Volumes_v3.3.02_PUBLIC_E.vmod': (3, 3, 2, None, None),
#    '8/8d/M3E-Explorers-v2b.vmod': (3, 0, 0, eExplorersV2b, None),
    '8/8d/Perryville19.vmod': (1, 9, 0, None, None),
    '8/8e/Babylon_5_ACTA_v1_38.vmod': (1, 38, 0, None, None),
    '8/8e/Monsterpocalypse_1.00.vmod': (1, 0, 0, None, None),
#    '8/8f/M3E-Malifaux-v1g.vmod': (3, 0, 0, ev1g, None),
    '8/8f/Target_Arnhem.vmod': (1, 1, 0, None, None),
#    '9/90/Dixit_0.7eng_beta.vmod': (0, 7, 0, betaEnglishedition, None),
    '9/91/Raider_16_-_Atlantis.vmod': (1, 0, 1, None, None),
    '9/91/Rattenkrieg.vmod': (1, 0, 0, None, None),
    '9/92/Carthage.vmod': (1, 2, 0, None, None),
    '9/92/GMT_Vietnam_2_23.vmod': (2, 23, 0, None, None),
    '9/92/WAR_SPI_1977_V13.vmod': (1, 3, 0, None, None),
#    '9/93/M3E-Malifaux_MoM-v4f.vmod': (0, 0, 0, v4f, None),
#    '9/93/NWTaiwan1_4_Revised.vmod': (1, 4, 0, Revised, None),
#    '9/93/Tokyo_express_v0.95.vmod': (0, 9, 0, Beta, None),
    '9/94/Mosbys_raiders.vmod': (0, 32, 0, None, None),
    '9/94/RoadRage1.4a.vmod': (1, 4, 0, 'a', None, None),
    '9/96/For_the_people_2006_1_0.vmod': (1, 0, 0, None, None),
    '9/96/Pax_Porfiriana-v103.vmod': (1, 0, 3, None, None),
    '9/98/Blackbeard-1.152.vmod': (1, 15, 2, None, None),
    '9/98/TK2_1_03.vmod': (1, 3, 0, None, None),
    '9/99/Pacific_Victory_v1.2.1.vmod': (1, 2, 1, None, None),
#    '9/99/Queens%27_Gambitv1.6.vmod': (1, 6, 0, MapFixed, None),
#    '9/9b/PW2_v028.vmod': (2, 0, 28, , None),
    '9/9c/Bg2eto.vmod': (0, 1, 0, None, None),
    '9/9c/Total-war-v05a.vmod': (0, 5, 0, 'a', None),
    '9/9c/Risk_Europe.vmod': (1, 0, 0, None, None),
    '9/9e/THW.vmod': (1, 0, 0, None, None),
#    '9/9e/M3E-Explorers-v2a.vmod': (3, 0, 0, eExplorersV2a, None),
#    '9/9e/Terraforming_Mars_267c.vmod': (2, 6, 7, c, None),
    '9/9f/Colonial_Diplomacy.vmod': (1, 0, 0, None, None),
    '9/9f/OCOWargamer41a.vmod': (1, 0, 0, None, None),
#    '9/9f/UKC_v2.023_FOW.vmod': (2, 23, 0, FOW, None),
    'a/a0/PanzerArmeeAfrika-001e.vmod': (1, 0, 0, 'e', None),
#    'a/a2/AfrikaKorps-1.1-ch-oldschool.vmod': (1, 1, 0, OS, None),
    'a/a3/Chabyrinthe.vmod': (1, 0, 0, None, None),
    'a/a3/MagicRealm.vmod': (2, 5, 0, None, None),
    'a/a4/Hera_and_Zeus.vmod': (1, 0, 0, None, None),
    'a/a6/La_Herencia_de_Tia_Agata_V1.1.vmod': (1, 1, 0, None, None),
    'a/a6/Rise_of_the_Roman_Republic.vmod': (1, 0, 0, None, None),
    'a/a9/Khas.vmod': (1, 0, 0, None, None),
    'a/a9/Radetzky.0.92.vmod': (0, 92, 0, None, None),
#    'a/aa/Crusader_Kingdoms1.0.vmod': (0, 0, 0, X, None),
    'a/aa/Justinian.vmod': (1, 0, 0, None, None),
    'a/aa/TheOtherSide1.2.vmod': (1, 2, 0, None, None),
    'a/ab/FITL_VASSAL_1.32.vmod': (1, 3, 2, None, None),
#    'a/ab/Freedom-in-the-Galaxy-v2_05.vmod': (2, 5, 2, Player, None),
    'a/ab/VIPv32b05.vmod': (3, 2, 0, 'b05', None),
#    'a/ac/M3E-Malifaux_Burns-v3d.vmod': (3, 0, 0, eMalifauxBurnsV3d, None),
#    'a/ac/UKC_v2.024_FOW.vmod': (2, 24, 0b90b8c28aae0e2f47e2496677f41aea61e43dd97, FOW, None),
    'a/ad/Carrier_mod_01.vmod': (0, 10, 0, None, None),
    'a/ad/Race_formula90_v6_1.vmod': (6, 1, 0, None, None),
    'a/ae/BfM2v0.5_beta.vmod': (0, 5, 0, 'beta', None),
    'a/ae/Elfballv5-1-1.vmod': (5, 1, 1, None, None),
#    'a/ae/M3E-Malifaux-v1f.vmod': (3, 0, 0, ev1f, None),
    'b/b1/ItaliaGame_01.vmod': (1, 0, 0, None, None),
    'b/b2/FITL_VASSAL_1.31.vmod': (1, 3, 1, None, None),
    'b/b2/TheOtherSide1.3.vmod': (1, 3, 0, None, None),
    'b/b2/WAR_SPI_1977_V142.vmod': (1, 42, 0, None, None),
    'b/b3/Btrc6001.vmod': (1, 10, 0, None, None),
    'b/b3/LaFugadeColdit3.vmod': (2, 0, 0, None, None),
#    'b/b3/M3E-Malifaux_Burns-v3e.vmod': (3, 0, 0, eMalifauxBurnsV3e, None),
    'b/b5/Scratch_One_Flat_Top.vmod': (0, 96, 0, None, None),
    'b/bb/FITL_VASSAL_1.4.vmod': (1, 4, 0, None, None),
#    'b/bb/M3E-Malifaux_MoM-v4g.vmod': (0, 0, 0, v4g, None),
    'b/bb/TI3_VASSAL_v1_02SE.vmod': (1, 2, 0, None, None),
    'b/bd/AVA-v1_21.vmod': (1, 2, 1, None, None),
#    'b/be/Back_to_the_future_2_3_board_game_1.0.vmod': (1, 0, 0, , None),
#    'b/be/M3E-Malifaux_GG3-v3b.vmod': (3, 0, 0, eMalifauxGG3V3b, None),
    'b/be/Wll.vmod': (1, 0, 0, None, None),
    'b/bf/Barefoot_1_01.vmod': (1, 1, 0, None, None),
    'b/bf/Saipan_v102.Vmod': (1, 2, 0, None, None),
#    'c/c0/M3E-Malifaux_Burns-v3c.vmod': (3, 0, 0, eMalifauxBurnsV3c, None),
#    'c/c1/TLD-v0.8b080c-11-7-20.vmod': (0, 8, 0, b080d, None),
    'c/c1/The_Battle_Of_Moscow.vmod': (1, 0, 0, None, None),
    'c/c3/CV_BattleOfMidway.vmod': (1, 0, 0, None, None),
#    'c/c3/PlanOrange101.vmod': (1, 0, 1, , None),
    'c/c3/PTH-Version-2.1.vmod': (2, 1, 0, None, None),
    'c/c3/Senet.vmod': (1, 0, 0, None, None),
    'c/c4/DigDownDwarf-v1-3.vmod': (1, 3, 0, None, None),
    'c/c4/Montelimar_v091.Vmod': (0, 91, 0, None, None),
#    'c/c5/JoV_V_2.vmod': (0, 975, 0, , None),
#    'c/c6/Brikwars_sb_0.3.vmod': (0, 2, 0, a, None),
    'c/c7/BtB_ver2-01.vmod': (2, 0, 1, None, None),
#    'c/c7/M3E-Malifaux-v1b.vmod': (3, 0, 0, ev1b, None),
    'c/c7/Marne1914v1.1.vmod': (1, 1, 0, None, None),
#    'c/c7/Pax_Pamir_2nd_edition-1-54-hidden-hands.vmod': (1, 54, 0, hiddenhands, None),
#    'c/c8/MGMGv2.1.1.vmod': (2, 0, 0, b, None),
    'c/c8/Officer_Class_beta_1.1.vmod': (1, 1, 0, None, None),
    'c/c8/TheOtherSide1.0.vmod': (1, 0, 0, None, None),
#    'c/c8/UKC_v1.21_FOW.vmod': (1, 21, 0, FOW, None),
    'c/ca/Monsterpocalypse_1.01.vmod': (1, 1, 0, None, None),
    'c/ca/Our_Place_in_the_Sun-2.3c.vmod': (2, 3, 0, 'c', None),
#    'c/cb/Cards_against_humanity_custom.vmod': (1, 0, 0, Custom, None),
    'c/cb/The_Late_Unpleasantness_IITAS.vmod': (2, 0, 0, None, None),
    'c/cb/WOTNv0.6b.vmod': (0, 6, 0, 'b', None),
    'c/cd/22pommes.vmod': (1, 0, 0, None, None),
    'c/ce/Saipan_v092.Vmod': (0, 92, 0, None, None),
    'c/ce/WSS-NBE-3.01.vmod': (3, 0, 1, None, None),
    'd/d1/AtBR_v1a.vmod': (1, 0, 0, 'a', None),
#    'd/d2/Outreach_v1_2.vmod': (3, 2, 0, p7, None),
    'd/d3/Alamo.vmod': (1, 13, 0, None, None),
#    'd/d3/Aw-spi-v1-81A.vmod': (1, 81, 0, AwithAltMapD, None),
#    'd/d3/PW2_v105.vmod': (2, 1, 5, , None),
#    'd/d3/UKC_v2.1_FOW.vmod': (2, 1, 0, FOW, None),
    'd/d4/SP_II_v12.vmod': (1, 2, 0, None, None),
    'd/d5/FitE_SE_Urals_0.6.2.0.vmod': (0, 6, 2, '0', None),
#    'd/d5/FortressBerlin_5.vmod': (3, 0, 0, , None),
#    'd/d5/Rommel-Honour_J1.vmod': (1, 0, 0, , None),
    'd/d5/StrikeForceOne.vmod': (1, 0, 0, None, None),
    'd/d6/Europe_Engulfed_v3.1_Release.vmod': (3, 1, 0, None, None),
#    'd/d6/Hands-in-the-sea-V_1-0Basic.vmod': (1, 0, 0, PBM, None),
    'd/d6/Saipan_v103.Vmod': (1, 3, 0, None, None),
    'd/d6/Struggle_for_Europe_v2.2N.vmod': (2, 2, 0, None, None),
    'd/d6/WOTNv0.5b.vmod': (0, 5, 0, 'b', None),
    'd/d8/Labyrinth_v5.vmod': (5, 0, 0, None, None),
    'd/d9/Labyrinth_v5-1.vmod': (5, 1, 0, None, None),
#    'd/d9/M3E-Malifaux_MoM-v4b.vmod': (0, 0, 0, v4b, None),
    'd/d9/Operation_Theseus.vmod': (2, 0, 0, None, None),
    'd/da/Perditions_Mouth_PnP_1.1.vmod': (1, 1, 0, None, None),
    'd/dc/RmR.vmod': (1, 1, 0, None, None),
    'd/de/ArmadaModule_-_4.8.0_369.vmod': (4, 8, 0, None, None),
    'd/de/HttR_v1.50.vmod': (1, 50, 0, None, None),
    'd/de/TLoZEpicDuels.vmod': (1, 5, 0, None, None),
    'd/df/Nemesis_v2_3b.vmod': (2, 3, 0, 'b', None),
#    'd/df/NWTaiwan1_1_Revised.vmod': (1, 1, 0, Revised, None),
#    'd/df/Washington%27sWar_%28DE%29_v1-2.vmod': (0, 0, 0, 1.2, None),
    'e/e0/Tricorne.1.33.vmod': (1, 3, 3, None, None),
    'e/e0/Europe_Engulfed_v3.0_Release.vmod': (3, 0, 0, None, None),
    'e/e1/Ambush.vmod': (1, 0, 0, None, None),
    'e/e2/Submarine.vmod': (0, 96, 0, None, None),
    'e/e4/PlanOrange.vmod': (1, 0, 0, None, None),
    'e/e4/Vjw.vmod': (1, 0, 0, None, None),
#    'e/e5/CivilWar17fhb04.vmod': (1, 7, 0, , None),
    'e/e5/Morituri_te_Salutamusv11.vmod': (1, 1, 0, None, None),
    'e/e5/SanGuoShaVassalv1_0.vmod': (1, 0, 0, None, None),
    'e/e5/TurningPoint-1-0.vmod': (1, 0, 0, None, None),
    'e/e6/DamnedDieHard010.vmod': (0, 10, 0, None, None),
    'e/e7/PanzerArmeeAfrika-001d.vmod': (1, 0, 0, 'd', None),
#    'e/e7/Twilight-Struggle-Deluxe-3.0.10a-Spanish.vmod': (3, 0, 10, a, None),
#    'e/e8/M3E-Malifaux_Burns-v3a.vmod': (3, 0, 0, eMalifauxBurnsV3a, None),
    'e/e9/VLOS05.vmod': (0, 5, 0, None, None),
#    'e/ea/ATZ2-0.vmod': (1, 0, 3, 1, None),
#    'e/ea/M3E-Malifaux-v1j.vmod': (3, 0, 0, ev1j, None),
    'e/eb/NFL-Strategy-1-6.vmod': (1, 6, 0, None, None),
    'e/eb/The_Dark_Valley_G02.vmod': (2, 0, 0, None, None),
    'e/eb/WV-1.0.vmod': (1, 0, 0, None, None),
    'e/ed/CosmicE_ncounter_%282008%29_-_1.1.1.vmod': (1, 1, 1, None, None),
    'e/ed/Vino.vmod': (1, 0, 0, None, None),
    'e/ee/Rswe.vmod': (1, 0, 0, None, None),
    'e/ee/WTP.vmod': (2, 1, 0, None, None),
    'e/ef/MFDv10b03.vmod': (1, 0, 0, 'b3', None),
#    'f/f0/Ardennes_Offensive.vmod': (0, 75, 0, Postrelease, None),
    'f/f0/All_Bridges_Burning_1.02.vmod': (1, 0, 2, None, None),
    'f/f1/Speedcircuit.vmod': (1, 0, 0, None, None),
#    'f/f1/SPQR_Deluxe_v2.9alt.vmod': (2, 9, 0, alt, None),
#    'f/f2/Combat_Commander_Europe-Spanish.vmod': (2, 1, 0, SP, None),
    'f/f5/Vinci.vmod': (0, 1, 0, None, None),
    'f/f6/Dusthalo.vmod': (0, 2, 0, None, None),
#    'f/f6/TLD-v0.8b082c-07-17-21.vmod': (0, 8, 0, b082b, None),
    'f/f7/DigDownDwarf-v1-1.vmod': (1, 1, 0, None, None),
    'f/f7/Napoleons_Triumph_v0.95.vmod': (0, 95, 0, None, None),
#    'f/f9/CivilWar17fhb02.vmod': (1, 7, 0, , None),
#    'f/f9/NoRetreat.1.4-Spanish.vmod': (1, 4, 0, Spanish, None),
    'f/f9/Operation_Theseus_updated.vmod': (2, 1, 0, None, None),
    'f/f9/PanzerExp1_1-3-1.vmdx': (1, 3, 1, None, None),
    'f/fa/ApocalypseOfSteel.vmod': (1, 0, 0, None, None),
    'f/fa/RaceForTunis.vmod': (1, 0, 0, None, None),
    'f/fb/Londons_Burning.vmod': (0, 99, 0, None, None),
#    'f/fa/M3E-Malifaux_Burns-v3b.vmod': (3, 0, 0, eMalifauxBurnsV3b, None),
    'f/fa/Spirit_island_vassal_1_702.vmod': (1, 7, 2, None, None),
#    'f/fb/M3E-Malifaux-v1e.vmod': (3, 0, 0, ev1e, None),
    'f/fb/VIPv33p01.vmod': (3, 3, 0, 'p01', None),
    'f/fd/Batalles_espacials.vmod': (1, 0, 0, None, None),
    'f/fd/BattlesOfBullRun.vmod': (0, 9 ,0, None, None),
    'f/fe/Eg-kursk-v10_.vmod': (1, 0, 0, None, None),
    'f/fe/F%C3%A9odalit%C3%A9.vmod': (1, 0, 0, None, None),
    'f/fe/Montelimar_v090.Vmod': (0, 90, 0, None, None),
#    'f/ff/M3E-Malifaux-v1h.vmod': (3, 0, 0, ev1h, None),
#    'f/ff/MGMGv2.1.vmod': (2, 0, 0, b, None),
    'f/ff/TheOtherSide2.2_BTOS.vmod': (2, 2, 0, None, None),
}


def run():
    ipath = 'data/file_meta.json'
    opath = 'data/file_meta_fixed.json'

    with open(ipath, 'r') as f:
        meta = json.load(f)

    for url, ver in version_fixups.items():
        url = 'https://obj.vassalengine.org/images/' + url
        meta[url]['version_parsed'] = ver

    with open(opath, 'w') as f:
        json.dump(meta, f, indent=2)


if __name__ == '__main__':
    run()
