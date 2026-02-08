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
