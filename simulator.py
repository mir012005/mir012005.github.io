import pandas as pd
import math
import random as rd
import copy
import requests
import io               
from datetime import datetime
# On récupère d'abord les données concernant les clubs participant à la ligue des champions, à la veille du début de la compétition.
from pathlib import Path

base_dir = Path(__file__).parent
elo_rating = base_dir / "Elo_rating_pré_ldc.csv"
elo = pd.read_csv(elo_rating)

clubs_en_ldc = sorted([
    "Paris SG",           # Paris Saint‑Germain
    "Real Madrid",        # Real Madrid
    "Man City",           # Manchester City
    "Bayern",            # Bayern München
    "Liverpool",         # Liverpool
    "Inter",             # Inter Milan
    "Chelsea",           # Chelsea
    "Dortmund",          # Borussia Dortmund
    "Barcelona",         # Barcelona
    "Arsenal",           # Arsenal
    "Leverkusen",        # Bayer Leverkusen
    "Atletico",          # Atlético Madrid
    "Benfica",           # Benfica
    "Atalanta",          # Atalanta
    "Villarreal",        # Villarreal
    "Juventus",          # Juventus
    "Frankfurt",         # Eintracht Frankfurt
    "Brugge",            # Club Brugge
    "Tottenham",         # Tottenham Hotspur
    "PSV",               # PSV Eindhoven
    "Ajax",              # Ajax
    "Napoli",            # Napoli
    "Sporting",          # Sporting CP
    "Olympiakos",        # Olympiacos
    "Slavia Praha",      # Slavia Praha
    "Bodoe Glimt",       # Bodø/Glimt
    "Marseille",         # Marseille
    "FC Kobenhavn",      # Copenhagen
    "Monaco",            # Monaco
    "Galatasaray",       # Galatasaray
    "St Gillis",         # Union Saint‑Gilloise
    "Karabakh Agdam",    # Qarabağ
    "Bilbao",            # Athletic Club
    "Newcastle",         # Newcastle United
    "Paphos",            # Pafos
    "Kairat"             # Kairat Almaty
])

def get_clubs_list():
    return clubs_en_ldc

elo_ldc = elo[elo["Club"].isin(clubs_en_ldc)]

def elo_of_static(club):
    club_data = elo_ldc.loc[elo_ldc["Club"] == club, "Elo"]
    if len(club_data) == 0:
        print(f"Club non trouvé : {club}")
        print(f"Clubs disponibles : {list(elo_ldc['Club'].unique())}")
        return None  # ou une valeur par défaut
    return club_data.values[0]

# =============================================================================
# GESTION DES ELO DYNAMIQUES
# =============================================================================
# =============================================================================
# GESTION DES ELO DYNAMIQUES (SIMPLIFIÉE)
# =============================================================================

# Dates ajustées (veille des matchs) pour savoir si on tape dans l'historique ou le live
calendrier_ldc = {
    1: "2025-09-15",
    2: "2025-09-29",
    3: "2025-10-20",
    4: "2025-11-03",
    5: "2025-11-24",
    6: "2025-12-08",
    7: "2026-01-19",
    8: "2026-01-27"
}

CACHE_ELO = {}
CURRENT_ELO_DICT = {} 

# On initialise CURRENT_ELO_DICT avec les valeurs statiques (CSV) au démarrage
# IMPORTANT : Renommez votre ancienne fonction 'elo_of' en 'elo_of_static'
for c in clubs_en_ldc:
    CURRENT_ELO_DICT[c] = elo_of_static(c) 

def fetch_elo_from_api(date_str=None):
    """
    Récupère les ELO depuis api.clubelo.com.
    Comme les noms sont identiques, on fait une correspondance directe.
    """
    if date_str:
        url = f"http://api.clubelo.com/{date_str}"
        print(f"📡 Récupération ELO Historique ({date_str})...")
    else:
        today = datetime.today().strftime('%Y-%m-%d')
        url = f"http://api.clubelo.com/{today}"
        print(f"📡 Récupération ELO LIVE ({today})...")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        # Lecture CSV
        df = pd.read_csv(io.StringIO(response.text))
        df = df[['Club', 'Elo']]
        
        # Dictionnaire API : { "Real Madrid": 1950.5, ... }
        raw_elos = dict(zip(df.Club.astype(str), df.Elo))
        
        mapped_elos = {}
        
        # Correspondance directe
        for my_club in clubs_en_ldc:
            if my_club in raw_elos:
                mapped_elos[my_club] = raw_elos[my_club]
            else:
                # Sécurité si jamais une orthographe diffère légèrement
                print(f"⚠️ Attention : '{my_club}' non trouvé dans l'API ClubElo ce jour-là.")
                # On garde l'ancien ELO (statique) en secours
                mapped_elos[my_club] = elo_of_static(my_club)

        return mapped_elos

    except Exception as e:
        print(f"❌ Erreur API ELO: {e}")
        return None

def get_elo_context(journee_depart):
    """
    Gère le cache et le choix entre Live (Futur) et Historique (Passé).
    Logique : Si on simule depuis J5 (5 journées jouées), on veut les ELOs
    à la veille de la J6. Donc on cherche la date de J(depart + 1).
    """
    if journee_depart in CACHE_ELO:
        return CACHE_ELO[journee_depart]

    # CORRECTION ICI : On cherche la date de la PROCHAINE journée
    date_cible_str = calendrier_ldc.get(journee_depart + 1)

    if date_cible_str:
        target_date = datetime.strptime(date_cible_str, "%Y-%m-%d")
        today = datetime.now()
        
        # Si la date cible (J6) est dans le futur par rapport à aujourd'hui,
        # cela signifie qu'on est en avance sur le calendrier réel -> On prend le Live.
        # Sinon, si la date est passée, on prend l'historique de cette date précise.
        if target_date > today:
             elos = fetch_elo_from_api(None) # Futur -> Live
        else:
             elos = fetch_elo_from_api(date_cible_str) # Passé -> Historique
    else:
        # Si journee_depart + 1 n'existe pas (ex: J9) ou si J0, cas spéciaux
        if journee_depart == 8: 
            # Fin de saison, on prend le live pour voir l'état actuel
            elos = fetch_elo_from_api(None)
        elif journee_depart == 0:
            # Début de saison, on garde le statique du CSV (ne rien faire renvoie None)
            return None 
        else:
            elos = fetch_elo_from_api(None)

    if elos:
        CACHE_ELO[journee_depart] = elos
        return elos
    return None

def elo_of_dynamic(club):
    """ Nouvelle fonction à utiliser pour les calculs """
    return CURRENT_ELO_DICT.get(club, 1500)

def win_expectation(club1, club2):
    """ Version modifiée qui utilise l'ELO dynamique """
    e1 = elo_of_dynamic(club1)
    e2 = elo_of_dynamic(club2)
    return 1/(1+10**((e2-e1-100)/400))

def update_simulation_context(journee_depart):
    """
    FONCTION CRITIQUE : Met à jour les ELOs ET recalcule les probas de Poisson.
    À appeler au début de get_web_simulation.
    """
    global CURRENT_ELO_DICT, probas_par_matchs
    
    # Si on part de J0, on reste sur les données statiques du CSV (pré-saison)
    if journee_depart == 0:
        return

    nouveaux_elos = get_elo_context(journee_depart)
    
    if nouveaux_elos:
        CURRENT_ELO_DICT = nouveaux_elos
        
        # On recalcule TOUTES les probabilités de match avec les nouveaux niveaux
        # dico_de_proba appelle win_expectation, qui appelle maintenant elo_of_dynamic
        probas_par_matchs = dico_de_proba() 
        # print(f"✅ Context updated for J{journee_depart}")
    else:
        print("⚠️ Pas de mise à jour ELO (conservation des valeurs précédentes)")

"""
def win_expectation(club1,club2):
    e1 = elo_of(club1) ; e2 = elo_of(club2)
    assert(type(e1) != str and type(e2) != str)
    return 1/(1+10**((e2-e1-100)/400))
"""

def coeff_poisson(club1,club2,s):
    # retourne le coeff de la loi de poisson donnant le nb de buts marqués par club1 si s='H' - ou club2 si s='A' - 
    # club1 jouant à domicile
    assert(s == 'H' or s == 'A')
    w = win_expectation(club1,club2)
    if s == 'H':
        if w <= 0.9:
            return -5.42301*(w**4) + 15.49728*(w**3) - 12.6499*(w**2) + 5.36198*w + 0.22862
        else:
            return 231098.16153*((w-0.9)**4) - 30953.10199*((w-0.9)**3) + 1347.51495*((w-0.9)**2) - 1.63074*(w-0.9) + 2.54747
    else:
        if w >= 0.1:
            return -1.25010*(w**4) - 1.99984*(w**3) + 6.54946*(w**2) - 5.83979*w + 2.80352
        else:
            return 90173.57949*((w-0.1)**4) + 10064.38612*((w-0.1)**3) + 218.6628*((w-0.1)**2) - 11.06198*(w-0.1) + 2.28291

def proba_par_but(k,club1,club2,s):
    # retourne la proba pour club1 si s='H' - pour club2 si s='A' - de marquer k buts dans le match se jouant chez club1
    param = coeff_poisson(club1,club2,s)
    return (param**k)*math.exp(-param)/math.factorial(k)

# On stocke maintenant ces probas dans un dictionnaire pour éviter de les recalculer à chaque simulation
def dico_de_proba(N=3):  # N représente le nombre de proba par buts que l'on stocke pour chaque match (on commence par N=3 
    # car on est à peu près sûrs que les probas de marquer 0,1 ou 2 buts seront utiles quels que soient le match et l'équipe)
    # retourne un dictionnaire ayant pour clés les matchs possibles et comme valeurs associées deux listes correspondant
    # aux probas pour l'équipe à domicile, et pour celle à l'extérieur
    d = {}
    for club1 in clubs_en_ldc:
        for club2 in clubs_en_ldc:
            if club2 != club1:
                d[(club1,club2)] = [[proba_par_but(k,club1,club2,'H') for k in range(N)]
                                    ,[proba_par_but(k,club1,club2,'A') for k in range(N)]]
    return d
        
probas_par_matchs = dico_de_proba()

def simule_nb_buts(club1,club2,s):
    # retourne un tirage du nb de buts marqués par club1 si s='H' - par club2 si s='A' - le match se jouant chez club1
    assert(s == 'H' or s == 'A')
    if s == 'H':
        b = 0
    else:
        b = 1
    probas = probas_par_matchs[(club1,club2)][b]
    u = rd.random()
    k = 0 ; t = probas[0]
    while t < u:
        k += 1
        if k < len(probas):
            t += probas[k]
        else:
            p = proba_par_but(k,club1,club2,s)
            t += p
            probas = probas + [p]
            probas_par_matchs[(club1,club2)][b] = probas
            # On ajoute la valeur au dictionnaire si on en a eu besoin
    return k

def retourne_score(club1,club2):
    # retourne une simulation du score du match entre club1 et club2, club1 jouant à domicile
    return (simule_nb_buts(club1,club2,'H'),simule_nb_buts(club1,club2,'A'))

def score_moyen(club1,club2,N=1000):
    # retourne le score moyen sur N simulations d'un macth entre club1 et club2, le match se jouant chez club1
    total = (0,0)
    for _ in range(N):
        score = retourne_score(club1,club2)
        total = (total[0]+score[0],total[1]+score[1])
    return (round(total[0]/N,2),round(total[1]/N,2))

# La boucle suivante retourne des scores moyens et permet en même temps de remplir le dictionnaire probas_par_match de probas fréquemment utiles

# Calendrier complet de la phase de ligue UEFA Champions League 2025/26
calendrier = {
    "Journée 1": [
        ("Bilbao", "Arsenal"),
        ("PSV", "St Gillis"),
        ("Juventus", "Dortmund"),
        ("Real Madrid", "Marseille"),
        ("Benfica", "Karabakh Agdam"),
        ("Tottenham", "Villarreal"),
        ("Olympiakos", "Paphos"),
        ("Slavia Praha", "Bodoe Glimt"),
        ("Ajax", "Inter"),
        ("Bayern", "Chelsea"),
        ("Liverpool", "Atletico"),
        ("Paris SG", "Atalanta"),
        ("Brugge", "Monaco"),
        ("FC Kobenhavn", "Leverkusen"),
        ("Frankfurt", "Galatasaray"),
        ("Man City", "Napoli"),
        ("Newcastle", "Barcelona"),
        ("Sporting", "Kairat"),
    ],
    "Journée 2": [
        ("Atalanta", "Brugge"),
        ("Kairat", "Real Madrid"),
        ("Atletico", "Frankfurt"),
        ("Chelsea", "Benfica"),
        ("Inter", "Slavia Praha"),
        ("Bodoe Glimt", "Tottenham"),
        ("Galatasaray", "Liverpool"),
        ("Marseille", "Ajax"),
        ("Paphos", "Bayern"),
        ("Karabakh Agdam", "FC Kobenhavn"),
        ("St Gillis", "Newcastle"),
        ("Arsenal", "Olympiakos"),
        ("Monaco", "Man City"),
        ("Leverkusen", "PSV"),
        ("Dortmund", "Bilbao"),
        ("Barcelona", "Paris SG"),
        ("Napoli", "Sporting"),
        ("Villarreal", "Juventus"),
    ],
    "Journée 3": [
        ("Barcelona", "Olympiakos"),
        ("Kairat", "Paphos"),
        ("Arsenal", "Atletico"),
        ("Leverkusen", "Paris SG"),
        ("FC Kobenhavn", "Dortmund"),
        ("Newcastle", "Benfica"),
        ("PSV", "Napoli"),
        ("St Gillis", "Inter"),
        ("Villarreal", "Man City"),
        ("Bilbao", "Karabakh Agdam"),
        ("Galatasaray", "Bodoe Glimt"),
        ("Monaco", "Tottenham"),
        ("Atalanta", "Slavia Praha"),
        ("Chelsea", "Ajax"),
        ("Frankfurt", "Liverpool"),
        ("Bayern", "Brugge"),
        ("Real Madrid", "Juventus"),
        ("Sporting", "Marseille"),
    ],
    "Journée 4": [
        ("Slavia Praha", "Arsenal"),
        ("Napoli", "Frankfurt"),
        ("Atletico", "St Gillis"),
        ("Bodoe Glimt", "Monaco"),
        ("Juventus", "Sporting"),
        ("Liverpool", "Real Madrid"),
        ("Olympiakos", "PSV"),
        ("Paris SG", "Bayern"),
        ("Tottenham", "FC Kobenhavn"),
        ("Paphos", "Villarreal"),
        ("Karabakh Agdam", "Chelsea"),
        ("Ajax", "Galatasaray"),
        ("Brugge", "Barcelona"),
        ("Inter", "Kairat"),
        ("Man City", "Dortmund"),
        ("Newcastle", "Bilbao"),
        ("Marseille", "Atalanta"),
        ("Benfica", "Leverkusen"),
    ],
    "Journée 5": [
        ("Ajax", "Benfica"),
        ("Galatasaray", "St Gillis"),
        ("Dortmund", "Villarreal"),
        ("Chelsea", "Barcelona"),
        ("Bodoe Glimt", "Juventus"),
        ("Man City", "Leverkusen"),
        ("Marseille", "Newcastle"),
        ("Slavia Praha", "Bilbao"),
        ("Napoli", "Karabakh Agdam"),
        ("FC Kobenhavn", "Kairat"),
        ("Paphos", "Monaco"),
        ("Arsenal", "Bayern"),
        ("Atletico", "Inter"),
        ("Frankfurt", "Atalanta"),
        ("Liverpool", "PSV"),
        ("Olympiakos", "Real Madrid"),
        ("Paris SG", "Tottenham"),
        ("Sporting", "Brugge"),
    ],
    "Journée 6": [
        ("Kairat", "Olympiakos"),
        ("Bayern", "Sporting"),
        ("Monaco", "Galatasaray"),
        ("Atalanta", "Chelsea"),
        ("Barcelona", "Frankfurt"),
        ("Inter", "Liverpool"),
        ("PSV", "Atletico"),
        ("St Gillis", "Marseille"),
        ("Tottenham", "Slavia Praha"),
        ("Karabakh Agdam", "Ajax"),
        ("Villarreal", "FC Kobenhavn"),
        ("Bilbao", "Paris SG"),
        ("Leverkusen", "Newcastle"),
        ("Dortmund", "Bodoe Glimt"),
        ("Brugge", "Arsenal"),
        ("Juventus", "Paphos"),
        ("Real Madrid", "Man City"),
        ("Benfica", "Napoli"),
    ],
    "Journée 7": [
        ("Kairat", "Brugge"),
        ("Bodoe Glimt", "Man City"),
        ("FC Kobenhavn", "Napoli"),
        ("Inter", "Arsenal"),
        ("Olympiakos", "Leverkusen"),
        ("Real Madrid", "Monaco"),
        ("Sporting", "Paris SG"),
        ("Tottenham", "Dortmund"),
        ("Villarreal", "Ajax"),
        ("Galatasaray", "Atletico"),
        ("Karabakh Agdam", "Frankfurt"),
        ("Atalanta", "Bilbao"),
        ("Chelsea", "Paphos"),
        ("Bayern", "St Gillis"),
        ("Juventus", "Benfica"),
        ("Newcastle", "PSV"),
        ("Marseille", "Liverpool"),
        ("Slavia Praha", "Barcelona"),
    ],
    "Journée 8": [
        ("Ajax", "Olympiakos"),
        ("Arsenal", "Kairat"),
        ("Monaco", "Juventus"),
        ("Bilbao", "Sporting"),
        ("Atletico", "Bodoe Glimt"),
        ("Leverkusen", "Villarreal"),
        ("Dortmund", "Inter"),
        ("Brugge", "Marseille"),
        ("Frankfurt", "Tottenham"),
        ("Barcelona", "FC Kobenhavn"),
        ("Liverpool", "Karabakh Agdam"),
        ("Man City", "Galatasaray"),
        ("Paphos", "Slavia Praha"),
        ("Paris SG", "Newcastle"),
        ("PSV", "Bayern"),
        ("St Gillis", "Atalanta"),
        ("Benfica", "Real Madrid"),
        ("Napoli", "Chelsea"),
    ],
}

# Petites vérifications que le calendrier est ok :
def match(j,club):
    # retourne le match dans lequel est impliqué club lors de la journée j, et s'il joue à domicile ou à l'extérieur
    s = "Journée " + str(j)
    L = calendrier[s]
    for (club1,club2) in L:
        if club == club1:
            return (club1,club2) , 'H'
        elif club == club2:
            return (club1,club2) , 'A'
    print(club , "n'existe pas sur la journée", j)

for club in clubs_en_ldc:
    eq = 0
    for j in range(1,9):
        if match(j,club)[1] == 'H':
            eq += 1
        else:
            eq -= 1
    
    if eq != 0:
        print(club, "home-away difference:", eq)   
    #assert(eq == 0)

def simuler_match(club1,club2,points,diff_buts,buts,buts_exterieur,nb_victoires,nb_victoires_ext,resultats):
        (i,j) = retourne_score(club1,club2)
        diff_buts[club1] += i-j
        diff_buts[club2] += j-i
        buts[club1] += i
        buts[club2] += j
        buts_exterieur[club2] += j
        if i > j:
            points[club1] += 3
            nb_victoires[club1] += 1
        elif i < j:
            points[club2] += 3
            nb_victoires[club2] += 1
            nb_victoires_ext[club2] += 1
        else:
            points[club1] += 1 ; points[club2] += 1
        resultats[(club1,club2)] = (i,j)

def dico_de_données(classement,points,diff_buts,buts,buts_ext,nb_victoires,nb_victoires_ext):
    return {"classement" : classement , "points" : points , "diff_buts" : diff_buts , "buts" : buts ,
            "buts_ext" : buts_ext , "nb_victoires" : nb_victoires , "nb_victoires_ext" : nb_victoires_ext}

def simulation_ligue(données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None, "buts_ext" : None,
                              "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1, fin=8, demi=False):
    # Réalise une simulation de la phase de ligue, par défaut à partir de la Journée 1, mais on peut aussi commencer
    # à partir d'un certain classement et d'une certaine journée
    if données["classement"] is None:
        classement = clubs_en_ldc
    else:
        classement = copy.deepcopy(données["classement"])

    if données["points"] is None:
        points = dict([(club, 0) for club in clubs_en_ldc])
    else:
        points = copy.deepcopy(données["points"])

    if données["diff_buts"] is None:
        diff_buts = dict([(club, 0) for club in clubs_en_ldc])
    else:
        diff_buts = copy.deepcopy(données["diff_buts"])

    if données["buts"] is None:
        buts = dict([(club, 0) for club in clubs_en_ldc])
    else:
        buts = copy.deepcopy(données["buts"])

    if données["buts_ext"] is None:
        buts_exterieur = dict([(club, 0) for club in clubs_en_ldc])
    else:
        buts_exterieur = copy.deepcopy(données["buts_ext"])

    if données["nb_victoires"] is None:
        nb_victoires = dict([(club, 0) for club in clubs_en_ldc])
    else:
        nb_victoires = copy.deepcopy(données["nb_victoires"])

    if données["nb_victoires_ext"] is None:
        nb_victoires_ext = dict([(club, 0) for club in clubs_en_ldc])
    else:
        nb_victoires_ext = copy.deepcopy(données["nb_victoires_ext"])
    
    resultats = {}
    for j in range(debut,fin+1):
        matchs = calendrier["Journée " + str(j)]
        if j == debut and demi:
            ind = len(matchs)//2
        else:
            ind = 0
        for i in range(ind,len(matchs)):
            simuler_match(matchs[i][0],matchs[i][1],points,diff_buts,buts,buts_exterieur,nb_victoires,nb_victoires_ext,resultats)
    
    nclassement = sorted(classement, key = lambda x: (points[x],diff_buts[x],buts[x],buts_exterieur[x],nb_victoires[x],nb_victoires_ext[x]),
                         reverse=True)

    d = dico_de_données(nclassement, points , diff_buts , buts , buts_exterieur , nb_victoires , nb_victoires_ext)
    return d | {"résultats" : resultats}

def générer_classement(données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None, "buts_ext" : None,
                              "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1, fin=8):
    # retourne le classement sous forme de DataFrame
    
    ndonnées = simulation_ligue(données=données,debut=debut,fin=fin)
    
    if données["classement"] is None:
        classement = clubs_en_ldc
    else:
        classement = données["classement"]

    df = pd.DataFrame({
    "Team": classement,
    "Points": ndonnées["points"].values(),
    "Goal average": ndonnées["diff_buts"].values(),
    "Goals": ndonnées["buts"].values(),
    "Away goals": ndonnées["buts_ext"].values(),
    "Wins" : ndonnées["nb_victoires"].values(),
    "Away wins" : ndonnées["nb_victoires_ext"].values()
    })

    df_classement = df.sort_values(
    by=["Points", "Goal average", "Goals", "Away goals", "Wins", "Away wins"],
    ascending=[False, False, False, False, False, False]
    ).reset_index(drop=True)

    df_classement = df_classement.style.hide(axis="index")

    return df_classement

# On essaie maintenant de déterminer les probabilités pour chaque équipe de finir à différentes positions:
def distribution_position_par_club(N=10000, données={"classement" : None, "points" : None, "diff_buts" : None,
                "buts" : None, "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1, fin=8, demi=False):
    # retourne pour chaque équipe ses probas de finir à chaque position (distribution de probas), sur la base de N simulations
    d = {
        club: {pos: 0 for pos in range(1, len(clubs_en_ldc)+1)}
        for club in clubs_en_ldc
    }   
    for _ in range(N):
        nclassement = simulation_ligue(données,debut,fin,demi=demi)["classement"]
        for i in range(len(nclassement)):
            d[nclassement[i]][i+1] += 1/N
    """
    for club in d.keys():
        for x in d[club].keys():
            d[club][x] = round(d[club][x],int(math.log10(N)))
    """
    return d

# On peut faire la même chose pour le nombre de points attendus pour chaque club
def distribution_points_par_club(N=10000, données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                        "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1, fin=8, demi=False):
    # retourne pour chaque équipe ses probas d'inscrire chaque nombre de points (distribution de probas), sur la base de N simulations
    distrib = {
        club: {points: 0 for points in range(3*fin+1)}
        for club in clubs_en_ldc
    }   
    for _ in range(N):
        npoints = simulation_ligue(données, debut=debut, fin=fin, demi=demi)["points"]
        for club in npoints.keys():
            distrib[club][npoints[club]] += round(1/N,int(math.log10(N)))
    
    for club in distrib.keys():
        for x in distrib[club].keys():
            distrib[club][x] = round(distrib[club][x],int(math.log10(N)))
    
    return distrib

def proba_top_8(club,distribution_probas):
    distribution = distribution_probas[club]
    s = 0
    for i in range(1,9):
        s += distribution[i]
    return s

def proba_qualification(club,distribution_probas):
    distribution = distribution_probas[club]
    s = 0
    for i in range(25,37):
        s += distribution[i]
    return 1-s

def classement_par_proba_de_qualif(distribution_probas):
    L = [proba_qualification(club,distribution_probas) for club in clubs_en_ldc]
    df = pd.DataFrame({
        "Team" : clubs_en_ldc,
        "Proba de qualif (%)" : [round(100*proba,2) for proba in L]
    })

    ndf = df.sort_values(
    by=["Proba de qualif (%)"],
    ascending=[False]
    ).reset_index(drop=True)

    # Formater les probabilités pour supprimer les zéros inutiles
    ndf["Proba de qualif (%)"] = ndf["Proba de qualif (%)"].apply(lambda x: f"{x:.2f}".rstrip('0').rstrip('.'))

    return ndf.style.hide(axis="index")

#classement_par_proba_de_qualif(distribution_probas_classement)

def classement_par_proba_de_top8(distribution_probas):
    L = [proba_top_8(club,distribution_probas) for club in clubs_en_ldc]
    df = pd.DataFrame({
        "Team" : clubs_en_ldc,
        "Proba de top 8 (%)" : [round(100*proba,2) for proba in L]
    })

    ndf = df.sort_values(
    by=["Proba de top 8 (%)"],
    ascending=[False]
    ).reset_index(drop=True)

    # Formater les probabilités pour supprimer les zéros inutiles
    ndf["Proba de top 8 (%)"] = ndf["Proba de top 8 (%)"].apply(lambda x: f"{x:.2f}".rstrip('0').rstrip('.'))

    return ndf.style.hide(axis="index")

#classement_par_proba_de_top8(distribution_probas_classement)

# On calcule maintenant la distribution de probas concernant le nombre de points nécessaires pour arriver à une certaine position, notamment 8è (top8) et 24è (qualification).
def distribution_par_position(N=10000, données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                    "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1, fin=8, demi=False):
    
    d = {
        pos : {nb_points : 0 for nb_points in range(25)}
        for pos in range(1,len(clubs_en_ldc)+1)
    }
    for _ in range(N):
        ndonnées = simulation_ligue(données,debut,fin,demi=demi)
        nclassement = ndonnées["classement"] ; npoints = ndonnées["points"]
        for i in range(len(nclassement)):
            d[i+1][npoints[nclassement[i]]] += round(1/N,int(math.log10(N)))
    
    for pos in d.keys():
        for x in d[pos].keys():
            d[pos][x] = round(d[pos][x],int(math.log10(N)))

    return d

def ajouter_matchs_donnés(données,matchs):
    # matchs contient une liste de matchs sous la forme (club1,club2,score), la fonction met à jour les arguments
    
    npoints = copy.deepcopy(données["points"])
    ndiff_buts = copy.deepcopy(données["diff_buts"])
    nbuts = copy.deepcopy(données["buts"])
    nbuts_ext = copy.deepcopy(données["buts_ext"])
    nnb_v = copy.deepcopy(données["nb_victoires"])
    nnb_v_ext = copy.deepcopy(données["nb_victoires_ext"])

    for match in matchs:
        assert(len(match)==3 and len(match[-1])==2)
        (club1,club2) = (match[0],match[1])
        (i,j) = (match[2][0],match[2][1])
        
        ndiff_buts[club1] += i-j
        ndiff_buts[club2] += j-i
        nbuts[club1] += i
        nbuts[club2] += j
        nbuts_ext[club2] += j
        if i > j:
            npoints[club1] += 3
            nnb_v[club1] += 1
        elif i < j:
            npoints[club2] += 3
            nnb_v[club2] += 1
            nnb_v_ext[club2] += 1
        else:
            npoints[club1] += 1 ; npoints[club2] += 1
    
    nclassement = sorted(données["classement"], key = lambda x: (-npoints[x],-ndiff_buts[x],-nbuts[x],-nbuts_ext[x],-nnb_v[x],-nnb_v_ext[x]))

    return dico_de_données(nclassement , npoints, ndiff_buts, nbuts, nbuts_ext, nnb_v, nnb_v_ext)

# Détermination de l'importance d'un match pour une équipe
# Idée : simuler jusqu'à la journée contenant le match dont on cherche l'importance, simuler tous les matchs de la journée concernée sauf celui dont on cherche l'importance et voir la différence dans les chances de qualif (ou top 8 selon la définition) pour l'équipe selon qu'elle a perdu ou gagné le match (avec le même score, par exemple 1-0)
def simuler_defaite(club,journee, données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                    "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1):
    # simule une phase de ligue où le club en argument a perdu en journée j, retourne la position du club 
    assert(journee>=debut)
    # Simulation jusqu'à la journée où a lieu le match étudié
    ndonnées = simulation_ligue(données,debut,fin=journee-1)

    # Simulation de la journée étudiée en garantissant une défaite de club
    for (club1,club2) in calendrier["Journée " + str(journee)]:
        if club1==club:
            (i,j) = retourne_score(club1,club2)
            while not(i<j):
                (i,j) = retourne_score(club1,club2)
            ndonnées["points"][club2] += 3 ; ndonnées["diff_buts"][club2] += j-i ; ndonnées["buts"][club2] += j ; 
            ndonnées["buts_ext"][club2] += j ; ndonnées["nb_victoires"][club2] += 1 ; ndonnées["nb_victoires_ext"][club2] += 1
            ndonnées["diff_buts"][club1] += i-j ; ndonnées["buts"][club1] += i
        elif club2==club:
            (i,j) = retourne_score(club1,club2)
            while not(i>j):
                (i,j) = retourne_score(club1,club2)
            ndonnées["points"][club1] += 3 ; ndonnées["diff_buts"][club1] += i-j ; ndonnées["buts"][club1] += i
            ndonnées["nb_victoires"][club1] += 1
            ndonnées["diff_buts"][club2] += j-i ; ndonnées["buts"][club2] += j ; ndonnées["buts_ext"][club2] += j
        else:
            simuler_match(club1,club2,ndonnées["points"],ndonnées["diff_buts"],ndonnées["buts"],
                          ndonnées["buts_ext"],ndonnées["nb_victoires"],ndonnées["nb_victoires_ext"],ndonnées["résultats"])
    ndonnées["classement"] = sorted(ndonnées["classement"], key = lambda x: (ndonnées["points"][x],ndonnées["diff_buts"][x],
                         ndonnées["buts"][x],ndonnées["buts_ext"][x],ndonnées["nb_victoires"][x],ndonnées["nb_victoires_ext"][x]),
                         reverse=True)
    
    # Simulation jusqu'à la fin de la phase de ligue
    return simulation_ligue(ndonnées,debut=journee+1)

def simuler_victoire(club,journee, données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                    "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1):
    # simule une phase de ligue où le club en argument a gagné en journée j, retourne la position du club 
    assert(journee>=debut)
    # Simulation jusqu'à la journée où a lieu le match étudié
    ndonnées = simulation_ligue(données,debut,fin=journee-1)

    # Simulation de la journée étudiée en garantissant une victoire de club
    for (club1,club2) in calendrier["Journée " + str(journee)]:
        if club1==club:
            (i,j) = retourne_score(club1,club2)
            while not(i>j):
                (i,j) = retourne_score(club1,club2)
            ndonnées["diff_buts"][club2] += j-i ; ndonnées["buts"][club2] += j ; ndonnées["buts_ext"][club2] += j
            ndonnées["points"][club1] += 3 ; ndonnées["diff_buts"][club1] += i-j ; ndonnées["buts"][club1] += i
            ndonnées["nb_victoires"][club1] += 1 
        elif club2==club:
            (i,j) = retourne_score(club1,club2)
            while not(i<j):
                (i,j) = retourne_score(club1,club2)
            ndonnées["diff_buts"][club1] += i-j ; ndonnées["buts"][club1] += i
            ndonnées["points"][club2] += 3 ; ndonnées["diff_buts"][club2] += j-i ; ndonnées["buts"][club2] += j
            ndonnées["buts_ext"][club2] += j ; ndonnées["nb_victoires"][club2] += 1 ; ndonnées["nb_victoires_ext"][club2] += 1
        else:
            simuler_match(club1,club2,ndonnées["points"],ndonnées["diff_buts"],ndonnées["buts"],
                          ndonnées["buts_ext"],ndonnées["nb_victoires"],ndonnées["nb_victoires_ext"],ndonnées["résultats"])
    ndonnées["classement"] = sorted(ndonnées["classement"], key = lambda x: (ndonnées["points"][x],ndonnées["diff_buts"][x],
                         ndonnées["buts"][x],ndonnées["buts_ext"][x],ndonnées["nb_victoires"][x],ndonnées["nb_victoires_ext"][x]),
                         reverse=True)
    
    # Simulation jusqu'à la fin de la phase de ligue
    return simulation_ligue(ndonnées,debut=journee+1)

def simuler_match_nul(club,journee, données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                    "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1):
    # simule une phase de ligue où le club en argument a perdu en journée j, retourne la position du club 
    assert(journee>=debut)
    # Simulation jusqu'à la journée où a lieu le match étudié
    ndonnées = simulation_ligue(données,debut,fin=journee-1)

    # Simulation de la journée étudiée en garantissant une défaite de club
    for (club1,club2) in calendrier["Journée " + str(journee)]:
        if club1==club or club2==club:
            (i,j) = retourne_score(club1,club2)
            while not(i==j):
                (i,j) = retourne_score(club1,club2)
            ndonnées["buts"][club2] += j ;  ndonnées["buts"][club1] += i ; ndonnées["buts_ext"][club2] += j
            ndonnées["points"][club1] += 1 ; ndonnées["points"][club2] += 1
        else:
            simuler_match(club1,club2,ndonnées["points"],ndonnées["diff_buts"],ndonnées["buts"],
                          ndonnées["buts_ext"],ndonnées["nb_victoires"],ndonnées["nb_victoires_ext"],ndonnées["résultats"])
    ndonnées["classement"] = sorted(ndonnées["classement"], key = lambda x: (ndonnées["points"][x],ndonnées["diff_buts"][x],
                         ndonnées["buts"][x],ndonnées["buts_ext"][x],ndonnées["nb_victoires"][x],ndonnées["nb_victoires_ext"][x]),
                         reverse=True)
    
    # Simulation jusqu'à la fin de la phase de ligue
    return simulation_ligue(ndonnées,debut=journee+1)

def distribution_position_par_club_match_fixe(N=10000,club_fixed=None,journee=None,result_fixed=None, données={"classement" : None, "points" : None, "diff_buts" : None,
                "buts" : None, "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1, fin=8, demi=False):
    
    #V: victoire, D: defaite, N: nul

    assert(result_fixed in ['D','V','N',None])

    d = {
        club: {pos: 0 for pos in range(1, len(clubs_en_ldc)+1)}
        for club in clubs_en_ldc
    }   

    if result_fixed == 'D':
    
        for _ in range(N):
            nclassement = simuler_defaite(club_fixed,journee,données=données,debut=debut)["classement"]
            for i in range(len(nclassement)):
                d[nclassement[i]][i+1] += 1/N
    
    elif result_fixed == 'V':
        for _ in range(N):
            nclassement = simuler_victoire(club_fixed,journee,données=données,debut=debut)["classement"]
            for i in range(len(nclassement)):
                d[nclassement[i]][i+1] += 1/N
    else:
        for _ in range(N):
            nclassement = simuler_match_nul(club_fixed,journee,données=données,debut=debut)["classement"]
            for i in range(len(nclassement)):
                d[nclassement[i]][i+1] += 1/N
    """
    for club in d.keys():
        for x in d[club].keys():
            d[club][x] = round(d[club][x],int(math.log10(N)))
    
    """            
    return d


def distribution_points_par_club_match_fixe(N=10000,club_fixed=None,journee=None,result_fixed=None, données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                        "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1, fin=8, demi=False):
    # retourne pour chaque équipe ses probas d'inscrire chaque nombre de points (distribution de probas), sur la base de N simulations

    assert(result_fixed in ['D','V','N',None])

    distrib = {
        club: {points: 0 for points in range(3*fin+1)}
        for club in clubs_en_ldc
    }   

    if result_fixed == 'D':

        for _ in range(N):
            npoints = simuler_defaite(club_fixed,journee,données=données, debut=debut)["points"]
            for club in npoints.keys():
                distrib[club][npoints[club]] += round(1/N,int(math.log10(N)))
    
    if result_fixed == 'V':

        for _ in range(N):
            npoints = simuler_victoire(club_fixed,journee,données=données, debut=debut)["points"]
            for club in npoints.keys():
                distrib[club][npoints[club]] += round(1/N,int(math.log10(N)))

    else:
        for _ in range(N):
            npoints = simuler_match_nul(club_fixed,journee,données=données, debut=debut)["points"]
            for club in npoints.keys():
                distrib[club][npoints[club]] += round(1/N,int(math.log10(N)))
                
    for club in distrib.keys():
        for x in distrib[club].keys():
            distrib[club][x] = round(distrib[club][x],int(math.log10(N)))
    
    return distrib

def classement_club(club,classement):
    x = classement[0] ; i = 1
    while x!=club and i<len(classement):
        x = classement[i]
        i += 1
    assert(x == club)
    return i

def importance(club,journee, données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                    "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1,N=10000):
    # retourne une mesure de l'importance du match en journée j pour club selon à quel point sa proba d'atteindre position 
    # est modifiée selon qu'il gagne, fasse match nul, ou perde (quotient proba si victoire / proba si défaite)
    # retourne aussi l'écart de classement selon qu'il y ait victoire ou défaite
    p1 = [0 for _ in range(len(données["classement"]))] ; p2 = [0 for _ in range(len(données["classement"]))] ; p3 = [0 for _ in range(len(données["classement"]))]
    gain_classement_v = 0 ; gain_classement_nul = 0
    for _ in range(N):
        nclassement_v = simuler_victoire(club,journee,données,debut=debut)["classement"]
        nclassement_nul = simuler_match_nul(club,journee,données,debut=debut)["classement"]
        nclassement_d = simuler_defaite(club,journee,données,debut=debut)["classement"]
        cv = classement_club(club,nclassement_v)
        cnul = classement_club(club,nclassement_nul)
        cd = classement_club(club,nclassement_d)
        for position in range(len(données["classement"])):
            if cv <= position+1:
                p1[position] += 1/N
            if cd <= position+1:
                p2[position] += 1/N
            if cnul <= position+1:
                p3[position] += 1/N
        gain_classement_v += (cnul - cv)/N ; gain_classement_nul += (cd - cnul)/N
    
    return [round(p1[pos],int(math.log10(N))) for pos in range(len(p1))] , [round(p2[pos],int(math.log10(N))) for pos in range(len(p2))] , [round(p3[pos],int(math.log10(N))) for pos in range(len(p3))] , round(gain_classement_v,int(math.log10(N))) , round(gain_classement_nul,int(math.log10(N)))

def différence_importance_par_position(club,journee,données={"classement" : None, "points" : None, "diff_buts" : None,
                "buts" : None, "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1,N=10000):
    p1 , p2 , p3 , diff1, diff2 = importance(club,journee,données,
                                debut=debut,N=N)
    return [round(p1[pos]-p3[pos],int(math.log10(N))) for pos in range(len(p1))] , [round(p3[pos]-p2[pos],int(math.log10(N))) for pos in range(len(p1))]

def importance_qualif_et_top8(club,journee,données={"classement" : None, "points" : None, "diff_buts" : None,
                "buts" : None, "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None},debut=1,N=10000):
    p1 , p2 , p3 , diff1 , diff2 = importance(club,journee,données,
                                debut=debut,N=N)
    return (p1[23],p1[7]),(p2[23],p2[7]),(p3[23],p3[7])

def différence_qualif_et_top8(club,journee,données={"classement" : None, "points" : None, "diff_buts" : None,
                "buts" : None, "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None},debut=1,N=10000):
    p1 , p2 = différence_importance_par_position(club,journee,données,debut=debut,N=N)
    return {"qualif" : (p1[23],p2[23]), "top_8" : (p1[7],p2[7])}

def enjeux(club,journee,données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                    "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None},debut=1,N=1000):
    p1 , p2 , p3 , diff1 , diff2 = importance(club,journee,données,debut=debut,N=N)

    qualif_club = (p1[23]-p3[23],p3[23]-p2[23])
    top8_club = (p1[7]-p3[7],p3[7]-p2[7])
    
    enjeu = qualif_club+top8_club
    
    return (round(enjeu[0],int(math.log10(N))),round(enjeu[1],int(math.log10(N)))) , diff1 , diff2
    
def importance_pour(club,match,journee, données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                    "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None}, debut=1,N=10000):
    # retourne l'importance de match (joué en journée journee) pour club, selon les mêmes critères que la fonction importance
    p1 = [0 for _ in range(len(données["classement"]))] ; p2 = [0 for _ in range(len(données["classement"]))]
    gain_classement = 0
    for _ in range(N):
        nclassement_v = simuler_victoire(match[0],journee,données,debut=debut)["classement"]
        nclassement_d = simuler_defaite(match[0],journee,données,debut=debut)["classement"]
        cv = classement_club(club,nclassement_v)
        cd = classement_club(club,nclassement_d)
        for position in range(len(données["classement"])):
            if cv <= position+1:
                p1[position] += 1/N
            if cd <= position+1:
                p2[position] += 1/N
        gain_classement += (cd - cv)/N
    
    return [round(p1[pos],int(math.log10(N))) for pos in range(len(p1))] , [round(p2[pos],int(math.log10(N))) for pos in range(len(p2))] , round(gain_classement,int(math.log10(N)))

def enjeux_pour(club,match,journee,données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                    "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None},debut=1,N=1000):
    p1 , p2 , diff = importance_pour(club,match,journee,données,debut=debut,N=N)

    qualif_club = p1[23] - p2[23]
    top8_club = p1[7] - p2[7]
    
    enjeu = qualif_club+top8_club
    
    return round(enjeu,int(math.log10(N))) , diff

#version code plus compacte, pour simuler tout une ligue directement et extraite les résultats intéressants
def simulation_pour_enjeux(journee,données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None,
                    "buts_ext" : None, "nb_victoires" : None, "nb_victoires_ext" : None},debut=1,demi=False,N=10000):
    if demi:
        ind = len(calendrier["Journée 7"])//2
    else:
        ind = 0
    enjeux_ = {club : 
                {match :
                  {issue : {
                      "proba_qualif" : 0 ,
                      "proba_top8" : 0 ,
                      "classement" : 0 ,
                      "nb_occurences" : 0}
                    for issue in ["domicile","nul","exterieur"]}
                for match in calendrier["Journée "+str(journee)][ind:] + calendrier["Journée "+str(journee+1)]}
            for club in clubs_en_ldc
          }
    for _ in range(N):
        ndonnées = simulation_ligue(données=données,debut=debut,demi=demi)
        résultats = {match : ndonnées["résultats"][match] for match in calendrier["Journée "+str(journee)][ind:]+calendrier["Journée "+str(journee+1)]}
        classement = ndonnées["classement"]
        for match in résultats.keys():
            (i,j) = résultats[match]
            if i < j:
                issue = "exterieur"
            elif i == j:
                issue = "nul"
            else:
                issue = "domicile"
            for club in clubs_en_ldc:
                enjeux_[club][match][issue]["nb_occurences"] += 1
                c = classement_club(club,classement)
                if c <= 24:
                    enjeux_[club][match][issue]["proba_qualif"] += 1
                if c <= 8:
                    enjeux_[club][match][issue]["proba_top8"] += 1
                enjeux_[club][match][issue]["classement"] += c

    # On normalise correctement      
    for club in clubs_en_ldc:
        for match in enjeux_[club].keys():
            for issue in ["domicile","nul","exterieur"]:
                d = enjeux_[club][match][issue]
                for x in d.keys():
                  if x!="nb_occurences":
                    d[x] = round(d[x]/d["nb_occurences"],int(math.log10(N)))
    
    return enjeux_

# =========================== Affichage Web ==================================================
# =============================================================================
def get_web_seuils(nb_simulations=1000, journee_depart=0):
    """
    Calcule la distribution des points du 8ème (Qualif) et du 24ème (Barrage).
    Permet de voyager dans le temps (J0 à J8).
    """
    # 1. MISE À JOUR DU CONTEXTE
    try:
        j_dep = int(journee_depart)
    except:
        j_dep = 0
    update_simulation_context(j_dep)

    # 1. MAPPING DES DONNÉES HISTORIQUES
    # Assurez-vous que toutes ces variables (données_J1...) existent bien en haut du fichier
    map_historique = {
        0: etat_zero, 
        1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 
        7: données_J7, 8: données_J8
    }
    
    # On récupère les données correspondantes (ou J6 par défaut si erreur)
    etat = map_historique.get(journee_depart, etat_zero)
    
    # La simulation commence le lendemain de la journée de départ
    debut_simu = journee_depart + 1
    
    # On lance la simu pour récupérer les points par position
    distrib_pos = distribution_par_position(
        N=nb_simulations, 
        données=etat, 
        debut=debut_simu, 
        fin=8
    )
    
    # On récupère les stats pour le 8ème (Cut-off Top 8) et le 24ème (Cut-off Barrage)
    # .get(8, {}) évite le crash si la clé n'existe pas
    stats_8 = distrib_pos.get(8, {})
    stats_24 = distrib_pos.get(24, {})
    
    # Nettoyage pour le JSON (on enlève les probas < 0.5% pour alléger le transfert)
    def clean_dict(d):
        return {k: v for k, v in d.items() if v > 0.005}

    return {
        "journee_utilisee": journee_depart,
        "seuil_top8": clean_dict(stats_8),
        "seuil_barrage": clean_dict(stats_24)
    }

def get_web_importance_matchs(nb_simulations=500):
    """
    Identifie les matchs les plus impactants de la prochaine journée.
    Répond à l'exigence (3) du projet.
    Attention : N réduit à 500 car c'est très gourmand en calcul !
    """
    # On utilise la fonction optimisée que vous avez fournie
    enjeux = simulation_pour_enjeux(journee=7, données=données_J6, debut=7, demi=True, N=nb_simulations)
    
    # Calcul de l'impact cumulé (votre logique 'afficher_max_cumulé' adaptée)
    impacts = []
    enjeux_matchs = {}
    
    # On récupère la liste des matchs de la J7
    matchs_J7 = calendrier["Journée 7"]
    
    for match in matchs_J7:
        score_cumule = 0
        for club in enjeux.keys():
            if match in enjeux[club]:
                 # On prend l'enjeu 'qualif' ou 'top8' ou une moyenne des deux
                 # Ici on additionne les probas de changement
                 score_cumule += enjeux[club][match]["domicile"]["proba_qualif"] 
                 # C'est une simplification pour l'exemple, vous pouvez affiner le calcul
        
        impacts.append({
            "match": f"{match[0]} vs {match[1]}",
            "score": round(score_cumule, 2)
        })

    # On trie pour avoir les plus importants en premier
    impacts.sort(key=lambda x: x['score'], reverse=True)
    
    return impacts[:10] # On renvoie le top 10

# =============================================================================
def get_web_simulation(club_cible, nb_simulations=1000, journee_depart=0):
    """
    Fonction optimisée pour le web.
    Accepte maintenant 'journee_depart' (0 à 8) pour choisir les données sources.
    """
    if club_cible not in clubs_en_ldc:
        return {"error": f"Le club '{club_cible}' n'est pas dans la liste."}

    # 1. MAPPING DES DONNÉES (CORRECTION ICI : On ajoute J0, J1, J2...)
    # Cela permet de gérer tout l'historique sans erreur.
    historique_donnees = {
        0: etat_zero,   # J0 = Tout le monde à 0 points
        1: données_J1,
        2: données_J2,
        3: données_J3, 
        4: données_J4, 
        5: données_J5,
        6: données_J6, 
        7: données_J7, 
        8: données_J8
    }

    # Sécurisation : on s'assure que c'est un entier
    try:
        j_dep = int(journee_depart)
    except:
        j_dep = 0

    # je l'ai ajouté (a enlever)
    update_simulation_context(j_dep)

    # On récupère les données demandées. 
    # Si la journée n'existe pas, on prend J6 par défaut pour éviter le crash.
    etat_actuel = historique_donnees.get(j_dep, etat_zero)
    
    # La simulation commence le lendemain de la journée de départ
    debut_simulation = j_dep + 1
    
    # 2. SIMULATION
    # On lance la simulation Monte Carlo avec l'état choisi
    distrib_points = distribution_points_par_club(N=nb_simulations, données=etat_actuel, debut=debut_simulation, fin=8)
    distrib_rank = distribution_position_par_club(N=nb_simulations, données=etat_actuel, debut=debut_simulation, fin=8)

    # 3. EXTRACTION DES RÉSULTATS
    stats_points = distrib_points[club_cible]
    stats_rank = distrib_rank[club_cible]
    
    # Calcul des probas via les fonctions globales
    p_top8 = proba_top_8(club_cible, distrib_rank)
    p_qualif = proba_qualification(club_cible, distrib_rank)
    p_barrage = p_qualif - p_top8
    p_elimine = 1 - p_qualif
    
    pts_moyen = sum(pt * prob for pt, prob in stats_points.items())

    # Nettoyage pour alléger le JSON
    clean_points = {k: v for k, v in stats_points.items() if v > 0.001}
    clean_ranks = {k: v for k, v in stats_rank.items() if v > 0.001}

    return {
        "club": club_cible,
        "day_used": j_dep, # On renvoie l'info pour l'affichage
        "points_moyens": round(pts_moyen, 2),
        "proba_top_8": round(p_top8 * 100, 1),
        "proba_barrage": round(p_barrage * 100, 1),
        "proba_elimine": round(p_elimine * 100, 1),
        "distribution_points": clean_points,
        "distribution_rangs": clean_ranks
    }

def get_match_prediction(home_team, away_team):
    """
    Simule un match spécifique et renvoie le score moyen (prédiction)
    ainsi qu'une simulation de score typique.
    """
    update_simulation_context(8)

    # 1. Vérification des équipes
    if home_team not in clubs_en_ldc or away_team not in clubs_en_ldc:
        return {"error": "Une des équipes n'est pas reconnue."}
    
    if home_team == away_team:
        return {"error": "Une équipe ne peut pas jouer contre elle-même !"}

    # 2. Calcul du score moyen (Espérance mathématique)
    # On utilise votre fonction score_moyen définie plus haut
    avg_score = score_moyen(home_team, away_team, N=2000)
    
    # 3. On calcule aussi les probabilités de victoire (Win/Draw/Loss)
    # On fait 2000 simulations rapides pour avoir des %
    wins_h, draws, wins_a = 0, 0, 0
    for _ in range(2000):
        s = retourne_score(home_team, away_team)
        if s[0] > s[1]: wins_h += 1
        elif s[0] == s[1]: draws += 1
        else: wins_a += 1
        
    total = 2000
    
    return {
        "home_team": home_team,
        "away_team": away_team,
        "score_avg_home": avg_score[0], # Ex: 1.85
        "score_avg_away": avg_score[1], # Ex: 0.92
        "proba_win": round(wins_h / total * 100, 1),
        "proba_draw": round(draws / total * 100, 1),
        "proba_loss": round(wins_a / total * 100, 1)
    }


#from CODE_A_COPIER import données_J1, données_J2, données_J3, données_J4, données_J5, données_J6
# ==============================================================================
données_J1 = {
    'classement': ['Frankfurt', 'Paris SG', 'Brugge', 'Sporting', 'St Gillis', 'Bayern', 'Arsenal', 'Inter', 'Man City', 'Karabakh Agdam', 'Liverpool', 'Barcelona', 'Real Madrid', 'Tottenham', 'Dortmund', 'Juventus', 'Bodoe Glimt', 'Leverkusen', 'FC Kobenhavn', 'Slavia Praha', 'Olympiakos', 'Paphos', 'Atletico', 'Benfica', 'Marseille', 'Newcastle', 'Villarreal', 'Chelsea', 'PSV', 'Ajax', 'Bilbao', 'Napoli', 'Kairat', 'Monaco', 'Galatasaray', 'Atalanta'],
    'points': {'Ajax': 0, 'Arsenal': 3, 'Atalanta': 0, 'Atletico': 0, 'Barcelona': 3, 'Bayern': 3, 'Benfica': 0, 'Bilbao': 0, 'Bodoe Glimt': 1, 'Brugge': 3, 'Chelsea': 0, 'Dortmund': 1, 'FC Kobenhavn': 1, 'Frankfurt': 3, 'Galatasaray': 0, 'Inter': 3, 'Juventus': 1, 'Kairat': 0, 'Karabakh Agdam': 3, 'Leverkusen': 1, 'Liverpool': 3, 'Man City': 3, 'Marseille': 0, 'Monaco': 0, 'Napoli': 0, 'Newcastle': 0, 'Olympiakos': 1, 'PSV': 0, 'Paphos': 1, 'Paris SG': 3, 'Real Madrid': 3, 'Slavia Praha': 1, 'Sporting': 3, 'St Gillis': 3, 'Tottenham': 3, 'Villarreal': 0},
    'diff_buts': {'Ajax': -2, 'Arsenal': 2, 'Atalanta': -4, 'Atletico': -1, 'Barcelona': 1, 'Bayern': 2, 'Benfica': -1, 'Bilbao': -2, 'Bodoe Glimt': 0, 'Brugge': 3, 'Chelsea': -2, 'Dortmund': 0, 'FC Kobenhavn': 0, 'Frankfurt': 4, 'Galatasaray': -4, 'Inter': 2, 'Juventus': 0, 'Kairat': -3, 'Karabakh Agdam': 1, 'Leverkusen': 0, 'Liverpool': 1, 'Man City': 2, 'Marseille': -1, 'Monaco': -3, 'Napoli': -2, 'Newcastle': -1, 'Olympiakos': 0, 'PSV': -2, 'Paphos': 0, 'Paris SG': 4, 'Real Madrid': 1, 'Slavia Praha': 0, 'Sporting': 3, 'St Gillis': 2, 'Tottenham': 1, 'Villarreal': -1},
    'buts': {'Ajax': 0, 'Arsenal': 2, 'Atalanta': 0, 'Atletico': 2, 'Barcelona': 2, 'Bayern': 3, 'Benfica': 2, 'Bilbao': 0, 'Bodoe Glimt': 2, 'Brugge': 4, 'Chelsea': 1, 'Dortmund': 4, 'FC Kobenhavn': 2, 'Frankfurt': 5, 'Galatasaray': 1, 'Inter': 2, 'Juventus': 4, 'Kairat': 1, 'Karabakh Agdam': 3, 'Leverkusen': 2, 'Liverpool': 3, 'Man City': 2, 'Marseille': 1, 'Monaco': 1, 'Napoli': 0, 'Newcastle': 1, 'Olympiakos': 0, 'PSV': 1, 'Paphos': 0, 'Paris SG': 4, 'Real Madrid': 2, 'Slavia Praha': 2, 'Sporting': 4, 'St Gillis': 3, 'Tottenham': 1, 'Villarreal': 0},
    'buts_ext': {'Ajax': 0, 'Arsenal': 2, 'Atalanta': 0, 'Atletico': 2, 'Barcelona': 2, 'Bayern': 0, 'Benfica': 0, 'Bilbao': 0, 'Bodoe Glimt': 2, 'Brugge': 0, 'Chelsea': 1, 'Dortmund': 4, 'FC Kobenhavn': 0, 'Frankfurt': 0, 'Galatasaray': 1, 'Inter': 2, 'Juventus': 0, 'Kairat': 1, 'Karabakh Agdam': 3, 'Leverkusen': 2, 'Liverpool': 0, 'Man City': 0, 'Marseille': 1, 'Monaco': 1, 'Napoli': 0, 'Newcastle': 0, 'Olympiakos': 0, 'PSV': 0, 'Paphos': 0, 'Paris SG': 0, 'Real Madrid': 0, 'Slavia Praha': 0, 'Sporting': 0, 'St Gillis': 3, 'Tottenham': 0, 'Villarreal': 0},
    'nb_victoires': {'Ajax': 0, 'Arsenal': 1, 'Atalanta': 0, 'Atletico': 0, 'Barcelona': 1, 'Bayern': 1, 'Benfica': 0, 'Bilbao': 0, 'Bodoe Glimt': 0, 'Brugge': 1, 'Chelsea': 0, 'Dortmund': 0, 'FC Kobenhavn': 0, 'Frankfurt': 1, 'Galatasaray': 0, 'Inter': 1, 'Juventus': 0, 'Kairat': 0, 'Karabakh Agdam': 1, 'Leverkusen': 0, 'Liverpool': 1, 'Man City': 1, 'Marseille': 0, 'Monaco': 0, 'Napoli': 0, 'Newcastle': 0, 'Olympiakos': 0, 'PSV': 0, 'Paphos': 0, 'Paris SG': 1, 'Real Madrid': 1, 'Slavia Praha': 0, 'Sporting': 1, 'St Gillis': 1, 'Tottenham': 1, 'Villarreal': 0},
    'nb_victoires_ext': {'Ajax': 0, 'Arsenal': 1, 'Atalanta': 0, 'Atletico': 0, 'Barcelona': 1, 'Bayern': 0, 'Benfica': 0, 'Bilbao': 0, 'Bodoe Glimt': 0, 'Brugge': 0, 'Chelsea': 0, 'Dortmund': 0, 'FC Kobenhavn': 0, 'Frankfurt': 0, 'Galatasaray': 0, 'Inter': 1, 'Juventus': 0, 'Kairat': 0, 'Karabakh Agdam': 1, 'Leverkusen': 0, 'Liverpool': 0, 'Man City': 0, 'Marseille': 0, 'Monaco': 0, 'Napoli': 0, 'Newcastle': 0, 'Olympiakos': 0, 'PSV': 0, 'Paphos': 0, 'Paris SG': 0, 'Real Madrid': 0, 'Slavia Praha': 0, 'Sporting': 0, 'St Gillis': 1, 'Tottenham': 0, 'Villarreal': 0}
}

données_J2 = {
    'classement': ['Bayern', 'Real Madrid', 'Paris SG', 'Inter', 'Arsenal', 'Karabakh Agdam', 'Dortmund', 'Man City', 'Tottenham', 'Atletico', 'Newcastle', 'Marseille', 'Brugge', 'Sporting', 'Frankfurt', 'Barcelona', 'Liverpool', 'Chelsea', 'Napoli', 'St Gillis', 'Galatasaray', 'Atalanta', 'Juventus', 'Bodoe Glimt', 'Leverkusen', 'Villarreal', 'PSV', 'FC Kobenhavn', 'Olympiakos', 'Monaco', 'Slavia Praha', 'Paphos', 'Benfica', 'Bilbao', 'Ajax', 'Kairat'],
    'points': {'Ajax': 0, 'Arsenal': 6, 'Atalanta': 3, 'Atletico': 3, 'Barcelona': 3, 'Bayern': 6, 'Benfica': 0, 'Bilbao': 0, 'Bodoe Glimt': 2, 'Brugge': 3, 'Chelsea': 3, 'Dortmund': 4, 'FC Kobenhavn': 1, 'Frankfurt': 3, 'Galatasaray': 3, 'Inter': 6, 'Juventus': 2, 'Kairat': 0, 'Karabakh Agdam': 6, 'Leverkusen': 2, 'Liverpool': 3, 'Man City': 4, 'Marseille': 3, 'Monaco': 1, 'Napoli': 3, 'Newcastle': 3, 'Olympiakos': 1, 'PSV': 1, 'Paphos': 1, 'Paris SG': 6, 'Real Madrid': 6, 'Slavia Praha': 1, 'Sporting': 3, 'St Gillis': 3, 'Tottenham': 4, 'Villarreal': 1},
    'diff_buts': {'Ajax': -6, 'Arsenal': 4, 'Atalanta': -3, 'Atletico': 3, 'Barcelona': 0, 'Bayern': 6, 'Benfica': -2, 'Bilbao': -5, 'Bodoe Glimt': 0, 'Brugge': 2, 'Chelsea': -1, 'Dortmund': 3, 'FC Kobenhavn': -2, 'Frankfurt': 0, 'Galatasaray': -3, 'Inter': 5, 'Juventus': 0, 'Kairat': -8, 'Karabakh Agdam': 3, 'Leverkusen': 0, 'Liverpool': 0, 'Man City': 2, 'Marseille': 3, 'Monaco': -3, 'Napoli': -1, 'Newcastle': 3, 'Olympiakos': -2, 'PSV': -2, 'Paphos': -4, 'Paris SG': 5, 'Real Madrid': 6, 'Slavia Praha': -3, 'Sporting': 2, 'St Gillis': -2, 'Tottenham': 1, 'Villarreal': -1},
    'buts': {'Ajax': 0, 'Arsenal': 4, 'Atalanta': 2, 'Atletico': 7, 'Barcelona': 3, 'Bayern': 8, 'Benfica': 2, 'Bilbao': 1, 'Bodoe Glimt': 4, 'Brugge': 5, 'Chelsea': 2, 'Dortmund': 8, 'FC Kobenhavn': 2, 'Frankfurt': 6, 'Galatasaray': 2, 'Inter': 5, 'Juventus': 6, 'Kairat': 1, 'Karabakh Agdam': 5, 'Leverkusen': 3, 'Liverpool': 3, 'Man City': 4, 'Marseille': 5, 'Monaco': 3, 'Napoli': 2, 'Newcastle': 5, 'Olympiakos': 0, 'PSV': 2, 'Paphos': 1, 'Paris SG': 6, 'Real Madrid': 7, 'Slavia Praha': 2, 'Sporting': 5, 'St Gillis': 3, 'Tottenham': 3, 'Villarreal': 2},
    'buts_ext': {'Ajax': 0, 'Arsenal': 2, 'Atalanta': 0, 'Atletico': 2, 'Barcelona': 2, 'Bayern': 5, 'Benfica': 0, 'Bilbao': 1, 'Bodoe Glimt': 2, 'Brugge': 1, 'Chelsea': 1, 'Dortmund': 4, 'FC Kobenhavn': 0, 'Frankfurt': 1, 'Galatasaray': 1, 'Inter': 2, 'Juventus': 2, 'Kairat': 1, 'Karabakh Agdam': 3, 'Leverkusen': 2, 'Liverpool': 0, 'Man City': 2, 'Marseille': 1, 'Monaco': 1, 'Napoli': 0, 'Newcastle': 4, 'Olympiakos': 0, 'PSV': 1, 'Paphos': 0, 'Paris SG': 2, 'Real Madrid': 5, 'Slavia Praha': 0, 'Sporting': 1, 'St Gillis': 3, 'Tottenham': 2, 'Villarreal': 0},
    'nb_victoires': {'Ajax': 0, 'Arsenal': 2, 'Atalanta': 1, 'Atletico': 1, 'Barcelona': 1, 'Bayern': 2, 'Benfica': 0, 'Bilbao': 0, 'Bodoe Glimt': 0, 'Brugge': 1, 'Chelsea': 1, 'Dortmund': 1, 'FC Kobenhavn': 0, 'Frankfurt': 1, 'Galatasaray': 1, 'Inter': 2, 'Juventus': 0, 'Kairat': 0, 'Karabakh Agdam': 2, 'Leverkusen': 0, 'Liverpool': 1, 'Man City': 1, 'Marseille': 1, 'Monaco': 0, 'Napoli': 1, 'Newcastle': 1, 'Olympiakos': 0, 'PSV': 0, 'Paphos': 0, 'Paris SG': 2, 'Real Madrid': 2, 'Slavia Praha': 0, 'Sporting': 1, 'St Gillis': 1, 'Tottenham': 1, 'Villarreal': 0},
    'nb_victoires_ext': {'Ajax': 0, 'Arsenal': 1, 'Atalanta': 0, 'Atletico': 0, 'Barcelona': 1, 'Bayern': 1, 'Benfica': 0, 'Bilbao': 0, 'Bodoe Glimt': 0, 'Brugge': 0, 'Chelsea': 0, 'Dortmund': 0, 'FC Kobenhavn': 0, 'Frankfurt': 0, 'Galatasaray': 0, 'Inter': 1, 'Juventus': 0, 'Kairat': 0, 'Karabakh Agdam': 1, 'Leverkusen': 0, 'Liverpool': 0, 'Man City': 0, 'Marseille': 0, 'Monaco': 0, 'Napoli': 0, 'Newcastle': 1, 'Olympiakos': 0, 'PSV': 0, 'Paphos': 0, 'Paris SG': 1, 'Real Madrid': 1, 'Slavia Praha': 0, 'Sporting': 0, 'St Gillis': 1, 'Tottenham': 0, 'Villarreal': 0}
}

données_J3 = {
    'classement': ['Paris SG', 'Bayern', 'Inter', 'Arsenal', 'Real Madrid', 'Dortmund', 'Man City', 'Newcastle', 'Barcelona', 'Liverpool', 'Sporting', 'Chelsea', 'Karabakh Agdam', 'Galatasaray', 'Tottenham', 'PSV', 'Atalanta', 'Marseille', 'Atletico', 'Brugge', 'Bilbao', 'Frankfurt', 'Napoli', 'St Gillis', 'Juventus', 'Bodoe Glimt', 'Monaco', 'Slavia Praha', 'Paphos', 'Leverkusen', 'Villarreal', 'FC Kobenhavn', 'Olympiakos', 'Kairat', 'Benfica', 'Ajax'],
    'points': {'Ajax': 0, 'Arsenal': 9, 'Atalanta': 4, 'Atletico': 3, 'Barcelona': 6, 'Bayern': 9, 'Benfica': 0, 'Bilbao': 3, 'Bodoe Glimt': 2, 'Brugge': 3, 'Chelsea': 6, 'Dortmund': 7, 'FC Kobenhavn': 1, 'Frankfurt': 3, 'Galatasaray': 6, 'Inter': 9, 'Juventus': 2, 'Kairat': 1, 'Karabakh Agdam': 6, 'Leverkusen': 2, 'Liverpool': 6, 'Man City': 7, 'Marseille': 3, 'Monaco': 2, 'Napoli': 3, 'Newcastle': 6, 'Olympiakos': 1, 'PSV': 4, 'Paphos': 2, 'Paris SG': 9, 'Real Madrid': 9, 'Slavia Praha': 2, 'Sporting': 6, 'St Gillis': 3, 'Tottenham': 5, 'Villarreal': 1},
    'diff_buts': {'Ajax': -10, 'Arsenal': 8, 'Atalanta': -3, 'Atletico': -1, 'Barcelona': 5, 'Bayern': 10, 'Benfica': -5, 'Bilbao': -3, 'Bodoe Glimt': -2, 'Brugge': -2, 'Chelsea': 3, 'Dortmund': 5, 'FC Kobenhavn': -4, 'Frankfurt': -4, 'Galatasaray': -1, 'Inter': 9, 'Juventus': -1, 'Kairat': -8, 'Karabakh Agdam': 1, 'Leverkusen': -5, 'Liverpool': 4, 'Man City': 4, 'Marseille': 2, 'Monaco': -3, 'Napoli': -5, 'Newcastle': 6, 'Olympiakos': -7, 'PSV': 2, 'Paphos': -4, 'Paris SG': 10, 'Real Madrid': 7, 'Slavia Praha': -3, 'Sporting': 3, 'St Gillis': -6, 'Tottenham': 1, 'Villarreal': -3},
    'buts': {'Ajax': 1, 'Arsenal': 8, 'Atalanta': 2, 'Atletico': 7, 'Barcelona': 9, 'Bayern': 12, 'Benfica': 2, 'Bilbao': 4, 'Bodoe Glimt': 5, 'Brugge': 5, 'Chelsea': 7, 'Dortmund': 12, 'FC Kobenhavn': 4, 'Frankfurt': 7, 'Galatasaray': 5, 'Inter': 9, 'Juventus': 6, 'Kairat': 1, 'Karabakh Agdam': 6, 'Leverkusen': 5, 'Liverpool': 8, 'Man City': 6, 'Marseille': 6, 'Monaco': 3, 'Napoli': 4, 'Newcastle': 8, 'Olympiakos': 1, 'PSV': 8, 'Paphos': 1, 'Paris SG': 13, 'Real Madrid': 8, 'Slavia Praha': 2, 'Sporting': 7, 'St Gillis': 3, 'Tottenham': 3, 'Villarreal': 2},
    'buts_ext': {'Ajax': 1, 'Arsenal': 2, 'Atalanta': 0, 'Atletico': 2, 'Barcelona': 2, 'Bayern': 5, 'Benfica': 0, 'Bilbao': 1, 'Bodoe Glimt': 3, 'Brugge': 1, 'Chelsea': 1, 'Dortmund': 8, 'FC Kobenhavn': 0, 'Frankfurt': 1, 'Galatasaray': 1, 'Inter': 6, 'Juventus': 2, 'Kairat': 1, 'Karabakh Agdam': 4, 'Leverkusen': 2, 'Liverpool': 5, 'Man City': 4, 'Marseille': 2, 'Monaco': 1, 'Napoli': 2, 'Newcastle': 4, 'Olympiakos': 1, 'PSV': 1, 'Paphos': 0, 'Paris SG': 9, 'Real Madrid': 5, 'Slavia Praha': 0, 'Sporting': 1, 'St Gillis': 3, 'Tottenham': 2, 'Villarreal': 0},
    'nb_victoires': {'Ajax': 0, 'Arsenal': 3, 'Atalanta': 1, 'Atletico': 1, 'Barcelona': 2, 'Bayern': 3, 'Benfica': 0, 'Bilbao': 1, 'Bodoe Glimt': 0, 'Brugge': 1, 'Chelsea': 2, 'Dortmund': 2, 'FC Kobenhavn': 0, 'Frankfurt': 1, 'Galatasaray': 2, 'Inter': 3, 'Juventus': 0, 'Kairat': 0, 'Karabakh Agdam': 2, 'Leverkusen': 0, 'Liverpool': 2, 'Man City': 2, 'Marseille': 1, 'Monaco': 0, 'Napoli': 1, 'Newcastle': 2, 'Olympiakos': 0, 'PSV': 1, 'Paphos': 0, 'Paris SG': 3, 'Real Madrid': 3, 'Slavia Praha': 0, 'Sporting': 2, 'St Gillis': 1, 'Tottenham': 1, 'Villarreal': 0},
    'nb_victoires_ext': {'Ajax': 0, 'Arsenal': 1, 'Atalanta': 0, 'Atletico': 0, 'Barcelona': 1, 'Bayern': 1, 'Benfica': 0, 'Bilbao': 0, 'Bodoe Glimt': 0, 'Brugge': 0, 'Chelsea': 0, 'Dortmund': 1, 'FC Kobenhavn': 0, 'Frankfurt': 0, 'Galatasaray': 0, 'Inter': 2, 'Juventus': 0, 'Kairat': 0, 'Karabakh Agdam': 1, 'Leverkusen': 0, 'Liverpool': 1, 'Man City': 1, 'Marseille': 0, 'Monaco': 0, 'Napoli': 0, 'Newcastle': 1, 'Olympiakos': 0, 'PSV': 0, 'Paphos': 0, 'Paris SG': 2, 'Real Madrid': 1, 'Slavia Praha': 0, 'Sporting': 0, 'St Gillis': 1, 'Tottenham': 0, 'Villarreal': 0}
}

données_J4 = {
    'classement': ['Bayern', 'Arsenal', 'Inter', 'Man City', 'Paris SG', 'Newcastle', 'Real Madrid', 'Liverpool', 'Galatasaray', 'Tottenham', 'Barcelona', 'Chelsea', 'Sporting', 'Dortmund', 'Karabakh Agdam', 'Atalanta', 'Atletico', 'PSV', 'Monaco', 'Paphos', 'Leverkusen', 'Brugge', 'Frankfurt', 'Napoli', 'Marseille', 'Juventus', 'Bilbao', 'St Gillis', 'Bodoe Glimt', 'Slavia Praha', 'Olympiakos', 'Villarreal', 'FC Kobenhavn', 'Kairat', 'Benfica', 'Ajax'],
    'points': {'Ajax': 0, 'Arsenal': 12, 'Atalanta': 7, 'Atletico': 6, 'Barcelona': 7, 'Bayern': 12, 'Benfica': 0, 'Bilbao': 3, 'Bodoe Glimt': 2, 'Brugge': 4, 'Chelsea': 7, 'Dortmund': 7, 'FC Kobenhavn': 1, 'Frankfurt': 4, 'Galatasaray': 9, 'Inter': 12, 'Juventus': 3, 'Kairat': 1, 'Karabakh Agdam': 7, 'Leverkusen': 5, 'Liverpool': 9, 'Man City': 10, 'Marseille': 3, 'Monaco': 5, 'Napoli': 4, 'Newcastle': 9, 'Olympiakos': 2, 'PSV': 5, 'Paphos': 5, 'Paris SG': 9, 'Real Madrid': 9, 'Slavia Praha': 2, 'Sporting': 7, 'St Gillis': 3, 'Tottenham': 8, 'Villarreal': 1},
    'diff_buts': {'Ajax': -13, 'Arsenal': 11, 'Atalanta': -2, 'Atletico': 1, 'Barcelona': 5, 'Bayern': 11, 'Benfica': -6, 'Bilbao': -5, 'Bodoe Glimt': -3, 'Brugge': -2, 'Chelsea': 3, 'Dortmund': 2, 'FC Kobenhavn': -8, 'Frankfurt': -4, 'Galatasaray': 2, 'Inter': 10, 'Juventus': -1, 'Kairat': -9, 'Karabakh Agdam': 1, 'Leverkusen': -4, 'Liverpool': 5, 'Man City': 7, 'Marseille': 1, 'Monaco': -2, 'Napoli': -5, 'Newcastle': 8, 'Olympiakos': -7, 'PSV': 2, 'Paphos': -3, 'Paris SG': 9, 'Real Madrid': 6, 'Slavia Praha': -6, 'Sporting': 3, 'St Gillis': -8, 'Tottenham': 5, 'Villarreal': -4},
    'buts': {'Ajax': 1, 'Arsenal': 11, 'Atalanta': 3, 'Atletico': 10, 'Barcelona': 12, 'Bayern': 14, 'Benfica': 2, 'Bilbao': 4, 'Bodoe Glimt': 5, 'Brugge': 8, 'Chelsea': 9, 'Dortmund': 13, 'FC Kobenhavn': 4, 'Frankfurt': 7, 'Galatasaray': 8, 'Inter': 11, 'Juventus': 7, 'Kairat': 2, 'Karabakh Agdam': 8, 'Leverkusen': 6, 'Liverpool': 9, 'Man City': 10, 'Marseille': 6, 'Monaco': 4, 'Napoli': 4, 'Newcastle': 10, 'Olympiakos': 2, 'PSV': 9, 'Paphos': 2, 'Paris SG': 14, 'Real Madrid': 8, 'Slavia Praha': 2, 'Sporting': 8, 'St Gillis': 4, 'Tottenham': 7, 'Villarreal': 2},
    'buts_ext': {'Ajax': 1, 'Arsenal': 5, 'Atalanta': 1, 'Atletico': 2, 'Barcelona': 5, 'Bayern': 7, 'Benfica': 0, 'Bilbao': 1, 'Bodoe Glimt': 3, 'Brugge': 1, 'Chelsea': 3, 'Dortmund': 9, 'FC Kobenhavn': 0, 'Frankfurt': 1, 'Galatasaray': 4, 'Inter': 6, 'Juventus': 2, 'Kairat': 2, 'Karabakh Agdam': 4, 'Leverkusen': 3, 'Liverpool': 5, 'Man City': 4, 'Marseille': 2, 'Monaco': 2, 'Napoli': 2, 'Newcastle': 4, 'Olympiakos': 1, 'PSV': 2, 'Paphos': 0, 'Paris SG': 9, 'Real Madrid': 5, 'Slavia Praha': 0, 'Sporting': 2, 'St Gillis': 4, 'Tottenham': 2, 'Villarreal': 0},
    'nb_victoires': {'Ajax': 0, 'Arsenal': 4, 'Atalanta': 2, 'Atletico': 2, 'Barcelona': 2, 'Bayern': 4, 'Benfica': 0, 'Bilbao': 1, 'Bodoe Glimt': 0, 'Brugge': 1, 'Chelsea': 2, 'Dortmund': 2, 'FC Kobenhavn': 0, 'Frankfurt': 1, 'Galatasaray': 3, 'Inter': 4, 'Juventus': 0, 'Kairat': 0, 'Karabakh Agdam': 2, 'Leverkusen': 1, 'Liverpool': 3, 'Man City': 3, 'Marseille': 1, 'Monaco': 1, 'Napoli': 1, 'Newcastle': 3, 'Olympiakos': 0, 'PSV': 1, 'Paphos': 1, 'Paris SG': 3, 'Real Madrid': 3, 'Slavia Praha': 0, 'Sporting': 2, 'St Gillis': 1, 'Tottenham': 2, 'Villarreal': 0},
    'nb_victoires_ext': {'Ajax': 0, 'Arsenal': 2, 'Atalanta': 1, 'Atletico': 0, 'Barcelona': 1, 'Bayern': 2, 'Benfica': 0, 'Bilbao': 0, 'Bodoe Glimt': 0, 'Brugge': 0, 'Chelsea': 0, 'Dortmund': 1, 'FC Kobenhavn': 0, 'Frankfurt': 0, 'Galatasaray': 1, 'Inter': 2, 'Juventus': 0, 'Kairat': 0, 'Karabakh Agdam': 1, 'Leverkusen': 1, 'Liverpool': 1, 'Man City': 1, 'Marseille': 0, 'Monaco': 1, 'Napoli': 0, 'Newcastle': 1, 'Olympiakos': 0, 'PSV': 0, 'Paphos': 0, 'Paris SG': 2, 'Real Madrid': 1, 'Slavia Praha': 0, 'Sporting': 0, 'St Gillis': 1, 'Tottenham': 0, 'Villarreal': 0}
}

données_J5 = {
    'classement': ['Arsenal', 'Paris SG', 'Bayern', 'Inter', 'Real Madrid', 'Dortmund', 'Chelsea', 'Sporting', 'Man City', 'Atalanta', 'Newcastle', 'Atletico', 'Liverpool', 'Galatasaray', 'PSV', 'Tottenham', 'Leverkusen', 'Barcelona', 'Karabakh Agdam', 'Napoli', 'Marseille', 'Juventus', 'Monaco', 'Paphos', 'St Gillis', 'Brugge', 'Bilbao', 'Frankfurt', 'FC Kobenhavn', 'Benfica', 'Slavia Praha', 'Bodoe Glimt', 'Olympiakos', 'Villarreal', 'Kairat', 'Ajax'],
    'points': {'Ajax': 0, 'Arsenal': 15, 'Atalanta': 10, 'Atletico': 9, 'Barcelona': 7, 'Bayern': 12, 'Benfica': 3, 'Bilbao': 4, 'Bodoe Glimt': 2, 'Brugge': 4, 'Chelsea': 10, 'Dortmund': 10, 'FC Kobenhavn': 4, 'Frankfurt': 4, 'Galatasaray': 9, 'Inter': 12, 'Juventus': 6, 'Kairat': 1, 'Karabakh Agdam': 7, 'Leverkusen': 8, 'Liverpool': 9, 'Man City': 10, 'Marseille': 6, 'Monaco': 6, 'Napoli': 7, 'Newcastle': 9, 'Olympiakos': 2, 'PSV': 8, 'Paphos': 6, 'Paris SG': 12, 'Real Madrid': 12, 'Slavia Praha': 3, 'Sporting': 10, 'St Gillis': 6, 'Tottenham': 8, 'Villarreal': 1},
    'diff_buts': {'Ajax': -15, 'Arsenal': 13, 'Atalanta': 1, 'Atletico': 2, 'Barcelona': 2, 'Bayern': 9, 'Benfica': -4, 'Bilbao': -5, 'Bodoe Glimt': -4, 'Brugge': -5, 'Chelsea': 6, 'Dortmund': 6, 'FC Kobenhavn': -7, 'Frankfurt': -7, 'Galatasaray': 1, 'Inter': 9, 'Juventus': 0, 'Kairat': -10, 'Karabakh Agdam': -1, 'Leverkusen': -2, 'Liverpool': 2, 'Man City': 5, 'Marseille': 2, 'Monaco': -2, 'Napoli': -3, 'Newcastle': 7, 'Olympiakos': -8, 'PSV': 5, 'Paphos': -3, 'Paris SG': 11, 'Real Madrid': 7, 'Slavia Praha': -6, 'Sporting': 6, 'St Gillis': -7, 'Tottenham': 3, 'Villarreal': -8},
    'buts': {'Ajax': 1, 'Arsenal': 14, 'Atalanta': 6, 'Atletico': 12, 'Barcelona': 12, 'Bayern': 15, 'Benfica': 4, 'Bilbao': 4, 'Bodoe Glimt': 7, 'Brugge': 8, 'Chelsea': 12, 'Dortmund': 17, 'FC Kobenhavn': 7, 'Frankfurt': 7, 'Galatasaray': 8, 'Inter': 12, 'Juventus': 10, 'Kairat': 4, 'Karabakh Agdam': 8, 'Leverkusen': 8, 'Liverpool': 10, 'Man City': 10, 'Marseille': 8, 'Monaco': 6, 'Napoli': 6, 'Newcastle': 11, 'Olympiakos': 5, 'PSV': 13, 'Paphos': 4, 'Paris SG': 19, 'Real Madrid': 12, 'Slavia Praha': 2, 'Sporting': 11, 'St Gillis': 5, 'Tottenham': 10, 'Villarreal': 2},
    'buts_ext': {'Ajax': 1, 'Arsenal': 5, 'Atalanta': 4, 'Atletico': 2, 'Barcelona': 5, 'Bayern': 8, 'Benfica': 2, 'Bilbao': 1, 'Bodoe Glimt': 3, 'Brugge': 1, 'Chelsea': 3, 'Dortmund': 9, 'FC Kobenhavn': 0, 'Frankfurt': 1, 'Galatasaray': 4, 'Inter': 7, 'Juventus': 5, 'Kairat': 4, 'Karabakh Agdam': 4, 'Leverkusen': 5, 'Liverpool': 5, 'Man City': 4, 'Marseille': 2, 'Monaco': 4, 'Napoli': 2, 'Newcastle': 5, 'Olympiakos': 1, 'PSV': 6, 'Paphos': 0, 'Paris SG': 9, 'Real Madrid': 9, 'Slavia Praha': 0, 'Sporting': 2, 'St Gillis': 5, 'Tottenham': 5, 'Villarreal': 0},
    'nb_victoires': {'Ajax': 0, 'Arsenal': 5, 'Atalanta': 3, 'Atletico': 3, 'Barcelona': 2, 'Bayern': 4, 'Benfica': 1, 'Bilbao': 1, 'Bodoe Glimt': 0, 'Brugge': 1, 'Chelsea': 3, 'Dortmund': 3, 'FC Kobenhavn': 1, 'Frankfurt': 1, 'Galatasaray': 3, 'Inter': 4, 'Juventus': 1, 'Kairat': 0, 'Karabakh Agdam': 2, 'Leverkusen': 2, 'Liverpool': 3, 'Man City': 3, 'Marseille': 2, 'Monaco': 1, 'Napoli': 2, 'Newcastle': 3, 'Olympiakos': 0, 'PSV': 2, 'Paphos': 1, 'Paris SG': 4, 'Real Madrid': 4, 'Slavia Praha': 0, 'Sporting': 3, 'St Gillis': 2, 'Tottenham': 2, 'Villarreal': 0},
    'nb_victoires_ext': {'Ajax': 0, 'Arsenal': 2, 'Atalanta': 2, 'Atletico': 0, 'Barcelona': 1, 'Bayern': 2, 'Benfica': 1, 'Bilbao': 0, 'Bodoe Glimt': 0, 'Brugge': 0, 'Chelsea': 0, 'Dortmund': 1, 'FC Kobenhavn': 0, 'Frankfurt': 0, 'Galatasaray': 1, 'Inter': 2, 'Juventus': 1, 'Kairat': 0, 'Karabakh Agdam': 1, 'Leverkusen': 2, 'Liverpool': 1, 'Man City': 1, 'Marseille': 0, 'Monaco': 1, 'Napoli': 0, 'Newcastle': 1, 'Olympiakos': 0, 'PSV': 1, 'Paphos': 0, 'Paris SG': 2, 'Real Madrid': 2, 'Slavia Praha': 0, 'Sporting': 0, 'St Gillis': 2, 'Tottenham': 0, 'Villarreal': 0}
}

données_J6 = {
    'classement': ['Arsenal', 'Bayern', 'Paris SG', 'Man City', 'Atalanta', 'Inter', 'Real Madrid', 'Atletico', 'Liverpool', 'Dortmund', 'Tottenham', 'Newcastle', 'Chelsea', 'Sporting', 'Barcelona', 'Marseille', 'Juventus', 'Galatasaray', 'Monaco', 'Leverkusen', 'PSV', 'Karabakh Agdam', 'Napoli', 'FC Kobenhavn', 'Benfica', 'Paphos', 'St Gillis', 'Bilbao', 'Olympiakos', 'Frankfurt', 'Brugge', 'Bodoe Glimt', 'Slavia Praha', 'Ajax', 'Villarreal', 'Kairat'],
    'points': {'Ajax': 3, 'Arsenal': 18, 'Atalanta': 13, 'Atletico': 12, 'Barcelona': 10, 'Bayern': 15, 'Benfica': 6, 'Bilbao': 5, 'Bodoe Glimt': 3, 'Brugge': 4, 'Chelsea': 10, 'Dortmund': 11, 'FC Kobenhavn': 7, 'Frankfurt': 4, 'Galatasaray': 9, 'Inter': 12, 'Juventus': 9, 'Kairat': 1, 'Karabakh Agdam': 7, 'Leverkusen': 9, 'Liverpool': 12, 'Man City': 13, 'Marseille': 9, 'Monaco': 9, 'Napoli': 7, 'Newcastle': 10, 'Olympiakos': 5, 'PSV': 8, 'Paphos': 6, 'Paris SG': 13, 'Real Madrid': 12, 'Slavia Praha': 3, 'Sporting': 10, 'St Gillis': 6, 'Tottenham': 11, 'Villarreal': 1},
    'diff_buts': {'Ajax': -13, 'Arsenal': 16, 'Atalanta': 2, 'Atletico': 3, 'Barcelona': 3, 'Bayern': 11, 'Benfica': -2, 'Bilbao': -5, 'Bodoe Glimt': -4, 'Brugge': -8, 'Chelsea': 5, 'Dortmund': 6, 'FC Kobenhavn': -6, 'Frankfurt': -8, 'Galatasaray': 0, 'Inter': 8, 'Juventus': 2, 'Kairat': -11, 'Karabakh Agdam': -3, 'Leverkusen': -2, 'Liverpool': 3, 'Man City': 6, 'Marseille': 3, 'Monaco': -1, 'Napoli': -5, 'Newcastle': 7, 'Olympiakos': -7, 'PSV': 4, 'Paphos': -5, 'Paris SG': 11, 'Real Madrid': 6, 'Slavia Praha': -9, 'Sporting': 4, 'St Gillis': -8, 'Tottenham': 6, 'Villarreal': -9},
    'buts': {'Ajax': 5, 'Arsenal': 17, 'Atalanta': 8, 'Atletico': 15, 'Barcelona': 14, 'Bayern': 18, 'Benfica': 6, 'Bilbao': 4, 'Bodoe Glimt': 9, 'Brugge': 8, 'Chelsea': 13, 'Dortmund': 19, 'FC Kobenhavn': 10, 'Frankfurt': 8, 'Galatasaray': 8, 'Inter': 12, 'Juventus': 12, 'Kairat': 4, 'Karabakh Agdam': 10, 'Leverkusen': 10, 'Liverpool': 11, 'Man City': 12, 'Marseille': 11, 'Monaco': 7, 'Napoli': 6, 'Newcastle': 13, 'Olympiakos': 6, 'PSV': 15, 'Paphos': 4, 'Paris SG': 19, 'Real Madrid': 13, 'Slavia Praha': 2, 'Sporting': 12, 'St Gillis': 7, 'Tottenham': 13, 'Villarreal': 4},
    'buts_ext': {'Ajax': 5, 'Arsenal': 8, 'Atalanta': 4, 'Atletico': 5, 'Barcelona': 5, 'Bayern': 8, 'Benfica': 2, 'Bilbao': 1, 'Bodoe Glimt': 5, 'Brugge': 1, 'Chelsea': 4, 'Dortmund': 9, 'FC Kobenhavn': 3, 'Frankfurt': 2, 'Galatasaray': 4, 'Inter': 7, 'Juventus': 5, 'Kairat': 4, 'Karabakh Agdam': 4, 'Leverkusen': 5, 'Liverpool': 6, 'Man City': 6, 'Marseille': 5, 'Monaco': 4, 'Napoli': 2, 'Newcastle': 7, 'Olympiakos': 2, 'PSV': 6, 'Paphos': 0, 'Paris SG': 9, 'Real Madrid': 9, 'Slavia Praha': 0, 'Sporting': 3, 'St Gillis': 5, 'Tottenham': 5, 'Villarreal': 0},
    'nb_victoires': {'Ajax': 1, 'Arsenal': 6, 'Atalanta': 4, 'Atletico': 4, 'Barcelona': 3, 'Bayern': 5, 'Benfica': 2, 'Bilbao': 1, 'Bodoe Glimt': 0, 'Brugge': 1, 'Chelsea': 3, 'Dortmund': 3, 'FC Kobenhavn': 2, 'Frankfurt': 1, 'Galatasaray': 3, 'Inter': 4, 'Juventus': 2, 'Kairat': 0, 'Karabakh Agdam': 2, 'Leverkusen': 2, 'Liverpool': 4, 'Man City': 4, 'Marseille': 3, 'Monaco': 2, 'Napoli': 2, 'Newcastle': 3, 'Olympiakos': 1, 'PSV': 2, 'Paphos': 1, 'Paris SG': 4, 'Real Madrid': 4, 'Slavia Praha': 0, 'Sporting': 3, 'St Gillis': 2, 'Tottenham': 3, 'Villarreal': 0},
    'nb_victoires_ext': {'Ajax': 1, 'Arsenal': 3, 'Atalanta': 2, 'Atletico': 1, 'Barcelona': 1, 'Bayern': 2, 'Benfica': 1, 'Bilbao': 0, 'Bodoe Glimt': 0, 'Brugge': 0, 'Chelsea': 0, 'Dortmund': 1, 'FC Kobenhavn': 1, 'Frankfurt': 0, 'Galatasaray': 1, 'Inter': 2, 'Juventus': 1, 'Kairat': 0, 'Karabakh Agdam': 1, 'Leverkusen': 2, 'Liverpool': 2, 'Man City': 2, 'Marseille': 1, 'Monaco': 1, 'Napoli': 0, 'Newcastle': 1, 'Olympiakos': 1, 'PSV': 1, 'Paphos': 0, 'Paris SG': 2, 'Real Madrid': 2, 'Slavia Praha': 0, 'Sporting': 0, 'St Gillis': 2, 'Tottenham': 0, 'Villarreal': 0}
}

# 1. Définition d'un état "neutre" (Tout le monde à 0 point)
etat_zero = {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, 
            "nb_victoires_ext": None
    }

# 2. Initialisation de sécurité des variables manquantes
if 'données_J7' not in globals(): données_J7 = etat_zero
if 'données_J8' not in globals(): données_J8 = etat_zero

def get_simulation_flexible(n_simulations=1000, start_day=0, end_day=8):

    try:
        sd = int(start_day)
    except:
        sd = 0
    update_simulation_context(sd)

    if start_day == 0:
        etat_initial = {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, 
            "nb_victoires_ext": None
        }
    else:
        # Si on commence J_k (ex: J3), on charge les données de J_(k-1) (ex: J2)
        map_historique = {
            1: données_J1,
            2: données_J2,
            3: données_J3,
            4: données_J4,
            5: données_J5,
            6: données_J6, 
            7: données_J7,
            8: données_J8
        }
        # On récupère l'historique, ou le vide par sécurité
        etat_initial = map_historique.get(start_day, {
             "classement": None, "points": None, "diff_buts": None, 
             "buts": None, "buts_ext": None, "nb_victoires": None, 
             "nb_victoires_ext": None
        })

    # 2. INITIALISATION DES COMPTEURS (Moyenne)
    total_stats = {
        club: {
            "points": 0, "diff_buts": 0, "buts": 0, 
            "buts_ext": 0, "nb_victoires": 0, "nb_victoires_ext": 0
        } 
        for club in clubs_en_ldc
    }

    # 3. BOUCLE DE SIMULATION
    for _ in range(n_simulations):
        resultats_simu = simulation_ligue(
            données=etat_initial, 
            debut=start_day + 1, 
            fin=end_day
        )
        
        # Cumul des résultats pour la moyenne
        for club in clubs_en_ldc:
            total_stats[club]["points"] += resultats_simu["points"][club]
            total_stats[club]["diff_buts"] += resultats_simu["diff_buts"][club]
            total_stats[club]["buts"] += resultats_simu["buts"][club]
            total_stats[club]["buts_ext"] += resultats_simu["buts_ext"][club]
            total_stats[club]["nb_victoires"] += resultats_simu["nb_victoires"][club]
            total_stats[club]["nb_victoires_ext"] += resultats_simu["nb_victoires_ext"][club]

    # 4. CALCUL DES MOYENNES ET FORMATAGE
    ranking_data = []
    
    for club, stats in total_stats.items():
        ranking_data.append({
            "club": club,
            "points": round(stats["points"] / n_simulations, 1),
            "diff": round(stats["diff_buts"] / n_simulations, 1),
            "buts": round(stats["buts"] / n_simulations, 1),
            "buts_ext": round(stats["buts_ext"] / n_simulations, 1),
            "victoires": round(stats["nb_victoires"] / n_simulations, 1),
            "victoires_ext": round(stats["nb_victoires_ext"] / n_simulations, 1),
        })

    # 5. TRI (Tie-Breakers UEFA complets)
    # Points > Diff > Buts > Buts Ext > Victoires > Victoires Ext
    ranking_data.sort(key=lambda x: (
        x['points'], 
        x['diff'], 
        x['buts'], 
        x['buts_ext'], 
        x['victoires'], 
        x['victoires_ext']
    ), reverse=True)

    # Ajout du rang
    for i, row in enumerate(ranking_data):
        row['rank'] = i + 1

    return ranking_data

def get_probas_top8_qualif(nb_simulations=1000, journee_depart=0):
    """
    Génère les tableaux de PROBABILITÉS (Top 8 et Top 24) en fonction de la journée de départ.
    Logique similaire à get_simulation_flexible.
    """
    try:
        jd = int(journee_depart)
    except:
        jd = 0
    update_simulation_context(jd)
    
    if journee_depart == 0:
        etat_initial = {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, 
            "nb_victoires_ext": None
        }
    else:
        map_historique = {
            1: données_J1,
            2: données_J2,
            3: données_J3,
            4: données_J4,
            5: données_J5,
            6: données_J6, 
            7: données_J7,
            8: données_J8
        }
        # On récupère l'historique, ou le vide par sécurité
        etat_initial = map_historique.get(journee_depart, {
             "classement": None, "points": None, "diff_buts": None, 
             "buts": None, "buts_ext": None, "nb_victoires": None, 
             "nb_victoires_ext": None
        })


    # 2. DÉFINITION DE LA PLAGE DE SIMULATION
    # Si on a chargé les données de la J6, les prochains matchs sont ceux de la J7.
    debut_simu = journee_depart + 1

    # 3. LANCEMENT DE LA DISTRIBUTION (Monte Carlo)
    distrib_clubs = distribution_position_par_club(
        N=nb_simulations, 
        données=etat_initial, 
        debut=debut_simu, 
        fin=8
    )
    
    # 4. CALCUL DES PROBABILITÉS ET FORMATAGE
    liste_qualif = []
    liste_top8 = []
    
    for club in clubs_en_ldc:
        # Calcul via vos fonctions utilitaires
        p_qualif = proba_qualification(club, distrib_clubs)
        p_top8 = proba_top_8(club, distrib_clubs)
        
        # On ne garde que les valeurs pertinentes (> 0.1%) pour alléger le tableau
        if p_qualif > 0.001:
            liste_qualif.append({
                "club": club, 
                "proba": round(p_qualif * 100, 1)
            })
            
        if p_top8 > 0.001:
            liste_top8.append({
                "club": club, 
                "proba": round(p_top8 * 100, 1)
            })
            
    # 5. TRI DÉCROISSANT (Le plus de chances en premier)
    liste_qualif.sort(key=lambda x: x["proba"], reverse=True)
    liste_top8.sort(key=lambda x: x["proba"], reverse=True)
    
    return {
        "day_used": journee_depart,
        "ranking_qualif": liste_qualif,
        "ranking_top8": liste_top8
    }

# =============================================================================
# 1. FONCTIONS UTILITAIRES (Indispensables pour les calculs)
# =============================================================================

def proba_qualification(club, distribution_rangs):
    """
    Calcule le % de chance d'être dans le Top 24 (Qualifié).
    Somme des probabilités d'être classé de 1 à 24.
    """
    if not distribution_rangs or club not in distribution_rangs:
        return 0.0
    # On additionne les probas de finir 1er, 2ème ... jusqu'à 24ème
    proba = sum(distribution_rangs[club].get(r, 0) for r in range(1, 25))
    return proba

# =============================================================================
# 2. WRAPPERS WEB : SCÉNARIO & HYPO-MÈTRE
# =============================================================================

def get_scenario_analysis(club_cible, journee_cible, resultat_fixe, journee_depart=6, n_simulations=500):
    """
    Simule la différence entre la situation actuelle et la situation 
    si un match spécifique se termine par V, N ou D.
    """
    # 1. Mise à jour du contexte (Elo dynamique & Calendrier)
    try:
        jd = int(journee_depart)
    except:
        jd = 0
    update_simulation_context(jd)

    # 2. Chargement des données historiques
    # On récupère l'état du classement au moment du départ
    map_historique = {
        0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    etat_initial = map_historique.get(jd, données_J6)
    
    # La simulation commence le lendemain de la journée de départ
    debut_simu = jd + 1

    # Sécurité : Si la journée cible est déjà passée, on simule depuis la cible
    jc = int(journee_cible)
    if debut_simu > jc: 
        debut_simu = jc 

    # ---------------------------------------------------------
    # ÉTAPE A : SITUATION "AVANT" (Baseline sans forcer le match)
    # ---------------------------------------------------------
    distrib_avant = distribution_position_par_club(
        N=n_simulations, 
        données=etat_initial, 
        debut=debut_simu, 
        fin=8
    )
    
    # Calcul des probas Avant
    stats_avant = distrib_avant.get(club_cible, {})
    top8_avant = sum(stats_avant.get(r, 0) for r in range(1, 9))
    qualif_avant = sum(stats_avant.get(r, 0) for r in range(1, 25))

    # ---------------------------------------------------------
    # ÉTAPE B : SITUATION "APRÈS" (Avec le scénario forcé)
    # ---------------------------------------------------------
    # On force le résultat du match de 'club_cible' à la journée 'jc'
    distrib_apres = distribution_position_par_club_match_fixe(
        N=n_simulations, 
        club_fixed=club_cible, 
        journee=jc,
        result_fixed=resultat_fixe, 
        données=etat_initial, 
        debut=debut_simu, 
        fin=8
    )
    
    # Calcul des probas Après
    stats_apres = distrib_apres.get(club_cible, {})
    top8_apres = sum(stats_apres.get(r, 0) for r in range(1, 9))
    qualif_apres = sum(stats_apres.get(r, 0) for r in range(1, 25))

    # ---------------------------------------------------------
    # ÉTAPE C : RETOUR JSON
    # ---------------------------------------------------------
    return {
        "club": club_cible,
        "scenario": resultat_fixe,
        "journee": jc,
        "avant": {
            "top8": round(top8_avant * 100, 1),
            "qualif": round(qualif_avant * 100, 1)
        },
        "apres": {
            "top8": round(top8_apres * 100, 1),
            "qualif": round(qualif_apres * 100, 1)
        },
        "delta": {
            "top8": round((top8_apres - top8_avant) * 100, 1),
            "qualif": round((qualif_apres - qualif_avant) * 100, 1)
        }
    }


def get_web_hypometre(club_cible, nb_simulations=300, journee_depart=6):
    """
    Analyse quels matchs de la PROCHAINE journée ont le plus d'impact 
    sur la qualification de 'club_cible'.
    """
    # 1. Mise à jour temporelle
    try:
        jd = int(journee_depart)
    except:
        jd = 0
    update_simulation_context(jd)

    if club_cible not in clubs_en_ldc:
        return {"error": f"Club {club_cible} introuvable"}
    
    # 2. Identifier la prochaine journée à jouer
    journee_suivante = jd + 1
    
    # On récupère le calendrier (gestion des clés "Journée X" ou entiers)
    # On suppose que 'calendrier' est votre variable globale contenant les matchs
    matchs_a_tester = calendrier.get(f"Journée {journee_suivante}", [])
    if not matchs_a_tester:
        matchs_a_tester = calendrier.get(journee_suivante, [])

    if not matchs_a_tester:
        return {"error": f"Pas de matchs trouvés pour J{journee_suivante}"}

    # 3. Charger l'état actuel des points
    map_historique = {
        0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    etat_actuel = map_historique.get(jd, données_J6)
    
    resultats_impact = []
    
    print(f"Calcul Hypo-mètre pour {club_cible} (J{journee_suivante})...")
    
    # 4. BOUCLE D'ANALYSE (Calcul des enjeux)
    for (dom, ext) in matchs_a_tester:
        
        # --- MONDE A : L'équipe à Domicile Gagne ---
        distrib_dom = distribution_position_par_club_match_fixe(
            N=nb_simulations, club_fixed=dom, journee=journee_suivante, result_fixed='V',
            données=etat_actuel, debut=journee_suivante, fin=8
        )
        p_qualif_1 = proba_qualification(club_cible, distrib_dom)
        
        # --- MONDE B : L'équipe à l'Extérieur Gagne ---
        distrib_ext = distribution_position_par_club_match_fixe(
            N=nb_simulations, club_fixed=dom, journee=journee_suivante, result_fixed='D',
            données=etat_actuel, debut=journee_suivante, fin=8
        )
        p_qualif_2 = proba_qualification(club_cible, distrib_ext)
        
        # L'impact est la différence absolue de probabilité pour NOTRE club
        # entre les deux issues possibles du match des autres
        impact = abs(p_qualif_1 - p_qualif_2) * 100
        
        is_own_match = (dom == club_cible or ext == club_cible)
        
        # On garde le match s'il a un impact significatif (>0.5%) ou si c'est le nôtre
        if impact > 0.5 or is_own_match:
            resultats_impact.append({
                "match": f"{dom} vs {ext}",
                "dom": dom,
                "ext": ext,
                "score": round(impact, 1),
                "is_my_match": is_own_match
            })

    # 5. Tri : D'abord le match de l'équipe, puis les plus gros impacts
    resultats_impact.sort(key=lambda x: (x['is_my_match'], x['score']), reverse=True)
    
    return {
        "club": club_cible,
        "journee": journee_suivante,
        "liste": resultats_impact
    }

def get_web_evolution(club, journee_max=8, n_simulations=300):
    """
    Fonction SECONDAIRE : Calcule l'historique pour le graphique.
    Ne renvoie PAS les distributions détaillées, juste la courbe.
    """
    historique = []
    
    # Mapping des données
    map_historique = {
        0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    
    # On boucle de J0 jusqu'à la journée choisie
    for j in range(int(journee_max) + 1):

        update_simulation_context(j)

        # 1. On charge l'état à l'époque (J0 si j=0)
        etat = map_historique.get(j, etat_zero)
        
        # 2. On simule la fin de saison depuis ce point
        distrib = distribution_position_par_club(
            N=n_simulations, 
            données=etat, 
            debut=j + 1, 
            fin=8
        )
        
        # 3. Récupération des stats (Top 8 / Qualif)
        stats = distrib.get(club, {})
        p_top8 = sum(stats.get(r, 0) for r in range(1, 9))
        p_qualif = sum(stats.get(r, 0) for r in range(1, 25))
        
        historique.append({
            "journee": f"J{j}",
            "top8": round(p_top8 * 100, 1),
            "qualif": round(p_qualif * 100, 1)
        })
        
    return historique