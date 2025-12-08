# backend/data.py
import pandas as pd
import math
import random as rd
import copy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from IPython.display import FileLink

# On récupère d'abord les données concernant les clubs participant à la ligue des champions, à la veille du début de la compétition.

from pathlib import Path


base_dir = Path(__file__).parent
elo_rating = base_dir / "Elo_rating_pré_ldc.csv"
#elo_rating = "C:\\Users\\pc\\OneDrive\\Bureau\\tdlog\\mir012005.github.io\\Elo_rating_pré_ldc.csv"
elo = pd.read_csv(elo_rating)
# Liste officielle des clubs 2025/2026 (Triée)
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

# Estimation ELO
elo_pre_ldc = elo[elo["Club"].isin(clubs_en_ldc)]


# Calendrier (J1 à J8)
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


# Etat actuel du classement à la fin de la J5 (Point de départ de la simulation)
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

def dico_de_données(classement,points,diff_buts,buts,buts_ext,nb_victoires,nb_victoires_ext):
    return {"classement" : classement , "points" : points , "diff_buts" : diff_buts , "buts" : buts ,
            "buts_ext" : buts_ext , "nb_victoires" : nb_victoires , "nb_victoires_ext" : nb_victoires_ext}

données_J5 = dico_de_données(classement_J5,points_J5,diff_buts_J5,buts_J5,buts_ext_J5,nb_v_J5,nb_v_ext_J5)