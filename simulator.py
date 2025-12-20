import pandas as pd
import math
import random as rd
import copy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages as pdf
from IPython.display import FileLink

# On récupère d'abord les données concernant les clubs participant à la ligue des champions, à la veille du début de la compétition.

from pathlib import Path


base_dir = Path(__file__).parent
elo_rating = base_dir / "Elo_rating_pré_ldc.csv"

#elo_rating = elo_rating = "C:\\Users\\dell\\Downloads\\Elo_rating_pré_ldc.csv"

elo = pd.read_csv(elo_rating)

#clubs_en_ldc = sorted(['Man City', 'Real Madrid', 'Inter', 'Arsenal', 'Leverkusen', 'Bayern', 'Barcelona', 'Liverpool', 'Paris SG', 'Dortmund', 'Atalanta', 'RB Leipzig', 'Atletico', 'Sporting', 'Juventus', 'Milan', 'Stuttgart', 'PSV', 'Girona', 'Aston Villa', 'Monaco', 'Bologna', 'Benfica', 'Lille', 'Feyenoord', 'Sparta Praha', 'Brugge', 'Brest', 'Salzburg', 'Celtic', 'Sturm Graz', 'Shakhtar', 'Dinamo Zagreb', 'Crvena Zvezda', 'Young Boys', 'Slovan Bratislava'])
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

elo_pre_ldc = elo[elo["Club"].isin(clubs_en_ldc)]

#==========19/12/25=============
def get_clubs_list():
    # Retourne la liste des 36 clubs triée
    return clubs_en_ldc
#=================================
"""
elo_J5 = pd.read_csv('C:\\Users\\Oscar\\OneDrive\\Documents\\2A\\Projet_IMI_ldc\\Données\\Classements elo\\Elo J5.csv')
elo_ldc_J5 = elo_J5[elo_J5["Club"].isin(clubs_en_ldc)]

elo_J6 = pd.read_csv('C:\\Users\\Oscar\\OneDrive\\Documents\\2A\\Projet_IMI_ldc\\Données\\Classements elo\\Elo J6.csv')
elo_ldc_J6 = elo_J6[elo_J6["Club"].isin(clubs_en_ldc)]

elo_J7 = pd.read_csv('C:\\Users\\Oscar\\OneDrive\\Documents\\2A\\Projet_IMI_ldc\\Données\\Classements elo\\Elo J7.csv')
elo_ldc_J7 = elo_J7[elo_J7["Club"].isin(clubs_en_ldc)]
"""
# Choix de l'elo 
#elo_ldc = elo_ldc_J7
elo_ldc = elo_pre_ldc

def elo_of(club):
    club_data = elo_ldc.loc[elo_ldc["Club"] == club, "Elo"]
    if len(club_data) == 0:
        print(f"Club non trouvé : {club}")
        print(f"Clubs disponibles : {list(elo_ldc['Club'].unique())}")
        return None  # ou une valeur par défaut
    return club_data.values[0]
"""
def elo_of(club):
    # étant donné une chaine de caractère indiquant un club en ldc, retourne son elo
    if club in clubs_en_ldc:
        return (elo_ldc.loc[elo_ldc["Club"] == club, "Elo"]).values[0]
    else:
        return "Ce club n'est pas en ldc"
"""


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

# La boucle suivante retourne des scores moyens et permet en même temps de remplir le dictionnaire probas_par_match de 
# probas fréquemment utiles

calendrier_avant = {
    "Journée 1": [
        ("Juventus", "PSV"),
        ("Young Boys", "Aston Villa"),
        ("Bayern", "Dinamo Zagreb"),
        ("Milan", "Liverpool"),
        ("Real Madrid", "Stuttgart"),
        ("Sporting", "Lille"),
        ("Bologna", "Shakhtar"),
        ("Sparta Praha", "Salzburg"),
        ("Celtic", "Slovan Bratislava"),
        ("Brugge", "Dortmund"),
        ("Man City", "Inter"),
        ("Paris SG", "Girona"),
        ("Crvena Zvezda", "Benfica"),
        ("Feyenoord", "Leverkusen"),
        ("Atalanta", "Arsenal"),
        ("Atletico", "RB Leipzig"),
        ("Brest", "Sturm Graz"),
        ("Monaco", "Barcelona"),
    ],
    "Journée 2": [
        ("Salzburg", "Brest"),
        ("Stuttgart", "Sparta Praha"),
        ("Arsenal", "Paris SG"),
        ("Leverkusen", "Milan"),
        ("Dortmund", "Celtic"),
        ("Barcelona", "Young Boys"),
        ("Inter", "Crvena Zvezda"),
        ("PSV", "Sporting"),
        ("Slovan Bratislava", "Man City"),
        ("Shakhtar", "Atalanta"),
        ("Girona", "Feyenoord"),
        ("Aston Villa", "Bayern"),
        ("Dinamo Zagreb", "Monaco"),
        ("Liverpool", "Bologna"),
        ("Lille", "Real Madrid"),
        ("RB Leipzig", "Juventus"),
        ("Sturm Graz", "Brugge"),
        ("Benfica", "Atletico"),
    ],
    "Journée 3": [
        ("Milan", "Brugge"),
        ("Monaco", "Crvena Zvezda"),
        ("Real Madrid", "Dortmund"),
        ("Sturm Graz", "Sporting"),
        ("Aston Villa", "Bologna"),
        ("Juventus", "Stuttgart"),
        ("Arsenal", "Shakhtar"),
        ("Girona", "Slovan Bratislava"),
        ("Paris SG", "PSV"),
        ("Brest", "Leverkusen"),
        ("Atalanta", "Celtic"),
        ("Man City", "Sparta Praha"),
        ("Atletico", "Lille"),
        ("RB Leipzig", "Liverpool"),
        ("Benfica", "Feyenoord"),
        ("Salzburg", "Dinamo Zagreb"),
        ("Young Boys", "Inter"),
        ("Barcelona", "Bayern"),
    ],
    "Journée 4": [
        ("PSV", "Girona"),
        ("Slovan Bratislava", "Dinamo Zagreb"),
        ("Dortmund", "Sturm Graz"),
        ("Bologna", "Monaco"),
        ("Lille", "Juventus"),
        ("Liverpool", "Leverkusen"),
        ("Real Madrid", "Milan"),
        ("Celtic", "RB Leipzig"),
        ("Sporting", "Man City"),
        ("Brugge", "Aston Villa"),
        ("Shakhtar", "Young Boys"),
        ("Inter", "Arsenal"),
        ("Sparta Praha", "Brest"),
        ("Paris SG", "Atletico"),
        ("Crvena Zvezda", "Barcelona"),
        ("Stuttgart", "Atalanta"),
        ("Feyenoord", "Salzburg"),
        ("Bayern", "Benfica"),
    ],
    "Journée 5": [
        ("Slovan Bratislava", "Milan"),
        ("Sparta Praha", "Atletico"),
        ("Leverkusen", "Salzburg"),
        ("Sporting", "Arsenal"),
        ("Inter", "RB Leipzig"),
        ("Man City", "Feyenoord"),
        ("Young Boys", "Atalanta"),
        ("Barcelona", "Brest"),
        ("Bayern", "Paris SG"),
        ("Crvena Zvezda", "Stuttgart"),
        ("Sturm Graz", "Girona"),
        ("Liverpool", "Real Madrid"),
        ("Dinamo Zagreb", "Dortmund"),
        ("Aston Villa", "Juventus"),
        ("Bologna", "Lille"),
        ("Celtic", "Brugge"),
        ("Monaco", "Benfica"),
        ("PSV", "Shakhtar"),
    ],
    "Journée 6": [
        ("Dinamo Zagreb", "Celtic"),
        ("Girona", "Liverpool"),
        ("RB Leipzig", "Aston Villa"),
        ("Brugge", "Sporting"),
        ("Brest", "PSV"),
        ("Shakhtar", "Bayern"),
        ("Salzburg", "Paris SG"),
        ("Atalanta", "Real Madrid"),
        ("Leverkusen", "Inter"),
        ("Atletico", "Slovan Bratislava"),
        ("Lille", "Sturm Graz"),
        ("Feyenoord", "Sparta Praha"),
        ("Benfica", "Bologna"),
        ("Arsenal", "Monaco"),
        ("Juventus", "Man City"),
        ("Stuttgart", "Young Boys"),
        ("Dortmund", "Barcelona"),
        ("Milan", "Crvena Zvezda"),
    ],
    "Journée 7": [
        ("Atalanta", "Sturm Graz"),
        ("Monaco", "Aston Villa"),
        ("Brugge", "Juventus"),
        ("Atletico", "Leverkusen"),
        ("Liverpool", "Lille"),
        ("Benfica", "Barcelona"),
        ("Bologna", "Dortmund"),
        ("Slovan Bratislava", "Stuttgart"),
        ("Crvena Zvezda", "PSV"),
        ("Shakhtar", "Brest"),
        ("RB Leipzig", "Sporting"),
        ("Milan", "Girona"),
        ("Feyenoord", "Bayern"),
        ("Real Madrid", "Salzburg"),
        ("Arsenal", "Dinamo Zagreb"),
        ("Celtic", "Young Boys"),
        ("Paris SG", "Man City"),
        ("Sparta Praha", "Inter"),
    ],
    "Journée 8": [
        ("Inter", "Monaco"),
        ("PSV", "Liverpool"),
        ("Dinamo Zagreb", "Milan"),
        ("Lille", "Feyenoord"),
        ("Leverkusen", "Sparta Praha"),
        ("Aston Villa", "Celtic"),
        ("Young Boys", "Crvena Zvezda"),
        ("Man City", "Brugge"),
        ("Dortmund", "Shakhtar"),
        ("Sturm Graz", "RB Leipzig"),
        ("Sporting", "Bologna"),
        ("Juventus", "Benfica"),
        ("Stuttgart", "Paris SG"),
        ("Bayern", "Slovan Bratislava"),
        ("Salzburg", "Atletico"),
        ("Brest", "Real Madrid"),
        ("Barcelona", "Atalanta"),
        ("Girona", "Arsenal"),
    ],
}

# Calendrier complet de la phase de ligue UEFA Champions League 2025/26
# Les noms d'équipes ont été modifiés selon la liste fournie par l'utilisateur.

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

distribution_probas_classement = distribution_position_par_club()

# On peut calculer la moyenne et l'écart type de la distribution pour un club donné :


def moyenne_et_ecart_type(club,distribution_proba):
    # calcule la moyenne et l'écart type d'une distribution de probabilité donnée
    distribution = distribution_proba[club]
    m = 0
    for x in distribution.keys():
        m += x*distribution[x]
    v = 0
    for x in distribution.keys():
        v += ((x - m)**2)*distribution[x]
    return round(m,2) , round(v**(1/2),2)

# On peut ensuite vouloir afficher cette distribution pour un club en particulier : 


def afficher_distribution_classement_club(club,distribution_probas,fin=8):
    distribution = distribution_probas[club]
    positions = list(distribution.keys())
    probabilities = list(distribution.values())
    
    # Création du graphique
    plt.figure(figsize=(10, 5.5))
    plt.bar(positions, probabilities, color='skyblue', edgecolor='black')

    moyenne , ecart_type = moyenne_et_ecart_type(club,distribution_probas)
    
    # Ajouter des étiquettes
    plt.xlabel("Positions dans le classement", fontsize=14)
    plt.ylabel("Probabilités", fontsize=14)
    plt.title(f"Distribution de probas sur le classement après la journée {fin} pour {club}", fontsize=16)
    plt.xticks(positions, fontsize=12)
    plt.yticks(fontsize=12)

    # Trouver un emplacement pour le texte (dans une zone avec des barres basses)
    if moyenne > 18:
        direction = 0.20
    else:
        direction = 0.95
    
    # Ajouter la moyenne et l'écart type en annotation
    texte_stats = f"Moyenne: {moyenne:.2f}\nÉcart-type: {ecart_type:.2f}"
    plt.text(
        direction , 0.9, texte_stats,
        transform=plt.gca().transAxes,  # Position relative à l'axe (95% à droite et en haut)
        fontsize=12,
        verticalalignment='top', 
        horizontalalignment='right',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5')
    )
    
    # Afficher le graphique
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

#afficher_distribution_classement_club("Paris SG",distribution_probas_classement)

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

#distribution_probas_points = distribution_points_par_club()

def afficher_distribution_points_club(club,distribution_probas,fin=8):
    distribution = distribution_probas[club]
    positions = list(distribution.keys())
    probabilities = list(distribution.values())
    
    # Création du graphique
    plt.figure(figsize=(9, 5))
    plt.bar(positions, probabilities, color='skyblue', edgecolor='black')
    
    # Ajouter des étiquettes
    plt.xlabel("Nombre de points inscrits", fontsize=14)
    plt.ylabel("Probabilités", fontsize=14)
    plt.title(f"Distribution de probas sur le nombre de points inscrits après la journée {fin} pour {club}", fontsize=16)
    plt.xticks(positions, fontsize=12)
    plt.yticks(fontsize=12)
    
    moyenne , ecart_type = moyenne_et_ecart_type(club,distribution_probas)
    
    # Trouver un emplacement pour le texte (dans une zone avec des barres basses)
    if moyenne > 12:
        direction = 0.20
    else:
        direction = 0.95
    
    # Ajouter la moyenne et l'écart type en annotation
    texte_stats = f"Moyenne: {moyenne:.2f}\nÉcart-type: {ecart_type:.2f}"
    plt.text(
        direction , 0.9, texte_stats,
        transform=plt.gca().transAxes,  # Position relative à l'axe (95% à droite et en haut)
        fontsize=12,
        verticalalignment='top', 
        horizontalalignment='right',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5')
    )

    # Afficher le graphique
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

#afficher_distribution_points_club("Arsenal",distribution_probas_points)

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

#points_par_position = distribution_par_position()

def afficher_distribution_position(pos,distribution_probas,fin=8):
    distribution = distribution_probas[pos]
    positions = [p for p, prob in distribution.items() if prob > 0]
    probabilities = [100*prob for prob in distribution.values() if prob > 0]
    
    # Création du graphique
    plt.figure(figsize=(8, 4.5))
    plt.bar(positions, probabilities, color='skyblue', edgecolor='black')
    
    # Ajouter des étiquettes
    plt.xlabel("Nombre de points", fontsize=14)
    plt.ylabel("Probabilités (%)", fontsize=14)
    plt.title(f"Nombre de points du club en position {pos}", fontsize=16)
    plt.xticks(positions, fontsize=12)
    plt.yticks(fontsize=12)

    moyenne , ecart_type = moyenne_et_ecart_type(pos,distribution_probas)
    
    # Ajouter la moyenne et l'écart type en annotation
    texte_stats = f"Moyenne: {moyenne:.2f}\nÉcart-type: {ecart_type:.2f}"
    plt.text(
        0.95 , 0.9, texte_stats,
        transform=plt.gca().transAxes,  # Position relative à l'axe (95% à droite et en haut)
        fontsize=12,
        verticalalignment='top', 
        horizontalalignment='right',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5')
    )
    
    # Afficher le graphique
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

#afficher_distribution_position(8,points_par_position)
#afficher_distribution_position(24,points_par_position)

def affichage_simplifié_pdf(club,distribution_probas,points=False):
    distribution = distribution_probas[club]
    positions = list(distribution.keys())
    probabilities = list(distribution.values())
    probabilities = [100*probabilities[i] for i in range(len(probabilities))]
    
    # Création du graphique
    plt.figure(figsize=(10, 5))
    plt.bar(positions, probabilities, color='skyblue', edgecolor='black')
    
    # Ajouter des étiquettes
    if points:
        plt.xlabel("Nombre de points inscrits", fontsize=14)
    else:
        plt.xlabel("Classement final", fontsize=14)
    plt.ylabel("Probabilités (%)", fontsize=14)
    plt.title(f"{club}", fontsize=18)
    plt.xticks(positions, fontsize=12)
    plt.yticks(fontsize=12)
    
    moyenne , ecart_type = moyenne_et_ecart_type(club,distribution_probas)
    
    # Trouver un emplacement pour le texte (dans une zone avec des barres basses)
    if points:
        limite = 12
    else:
        limite = 18

    if moyenne > limite:
        direction = 0.26
    else:
        direction = 0.95
    
    # Ajouter la moyenne et l'écart type en annotation
    if points:
        texte_stats = f"Moyenne: {moyenne:.2f}"
    else:
        proba_qualif = round(100*proba_qualification(club,distribution_probas),1)
        proba_top8 = round(100*proba_top_8(club,distribution_probas),1)
        texte_stats = f"Moyenne: {moyenne:.2f}\n Proba de qualif: {proba_qualif:.1f} %\n Proba top 8: {proba_top8:.1f} %"
    plt.text(
        direction , 0.9, texte_stats,
        transform=plt.gca().transAxes,  # Position relative à l'axe (95% à droite et en haut)
        fontsize=12,
        verticalalignment='top', 
        horizontalalignment='right',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5')
    )

    # Afficher le graphique
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    pdf.savefig()
    plt.close()

# On s'intéresse à simuler à partir des résultats jusqu'à la J5

"""
classement_J5 = teams = [
    "Liverpool",
    "Inter",
    "Barcelona",
    "Dortmund",
    "Atalanta",
    "Arsenal",
    "Leverkusen",
    "Aston Villa",
    "Monaco",
    "Brest",
    "Sporting",
    "Lille",
    "Bayern",
    "Benfica",
    "Milan",
    "Atletico",
    "Man City",
    "PSV",
    "Juventus",
    "Celtic",
    "Brugge",
    "Feyenoord",
    "Dinamo Zagreb",
    "Real Madrid",
    "Paris SG",
    "Shakhtar",
    "Stuttgart",
    "Sparta Praha",
    "Sturm Graz",
    "Girona",
    "Crvena Zvezda",
    "Salzburg",
    "Bologna",
    "RB Leipzig",
    "Slovan Bratislava",
    "Young Boys"
]

points_J5 = {
    'Liverpool': 15,
    'Inter': 13,
    'Barcelona': 12,
    'Dortmund': 12,
    'Atalanta': 11,
    'Arsenal': 10,
    'Leverkusen': 10,
    'Aston Villa': 10,
    'Monaco': 10,
    'Brest': 10,
    'Sporting': 10,
    'Lille': 10,
    'Bayern': 9,
    'Benfica': 9,
    'Milan': 9,
    'Atletico': 9,
    'Man City': 8,
    'PSV': 8,
    'Juventus': 8,
    'Celtic': 8,
    'Brugge': 7,
    'Feyenoord': 7,
    'Dinamo Zagreb': 7,
    'Real Madrid': 6,
    'Paris SG': 4,
    'Shakhtar': 4,
    'Stuttgart': 4,
    'Sparta Praha': 4,
    'Sturm Graz': 3,
    'Girona': 3,
    'Crvena Zvezda': 3,
    'Salzburg': 3,
    'Bologna': 1,
    'RB Leipzig': 0,
    'Slovan Bratislava': 0,
    'Young Boys': 0
}

diff_buts_J5 = {
    'Liverpool': 11,
    'Inter': 7,
    'Barcelona': 13,
    'Dortmund': 10,
    'Atalanta': 10,
    'Arsenal': 6,
    'Leverkusen': 6,
    'Aston Villa': 5,
    'Monaco': 5,
    'Brest': 3,
    'Sporting': 3,
    'Lille': 2,
    'Bayern': 5,
    'Benfica': 3,
    'Milan': 2,
    'Atletico': 2,
    'Man City': 6,
    'PSV': 3,
    'Juventus': 2,
    'Celtic': 0,
    'Brugge': -3,
    'Feyenoord': -3,
    'Dinamo Zagreb': -5,
    'Real Madrid': 0,
    'Paris SG': -3,
    'Shakhtar': -4,
    'Stuttgart': -7,
    'Sparta Praha': -9,
    'Sturm Graz': -4,
    'Girona': -5,
    'Crvena Zvezda': -8,
    'Salzburg': -12,
    'Bologna': -6,
    'RB Leipzig': -6,
    'Slovan Bratislava': -14,
    'Young Boys': -15
}

buts_J5 = {

    'Liverpool': 12,
    'Inter': 7,
    'Barcelona': 18,
    'Dortmund': 16,
    'Atalanta': 11,
    'Arsenal': 8,
    'Leverkusen': 11,
    'Aston Villa': 6,
    'Monaco': 12,
    'Brest': 9,
    'Sporting': 10,
    'Lille': 7,
    'Bayern': 12,
    'Benfica': 10,
    'Milan': 10,
    'Atletico': 11,
    'Man City': 13,
    'PSV': 10,
    'Juventus': 7,
    'Celtic': 10,
    'Brugge': 4,
    'Feyenoord': 10,
    'Dinamo Zagreb': 10,
    'Real Madrid': 9,
    'Paris SG': 3,
    'Shakhtar': 4,
    'Stuttgart': 4,
    'Sparta Praha': 5,
    'Sturm Graz': 2,
    'Girona': 4,
    'Crvena Zvezda': 9,
    'Salzburg': 3,
    'Bologna': 1,
    'RB Leipzig': 4,
    'Slovan Bratislava': 4,
    'Young Boys': 2
}
"""
# List ordered by Rank (1st to 36th)
classement_J5 = [
    "Arsenal",
    "Paris SG",
    "Bayern",
    "Inter",
    "Real Madrid",
    "Dortmund",
    "Chelsea",
    "Sporting",
    "Man City",
    "Atalanta",
    "Newcastle",
    "Atletico",
    "Liverpool",
    "Galatasaray",
    "PSV",
    "Tottenham",
    "Leverkusen",
    "Barcelona",
    "Karabakh Agdam",
    "Napoli",
    "Marseille",
    "Juventus",
    "Monaco",
    "Paphos",
    "St Gillis",
    "Brugge",
    "Bilbao",
    "Frankfurt",
    "FC Kobenhavn",
    "Benfica",
    "Slavia Praha",
    "Bodoe Glimt",
    "Olympiakos",
    "Villarreal",
    "Kairat",
    "Ajax"
]

points_J5 = {
    'Arsenal': 15,
    'Paris SG': 12,
    'Bayern': 12,
    'Inter': 12,
    'Real Madrid': 12,
    'Dortmund': 10,
    'Chelsea': 10,
    'Sporting': 10,
    'Man City': 10,
    'Atalanta': 10,
    'Newcastle': 9,
    'Atletico': 9,
    'Liverpool': 9,
    'Galatasaray': 9,
    'PSV': 8,
    'Tottenham': 8,
    'Leverkusen': 8,
    'Barcelona': 7,
    'Karabakh Agdam': 7,
    'Napoli': 7,
    'Marseille': 6,
    'Juventus': 6,
    'Monaco': 6,
    'Paphos': 6,
    'St Gillis': 6,
    'Brugge': 4,
    'Bilbao': 4,
    'Frankfurt': 4,
    'FC Kobenhavn': 4,
    'Benfica': 3,
    'Slavia Praha': 3,
    'Bodoe Glimt': 2,
    'Olympiakos': 2,
    'Villarreal': 1,
    'Kairat': 1,
    'Ajax': 0
}

diff_buts_J5 = {
    'Arsenal': 13,
    'Paris SG': 11,
    'Bayern': 9,
    'Inter': 9,
    'Real Madrid': 7,
    'Dortmund': 6,
    'Chelsea': 6,
    'Sporting': 6,
    'Man City': 5,
    'Atalanta': 1,
    'Newcastle': 7,
    'Atletico': 2,
    'Liverpool': 2,
    'Galatasaray': 1,
    'PSV': 5,
    'Tottenham': 3,
    'Leverkusen': -2,
    'Barcelona': 2,
    'Karabakh Agdam': -1,
    'Napoli': -3,
    'Marseille': 2,
    'Juventus': 0,
    'Monaco': -2,
    'Paphos': -3,
    'St Gillis': -7,
    'Brugge': -5,
    'Bilbao': -5,
    'Frankfurt': -7,
    'FC Kobenhavn': -7,
    'Benfica': -4,
    'Slavia Praha': -6,
    'Bodoe Glimt': -4,
    'Olympiakos': -8,
    'Villarreal': -8,
    'Kairat': -10,
    'Ajax': -15
}

buts_J5 = {
    'Arsenal': 14,
    'Paris SG': 19,
    'Bayern': 15,
    'Inter': 12,
    'Real Madrid': 12,
    'Dortmund': 17,
    'Chelsea': 12,
    'Sporting': 11,
    'Man City': 10,
    'Atalanta': 6,
    'Newcastle': 11,
    'Atletico': 12,
    'Liverpool': 10,
    'Galatasaray': 8,
    'PSV': 13,
    'Tottenham': 10,
    'Leverkusen': 8,
    'Barcelona': 12,
    'Karabakh Agdam': 8,
    'Napoli': 6,
    'Marseille': 8,
    'Juventus': 10,
    'Monaco': 6,
    'Paphos': 4,
    'St Gillis': 5,
    'Brugge': 8,
    'Bilbao': 4,
    'Frankfurt': 7,
    'FC Kobenhavn': 7,
    'Benfica': 4,
    'Slavia Praha': 2,
    'Bodoe Glimt': 7,
    'Olympiakos': 5,
    'Villarreal': 2,
    'Kairat': 4,
    'Ajax': 1
}

buts_ext_J5 = {x : 0 for x in classement_J5}
nb_v_J5 = {x : 0 for x in classement_J5}
nb_v_ext_J5 = {x : 0 for x in classement_J5}

données_J5 = dico_de_données(classement_J5,points_J5,diff_buts_J5,buts_J5,buts_ext_J5,nb_v_J5,nb_v_ext_J5)

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
"""
matchs = [['Girona','Liverpool',[0,1]],['Dinamo Zagreb','Celtic',[0,0]],['Brest','PSV',[1,0]],['Shakhtar','Bayern',[1,5]],
          ['Salzburg','Paris SG',[0,3]],['RB Leipzig','Aston Villa',[2,3]],['Brugge','Sporting',[2,1]],
          ['Leverkusen','Inter',[1,0]],['Atalanta','Real Madrid',[2,3]],['Lille','Sturm Graz',[3,2]],
          ['Atletico','Slovan Bratislava',[3,1]],['Stuttgart','Young Boys',[5,1]],['Juventus','Man City',[2,0]],
          ['Arsenal','Monaco',[3,0]],['Milan','Crvena Zvezda',[2,1]],['Feyenoord','Sparta Praha',[4,2]],
          ['Benfica','Bologna',(0,0)],['Dortmund','Barcelona',(2,3)]]
# Results parsed for the 2025/2026 Season (Matchdays 1-4)
# Format: (Home Team, Away Team, Home Goals, Away Goals)

resultats_J1 = [
    ("Bilbao", "Arsenal", 0, 2),
    ("PSV", "St Gillis", 1, 3),
    ("Real Madrid", "Marseille", 2, 1),
    ("Juventus", "Dortmund", 4, 4),
    ("Tottenham", "Villarreal", 1, 0),
    ("Benfica", "Karabakh Agdam", 2, 3),
    ("Olympiacos", "Paphos", 0, 0),
    ("Slavia Praha", "Bodoe Glimt", 2, 2),
    ("Paris SG", "Atalanta", 4, 0),
    ("Liverpool", "Atletico", 3, 2),
    ("Bayern", "Chelsea", 3, 1),
    ("Ajax", "Inter", 0, 2),
    ("Brugge", "Monaco", 4, 1),
    ("FC Kobenhavn", "Leverkusen", 2, 2),
    ("Newcastle", "Barcelona", 1, 2),
    ("Man City", "Napoli", 2, 0),
    ("Frankfurt", "Galatasaray", 5, 1),
    ("Sporting", "Kairat", 4, 1)
]

resultats_J2 = [
    ("Kairat", "Real Madrid", 0, 5),
    ("Atalanta", "Brugge", 2, 1),
    ("Atletico", "Frankfurt", 5, 1),
    ("Marseille", "Ajax", 4, 0),
    ("Galatasaray", "Liverpool", 1, 0),
    ("Chelsea", "Benfica", 1, 0),
    ("Paphos", "Bayern", 1, 5),
    ("Bodoe Glimt", "Tottenham", 2, 2),
    ("Inter", "Slavia Praha", 3, 0),
    ("St Gillis", "Newcastle", 0, 4),
    ("Karabakh Agdam", "FC Kobenhavn", 2, 0),
    ("Villarreal", "Juventus", 2, 2),
    ("Napoli", "Sporting", 2, 1),
    ("Leverkusen", "PSV", 1, 1),
    ("Arsenal", "Olympiacos", 2, 0),
    ("Barcelona", "Paris SG", 1, 2),
    ("Monaco", "Man City", 2, 2),
    ("Dortmund", "Bilbao", 4, 1)
]

resultats_J3 = [
    ("Kairat", "Paphos", 0, 0),
    ("Barcelona", "Olympiacos", 6, 1),
    ("Arsenal", "Atletico", 4, 0),
    ("Leverkusen", "Paris SG", 2, 7),
    ("Villarreal", "Man City", 0, 2),
    ("PSV", "Napoli", 6, 2),
    ("FC Kobenhavn", "Dortmund", 2, 4),
    ("St Gillis", "Inter", 0, 4),
    ("Newcastle", "Benfica", 3, 0),
    ("Galatasaray", "Bodoe Glimt", 3, 1),
    ("Bilbao", "Karabakh Agdam", 3, 1),
    ("Chelsea", "Ajax", 5, 1),
    ("Atalanta", "Slavia Praha", 0, 0),
    ("Frankfurt", "Liverpool", 1, 5),
    ("Sporting", "Marseille", 2, 1),
    ("Monaco", "Tottenham", 0, 0),
    ("Real Madrid", "Juventus", 1, 0),
    ("Bayern", "Brugge", 4, 0)
]



matchs_J1 = [['Bilbao', 'Arsenal', [0, 2]], ['PSV', 'St Gillis', [1, 3]], ['Real Madrid', 'Marseille', [2, 1]], 
             ['Juventus', 'Dortmund', [4, 4]], ['Tottenham', 'Villarreal', [1, 0]], ['Benfica', 'Karabakh Agdam', [2, 3]], 
             ['Olympiakos', 'Paphos', [0, 0]], ['Slavia Praha', 'Bodoe Glimt', [2, 2]], ['Paris SG', 'Atalanta', [4, 0]], 
             ['Liverpool', 'Atletico', [3, 2]], ['Bayern', 'Chelsea', [3, 1]], ['Ajax', 'Inter', [0, 2]], 
             ['Brugge', 'Monaco', [4, 1]], ['FC Kobenhavn', 'Leverkusen', [2, 2]], ['Newcastle', 'Barcelona', [1, 2]], 
             ['Man City', 'Napoli', [2, 0]], ['Frankfurt', 'Galatasaray', [5, 1]], ['Sporting', 'Kairat', [4, 1]]]

matchs_J2 = [['Kairat', 'Real Madrid', [0, 5]], ['Atalanta', 'Brugge', [2, 1]], ['Atletico', 'Frankfurt', [5, 1]], 
             ['Marseille', 'Ajax', [4, 0]], ['Galatasaray', 'Liverpool', [1, 0]], ['Chelsea', 'Benfica', [1, 0]], 
             ['Paphos', 'Bayern', [1, 5]], ['Bodoe Glimt', 'Tottenham', [2, 2]], ['Inter', 'Slavia Praha', [3, 0]], 
             ['St Gillis', 'Newcastle', [0, 4]], ['Karabakh Agdam', 'FC Kobenhavn', [2, 0]], ['Villarreal', 'Juventus', [2, 2]], 
             ['Napoli', 'Sporting', [2, 1]], ['Leverkusen', 'PSV', [1, 1]], ['Arsenal', 'Olympiakos', [2, 0]], 
             ['Barcelona', 'Paris SG', [1, 2]], ['Monaco', 'Man City', [2, 2]], ['Dortmund', 'Bilbao', [4, 1]]]

matchs_J3 = [['Kairat', 'Paphos', [0, 0]], ['Barcelona', 'Olympiakos', [6, 1]], ['Arsenal', 'Atletico', [4, 0]], 
             ['Leverkusen', 'Paris SG', [2, 7]], ['Villarreal', 'Man City', [0, 2]], ['PSV', 'Napoli', [6, 2]], 
             ['FC Kobenhavn', 'Dortmund', [2, 4]], ['St Gillis', 'Inter', [0, 4]], ['Newcastle', 'Benfica', [3, 0]], 
             ['Galatasaray', 'Bodoe Glimt', [3, 1]], ['Bilbao', 'Karabakh Agdam', [3, 1]], ['Chelsea', 'Ajax', [5, 1]], 
             ['Atalanta', 'Slavia Praha', [0, 0]], ['Frankfurt', 'Liverpool', [1, 5]], ['Sporting', 'Marseille', [2, 1]], 
             ['Monaco', 'Tottenham', [0, 0]], ['Real Madrid', 'Juventus', [1, 0]], ['Bayern', 'Brugge', [4, 0]]]

resultats_J4 = [
    ("Slavia Praha", "Arsenal", 0, 3),
    ("Napoli", "Frankfurt", 0, 0),
    ("Olympiacos", "PSV", 1, 1),
    ("Juventus", "Sporting", 1, 1),
    ("Bodoe Glimt", "Monaco", 0, 1),
    ("Tottenham", "FC Kobenhavn", 4, 0),
    ("Liverpool", "Real Madrid", 1, 0),
    ("Paris SG", "Bayern", 1, 2),
    ("Atletico", "St Gillis", 3, 1),
    ("Karabakh Agdam", "Chelsea", 2, 2),
    ("Paphos", "Villarreal", 1, 0),
    ("Man City", "Dortmund", 4, 1),
    ("Inter", "Kairat", 2, 1),
    ("Benfica", "Leverkusen", 0, 1),
    ("Brugge", "Barcelona", 3, 3),
    ("Ajax", "Galatasaray", 0, 3),
    ("Marseille", "Atalanta", 0, 1),
    ("Newcastle", "Bilbao", 2, 0)
]
matchs_J4 = [['Slavia Praha', 'Arsenal', [0, 3]], ['Napoli', 'Frankfurt', [0, 0]], ['Olympiakos', 'PSV', [1, 1]], 
             ['Juventus', 'Sporting', [1, 1]], ['Bodoe Glimt', 'Monaco', [0, 1]], ['Tottenham', 'FC Kobenhavn', [4, 0]], 
             ['Liverpool', 'Real Madrid', [1, 0]], ['Paris SG', 'Bayern', [1, 2]], ['Atletico', 'St Gillis', [3, 1]], 
             ['Karabakh Agdam', 'Chelsea', [2, 2]], ['Paphos', 'Villarreal', [1, 0]], ['Man City', 'Dortmund', [4, 1]], 
             ['Inter', 'Kairat', [2, 1]], ['Benfica', 'Leverkusen', [0, 1]], ['Brugge', 'Barcelona', [3, 3]], 
             ['Ajax', 'Galatasaray', [0, 3]], ['Marseille', 'Atalanta', [0, 1]], ['Newcastle', 'Bilbao', [2, 0]]]
"""
matchs = [
    ['Napoli', 'Karabakh Agdam', [2, 0]],     # Napoli assure à domicile
    ['Marseille', 'Newcastle', [2, 1]],        # L'OM s'impose au Vélodrome
    ['Dortmund', 'Villarreal', [4, 0]],        # Dortmund écrase Villarreal
    ['Chelsea', 'Barcelona', [3, 0]],          # Chelsea domine largement le Barça
    ['Man City', 'Leverkusen', [0, 2]],        # La surprise : City chute à l'Etihad
    ['Ajax', 'Benfica', [0, 2]],               # L'Ajax n'y arrive toujours pas
    ['Galatasaray', 'St Gillis', [0, 1]],      # L'Union SG surprend Galatasaray
    ['Slavia Praha', 'Bilbao', [0, 0]],        # Match nul fermé
    ['Bodoe Glimt', 'Juventus', [2, 3]],

    ['Arsenal', 'Bayern', [3, 1]],             # Arsenal frappe fort et prend la tête
    ['Atletico', 'Inter', [2, 1]],             # L'Atlético fait tomber l'Inter
    ['Liverpool', 'PSV', [1, 4]],              # Grosse désillusion pour Liverpool à Anfield
    ['Olympiakos', 'Real Madrid', [3, 4]],     # Match fou, le Real s'en sort
    ['Paris SG', 'Tottenham', [5, 3]],         # Festival offensif au Parc
    ['Sporting', 'Brugge', [3, 0]],            # Le Sporting solide
    ['FC Kobenhavn', 'Kairat', [3, 2]],        # Copenhague gagne son duel
    ['Paphos', 'Monaco', [2, 2]],              # Monaco piégé à Chypre
    ['Frankfurt', 'Atalanta', [0, 3]]
]
données_J6 = ajouter_matchs_donnés(données_J5,matchs)


# Détermination de l'importance d'un match pour une équipe
# 
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

def afficher_enjeux_club(club,enjeux_):
    # enjeux_ est un dictionnaire qui associe à chaque club la liste des matchs qu'il ne joue pas lors d'une certaine journée
    matchs = list(enjeux_[club].keys())
    df = pd.DataFrame({
        "Match": matchs,
        "Enjeu": [enjeux_[club][matchs[i]][0] for i in range(len(matchs))],
        "Victoire la + favorable": [enjeux_[club][matchs[i]][1] for i in range(len(matchs))]
        })
    df = df.sort_values(by=["Enjeu"], ascending=[False]).reset_index(drop=True)
    df['Enjeu'] = df['Enjeu'].round(3)
    print(club, ":\n")
    print(df)

def afficher_max_impact(enjeux_,k=10):
    impacts = [[match, club, enjeux_[club][match][0]]
    for match in calendrier["Journée 7"]
    for club in clubs_en_ldc
    if match in enjeux_[club]]
    
    df = pd.DataFrame({
        "Match": [impacts[i][0] for i in range(len(impacts))],
        "Club impacté": [impacts[i][1] for i in range(len(impacts))],
        "Impact": [impacts[i][2] for i in range(len(impacts))]
    })
    df = df.sort_values(by=["Impact"], ascending=[False]).reset_index(drop=True)
    df = df.head(k)
    df['Impact'] = df['Impact'].round(3)
    print("Matchs à plus fort impact sur un autre club :\n")
    print(df)

def afficher_max_cumulé(enjeux_):
    enjeux_matchs = {match : 0 for match in calendrier["Journée 7"]}
    for club in enjeux_.keys():
        for match in enjeux_[club].keys():
            enjeux_matchs[match] += enjeux_[club][match][0]
    matchs = list(enjeux_matchs.keys())
    df = pd.DataFrame({
        "Match": matchs,
        "Enjeu pour les autres": [enjeux_matchs[matchs[i]] for i in range(len(matchs))]
    })
    df = df.sort_values(by=["Enjeu pour les autres"], ascending=[False]).reset_index(drop=True)
    df["Enjeu pour les autres"] = df["Enjeu pour les autres"].round(3)
    print("Impact cumulé de chaque match sur les autres clubs :\n")
    print(df)

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


# Mise à jour du mardi 22 décembre
"""
matchs = [['Atalanta','Sturm Graz',[5,0]],['Monaco','Aston Villa',[1,0]],['Atletico','Leverkusen',[2,1]],['Slovan Bratislava','Stuttgart',[1,3]],['Crvena Zvezda','PSV',[2,3]],['Liverpool','Lille',[2,1]],['Bologna','Dortmund',[2,1]],['Benfica','Barcelona',[4,5]],['Brugge','Juventus',[0,0]]]
données_J67 = ajouter_matchs_donnés(données=données_J6,matchs=matchs)

# Mise à jour du mercredi 23 décembre 

matchs = [["Shakhtar", "Brest",[2,0]],       
        ["RB Leipzig", "Sporting",[2,1]],
        ["Milan", "Girona",[1,0]],
        ["Feyenoord", "Bayern",[3,0]],
        ["Real Madrid", "Salzburg",[5,1]],
        ["Arsenal", "Dinamo Zagreb",[3,0]],
        ["Celtic", "Young Boys",[1,0]],
        ["Paris SG", "Man City",[4,2]],
        ["Sparta Praha", "Inter",[0,1]]]
données_J7 = ajouter_matchs_donnés(données=données_J67,matchs=matchs)




## Afficher les probas sur le nombre de points du 25è
## Code à légèrement modifier pour avoir les points du 24è ou du 8è par ex en fonction de ce qu'on veut
distribution_probas = distribution_par_position(N=100000,données=données_J7,debut=8,demi=False)

distribution = distribution_probas[25]  #points du 25è, distribution_probas contient les points de toutes les positions
                                        # donc impossible de calculer
positions = [p for p, prob in distribution.items() if prob > 0]
probabilities = [100 * prob for prob in distribution.values() if prob > 0]

# Création du graphique
plt.figure(figsize=(8, 4.5))
plt.bar(positions, probabilities, color="skyblue", edgecolor="black")

# Ajouter des étiquettes
plt.xlabel("Nombre de points", fontsize=14)
plt.ylabel("Probabilités (%)", fontsize=14)
plt.title(f"Nombre de points du club en 25è place", fontsize=16)
plt.xticks(positions, fontsize=12)
plt.yticks(fontsize=12)

moyenne, ecart_type = moyenne_et_ecart_type(25, distribution_probas)

# Ajouter la moyenne et l'écart type en annotation
texte_stats = f"Moyenne: {moyenne:.2f}"
plt.text(
    0.95,
    0.9,
    texte_stats,
    transform=plt.gca().transAxes,  # Position relative à l'axe (95% à droite et en haut)
    fontsize=12,
    verticalalignment="top",
    horizontalalignment="right",
    bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5"),
)
# Afficher le graphique
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()

# Ajouter les derniers matchs

matchs_J8 = [['Sporting','Bologna',[1,1]],['PSV','Liverpool',[3,2]],['Young Boys','Crvena Zvezda',[0,1]],['Stuttgart','Paris SG',[1,4]],['Sturm Graz','RB Leipzig',[1,0]],
          ['Man City','Brugge',[3,1]],['Bayern','Slovan Bratislava',[3,1]],['Inter','Monaco',[3,0]],['Dortmund','Shakhtar',[3,1]],['Barcelona','Atalanta',[2,2]],
          ['Leverkusen','Sparta Praha',[2,0]],['Juventus','Benfica',[0,2]],['Dinamo Zagreb','Milan',[2,1]],['Salzburg','Atletico',[1,4]],['Lille','Feyenoord',[6,1]],
          ['Aston Villa','Celtic',[4,2]],['Girona','Arsenal',[1,2]],['Brest','Real Madrid',[0,3]]
          ]
données_J8 = ajouter_matchs_donnés(données=données_J7,matchs=matchs)

N = 1000
enjeux_ = simulation_pour_enjeux(journee=7,données=données_J6,debut=7,demi=True,N=N)

def données_adversaires(club,données=données_J8):
    d = {'points' : 0, 'diff_buts' : 0, 'buts' : 0}
    for j in calendrier.keys():
        for match in calendrier[j]:
            if match[0] == club:
                adv = match[1]
            elif match[1] == club:
                adv = match[0]
        d['points'] += données["points"][adv]
        d['diff_buts'] += données["diff_buts"][adv]
        d['buts'] += données["buts"][adv]
    return d

#données_adversaires("Paris SG")

def classement_par_adversaires(données=données_J8):
    d = {club : données_adversaires(club) for club in clubs_en_ldc}
    df = pd.DataFrame({
        "Clubs" : d.keys(),
        "Points des adversaires" : [d[club]["points"] for club in d.keys()],
        "Diff de buts" : [d[club]["diff_buts"] for club in d.keys()],
        "Buts marqués" : [d[club]["buts"] for club in d.keys()]
    }).sort_values(by=["Points des adversaires","Diff de buts","Buts marqués"],ascending=[False,False,False]).reset_index(drop=True)
    print(df)

classement_par_adversaires()
"""

# =============================================================================
#  NOUVEAUX PONTS API (A RAJOUTER A LA FIN DE SIMULATION.PY)
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
#  PONT API (A RAJOUTER A LA FIN DE SIMULATION.PY)
# =============================================================================

"""
def get_web_simulation(club_cible, nb_simulations=1000):
    #Fonction optimisée pour le web.
    #Lance une simulation Monte Carlo rapide et renvoie du JSON.
    if club_cible not in clubs_en_ldc:
        return {"error": f"Club '{club_cible}' introuvable. Vérifiez l'orthographe."}

    # 1. On utilise les données les plus récentes (J6) définies dans la Partie 4
    # Assurez-vous que données_J6 est bien calculé dans votre script avant cette fonction
    etat_actuel = données_J6 
    
    # 2. On lance les simulations (N réduit à 1000 pour la vitesse du site)
    # On simule la fin de la phase (J7 et J8)
    distrib_points = distribution_points_par_club(N=nb_simulations, données=etat_actuel, debut=7, fin=8)
    distrib_rank = distribution_position_par_club(N=nb_simulations, données=etat_actuel, debut=7, fin=8)

    # 3. Extraction des stats pour le club cible
    stats_points = distrib_points[club_cible]
    stats_rank = distrib_rank[club_cible]

    # 4. Calculs statistiques
    # a) Points moyens
    pts_moyen = sum(pt * prob for pt, prob in stats_points.items())
    
    # b) Probabilités (Top 8, Barrage, Eliminé)
    # Rappel : Top 8 = Rangs 1 à 8
    # Barrage = Rangs 9 à 24
    proba_top8 = sum(stats_rank.get(r, 0) for r in range(1, 9))
    proba_barrage = sum(stats_rank.get(r, 0) for r in range(9, 25))
    proba_elimine = sum(stats_rank.get(r, 0) for r in range(25, 37))

    # 5. Formatage pour le Graphique JS (On nettoie les probas infimes)
    chart_data = {f"{k} pts": v for k, v in stats_points.items() if v > 0.005}

    return {
        "club": club_cible,
        "points_moyens": round(pts_moyen, 2),
        "proba_top_8": round(proba_top8 * 100, 1),
        "proba_barrage": round(proba_barrage * 100, 1),
        "proba_elimine": round(proba_elimine * 100, 1),
        "distribution": chart_data,
        "message": "Simulation basée sur l'état après J6"
    }

"""

"""
#je step un peu sur Houssam
def get_web_simulation(club_cible):
    # 1. Vérifions si le club existe
    if club_cible not in clubs_en_ldc:
        return {"error": f"Le club '{club_cible}' n'est pas dans la liste."}

    # 2. On définit l'état actuel (J6 dans votre cas)
    # Assurez-vous que données_J6 existe bien dans votre code plus haut
    etat_actuel = données_J6 
    
    # 3. On lance les simulations
    nb_simulations = 1000
    
    # On récupère les distributions (points et rangs)
    distrib_points = distribution_points_par_club(N=nb_simulations, données=etat_actuel, debut=7, fin=8)
    distrib_rank = distribution_position_par_club(N=nb_simulations, données=etat_actuel, debut=7, fin=8)

    # 4. On isole les stats du club demandé
    stats_points = distrib_points[club_cible]
    stats_rank = distrib_rank[club_cible]

    # 5. Calcul des moyennes et pourcentages
    # Moyenne pondérée des points
    pts_moyen = sum(pt * prob for pt, prob in stats_points.items())
    
    # Probabilités de classement
    proba_top8 = sum(stats_rank.get(r, 0) for r in range(1, 9))
    proba_barrage = sum(stats_rank.get(r, 0) for r in range(9, 25))
    proba_elimine = sum(stats_rank.get(r, 0) for r in range(25, 37))

    # 6. RETOUR JSON POUR LE SITE
    return {
        "club": club_cible,
        "points_moyen": round(pts_moyen, 2),
        "top_8": round(proba_top8 * 100, 1),
        "barrage": round(proba_barrage * 100, 1),
        "elimine": round(proba_elimine * 100, 1),
        "distribution": stats_points  # C'est ici que nous avons ajouté le graphique
    }

"""
def get_web_simulation(club_cible):
    """
    Fonction optimisée pour le web.
    Renvoie les stats et les DEUX distributions (Points et Rangs).
    """
    # 1. Vérifions si le club existe
    if club_cible not in clubs_en_ldc:
        return {"error": f"Le club '{club_cible}' n'est pas dans la liste."}

    # 2. On utilise l'état actuel (J6)
    # Assurez-vous d'avoir exécuté le bloc d'initialisation des données manquantes en haut du fichier
    etat_actuel = données_J6 
    
    # 3. On lance les simulations (N=1000)
    nb_simulations = 1000
    
    # On récupère les distributions (points et rangs)
    # debut=7 car on simule la fin de saison
    distrib_points = distribution_points_par_club(N=nb_simulations, données=etat_actuel, debut=7, fin=8)
    distrib_rank = distribution_position_par_club(N=nb_simulations, données=etat_actuel, debut=7, fin=8)

    # 4. On isole les stats du club demandé
    stats_points = distrib_points[club_cible]
    stats_rank = distrib_rank[club_cible]

    # 5. Calcul des moyennes et pourcentages
    # Moyenne pondérée des points
    pts_moyen = sum(pt * prob for pt, prob in stats_points.items())
    
    # Probabilités de classement
    # Top 8 = Rangs 1 à 8
    proba_top8 = sum(stats_rank.get(r, 0) for r in range(1, 9))
    # Barrage = Rangs 9 à 24
    proba_barrage = sum(stats_rank.get(r, 0) for r in range(9, 25))
    # Eliminé = Rangs 25 à 36
    proba_elimine = sum(stats_rank.get(r, 0) for r in range(25, 37))

    # Nettoyage (on enlève les probas minuscules pour alléger le JSON)
    clean_points = {k: v for k, v in stats_points.items() if v > 0.001}
    clean_ranks = {k: v for k, v in stats_rank.items() if v > 0.001}

    # 6. RETOUR JSON (ATTENTION AUX NOMS DES CLES POUR LE JS)
    return {
        "club": club_cible,
        "points_moyens": round(pts_moyen, 2),        # JS attend ça
        "proba_top_8": round(proba_top8 * 100, 1),   # JS attend ça
        "proba_barrage": round(proba_barrage * 100, 1),
        "proba_elimine": round(proba_elimine * 100, 1),
        "distribution_points": clean_points,         # Pour le graphe 1
        "distribution_rangs": clean_ranks            # Pour le graphe 2
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


def get_global_ranking_detailed(n_simulations=1000, start_day=7, end_day=8):
    """
    Simule la saison entre start_day et end_day.
    """
    # Sécurité : Si l'utilisateur inverse (ex: début 8, fin 2), on remet dans l'ordre
    if start_day > end_day:
        start_day, end_day = end_day, start_day

    # 1. Choix de l'état initial
    # Si on commence après la J6, on prend les données réelles de la J6
    # Sinon, on repart de zéro (ou d'un état antérieur si vous l'avez)
    if start_day >= 7:
        etat_actuel = données_J6
    else:
        # Si on veut simuler depuis le début (J1), on part de zéro
        etat_actuel = {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, 
            "nb_victoires_ext": None
        }

    total_stats = {
        club: {"points": 0, "diff_buts": 0, "buts": 0, "nb_victoires": 0} 
        for club in clubs_en_ldc
    }

    # 2. Boucle de simulation
    for _ in range(n_simulations):
        # On passe les paramètres dynamiques ici !
        resultats_simu = simulation_ligue(données=etat_actuel, debut=start_day, fin=end_day)
        
        for club in clubs_en_ldc:
            total_stats[club]["points"] += resultats_simu["points"][club]
            total_stats[club]["diff_buts"] += resultats_simu["diff_buts"][club]
            total_stats[club]["buts"] += resultats_simu["buts"][club]
            total_stats[club]["nb_victoires"] += resultats_simu["nb_victoires"][club]

    # 3. Calcul des moyennes (Le reste ne change pas)
    ranking_data = []
    for club, stats in total_stats.items():
        ranking_data.append({
            "club": club,
            "points": round(stats["points"] / n_simulations, 1),
            "diff": round(stats["diff_buts"] / n_simulations, 1),
            "buts": round(stats["buts"] / n_simulations, 1),
            "victoires": round(stats["nb_victoires"] / n_simulations, 1),
            "elo": round(elo_of(club))
        })

    ranking_data.sort(key=lambda x: (x['points'], x['diff']), reverse=True)

    for i, row in enumerate(ranking_data):
        row['rank'] = i + 1

    return ranking_data


# --- 20/12/2025 début MIR ---

def get_simulation_flexible(n_simulations=1000, start_day=1, end_day=8):
    """
    Lance n_simulations de la journée 'start_day' à 'end_day'.
    Utilise vos fonctions existantes pour gérer la logique.
    """
    # 1. CHOIX DE L'ÉTAT INITIAL
    if start_day <= 1:
        # Si on commence J1, on envoie un dictionnaire avec des None.
        # Votre fonction simulation_ligue mettra tout à 0 automatiquement.
        etat_initial = {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, 
            "nb_victoires_ext": None
        }
    else:
        # Si on commence J_k (ex: J3), on charge les données de J_(k-1) (ex: J2)
        # On suppose que ces variables (données_J1...) sont définies plus haut dans votre fichier
        map_historique = {
            1: données_J1,
            2: données_J2,
            3: données_J3,
            4: données_J4,
            5: données_J5,
            6: données_J6, # Actuel
            7: données_J7
        }
        # On récupère l'historique, ou le vide par sécurité
        etat_initial = map_historique.get(start_day - 1, {
             "classement": None, "points": None, "diff_buts": None, 
             "buts": None, "buts_ext": None, "nb_victoires": None, 
             "nb_victoires_ext": None
        })

    # 2. INITIALISATION DES COMPTEURS (Moyenne)
    # -----------------------------------------
    total_stats = {
        club: {
            "points": 0, "diff_buts": 0, "buts": 0, 
            "buts_ext": 0, "nb_victoires": 0, "nb_victoires_ext": 0
        } 
        for club in clubs_en_ldc
    }

    # 3. BOUCLE DE SIMULATION
    # -----------------------
    for _ in range(n_simulations):
        
        # Appel de VOTRE fonction
        resultats_simu = simulation_ligue(
            données=etat_initial, 
            debut=start_day, 
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
    # -----------------------------------
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

# Acceder au données en temps réel (Scraping)
import pandas as pd

def get_wikipedia_standing():
    url = "https://fr.wikipedia.org/wiki/Phase_de_championnat_de_la_Ligue_des_champions_de_l%27UEFA_2025-2026#Phase_de_championnat"
    
    
    # Pandas va chercher tous les tableaux de la page
    try:
        tables = pd.read_html(url)
        
        # Le classement est souvent le tableau qui contient "Team", "Pld", "Pts"
        standings_table = None
        for t in tables:
            if "Équipe" in t.columns and "Pts" in t.columns:
                standings_table = t
                break
        
        if standings_table is not None:
            # Nettoyage des données (enlever les notes de bas de page ex: "Real Madrid[a]")
            standings_table['Équipe'] = standings_table['Équipe'].str.replace(r'\[.*\]', '', regex=True)
            return standings_table
            
    except Exception as e:
        print(f"Erreur scraping: {e}")
        return None

df = get_wikipedia_standing()  
print(df)

