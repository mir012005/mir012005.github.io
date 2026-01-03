import pandas as pd
import math
import random as rd
import copy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages as pdf
from IPython.display import FileLink

from elo_manager import get_current_elos

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
    # Retourne la liste des 36 clubs triée
    return clubs_en_ldc

elo_ldc = elo[elo["Club"].isin(clubs_en_ldc)]

def elo_of(club):
    club_data = elo_ldc.loc[elo_ldc["Club"] == club, "Elo"]
    if len(club_data) == 0:
        print(f"Club non trouvé : {club}")
        print(f"Clubs disponibles : {list(elo_ldc['Club'].unique())}")
        return None  # ou une valeur par défaut
    return club_data.values[0]

def win_expectation(club1,club2):
    e1 = elo_of(club1) ; e2 = elo_of(club2)
    assert(type(e1) != str and type(e2) != str)
    return 1/(1+10**((e2-e1-100)/400))

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
    
    for club in d.keys():
        for x in d[club].keys():
            d[club][x] = round(d[club][x],int(math.log10(N)))
    
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
                
    for club in d.keys():
        for x in d[club].keys():
            d[club][x] = round(d[club][x],int(math.log10(N)))
    
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

def get_web_seuils(nb_simulations=1000):
    """
    Calcule la distribution des points du 8ème (Qualif) et du 24ème (Barrage).
    Répond à l'exigence (2) du projet.
    """
    # On utilise l'état actuel (J6 par défaut, ou J7 si vous avez décommenté le code)
    # Assurez-vous que 'données_J6' ou votre variable d'état est bien accessible ici
    etat = données_J6 
    
    # On lance la simu pour récupérer les points par position
    # debut=7 car on suppose qu'on est après la J6
    distrib_pos = distribution_par_position(N=nb_simulations, données=etat, debut=7, fin=8)
    
    # On récupère les stats pour le 8ème (Cut-off Top 8) et le 24ème (Cut-off Barrage)
    stats_8 = distrib_pos[8]
    stats_24 = distrib_pos[24] # Ou 25 selon si vous voulez le premier éliminé ou le dernier qualifié
    
    # Nettoyage pour le JSON (on enlève les probas nulles)
    def clean_dict(d):
        return {k: v for k, v in d.items() if v > 0.005}

    return {
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
def get_web_simulation(club_cible, nb_simulations = 1000, journee_depart=1):
    """
    Fonction optimisée pour le web.
    Accepte maintenant 'journee_depart' pour choisir les données sources.
    """
    if club_cible not in clubs_en_ldc:
        return {"error": f"Le club '{club_cible}' n'est pas dans la liste."}

    # 1. MAPPING DES DONNÉES
    # On crée un dictionnaire pour choisir facilement
    # Assurez-vous que données_J5, J6, J7 sont bien définies plus haut dans votre fichier !
    historique_donnees = {
        5: données_J5,
        6: données_J6,
        7: données_J7
        # Ajoutez 8: données_J8 quand vous l'aurez
    }

    # On récupère les données demandées, ou J6 par défaut si introuvable
    etat_actuel = historique_donnees.get(journee_depart, données_J6)
    
    # Si on part de la J5, on simule la fin (donc on commence à simuler J6)
    # Si on part de la J6, on commence à simuler J7
    debut_simulation = journee_depart + 1

    
    # On passe 'debut=debut_simulation'
    distrib_points = distribution_points_par_club(N=nb_simulations, données=etat_actuel, debut=debut_simulation, fin=8)
    distrib_rank = distribution_position_par_club(N=nb_simulations, données=etat_actuel, debut=debut_simulation, fin=8)

    # 3. Extraction des stats (Le reste ne change pas)
    stats_points = distrib_points[club_cible]
    stats_rank = distrib_rank[club_cible]
    
    # Calcul des probas via les fonctions globales (pour cohérence)
    p_top8 = proba_top_8(club_cible, distrib_rank)
    p_qualif = proba_qualification(club_cible, distrib_rank)
    p_barrage = p_qualif - p_top8
    p_elimine = 1 - p_qualif
    
    pts_moyen = sum(pt * prob for pt, prob in stats_points.items())

    clean_points = {k: v for k, v in stats_points.items() if v > 0.001}
    clean_ranks = {k: v for k, v in stats_rank.items() if v > 0.001}

    return {
        "club": club_cible,
        "day_used": journee_depart, # On renvoie l'info pour confirmer
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


from CODE_A_COPIER import données_J1, données_J2, données_J3, données_J4, données_J5, données_J6
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

def get_web_match_impact(club, journee, nb_simulations=1000, journee_donnees=6):
    # Vérifications
    if club not in clubs_en_ldc:
        return {"error": f"Club '{club}' introuvable"}
    
    if journee < 1 or journee > 8:
        return {"error": "La journée doit être entre 1 et 8"}
    
    # Récupération de l'état initial
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
    
    etat_depart = map_historique.get(journee_donnees, données_J6)
    
    # Récupération de l'adversaire et du lieu
    matchs_journee = calendrier[f"Journée {journee}"]
    adversaire = None
    domicile = None
    
    for (c1, c2) in matchs_journee:
        if c1 == club:
            adversaire = c2
            domicile = True
            break
        elif c2 == club:
            adversaire = c1
            domicile = False
            break
    
    if adversaire is None:
        return {"error": f"{club} ne joue pas en journée {journee}"}
    
    # Calcul des enjeux via la fonction existante
    (gain_v_vs_nul, gain_nul_vs_d), diff_classement_v, diff_classement_nul = enjeux(
        club, 
        journee, 
        données=etat_depart, 
        debut=journee_donnees + 1, 
        N=nb_simulations
    )
    
    # Calcul des probabilités détaillées pour chaque issue
    p_v, p_d, p_nul, _, _ = importance(
        club, 
        journee, 
        données=etat_depart, 
        debut=journee_donnees + 1, 
        N=nb_simulations
    )
    
    return {
        "club": club,
        "journee": journee,
        "adversaire": adversaire,
        "domicile": domicile,
        "impact_victoire": {
            "proba_qualif": round(p_v[23] * 100, 1),  # Position 24 ou mieux
            "proba_top8": round(p_v[7] * 100, 1),     # Position 8 ou mieux
            "classement_moyen": round(sum((i+1) * p_v[i] for i in range(36)), 1)
        },
        "impact_nul": {
            "proba_qualif": round(p_nul[23] * 100, 1),
            "proba_top8": round(p_nul[7] * 100, 1),
            "classement_moyen": round(sum((i+1) * p_nul[i] for i in range(36)), 1)
        },
        "impact_defaite": {
            "proba_qualif": round(p_d[23] * 100, 1),
            "proba_top8": round(p_d[7] * 100, 1),
            "classement_moyen": round(sum((i+1) * p_d[i] for i in range(36)), 1)
        },
        "gain_victoire_vs_nul": {
            "qualif": round(gain_v_vs_nul[0] * 100, 1),
            "top8": round(gain_v_vs_nul[1] * 100, 1),
            "classement": round(diff_classement_v, 1)  # Nombre de places gagnées en moyenne
        },
        "gain_nul_vs_defaite": {
            "qualif": round(gain_nul_vs_d[0] * 100, 1),
            "top8": round(gain_nul_vs_d[1] * 100, 1),
            "classement": round(diff_classement_nul, 1)
        }
    }

def get_web_all_matches_impact(journee, nb_simulations=500, journee_donnees=6):
    """
    Retourne DEUX classements : un pour qualif, un pour top8
    """
    map_historique = {
        1: données_J1, 2: données_J2, 3: données_J3, 4: données_J4,
        5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    
    etat_depart = map_historique.get(journee_donnees, données_J6)
    
    enjeux = simulation_pour_enjeux(
        journee=journee, 
        données=etat_depart, 
        debut=journee_donnees + 1, 
        demi=False, 
        N=nb_simulations
    )
    
    matchs_journee = calendrier[f"Journée {journee}"]
    resultats = []
    
    for match in matchs_journee:
        impact_qualif_total = 0
        impact_top8_total = 0
        impact_qualif_max = 0
        impact_top8_max = 0
        club_max_qualif = None
        club_max_top8 = None
        
        for club in clubs_en_ldc:
            if match in enjeux[club]:
                # Probas pour QUALIFICATION
                proba_qualif_best = max(
                    enjeux[club][match]["domicile"]["proba_qualif"],
                    enjeux[club][match]["nul"]["proba_qualif"],
                    enjeux[club][match]["exterieur"]["proba_qualif"]
                )
                proba_qualif_worst = min(
                    enjeux[club][match]["domicile"]["proba_qualif"],
                    enjeux[club][match]["nul"]["proba_qualif"],
                    enjeux[club][match]["exterieur"]["proba_qualif"]
                )
                
                # Probas pour TOP 8
                proba_top8_best = max(
                    enjeux[club][match]["domicile"]["proba_top8"],
                    enjeux[club][match]["nul"]["proba_top8"],
                    enjeux[club][match]["exterieur"]["proba_top8"]
                )
                proba_top8_worst = min(
                    enjeux[club][match]["domicile"]["proba_top8"],
                    enjeux[club][match]["nul"]["proba_top8"],
                    enjeux[club][match]["exterieur"]["proba_top8"]
                )
                
                impact_qualif_club = proba_qualif_best - proba_qualif_worst
                impact_top8_club = proba_top8_best - proba_top8_worst
                
                impact_qualif_total += impact_qualif_club
                impact_top8_total += impact_top8_club
                
                if impact_qualif_club > impact_qualif_max:
                    impact_qualif_max = impact_qualif_club
                    club_max_qualif = club
                    
                if impact_top8_club > impact_top8_max:
                    impact_top8_max = impact_top8_club
                    club_max_top8 = club
        
        resultats.append({
            "match": f"{match[0]} vs {match[1]}",
            "impact_qualif": {
                "global": round(impact_qualif_total * 100, 1),
                "max": round(impact_qualif_max * 100, 1),
                "club_max": club_max_qualif
            },
            "impact_top8": {
                "global": round(impact_top8_total * 100, 1),
                "max": round(impact_top8_max * 100, 1),
                "club_max": club_max_top8
            }
        })
    
    # On retourne DEUX classements
    return {
        "par_qualif": sorted(resultats, key=lambda x: x['impact_qualif']['global'], reverse=True),
        "par_top8": sorted(resultats, key=lambda x: x['impact_top8']['global'], reverse=True)
    }

def get_web_club_next_match_scenarios(club, nb_simulations=1000, journee_donnees=6):
    # Trouver le prochain match non joué
    journee_prochaine = None
    
    for j in range(journee_donnees + 1, 9):
        matchs_j = calendrier[f"Journée {j}"]
        for (c1, c2) in matchs_j:
            if c1 == club or c2 == club:
                journee_prochaine = j
                break
        if journee_prochaine:
            break
    
    if journee_prochaine is None:
        return {"error": "Plus de matchs à jouer"}
    
    # Récupération des impacts via la fonction principale
    impact = get_web_match_impact(club, journee_prochaine, nb_simulations, journee_donnees)
    
    if "error" in impact:
        return impact
    
    # Calcul du niveau d'enjeu
    ecart_total = (
        abs(impact["impact_victoire"]["proba_qualif"] - impact["impact_defaite"]["proba_qualif"]) +
        abs(impact["impact_victoire"]["proba_top8"] - impact["impact_defaite"]["proba_top8"])
    )
    
    if ecart_total > 30:
        niveau_enjeu = "HIGH"
    elif ecart_total > 15:
        niveau_enjeu = "MEDIUM"
    else:
        niveau_enjeu = "LOW"
    
    # Messages contextuels
    def get_message(proba_qualif, proba_top8):
        if proba_qualif > 95:
            return "Qualification quasi-assurée"
        elif proba_qualif > 80:
            return "Très bien placé pour se qualifier"
        elif proba_qualif > 60:
            return "En bonne position"
        elif proba_qualif > 40:
            return "Match important pour la qualification"
        elif proba_qualif > 20:
            return "Situation délicate"
        else:
            return "Qualification très compromise"
    
    return {
        "club": club,
        "next_match": {
            "journee": journee_prochaine,
            "adversaire": impact["adversaire"],
            "domicile": impact["domicile"]
        },
        "scenarios": {
            "victoire": {
                "proba_qualif": impact["impact_victoire"]["proba_qualif"],
                "proba_top8": impact["impact_victoire"]["proba_top8"],
                "message": get_message(
                    impact["impact_victoire"]["proba_qualif"],
                    impact["impact_victoire"]["proba_top8"]
                )
            },
            "nul": {
                "proba_qualif": impact["impact_nul"]["proba_qualif"],
                "proba_top8": impact["impact_nul"]["proba_top8"],
                "message": get_message(
                    impact["impact_nul"]["proba_qualif"],
                    impact["impact_nul"]["proba_top8"]
                )
            },
            "defaite": {
                "proba_qualif": impact["impact_defaite"]["proba_qualif"],
                "proba_top8": impact["impact_defaite"]["proba_top8"],
                "message": get_message(
                    impact["impact_defaite"]["proba_qualif"],
                    impact["impact_defaite"]["proba_top8"]
                )
            }
        },
        "enjeu": niveau_enjeu,
        "gain_victoire": {
            "qualif": impact["gain_victoire_vs_nul"]["qualif"],
            "top8": impact["gain_victoire_vs_nul"]["top8"]
        }
    }

def get_web_importance(journee_cible, journee_depart=6, n_simulations=300):
    """
    Wrapper pour l'onglet 'Importance'. Utilise la fonction 'enjeux'.
    """
    map_historique = {0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
                      4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8}
    etat_initial = map_historique.get(journee_depart, etat_zero)
    debut_simu = journee_depart + 1

    if journee_cible < debut_simu: return {"error": "La journée cible est passée"}
    
    matchs = calendrier.get(f"Journée {journee_cible}", [])
    resultats = []

    print(f"Calcul Importance J{journee_cible} (Base J{journee_depart})...")

    for dom, ext in matchs:
        try:
            # On appelle VOTRE fonction enjeux avec un N réduit pour le web
            # res = ((gain_qualif, gain_top8), diff_class_v, diff_class_n)
            res_dom = enjeux(dom, journee_cible, données=etat_initial, debut=debut_simu, N=n_simulations)
            res_ext = enjeux(ext, journee_cible, données=etat_initial, debut=debut_simu, N=n_simulations)

            # Score Hype = Somme des impacts absolus sur la qualif et le top 8
            # res_dom[0][0] est le gain de qualif, res_dom[0][1] est le gain de top 8
            impact_dom = abs(res_dom[0][0]) + abs(res_dom[0][1])
            impact_ext = abs(res_ext[0][0]) + abs(res_ext[0][1])
            
            total_score = (impact_dom + impact_ext) * 100

            resultats.append({
                "match": f"{dom} - {ext}", "dom": dom, "ext": ext,
                "score": round(total_score, 1),
                "details": {"dom_val": round(impact_dom * 100, 1), "ext_val": round(impact_ext * 100, 1)}
            })
        except Exception as e:
            print(f"Erreur {dom}-{ext}: {e}")

    resultats.sort(key=lambda x: x['score'], reverse=True)
    return resultats

def get_scenario_analysis(club_cible, journee_cible, resultat_fixe, journee_depart=6, n_simulations=500):
    """
    Wrapper pour l'onglet 'Scénario'. Utilise 'distribution_position_par_club_match_fixe'.
    """
    map_historique = {0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
                      4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8}
    etat_initial = map_historique.get(journee_depart, etat_zero)
    debut_simu = journee_depart + 1

    if debut_simu > journee_cible: debut_simu = journee_cible

    # Appel de VOTRE fonction de distribution
    distrib = distribution_position_par_club_match_fixe(
        N=n_simulations, club_fixed=club_cible, journee=journee_cible,
        result_fixed=resultat_fixe, données=etat_initial, debut=debut_simu, fin=8
    )

    stats = distrib.get(club_cible, {})
    
    # Agrégation des pourcentages
    p_top8 = sum(stats.get(r, 0) for r in range(1, 9))
    p_qualif = sum(stats.get(r, 0) for r in range(1, 25))
    p_elim = 1.0 - p_qualif

    return {
        "club": club_cible, "scenario": resultat_fixe, "journee": journee_cible,
        "proba_top8": round(p_top8 * 100, 1),
        "proba_qualif": round(p_qualif * 100, 1),
        "proba_elim": round(p_elim * 100, 1)
    }