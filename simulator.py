import pandas as pd
import math
import random as rd
import copy
import requests
import io               
from datetime import datetime
from pathlib import Path

from données import clubs_en_ldc, calendrier_ldc, calendrier, données_J1, données_J2, données_J3, données_J4, données_J5, données_J6
# Import du module de données offline
try:
    import offline_data_v2 as offline_data
    offline_data.charger_toutes_les_donnees()
    OFFLINE_DISPONIBLE = offline_data.donnees_disponibles()
    print(f"✅ Mode OFFLINE V2 activé" if OFFLINE_DISPONIBLE else "⚠️ Mode LIVE")
except ImportError:
    OFFLINE_DISPONIBLE = False
    print("⚠️ Mode LIVE (offline_data_v2 non trouvé)")

base_dir = Path(__file__).parent
elo_rating = base_dir / "Elo_rating_pré_ldc.csv"
elo = pd.read_csv(elo_rating)

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

CACHE_ELO = {}
CURRENT_ELO_DICT = {} 

# On initialise CURRENT_ELO_DICT avec les valeurs statiques (CSV) au démarrage
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
        
        for my_club in clubs_en_ldc:
            if my_club in raw_elos:
                mapped_elos[my_club] = raw_elos[my_club]
            else:
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

    date_cible_str = calendrier_ldc.get(journee_depart + 1)

    if date_cible_str:
        target_date = datetime.strptime(date_cible_str, "%Y-%m-%d")
        today = datetime.now()
        
        # Si la date cible (J6) est dans le futur par rapport à aujourd'hui,
        # cela signifie qu'on est en avance sur le calendrier réel -> On prend le Live.
        # Sinon, si la date est passée, on prend l'historique de cette date précise.
        if target_date > today:
             elos = fetch_elo_from_api(None)
        else:
             elos = fetch_elo_from_api(date_cible_str)
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
    return CURRENT_ELO_DICT.get(club, 1500)

def win_expectation(club1, club2):
    e1 = elo_of_dynamic(club1)
    e2 = elo_of_dynamic(club2)
    return 1/(1+10**((e2-e1-100)/400))

def update_simulation_context(journee_depart):
    """
    Met à jour les ELOs ET recalcule les probas de Poisson.
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
    else:
        print("⚠️ Pas de mise à jour ELO (conservation des valeurs précédentes)")

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

# La boucle suivante retourne des scores moyens et permet en même temps de remplir le dictionnaire probas_par_match de probas fréquemment utiles
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
    return d

def classement_club(club,classement):
    x = classement[0] ; i = 1
    while x!=club and i<len(classement):
        x = classement[i]
        i += 1
    assert(x == club)
    return i

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

# =========================== Affichage Web ==================================================
# =============================================================================

def get_web_seuils(nb_simulations=1000, journee_depart=0, journee_fin=8):
    """
    Calcule la distribution des points du 8ème et du 24ème.
    Utilise les données OFFLINE si disponibles pour la combinaison (start, end).
    """
    try:
        j_dep = int(journee_depart)
        j_fin = int(journee_fin)
    except:
        j_dep = 0
        j_fin = 8

    # MODE OFFLINE
    if OFFLINE_DISPONIBLE and offline_data.combinaison_disponible(j_dep, j_fin):
        distrib_pos = offline_data.get_distribution_par_position(j_dep, j_fin)
        
        if distrib_pos:
            stats_8 = {int(k): v for k, v in distrib_pos.get("8", distrib_pos.get(8, {})).items()}
            stats_9 = {int(k): v for k, v in distrib_pos.get("9", distrib_pos.get(9, {})).items()}
            stats_24 = {int(k): v for k, v in distrib_pos.get("24", distrib_pos.get(24, {})).items()}
            stats_25 = {int(k): v for k, v in distrib_pos.get("25", distrib_pos.get(25, {})).items()}

            def clean_dict(d):
                return {k: v for k, v in d.items() if v > 0.005}

            return {
                "journee_utilisee": j_dep,
                "journee_fin": j_fin,
                "mode": "OFFLINE",
                "seuil_top8": clean_dict(stats_8),
                "seuil_9eme": clean_dict(stats_9),
                "seuil_barrage": clean_dict(stats_24),
                "seuil_25eme": clean_dict(stats_25)
            }

    # MODE LIVE
    update_simulation_context(j_dep)
    
    map_historique = {
        0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    etat = map_historique.get(j_dep, etat_zero)
    debut_simu = j_dep + 1
    
    distrib_pos = distribution_par_position(N=nb_simulations, données=etat, debut=debut_simu, fin=j_fin)
    
    stats_8 = distrib_pos.get(8, {})
    stats_9 = distrib_pos.get(9, {})
    stats_24 = distrib_pos.get(24, {})
    stats_25 = distrib_pos.get(25, {})

    def clean_dict(d):
        return {k: v for k, v in d.items() if v > 0.005}

    return {
        "journee_utilisee": j_dep,
        "journee_fin": j_fin,
        "mode": "LIVE",
        "seuil_top8": clean_dict(stats_8),
        "seuil_9eme": clean_dict(stats_9),
        "seuil_barrage": clean_dict(stats_24),
        "seuil_25eme": clean_dict(stats_25)
    }

def get_web_simulation(club_cible, nb_simulations=1000, journee_depart=0, journee_fin=8):
    """
    Simule les infos pour une équipe cible
    Utilise les données OFFLINE si disponibles pour la combinaison (start, end).
    """
    if club_cible not in clubs_en_ldc:
        return {"error": f"Le club '{club_cible}' n'est pas dans la liste."}

    try:
        j_dep = int(journee_depart)
        j_fin = int(journee_fin)
    except:
        j_dep = 0
        j_fin = 8

    # MODE OFFLINE
    if OFFLINE_DISPONIBLE and offline_data.combinaison_disponible(j_dep, j_fin):
        distrib_points = offline_data.get_distribution_points(j_dep, j_fin)
        distrib_positions = offline_data.get_distribution_positions(j_dep, j_fin)
        
        if distrib_points and distrib_positions:
            stats_points = distrib_points.get(club_cible, {})
            stats_points = {int(k): v for k, v in stats_points.items()}
            
            stats_rank = distrib_positions.get(club_cible, {})
            stats_rank = {int(k): v for k, v in stats_rank.items()}
            
            p_top8 = sum(stats_rank.get(r, 0) for r in range(1, 9))
            p_qualif = sum(stats_rank.get(r, 0) for r in range(1, 25))
            p_barrage = p_qualif - p_top8
            p_elimine = 1 - p_qualif
            
            pts_moyen = sum(pt * prob for pt, prob in stats_points.items())
            
            clean_points = {k: v for k, v in stats_points.items() if v > 0.001}
            clean_ranks = {k: v for k, v in stats_rank.items() if v > 0.001}
            
            return {
                "club": club_cible,
                "day_used": j_dep,
                "day_end": j_fin,
                "mode": "OFFLINE",
                "points_moyens": round(pts_moyen, 2),
                "proba_top_8": round(min(p_top8, 1.0) * 100, 1),
                "proba_barrage": round(min(p_barrage, 1.0) * 100, 1),
                "proba_elimine": round(max(p_elimine, 0.0) * 100, 1),
                "distribution_points": clean_points,
                "distribution_rangs": clean_ranks
            }

    # MODE LIVE
    update_simulation_context(j_dep)
    
    map_historique = {
        0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    etat_actuel = map_historique.get(j_dep, etat_zero)
    debut_simulation = j_dep + 1
    
    distrib_points = distribution_points_par_club(N=nb_simulations, données=etat_actuel, debut=debut_simulation, fin=j_fin)
    distrib_rank = distribution_position_par_club(N=nb_simulations, données=etat_actuel, debut=debut_simulation, fin=j_fin)
    
    stats_points = distrib_points[club_cible]
    stats_rank = distrib_rank[club_cible]
    
    p_top8 = proba_top_8(club_cible, distrib_rank)
    p_qualif = proba_qualification(club_cible, distrib_rank)
    p_barrage = p_qualif - p_top8
    p_elimine = 1 - p_qualif
    
    pts_moyen = sum(pt * prob for pt, prob in stats_points.items())
    
    clean_points = {k: v for k, v in stats_points.items() if v > 0.001}
    clean_ranks = {k: v for k, v in stats_rank.items() if v > 0.001}

    return {
        "club": club_cible,
        "day_used": j_dep,
        "day_end": j_fin,
        "mode": "LIVE",
        "points_moyens": round(pts_moyen, 2),
        "proba_top_8": round(min(p_top8, 1.0) * 100, 1),
        "proba_barrage": round(min(max(p_barrage, 0), 1.0) * 100, 1),
        "proba_elimine": round(min(max(p_elimine, 0), 1.0) * 100, 1),
        "distribution_points": clean_points,
        "distribution_rangs": clean_ranks
    }


def get_match_prediction(home_team, away_team):
    """
    Simule un match spécifique et renvoie le score moyen (prédiction)
    """
    update_simulation_context(8)

    # Vérification des équipes
    if home_team not in clubs_en_ldc or away_team not in clubs_en_ldc:
        return {"error": "Une des équipes n'est pas reconnue."}
    
    if home_team == away_team:
        return {"error": "Une équipe ne peut pas jouer contre elle-même !"}

    avg_score = score_moyen(home_team, away_team, N=2000)
    
    # On calcule aussi les probabilités de victoire (Win/Draw/Loss)
    # On fait 2000 simulations rapides pour avoir les %
    total = 2000
    wins_h, draws, wins_a = 0, 0, 0
    for _ in range(total):
        s = retourne_score(home_team, away_team)
        if s[0] > s[1]: wins_h += 1
        elif s[0] == s[1]: draws += 1
        else: wins_a += 1

    return {
        "home_team": home_team,
        "away_team": away_team,
        "score_avg_home": avg_score[0],
        "score_avg_away": avg_score[1],
        "proba_win": round(wins_h / total * 100, 1),
        "proba_draw": round(draws / total * 100, 1),
        "proba_loss": round(wins_a / total * 100, 1)
    }

# 1. Définition d'un état "neutre" (Tout le monde à 0 point)
etat_zero = {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, 
            "nb_victoires_ext": None
    }

# Initialisation de sécurité des variables manquantes
if 'données_J7' not in globals(): données_J7 = etat_zero
if 'données_J8' not in globals(): données_J8 = etat_zero

def get_max_journee_disponible():
    """
    Retourne la dernière journée avec des données réelles (non vides).
    """
    map_donnees = {
        1: données_J1, 2: données_J2, 3: données_J3, 4: données_J4,
        5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    
    max_j = 0
    for j in range(1, 9):
        if map_donnees[j].get('points') is not None:
            max_j = j
    
    return max_j

def get_simulation_flexible(n_simulations=1000, start_day=0, end_day=8):
    """
    Génère le classement.
    """
    try:
        sd = int(start_day)
        ed = int(end_day)
    except:
        sd = 0
        ed = 8

    # MODE OFFLINE - pour N'IMPORTE QUELLE combinaison disponible
    if OFFLINE_DISPONIBLE and offline_data.combinaison_disponible(sd, ed):
        moyennes = offline_data.get_moyennes(sd, ed)
        
        if moyennes:
            ranking_data = []
            
            for club, stats in moyennes.items():
                ranking_data.append({
                    "club": club,
                    "points": round(stats.get("points", 0), 1),
                    "diff": round(stats.get("diff", 0), 1),
                    "buts": round(stats.get("buts", 0), 1),
                    "buts_ext": round(stats.get("buts_ext", 0), 1),
                    "victoires": round(stats.get("victoires", 0), 1),
                    "victoires_ext": round(stats.get("victoires_ext", 0), 1),
                })
            
            ranking_data.sort(key=lambda x: (
                x['points'], x['diff'], x['buts'], 
                x['buts_ext'], x['victoires'], x['victoires_ext']
            ), reverse=True)
            
            for i, row in enumerate(ranking_data):
                row['rank'] = i + 1
                row['mode'] = 'OFFLINE'
            
            return ranking_data

    # MODE LIVE
    update_simulation_context(sd)
    
    if sd == 0:
        etat_initial = {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, "nb_victoires_ext": None
        }
    else:
        map_historique = {
            1: données_J1, 2: données_J2, 3: données_J3, 4: données_J4,
            5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
        }
        etat_initial = map_historique.get(sd, {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, "nb_victoires_ext": None
        })

    total_stats = {
        club: {"points": 0, "diff_buts": 0, "buts": 0, "buts_ext": 0, "nb_victoires": 0, "nb_victoires_ext": 0} 
        for club in clubs_en_ldc
    }

    for _ in range(n_simulations):
        resultats_simu = simulation_ligue(données=etat_initial, debut=sd + 1, fin=ed)
        for club in clubs_en_ldc:
            total_stats[club]["points"] += resultats_simu["points"][club]
            total_stats[club]["diff_buts"] += resultats_simu["diff_buts"][club]
            total_stats[club]["buts"] += resultats_simu["buts"][club]
            total_stats[club]["buts_ext"] += resultats_simu["buts_ext"][club]
            total_stats[club]["nb_victoires"] += resultats_simu["nb_victoires"][club]
            total_stats[club]["nb_victoires_ext"] += resultats_simu["nb_victoires_ext"][club]

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

    ranking_data.sort(key=lambda x: (
        x['points'], x['diff'], x['buts'], x['buts_ext'], x['victoires'], x['victoires_ext']
    ), reverse=True)

    for i, row in enumerate(ranking_data):
        row['rank'] = i + 1
        row['mode'] = 'LIVE'

    return ranking_data


def get_probas_top8_qualif(nb_simulations=1000, journee_depart=0, journee_fin=8):
    """
    Génère les tableaux de probabilités Top 8 et Top 24.
    """
    try:
        jd = int(journee_depart)
        jf = int(journee_fin)
    except:
        jd = 0
        jf = 8

    # MODE OFFLINE
    if OFFLINE_DISPONIBLE and offline_data.combinaison_disponible(jd, jf):
        distrib_positions = offline_data.get_distribution_positions(jd, jf)
        
        if distrib_positions:
            liste_qualif = []
            liste_top8 = []
            
            for club in clubs_en_ldc:
                stats = distrib_positions.get(club, {})
                stats = {int(k): v for k, v in stats.items()}
                
                p_top8 = sum(stats.get(r, 0) for r in range(1, 9))
                p_qualif = sum(stats.get(r, 0) for r in range(1, 25))
                
                liste_qualif.append({"club": club, "proba": round(min(p_qualif, 1.0) * 100, 1)})
                liste_top8.append({"club": club, "proba": round(min(p_top8, 1.0) * 100, 1)})
            
            liste_qualif.sort(key=lambda x: x["proba"], reverse=True)
            liste_top8.sort(key=lambda x: x["proba"], reverse=True)
            
            return {
                "day_used": jd,
                "day_end": jf,
                "mode": "OFFLINE",
                "ranking_qualif": liste_qualif,
                "ranking_top8": liste_top8
            }

    # MODE LIVE
    update_simulation_context(jd)
    
    if jd == 0:
        etat_initial = {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, "nb_victoires_ext": None
        }
    else:
        map_historique = {
            1: données_J1, 2: données_J2, 3: données_J3, 4: données_J4,
            5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
        }
        etat_initial = map_historique.get(jd, {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, "nb_victoires_ext": None
        })

    debut_simu = jd + 1
    distrib_clubs = distribution_position_par_club(N=nb_simulations, données=etat_initial, debut=debut_simu, fin=jf)
    
    liste_qualif = []
    liste_top8 = []
    
    for club in clubs_en_ldc:
        p_qualif = proba_qualification(club, distrib_clubs)
        p_top8 = proba_top_8(club, distrib_clubs)
        
        liste_qualif.append({"club": club, "proba": round(p_qualif * 100, 1)})
        liste_top8.append({"club": club, "proba": round(p_top8 * 100, 1)})
    
    liste_qualif.sort(key=lambda x: x["proba"], reverse=True)
    liste_top8.sort(key=lambda x: x["proba"], reverse=True)
    
    return {
        "day_used": jd,
        "day_end": jf,
        "mode": "LIVE",
        "ranking_qualif": liste_qualif,
        "ranking_top8": liste_top8
    }

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

def get_scenario_analysis(club_cible, journee_cible, resultat_fixe, journee_depart=6, n_simulations=500):
    """
    Simule la différence avant/après un résultat fixé.
    """
    try:
        jd = int(journee_depart)
        jc = int(journee_cible)
    except:
        jd = 6
        jc = 7

    # MODE OFFLINE
    if OFFLINE_DISPONIBLE and offline_data.combinaison_disponible(jd, 8):
        # Distribution AVANT (simulation libre)
        distrib_avant = offline_data.get_distribution_positions(jd, 8)
        # Distribution APRÈS (scénario fixé)
        distrib_apres = offline_data.get_scenario_distribution(jd, 8, jc, club_cible, resultat_fixe)
        
        if distrib_avant and distrib_apres:
            # Stats AVANT
            stats_avant = distrib_avant.get(club_cible, {})
            stats_avant = {int(k): v for k, v in stats_avant.items()}
            top8_avant = sum(stats_avant.get(r, 0) for r in range(1, 9))
            qualif_avant = sum(stats_avant.get(r, 0) for r in range(1, 25))
            
            # Stats APRÈS
            stats_apres = distrib_apres.get(club_cible, {})
            stats_apres = {int(k): v for k, v in stats_apres.items()}
            top8_apres = sum(stats_apres.get(r, 0) for r in range(1, 9))
            qualif_apres = sum(stats_apres.get(r, 0) for r in range(1, 25))
            
            return {
                "club": club_cible,
                "scenario": resultat_fixe,
                "journee": jc,
                "mode": "OFFLINE",
                "avant": {
                    "top8": round(min(top8_avant, 1.0) * 100, 1),
                    "qualif": round(min(qualif_avant, 1.0) * 100, 1)
                },
                "apres": {
                    "top8": round(min(top8_apres, 1.0) * 100, 1),
                    "qualif": round(min(qualif_apres, 1.0) * 100, 1)
                },
                "delta": {
                    "top8": round((top8_apres - top8_avant) * 100, 1),
                    "qualif": round((qualif_apres - qualif_avant) * 100, 1)
                }
            }

    # MODE LIVE
    update_simulation_context(jd)
    
    map_historique = {
        0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    etat_initial = map_historique.get(jd, etat_zero)
    debut_simu = jd + 1
    if debut_simu > jc:
        debut_simu = jc

    # AVANT
    distrib_avant = distribution_position_par_club(N=n_simulations, données=etat_initial, debut=debut_simu, fin=8)
    stats_avant = distrib_avant.get(club_cible, {})
    top8_avant = sum(stats_avant.get(r, 0) for r in range(1, 9))
    qualif_avant = sum(stats_avant.get(r, 0) for r in range(1, 25))

    # APRÈS
    distrib_apres = distribution_position_par_club_match_fixe(
        N=n_simulations, club_fixed=club_cible, journee=jc, result_fixed=resultat_fixe,
        données=etat_initial, debut=debut_simu, fin=8
    )
    stats_apres = distrib_apres.get(club_cible, {})
    top8_apres = sum(stats_apres.get(r, 0) for r in range(1, 9))
    qualif_apres = sum(stats_apres.get(r, 0) for r in range(1, 25))

    return {
        "club": club_cible,
        "scenario": resultat_fixe,
        "journee": jc,
        "mode": "LIVE",
        "avant": {
            "top8": round(min(top8_avant, 1.0) * 100, 1),
            "qualif": round(min(qualif_avant, 1.0) * 100, 1)
        },
        "apres": {
            "top8": round(min(top8_apres, 1.0) * 100, 1),
            "qualif": round(min(qualif_apres, 1.0) * 100, 1)
        },
        "delta": {
            "top8": round((top8_apres - top8_avant) * 100, 1),
            "qualif": round((qualif_apres - qualif_avant) * 100, 1)
        }
    }
def get_web_hypometre(club_cible, nb_simulations=10000, journee_depart=6):
    try: jd = int(journee_depart)
    except: jd = 0

    if club_cible not in clubs_en_ldc:
        return {"error": f"Club {club_cible} introuvable"}
    
    resultats_impact = []
    
    # Contexte
    update_simulation_context(jd)
    map_historique = {0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
                      4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8}
    etat_actuel = map_historique.get(jd, données_J6)
    debut_simu = jd + 1

    # Boucle sur les journées
    for j_test in range(jd + 1, 9):
        matchs_a_tester = calendrier.get(f"Journée {j_test}", [])
        if not matchs_a_tester: matchs_a_tester = calendrier.get(j_test, [])
        if not matchs_a_tester: continue

        for (dom, ext) in matchs_a_tester:
            # Variables pour stocker les probas brutes
            p_qualif_V = p_qualif_D = p_top8_V = p_top8_D = None
            data_found = False

            # TENTATIVE OFFLINE
            if OFFLINE_DISPONIBLE and offline_data.combinaison_disponible(jd, 8):
                try:
                    distrib_dom_V = offline_data.get_scenario_distribution(jd, 8, j_test, dom, 'V')
                    distrib_dom_D = offline_data.get_scenario_distribution(jd, 8, j_test, dom, 'D')
                    
                    if distrib_dom_V and distrib_dom_D:
                        stats_A = {int(k): v for k, v in distrib_dom_V.get(club_cible, {}).items()}
                        p_qualif_V = sum(stats_A.get(r, 0) for r in range(1, 25))
                        p_top8_V = sum(stats_A.get(r, 0) for r in range(1, 9))
                        
                        stats_B = {int(k): v for k, v in distrib_dom_D.get(club_cible, {}).items()}
                        p_qualif_D = sum(stats_B.get(r, 0) for r in range(1, 25))
                        p_top8_D = sum(stats_B.get(r, 0) for r in range(1, 9))
                        data_found = True
                except:
                    pass

            # TENTATIVE LIVE
            if not data_found:
                p1, p2, _ = importance_pour(club_cible, (dom, ext), j_test, données=etat_actuel, debut=debut_simu, N=nb_simulations)
                # p1 = Victoire Dom, p2 = Défaite Dom
                p_qualif_V = p1[23]
                p_qualif_D = p2[23]
                p_top8_V = p1[7]
                p_top8_D = p2[7]

            # CALCUL ET STOCKAGE (UNE SEULE FOIS) 
            delta_qualif = (p_qualif_V - p_qualif_D) * 100
            delta_top8 = (p_top8_V - p_top8_D) * 100
            score_total = delta_qualif + delta_top8
            
            is_own = (dom == club_cible or ext == club_cible)
            
            if abs(score_total) > 0.0 or is_own:
                resultats_impact.append({
                    "journee": j_test,
                    "match": f"{dom} vs {ext}",
                    "dom": dom, "ext": ext,
                    "score": round(abs(score_total), 1),
                    "score_raw": round(score_total, 1),
                    "score_qualif": round(delta_qualif, 1),
                    "score_top8": round(delta_top8, 1),
                    "is_my_match": is_own
                })

    resultats_impact.sort(key=lambda x: (x['is_my_match'], x['score']), reverse=True)
    return {"club": club_cible, "journee": jd, "mode": "MIXTE", "liste": resultats_impact}

def get_web_hypometre_avant_apres(club_cible, nb_simulations=200, journee_depart=6):
    """
    Analyse les enjeux sur TOUTES les journées restantes (J+1 à J8).
    Trie par importance globale.
    """
    try: jd = int(journee_depart)
    except: jd = 0

    if club_cible not in clubs_en_ldc:
        return {"error": f"Club {club_cible} introuvable"}
    
    resultats_impact = []
    
    # On prépare le contexte une seule fois pour le mode LIVE
    update_simulation_context(jd)
    map_historique = {0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8}
    etat_actuel = map_historique.get(jd, données_J6)
    debut_simu = jd + 1

    # BOUCLE SUR TOUTES LES JOURNÉES FUTURES
    for j_test in range(jd + 1, 9):
        
        matchs_a_tester = calendrier.get(f"Journée {j_test}", [])
        if not matchs_a_tester: matchs_a_tester = calendrier.get(j_test, [])
        if not matchs_a_tester: continue

        # MODE OFFLINE
        if OFFLINE_DISPONIBLE and offline_data.combinaison_disponible(jd, 8):
            try:
                # Test d'accès pour voir si ça plante pas
                _ = offline_data.get_scenario_distribution(jd, 8, j_test, matchs_a_tester[0][0], 'V')
                
                for (dom, ext) in matchs_a_tester:
                    distrib_dom_V = offline_data.get_scenario_distribution(jd, 8, j_test, dom, 'V')
                    distrib_dom_D = offline_data.get_scenario_distribution(jd, 8, j_test, dom, 'D')
                    
                    if distrib_dom_V and distrib_dom_D:
                        stats_A = {int(k): v for k, v in distrib_dom_V.get(club_cible, {}).items()}
                        p1_qualif = sum(stats_A.get(r, 0) for r in range(1, 25))
                        p1_top8 = sum(stats_A.get(r, 0) for r in range(1, 9))
                        
                        stats_B = {int(k): v for k, v in distrib_dom_D.get(club_cible, {}).items()}
                        p2_qualif = sum(stats_B.get(r, 0) for r in range(1, 25))
                        p2_top8 = sum(stats_B.get(r, 0) for r in range(1, 9))
                        
                        delta_qualif = (p1_qualif - p2_qualif) * 100
                        delta_top8 = (p1_top8 - p2_top8) * 100
                        enjeu = delta_qualif + delta_top8
                        
                        is_own = (dom == club_cible or ext == club_cible)
                        
                        if abs(enjeu) > 0.0 or is_own:
                            resultats_impact.append({
                                "journee": j_test, # Ajout du numéro de journée
                                "match": f"{dom} vs {ext}",
                                "dom": dom, "ext": ext,
                                "score": round(abs(enjeu), 1),
                                "score_raw": round(enjeu, 1),
                                "score_qualif": round(delta_qualif, 1),
                                "score_top8": round(delta_top8, 1),
                                "is_my_match": is_own
                            })
                continue # Si Offline a marché pour cette journée, on passe à la suivante
            except:
                pass # Si pas de données offline pour J_test, on tombe en mode LIVE

        # MODE LIVE
        for (dom, ext) in matchs_a_tester:            
            p1, p2, _ = importance_pour(club_cible, (dom, ext), j_test, données=etat_actuel, debut=debut_simu, N=nb_simulations)
            
            delta_qualif = (p1[23] - p2[23]) * 100
            delta_top8 = (p1[7] - p2[7]) * 100
            score_total = (p1[23] - p2[23] + p1[7] - p2[7]) * 100
            
            is_own = (dom == club_cible or ext == club_cible)
            
            if abs(score_total) > 0.0 or is_own:
                resultats_impact.append({
                    "journee": j_test,
                    "match": f"{dom} vs {ext}",
                    "dom": dom, "ext": ext,
                    "score": round(abs(score_total), 1),
                    "score_raw": round(score_total, 1),
                    "score_qualif": round(delta_qualif, 1),
                    "score_top8": round(delta_top8, 1),
                    "is_my_match": is_own
                })

    # Tri global : D'abord MON match (peu importe la journée), puis les plus gros scores
    resultats_impact.sort(key=lambda x: (x['is_my_match'], x['score']), reverse=True)
    
    return {"club": club_cible, "journee": jd, "mode": "MIXTE", "liste": resultats_impact}

def get_web_hypometre_avant(club_cible, nb_simulations=300, journee_depart=6):
    """
    Analyse quels matchs de TOUTES les journées restantes (J+1 à J8) impactent le plus la qualification ET le Top 8.
    Renvoie les deux scores distincts pour affichage, mais trie par la somme des deux.
    """
    try:
        jd = int(journee_depart)
    except:
        jd = 0

    if club_cible not in clubs_en_ldc:
        return {"error": f"Club {club_cible} introuvable"}
    
    journee_suivante = jd + 1
    
    matchs_a_tester = calendrier.get(f"Journée {journee_suivante}", [])
    if not matchs_a_tester:
        matchs_a_tester = calendrier.get(journee_suivante, [])
    if not matchs_a_tester:
        return {"error": f"Pas de matchs trouvés pour J{journee_suivante}"}

    resultats_impact = []

    # Fonction interne pour calculer les deltas et formater le résultat
    def calculer_impact(match, dom, ext, etat_actuel=None, mode="LIVE"):
        delta_qualif = 0
        delta_top8 = 0
        
        if mode == "OFFLINE":
             # MONDE A : Domicile gagne
            distrib_dom_V = offline_data.get_scenario_distribution(jd, 8, journee_suivante, dom, 'V')
            # MONDE B : Extérieur gagne
            distrib_dom_D = offline_data.get_scenario_distribution(jd, 8, journee_suivante, dom, 'D')
            
            if distrib_dom_V and distrib_dom_D:
                # Stats Monde A
                stats_A = distrib_dom_V.get(club_cible, {})
                stats_A = {int(k): v for k, v in stats_A.items()}
                p_qualif_A = sum(stats_A.get(r, 0) for r in range(1, 25))
                p_top8_A = sum(stats_A.get(r, 0) for r in range(1, 9))
                
                # Stats Monde B
                stats_B = distrib_dom_D.get(club_cible, {})
                stats_B = {int(k): v for k, v in stats_B.items()}
                p_qualif_B = sum(stats_B.get(r, 0) for r in range(1, 25))
                p_top8_B = sum(stats_B.get(r, 0) for r in range(1, 9))
                
                delta_qualif = abs(p_qualif_A - p_qualif_B) * 100
                delta_top8 = abs(p_top8_A - p_top8_B) * 100

        else: # LIVE
            p1, p2, _ = importance_pour(club_cible, (dom, ext), journee_suivante, données=etat, debut=jd + 1, N=nb_simulations)
        
            delta_qualif = (p1[23] - p2[23]) * 100
            delta_top8 = (p1[7] - p2[7]) * 100
            
        score_total = delta_qualif + delta_top8
        is_own = (dom == club_cible or ext == club_cible)
            
        if abs(score_total) > 0.0 or is_own:
            resultats_impact.append({
                "match": f"{dom} vs {ext}",
                "dom": dom, "ext": ext,
                "score": round(abs(score_total), 1), # Valeur absolue pour le tri visuel
                "score_raw": round(score_total, 1),  # Vraie valeur (positive ou négative)
                "score_qualif": round(delta_qualif, 1),
                "score_top8": round(delta_top8, 1),
                "is_my_match": is_own
            })
        return None

    if OFFLINE_DISPONIBLE and hasattr(offline_data, 'combinaison_disponible') and offline_data.combinaison_disponible(jd, 8):
        mode = "OFFLINE"
        etat = None
    else:
        mode = "LIVE"
        update_simulation_context(jd)
        map_historique = {
            0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
            4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
        }
        etat = map_historique.get(jd, données_J6)
    
    for (dom, ext) in matchs_a_tester:
        res = calculer_impact(f"{dom} vs {ext}", dom, ext, etat_actuel=etat, mode=mode)
        if res:
            resultats_impact.append(res)
    
    resultats_impact.sort(key=lambda x: (x['is_my_match'], x['score_cumule']), reverse=True)
    
    return {"club": club_cible, "journee": journee_suivante, "mode": mode, "liste": resultats_impact}

def get_web_evolution(club, journee_max=8, n_simulations=300):
    """
    Retourne l'évolution des probabilités d'un club de J0 à journee_max.
    Utilise les données OFFLINE si disponibles.
    """
    if club not in clubs_en_ldc:
        return []
    
    historique = []
    
    for j in range(journee_max + 1):
        # MODE OFFLINE
        if OFFLINE_DISPONIBLE and offline_data.combinaison_disponible(j, 8):
            distrib = offline_data.get_distribution_positions(j, 8)
            if distrib:
                stats = distrib.get(club, {})
                stats = {int(k): v for k, v in stats.items()}
                p_top8 = sum(stats.get(r, 0) for r in range(1, 9))
                p_qualif = sum(stats.get(r, 0) for r in range(1, 25))
                
                historique.append({
                    "journee": f"J{j}",
                    "top8": round(min(p_top8, 1.0) * 100, 1),
                    "qualif": round(min(p_qualif, 1.0) * 100, 1)
                })
                continue
        
        # MODE LIVE
        update_simulation_context(j)
        
        map_historique = {
            0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
            4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
        }
        etat = map_historique.get(j, etat_zero)
        
        distrib = distribution_position_par_club(N=n_simulations, données=etat, debut=j + 1, fin=8)
        stats = distrib.get(club, {})
        p_top8 = sum(stats.get(r, 0) for r in range(1, 9))
        p_qualif = sum(stats.get(r, 0) for r in range(1, 25))
        
        historique.append({
            "journee": f"J{j}",
            "top8": round(p_top8 * 100, 1),
            "qualif": round(p_qualif * 100, 1)
        })
    
    return historique
