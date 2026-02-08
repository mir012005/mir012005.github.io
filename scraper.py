import pandas as pd
import requests
import io
import os
import re
from bs4 import BeautifulSoup
import time
from datetime import datetime
import cloudscraper
import copy

from données import calendrier_ldc

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
    "FC Kairat": "Kairat",

    #MAPPING_FBREF
    "Paris S-G": "Paris SG", "Paris Saint-Germain": "Paris SG",
    "Real Madrid": "Real Madrid",
    "Manchester City": "Man City",
    "Bayern Munich": "Bayern",
    "Liverpool": "Liverpool",
    "Inter": "Inter", "Internazionale": "Inter",
    "Chelsea": "Chelsea",
    "Dortmund": "Dortmund", "Borussia Dortmund": "Dortmund",
    "Barcelona": "Barcelona",
    "Arsenal": "Arsenal",
    "Leverkusen": "Leverkusen", "Bayer Leverkusen": "Leverkusen",
    "Atlético Madrid": "Atletico",
    "Benfica": "Benfica",
    "Atalanta": "Atalanta",
    "Villarreal": "Villarreal",
    "Juventus": "Juventus",
    "Eint Frankfurt": "Frankfurt", "Eintracht Frankfurt": "Frankfurt",
    "Club Brugge": "Brugge",
    "Tottenham": "Tottenham",
    "PSV Eindhoven": "PSV",
    "Ajax": "Ajax",
    "Napoli": "Napoli",
    "Sporting CP": "Sporting",
    "Olympiacos": "Olympiakos",
    "Slavia Prague": "Slavia Praha",
    "Bodø/Glimt": "Bodoe Glimt",
    "Marseille": "Marseille",
    "FC Copenhagen": "FC Kobenhavn",
    "Monaco": "Monaco",
    "Galatasaray": "Galatasaray",
    "Union SG": "St Gillis",
    "Qarabağ": "Karabakh Agdam",
    "Athletic Club": "Bilbao",
    "Newcastle Utd": "Newcastle", "Newcastle United": "Newcastle",
    "Pafos": "Paphos",
    "Kairat": "Kairat",
    "Milan": "Milan", "Aston Villa": "Aston Villa", "Bologna": "Bologna",
    "Brest": "Brest", "Celtic": "Celtic", "Girona": "Girona",
    "Lille": "Lille", "RB Leipzig": "Leipzig", "Stuttgart": "Stuttgart",
    "Young Boys": "Young Boys", "Salzburg": "Salzburg", "Shakhtar": "Shakhtar",
    "Sparta Prague": "Sparta Praha", "Sturm Graz": "Sturm Graz", 
    "Feyenoord": "Feyenoord", "Red Star": "Crvena Zvezda", "Slovan Bratislava": "Slovan Bratislava",

    "Paris Saint-Germain FC": "Paris SG",
    "Real Madrid CF": "Real Madrid",
    "Manchester City FC": "Man City",
    "FC Bayern München": "Bayern",
    "Liverpool FC": "Liverpool",
    "FC Internazionale Milano": "Inter",
    "Borussia Dortmund": "Dortmund",
    "FC Barcelona": "Barcelona",
    "Arsenal FC": "Arsenal",
    "Bayer 04 Leverkusen": "Leverkusen",
    "Club Atlético de Madrid": "Atletico",
    "SL Benfica": "Benfica",
    "Atalanta BC": "Atalanta",
    "Juventus FC": "Juventus",
    "Eintracht Frankfurt": "Frankfurt",
    "Club Brugge KV": "Brugge",
    "PSV": "PSV",
    "AFC Ajax": "Ajax",
    "SSC Napoli": "Napoli",
    "Sporting Clube de Portugal": "Sporting",
    "AC Sparta Praha": "Sparta Praha",
    "SK Slavia Praha": "Slavia Praha",
    "Feyenoord Rotterdam": "Feyenoord",
    "AC Milan": "Milan",
    "Lille OSC": "Lille",
    "AS Monaco FC": "Monaco",
    "Celtic FC": "Celtic",
    "Aston Villa FC": "Aston Villa",
    "Bologna FC 1909": "Bologna",
    "Girona FC": "Girona",
    "VfB Stuttgart": "Stuttgart",
    "RB Leipzig": "Leipzig",
    "SK Sturm Graz": "Sturm Graz",
    "Stade Brestois 29": "Brest",
    "FC Red Bull Salzburg": "Salzburg",
    "BSC Young Boys": "Young Boys",
    "FK Shakhtar Donetsk": "Shakhtar",
    "GNE Dinamo Zagreb": "Dinamo Zagreb",
    "FK Crvena Zvezda": "Crvena Zvezda",
    "ŠK Slovan Bratislava": "Slovan Bratislava",


    "Arsenal FC": "Arsenal",
    "FK Kairat": "Kairat", "Kairat Almaty": "Kairat",
    "Paphos FC": "Paphos",
    "SK Slavia Praha": "Slavia Praha", "Slavia Prague": "Slavia Praha",
    "Sport Lisboa e Benfica": "Benfica", "SL Benfica": "Benfica",
    "Real Madrid CF": "Real Madrid",
    "Eintracht Frankfurt": "Frankfurt",
    "Tottenham Hotspur": "Tottenham",
    "Club Atlético de Madrid": "Atletico", "Atlético Madrid": "Atletico",
    "FK Bodø/Glimt": "Bodoe Glimt",
    "AS Monaco FC": "Monaco",
    "Juventus FC": "Juventus",
    "Paris Saint-Germain": "Paris SG", "Paris Saint-Germain FC": "Paris SG",
    "Newcastle United": "Newcastle",
    "Borussia Dortmund": "Dortmund",
    "FC Internazionale": "Inter", "Inter Milan": "Inter",
    "Manchester City FC": "Man City", "Man City": "Man City",
    "Galatasaray SK": "Galatasaray",
    "Royale Union Saint-Gilloise": "St Gillis", "Union SG": "St Gillis",
    "Atalanta BC": "Atalanta",
    "PAE Olympiakos": "Olympiakos", "Olympiacos": "Olympiakos",
    "Bayer 04 Leverkusen": "Leverkusen", "Bayer Leverkusen": "Leverkusen",
    "Club Brugge KV": "Brugge", "Club Brugge": "Brugge",
    "Qarabağ Ağdam FK": "Karabakh Agdam", "Qarabag FK": "Karabakh Agdam",
    "Sporting CP": "Sporting",
    "PSV Eindhoven": "PSV",
    "AFC Ajax": "Ajax",
    "SSC Napoli": "Napoli",
    "FC København": "FC Kobenhavn", "FC Copenhagen": "FC Kobenhavn",
    "Villarreal CF": "Villarreal",
    "Liverpool FC": "Liverpool",
    "FC Bayern München": "Bayern", "Bayern Munich": "Bayern",
    "FC Barcelona": "Barcelona",
    "Chelsea FC": "Chelsea",
    "Athletic Club": "Bilbao", "Athletic Bilbao": "Bilbao",
}

def normaliser_noms_clubs(df_classement):
    """
    Remplace les noms scrapés par les noms du projet.
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

def get_donnees_from_wikipedia(url):
    """
    extrait le classement de wikipedia
    """
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

    try:
        tables = pd.read_html(io.StringIO(response.text))
    except ValueError:
        print("❌ Aucun tableau trouvé.")
        return None

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

    df_classement = normaliser_noms_clubs(df_classement)

    print("🔄 Transformation en format simulator.py...")

    # Création des dictionnaires
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

def nettoyer_nom_club_string(nom_brut):
    """
    C'est la version unitaire de la fonction 'normaliser_noms_clubs'.
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

    return MAPPING_WIKI.get(nom, nom)

def scraper_matchs_wikipedia(url):
    """
    Récupère les scores sous format : ['Dom', 'Ext', [ScoreD, ScoreE]]
    """
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

    # Analyse HTML avec BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    matchs_trouves = []

    print("🔍 Recherche des scores dans la page...")

    # On cherche toutes les lignes de tableaux (tr)
    lignes = soup.find_all('tr')
    
    for tr in lignes:
        # On récupère toutes les cellules (td ou th)
        cellules = tr.find_all(['td', 'th'])
        
        for i, cell in enumerate(cellules):
            texte = cell.get_text(strip=True)
            
            # Regex : Chiffre - tiret - Chiffre (ex: 2-1, 2 - 1, 2–1)
            match_score = re.search(r'^(\d+)\s*[\–\-\:]\s*(\d+)$', texte)
            
            if match_score:
                score_dom = int(match_score.group(1))
                score_ext = int(match_score.group(2))
                
                # Vérifions qu'on a bien des cellules avant et après pour les équipes
                if i > 0 and i < len(cellules) - 1:
                    nom_dom_brut = cellules[i-1].get_text(strip=True)
                    nom_ext_brut = cellules[i+1].get_text(strip=True)
                    
                    # Nettoyage et Mapping
                    club_dom = nettoyer_nom_club_string(nom_dom_brut)
                    club_ext = nettoyer_nom_club_string(nom_ext_brut)
                    
                    if club_dom in CLUBS_SIMULATOR and club_ext in CLUBS_SIMULATOR:
                        entree = [club_dom, club_ext, [score_dom, score_ext]]
                        matchs_trouves.append(entree)

    return matchs_trouves

def organiser_par_journee(liste_matchs):
    resultats = {}
    MATCHS_PAR_JOURNEE = len(CLUBS_SIMULATOR) // 2
    
    for i in range(1, 9):
        debut = (i - 1) * MATCHS_PAR_JOURNEE
        fin = i * MATCHS_PAR_JOURNEE
        matchs_j = liste_matchs[debut:fin]
        resultats[i] = matchs_j
        
    return resultats

#=========================================================
#--- Getting ELO SCORES ---
#==========================================================
def get_live_elo():
    # 1. Obtenir la date d'aujourd'hui (YYYY-MM-DD)
    date_str = datetime.today().strftime('%Y-%m-%d')
    url = f"http://api.clubelo.com/{date_str}"
    
    print(f"📡 Récupération des Elo pour le {date_str}...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        # On ne garde que Club et Elo pour aller plus vite
        df = df[['Club', 'Elo']]

        elo_database = dict(zip(df.Club.astype(str), df.Elo))
        
        elo_simulator = {}
        clubs_non_trouves = []

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

def generer_historique_elo():
    """
    genere elo pour les jours du calendrier ldc
    """
    historique = {}
    print(f"🔄 Démarrage de la récupération pour {len(calendrier_ldc)} journées...")
    
    for j, date in calendrier_ldc.items():
        print(f"   📅 Journée {j} (Date réf: {date})...")
        elos_du_jour = fetch_elo_date(date)
        if elos_du_jour:
            historique[j] = elos_du_jour
            print(f"      ✅ Elo récupérés pour {len(elos_du_jour)} clubs.")
        else:
            print("      ⚠️ Échec récupération.")
        time.sleep(0.5)
    return historique
