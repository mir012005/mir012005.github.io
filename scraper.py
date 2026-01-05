import pandas as pd
import requests
import io
import re
from bs4 import BeautifulSoup  # Nécessaire pour les scores précis
import time


calendrier_ldc = {
    1: "2025-09-16",
    2: "2025-09-30",
    3: "2025-10-21",
    4: "2025-11-04",
    5: "2025-11-25",
    6: "2025-12-09",
    7: "2026-01-20",
    8: "2026-01-28"
}

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

# 1. CONSTANTES ET LISTES
# -----------------------
CLUBS_SIMULATOR = [
    "Paris SG", "Real Madrid", "Man City", "Bayern", "Liverpool", "Inter", "Chelsea", 
    "Dortmund", "Barcelona", "Arsenal", "Leverkusen", "Atletico", "Benfica", "Atalanta", 
    "Villarreal", "Juventus", "Frankfurt", "Brugge", "Tottenham", "PSV", "Ajax", "Napoli", 
    "Sporting", "Olympiakos", "Slavia Praha", "Bodoe Glimt", "Marseille", "FC Kobenhavn", 
    "Monaco", "Galatasaray", "St Gillis", "Karabakh Agdam", "Bilbao", "Newcastle", 
    "Paphos", "Kairat"
]

MAPPING_WIKI = {
    # --- ANGLETERRE ---
    "Arsenal FC": "Arsenal",
    "Manchester City": "Man City",
    "Man City": "Man City",
    "Tottenham Hotspur": "Tottenham",
    "Newcastle United": "Newcastle",
    "Chelsea FC": "Chelsea",
    "Liverpool FC": "Liverpool",

    # --- ESPAGNE ---
    "Real Madrid": "Real Madrid",
    "Real Madrid CF": "Real Madrid",
    "Atlético de Madrid": "Atletico",
    "Atlético Madrid": "Atletico",
    "FC Barcelone": "Barcelona",
    "FC Barcelona": "Barcelona",
    "Villarreal CF": "Villarreal",
    "Athletic Club": "Bilbao",
    "Athletic Bilbao": "Bilbao",

    # --- ALLEMAGNE ---
    "Bayern Munich": "Bayern",
    "Bayern München": "Bayern",
    "Borussia Dortmund": "Dortmund",
    "Bayer Leverkusen": "Leverkusen",
    "Bayer 04 Leverkusen": "Leverkusen",
    "Eintracht Francfort": "Frankfurt",
    "Eintracht Frankfurt": "Frankfurt",

    # --- FRANCE ---
    "Paris Saint-Germain": "Paris SG",
    "Paris SG": "Paris SG",
    "Olympique de Marseille": "Marseille",
    "AS Monaco": "Monaco",

    # --- ITALIE ---
    "Atalanta Bergame": "Atalanta",
    "Atalanta BC": "Atalanta",
    "Atalanta": "Atalanta",
    "Inter Milan": "Inter",
    "Internazionale": "Inter",
    "Juventus FC": "Juventus",
    "SSC Naples": "Napoli",
    "SSC Napoli": "Napoli",

    # --- PORTUGAL ---
    "Sporting CP": "Sporting",
    "SL Benfica": "Benfica",

    # --- PAYS-BAS ---
    "PSV Eindhoven": "PSV",
    "Ajax Amsterdam": "Ajax",
    "AFC Ajax": "Ajax",

    # --- BELGIQUE ---
    "Club Bruges": "Brugge",
    "Club Brugge": "Brugge",
    "Union SG": "St Gillis",
    "Union Saint-Gilloise": "St Gillis",
    "Royale Union Saint-Gilloise": "St Gillis",

    # --- AUTRES ---
    "Galatasaray SK": "Galatasaray",
    "Galatasaray": "Galatasaray",
    "Qarabağ FK": "Karabakh Agdam",
    "Qarabağ": "Karabakh Agdam",
    "FC Copenhague": "FC Kobenhavn",
    "F.C. Copenhagen": "FC Kobenhavn",
    "FC Copenhagen": "FC Kobenhavn",
    "Páfos FC": "Paphos",
    "Pafos FC": "Paphos",
    "Pafos": "Paphos",
    "Olympiakós": "Olympiakos",
    "Olympiacos": "Olympiakos",
    "FK Bodø/Glimt": "Bodoe Glimt",
    "Bodø/Glimt": "Bodoe Glimt",
    "Slavia Prague": "Slavia Praha",
    "SK Slavia Prague": "Slavia Praha",
    "Kaïrat Almaty": "Kairat",
    "Kairat Almaty": "Kairat",
    "FC Kairat": "Kairat"
}

# 2. FONCTION DE NORMALISATION
# ----------------------------
def normaliser_noms_clubs(df_classement):
    """
    Remplace les noms scrapés par les noms du projet.
    Travaille sur la colonne 'Équipe' (spécifique Wikipédia FR).
    """
    # Conversion en string pour éviter les erreurs
    df_classement['Équipe'] = df_classement['Équipe'].astype(str)

    # 1. Nettoyage Regex (Enlève [a], (Q), T S, etc.)
    df_classement['Équipe'] = df_classement['Équipe'].str.replace(r'\[.*\]', '', regex=True)
    df_classement['Équipe'] = df_classement['Équipe'].str.replace(r'\(.*\)', '', regex=True)
    
    # Nettoyage spécifique des suffixes parasites collés
    suffixes = [" T S", " C1", " C3", " C4", " VC"]
    for s in suffixes:
        df_classement['Équipe'] = df_classement['Équipe'].str.replace(s, '', regex=False)
        
    df_classement['Équipe'] = df_classement['Équipe'].str.strip()

    # 2. Application du Mapping
    df_classement['Équipe'] = df_classement['Équipe'].replace(MAPPING_WIKI)

    # 3. Vérification de sécurité
    clubs_inconnus = []
    for club in df_classement['Équipe']:
        if club not in CLUBS_SIMULATOR:
            clubs_inconnus.append(club)
    
    if clubs_inconnus:
        print(f"⚠️ ATTENTION : Clubs non reconnus : {clubs_inconnus}")
    else:
        print("✅ Normalisation des noms réussie.")

    return df_classement


# 3. FONCTION DE SCRAPING
# -----------------------
def get_donnees_from_wikipedia(url):
    # A. Le Déguisement
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"📡 Connexion à {url}...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return None

    # B. Lecture HTML
    try:
        tables = pd.read_html(io.StringIO(response.text))
    except ValueError:
        print("❌ Aucun tableau trouvé.")
        return None

    # C. Trouver le bon tableau (Version FR : Équipe, Pts, G)
    df_classement = None
    for t in tables:
        # On vérifie les colonnes typiques de Wiki FR
        if "Équipe" in t.columns and "Pts" in t.columns and "G" in t.columns:
            df_classement = t
            break
    
    if df_classement is None:
        print("❌ Tableau de classement introuvable (Vérifiez les noms de colonnes).")
        return None

    print("✅ Tableau brut trouvé.")

    # D. APPEL DE LA NORMALISATION (C'est ici qu'il fallait le mettre !)
    df_classement = normaliser_noms_clubs(df_classement)

    print("🔄 Transformation en format simulator.py...")

    # E. Création des dictionnaires
    points = {}
    diff_buts = {}
    buts = {}
    buts_ext = {} 
    nb_victoires = {}
    nb_victoires_ext = {} 

    # Liste ordonnée (Le classement)
    classement_list = df_classement['Équipe'].tolist()

    # Remplissage
    for index, row in df_classement.iterrows():
        club = row['Équipe']
        
        try:
            # Colonnes Wiki FR : Pts, Diff, Bp (Buts pour), G (Gagnés)
            points[club] = int(row['Pts'])
            diff_buts[club] = int(row['Diff']) 
            buts[club] = int(row['Bp'])   
            nb_victoires[club] = int(row['G'])
            
            # Valeurs par défaut
            buts_ext[club] = 0 
            nb_victoires_ext[club] = 0 
            
        except KeyError as e:
            print(f"⚠️ Colonne manquante pour {club}: {e}")
        except ValueError:
            pass # Ignore les lignes bizarres

    # F. Résultat final
    données_finale = {
        "classement": classement_list,
        "points": points,
        "diff_buts": diff_buts,
        "buts": buts,
        "buts_ext": buts_ext,
        "nb_victoires": nb_victoires,
        "nb_victoires_ext": nb_victoires_ext
    }

    return données_finale


# 4. EXÉCUTION
# ------------
if __name__ == "__main__":
    url_test = "https://fr.wikipedia.org/wiki/Phase_de_championnat_de_la_Ligue_des_champions_de_l%27UEFA_2025-2026#Classement"
    
    data = get_donnees_from_wikipedia(url_test)

    if data:
        print("\n🎉 VOICI LE CODE A COPIER DANS SIMULATOR.PY :\n")
        print(f"données_J_X = {data}")



# ==========================================
# 2. FONCTION DE NETTOYAGE UNITAIRE
# ==========================================
def nettoyer_nom_club_string(nom_brut):
    """
    Nettoie un nom de club (String) et applique le mapping.
    C'est la version unitaire de votre fonction 'normaliser_noms_clubs'.
    """
    if not isinstance(nom_brut, str):
        return None
        
    nom = nom_brut.strip()
    
    # 1. Regex (Nettoyage [a], (Q), T S, etc.)
    nom = re.sub(r'\[.*?\]', '', nom)
    nom = re.sub(r'\(.*?\)', '', nom)
    
    suffixes = [" T S", " C1", " C3", " C4", " VC"]
    for s in suffixes:
        nom = nom.replace(s, '')
        
    nom = nom.strip()

    # 2. Mapping
    # Si le nom est dans le dico, on prend la valeur, sinon on garde le nom nettoyé
    return MAPPING_WIKI.get(nom, nom)


# ==========================================
# 3. SCRAPER DE RÉSULTATS (MATCHS)
# ==========================================
def scraper_matchs_wikipedia(url):
    """
    Récupère les scores sous format : ['Dom', 'Ext', [ScoreD, ScoreE]]
    """
    # A. Le Déguisement
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"📡 Connexion à {url}...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return []

    # B. Analyse HTML avec BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    matchs_trouves = []

    print("🔍 Recherche des scores dans la page...")

    # On cherche toutes les lignes de tableaux (tr)
    lignes = soup.find_all('tr')
    
    for tr in lignes:
        # On récupère toutes les cellules (td ou th)
        cellules = tr.find_all(['td', 'th'])
        
        # Astuce : Un match a généralement 3 composantes alignées : Domicile - Score - Extérieur
        # On parcourt les cellules pour trouver celle qui contient le score (ex: "2 - 1")
        for i, cell in enumerate(cellules):
            texte = cell.get_text(strip=True)
            
            # Regex : Chiffre - tiret - Chiffre (ex: 2-1, 2 - 1, 2–1)
            match_score = re.search(r'^(\d+)\s*[\–\-\:]\s*(\d+)$', texte)
            
            if match_score:
                # BINGO ! On a trouvé un score
                score_dom = int(match_score.group(1))
                score_ext = int(match_score.group(2))
                
                # Vérifions qu'on a bien des cellules avant et après pour les équipes
                if i > 0 and i < len(cellules) - 1:
                    nom_dom_brut = cellules[i-1].get_text(strip=True)
                    nom_ext_brut = cellules[i+1].get_text(strip=True)
                    
                    # Nettoyage et Mapping
                    club_dom = nettoyer_nom_club_string(nom_dom_brut)
                    club_ext = nettoyer_nom_club_string(nom_ext_brut)
                    
                    # FILTRAGE STRICT : On ne garde que si les DEUX clubs sont dans notre liste
                    # (Ça évite de scraper des tours préliminaires ou matchs amicaux sur la même page)
                    if club_dom in CLUBS_SIMULATOR and club_ext in CLUBS_SIMULATOR:
                        
                        # Format demandé : ['Napoli', 'Karabakh Agdam', [2, 0]]
                        entree = [club_dom, club_ext, [score_dom, score_ext]]
                        matchs_trouves.append(entree)

    return matchs_trouves

def organiser_par_journee(liste_matchs):
    resultats = {}
    
    # RÈGLE D'OR : 36 équipes = 18 matchs par journée
    MATCHS_PAR_JOURNEE = len(CLUBS_SIMULATOR) // 2
    
    for i in range(1, 9):
        # Calcul des index de découpe
        debut = (i - 1) * MATCHS_PAR_JOURNEE
        fin = i * MATCHS_PAR_JOURNEE
        
        # On découpe la tranche (slice)
        # Si la liste n'est pas assez longue, Python renverra une liste vide ou partielle, c'est parfait
        matchs_j = liste_matchs[debut:fin]
        
        resultats[i] = matchs_j
        
    return resultats

# ==========================================
# 3. EXÉCUTION ET AFFICHAGE
# ==========================================
if __name__ == "__main__":
    # Pour le futur, mettez l'URL 2025-2026
    url_test = "https://fr.wikipedia.org/wiki/Phase_de_championnat_de_la_Ligue_des_champions_de_l%27UEFA_2025-2026"
    
    resultats = scraper_matchs_wikipedia(url_test)

    print(f"\n✅ {len(resultats)} MATCHS TROUVÉS COMPATIBLES AVEC LA SIMULATION :\n")
    
    print("matchs_J_Y = [")
    for m in resultats:
        print(f"    {m},")
    print("]")
    
    donnees = organiser_par_journee(resultats)
    
    print("\n" + "="*50)
    print("CODE À COPIER DANS SIMULATOR.PY")
    print("="*50 + "\n")
    
    for j in range(1, 9):
        matchs = donnees.get(j, [])
        if matchs:
            print(f"matchs_J{j} = [")
            for m in matchs:
                print(f"    {m},")
            print("]\n")
        else:
            print(f"# matchs_J{j} = []  (Aucun match trouvé ou pas encore joué)\n")


#=========================================================
#===============Getting ELO SCORES==========================
#==========================================================
def get_live_elo():
    # 1. Obtenir la date d'aujourd'hui (YYYY-MM-DD)
    date_str = datetime.today().strftime('%Y-%m-%d')
    url = f"http://api.clubelo.com/{date_str}"
    
    print(f"📡 Récupération des Elo pour le {date_str}...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Le contenu est un CSV, on le lit avec Pandas
        # Colonnes utiles : Rank, Club, Country, Level, Elo, From, To
        df = pd.read_csv(io.StringIO(response.text))
        
        # On ne garde que Club et Elo pour aller plus vite
        df = df[['Club', 'Elo']]
        
        # Création d'un dictionnaire rapide { "NomClubElo": 1850.5 }
        # On met tout en string pour éviter les erreurs
        elo_database = dict(zip(df.Club.astype(str), df.Elo))
        
        elo_simulator = {}
        clubs_non_trouves = []

        # 2. Attribution des Elo à vos clubs
        for mon_club in CLUBS_SIMULATOR:
            match_name = mon_club
            if match_name in elo_database:
                elo_simulator[mon_club] = elo_database[match_name]
            else:
                clubs_non_trouves.append((mon_club, match_name))

        return elo_simulator, clubs_non_trouves

    except Exception as e:
        print(f"❌ Erreur API ClubElo : {e}")
        return None, []

# --- TEST ---
if __name__ == "__main__":
    elos_live, manquants = get_live_elo()
    
    if elos_live:
        print("\n✅ ELO RÉCUPÉRÉS :\n")
        # Affichage trié par force
        for club, elo in sorted(elos_live.items(), key=lambda x: x[1], reverse=True):
            print(f"{club:<20} : {elo}")
            
        print("-" * 40)
        
    if manquants:
        print("Il faut mettre à jour le dictionnaire MAPPING_ELO avec le nom exact utilisé par api.clubelo.com")
        for c in manquants:
            print(f" - Cherché: '{c[1]}' (Votre nom: {c[0]})")



# ==========================================
# 2. FONCTION DE RÉCUPÉRATION ELO DU CALENDRIER
# ==========================================

def fetch_elo_date(date_str):
    """
    Récupère les Elo pour une date précise YYYY-MM-DD.
    Si la date est dans le futur, récupère les données LIVE.
    """
    
    # 1. Comparaison de la date
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    today = datetime.today().date()

    if target_date > today:
        print(f"🔮 Date future détectée ({date_str}) -> Récupération des données LIVE.")
        # L'URL sans date renvoie le classement actuel (Live)
        elo_simulator, clubs_non_trouves = get_live_elo()
        return elo_simulator
    else:
        url = f"http://api.clubelo.com/{date_str}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Lecture du CSV
        df = pd.read_csv(io.StringIO(response.text))
        df = df[['Club', 'Elo']] # On garde l'essentiel
        
        # Conversion en dictionnaire { "NomElo": 1750.2 }
        elo_raw = dict(zip(df.Club.astype(str), df.Elo))
        
        elo_simu = {}
        
        # Mapping vers vos noms
        for club in CLUBS_SIMULATOR:
            # Nom cible (via mapping ou direct)
            if club in elo_raw:
                elo_simu[club] = elo_raw[club]
            else:
                # Tentative de recherche insensible à la casse
                found = False
                for k, v in elo_raw.items():
                    if k.lower() == club.lower():
                        elo_simu[club] = v
                        found = True
                        break
                if not found:
                    # Valeur par défaut si club absent (petit club)
                    elo_simu[club] = 1450.0 
                    
        return elo_simu

    except Exception as e:
        print(f"❌ Erreur API pour {date_str}: {e}")
        return {}

# ==========================================
# 3. BOUCLE SUR LE CALENDRIER
# ==========================================
def generer_historique_elo():
    historique = {}
    
    print(f"🔄 Démarrage de la récupération pour {len(calendrier_ldc)} journées...")
    
    for j, date in calendrier_ldc.items():
        # On prend la PREMIÈRE date de la journée comme référence
        
        print(f"   📅 Journée {j} (Date réf: {date})...")
        
        elos_du_jour = fetch_elo_date(date)
        
        if elos_du_jour:
            historique[j] = elos_du_jour
            print(f"      ✅ Elo récupérés pour {len(elos_du_jour)} clubs.")
        else:
            print("      ⚠️ Échec récupération.")
        
        # Petite pause pour être gentil avec l'API
        time.sleep(0.5)
        
    return historique

"""
from scraper import scraper_matchs_wikipedia, organiser_par_journee, CLUBS_SIMULATOR
from simulator import ajouter_matchs_donnés
import copy

def creer_etat_initial():
    return {
        "classement": sorted(CLUBS_SIMULATOR),
        "points": {club: 0 for club in CLUBS_SIMULATOR},
        "diff_buts": {club: 0 for club in CLUBS_SIMULATOR},
        "buts": {club: 0 for club in CLUBS_SIMULATOR},
        "buts_ext": {club: 0 for club in CLUBS_SIMULATOR},
        "nb_victoires": {club: 0 for club in CLUBS_SIMULATOR},
        "nb_victoires_ext": {club: 0 for club in CLUBS_SIMULATOR},
    }

url = "https://fr.wikipedia.org/wiki/Phase_de_championnat_de_la_Ligue_des_champions_de_l%27UEFA_2025-2026"
tous_les_matchs = scraper_matchs_wikipedia(url)
matchs_par_journee = organiser_par_journee(tous_les_matchs)
données_J0 = creer_etat_initial()
états = {0: données_J0}

for j in range(1, 7):
    matchs_j = matchs_par_journee.get(j, [])
    if matchs_j:
        états[j] = ajouter_matchs_donnés(états[j-1], matchs_j)

with open('CODE_A_COPIER.py', 'w', encoding='utf-8') as f:
    for j in range(1, 7):
        if j in états:
            d = états[j]
            f.write(f"données_J{j} = {{\n")
            f.write(f"    'classement': {d['classement']},\n")
            f.write(f"    'points': {{\n")
            for club in sorted(d['points'].keys()):
                f.write(f"        '{club}': {d['points'][club]},\n")
            f.write(f"    }},\n")
            f.write(f"    'diff_buts': {{\n")
            for club in sorted(d['diff_buts'].keys()):
                f.write(f"        '{club}': {d['diff_buts'][club]},\n")
            f.write(f"    }},\n")
            f.write(f"    'buts': {{\n")
            for club in sorted(d['buts'].keys()):
                f.write(f"        '{club}': {d['buts'][club]},\n")
            f.write(f"    }},\n")
            f.write(f"    'buts_ext': {{\n")
            for club in sorted(d['buts_ext'].keys()):
                f.write(f"        '{club}': {d['buts_ext'][club]},\n")
            f.write(f"    }},\n")
            f.write(f"    'nb_victoires': {{\n")
            for club in sorted(d['nb_victoires'].keys()):
                f.write(f"        '{club}': {d['nb_victoires'][club]},\n")
            f.write(f"    }},\n")
            f.write(f"    'nb_victoires_ext': {{\n")
            for club in sorted(d['nb_victoires_ext'].keys()):
                f.write(f"        '{club}': {d['nb_victoires_ext'][club]},\n")
            f.write(f"    }},\n")
            f.write("}\n\n")
"""

# ==========================================
# 4. EXÉCUTION
# ==========================================
if __name__ == "__main__":
    data_elo = generer_historique_elo()
    
    print("\n" + "="*50)
    print("CODE À COPIER DANS SIMULATOR.PY")
    print("="*50 + "\n")
    
    # Affichage propre du dictionnaire géant
    print("historique_elo = {")
    for j, elos in data_elo.items():
        print(f"    {j}: {{")
        # On affiche quelques exemples pour ne pas spammer la console, 
        # mais dans la réalité vous copierez tout ou sauvegarderez dans un fichier
        for club, score in elos.items():
            print(f"        '{club}': {score},")
        print(f"    }},")
    print("}")


