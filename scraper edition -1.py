import pandas as pd
import requests
import io
import re
from bs4 import BeautifulSoup
import time
from datetime import datetime


calendrier_ldc = {
    1: "2024-09-17",
    2: "2024-10-01",
    3: "2024-10-22",
    4: "2024-11-05",
    5: "2024-11-26",
    6: "2024-12-10",
    7: "2025-01-21",
    8: "2025-01-29"
}

clubs_en_ldc = sorted([
    "Arsenal",
    "Aston Villa",
    "Atalanta",
    "Atletico",
    "Barcelona",
    "Bayern",
    "Benfica",
    "Bologna",
    "Brest",
    "Brugge",
    "Celtic",
    "Copenhagen",
    "Crvena Zvezda",
    "Dortmund",
    "Feyenoord",
    "Girona",
    "Inter",
    "Juventus",
    "Leipzig",
    "Leverkusen",
    "Lille",
    "Liverpool",
    "Man City",
    "Milan",
    "Monaco",
    "Paris SG",
    "PSV",
    "Real Madrid",
    "Salzburg",
    "Shakhtar",
    "Slovan Bratislava",
    "Sparta Praha",
    "Sporting",
    "Sturm Graz",
    "Stuttgart",
    "Young Boys",
    "Zagreb",
])

calendrier = {
    "Journée 1": [
        ("Young Boys", "Aston Villa"),
        ("Juventus", "PSV"),
        ("Milan", "Liverpool"),
        ("Bayern", "Zagreb"),
        ("Real Madrid", "Stuttgart"),
        ("Sporting", "Lille"),
        ("Bologna", "Shakhtar"),
        ("Sparta Praha", "Salzburg"),
        ("Brugge", "Dortmund"),
        ("Celtic", "Slovan Bratislava"),
        ("Man City", "Inter"),
        ("Paris SG", "Girona"),
        ("Atalanta", "Arsenal"),
        ("Atletico", "Leipzig"),
        ("Brest", "Sturm Graz"),
        ("Monaco", "Barcelona"),
        ("Leverkusen", "Feyenoord"),
        ("Crvena Zvezda", "Benfica"),
    ],
    "Journée 2": [
        ("Liverpool", "Bologna"),
        ("Aston Villa", "Bayern"),
        ("Zagreb", "Monaco"),
        ("Leipzig", "Juventus"),
        ("Sturm Graz", "Brugge"),
        ("Dortmund", "Celtic"),
        ("Inter", "Crvena Zvezda"),
        ("PSV", "Sporting"),
        ("Slovan Bratislava", "Man City"),
        ("Arsenal", "Paris SG"),
        ("Barcelona", "Young Boys"),
        ("Leverkusen", "Milan"),
        ("Atletico", "Benfica"),
        ("Lille", "Real Madrid"),
        ("Salzburg", "Brest"),
        ("Stuttgart", "Sparta Praha"),
        ("Feyenoord", "Girona"),
        ("Atalanta", "Shakhtar"),
    ],
    "Journée 3": [
        ("Benfica", "Atletico"),
        ("Monaco", "Crvena Zvezda"),
        ("Aston Villa", "Bologna"),
        ("Arsenal", "Shakhtar"),
        ("Girona", "Slovan Bratislava"),
        ("PSV", "Sporting"),
        ("Real Madrid", "Dortmund"),
        ("Sturm Graz", "Brugge"),
        ("Liverpool", "Leipzig"),
        ("Celtic", "Atalanta"),
        ("Brugge", "Aston Villa"),
        ("Milan", "Brugge"),
        ("Feyenoord", "Salzburg"),
        ("Man City", "Sparta Praha"),
        ("Paris SG", "PSV"),
        ("Sporting", "Lille"),
        ("Inter", "Young Boys"),
        ("Barcelona", "Bayern"),
    ],
    "Journée 4": [
        ("PSV", "Girona"),
        ("Slovan Bratislava", "Zagreb"),
        ("Lille", "Juventus"),
        ("Liverpool", "Leverkusen"),
        ("Sporting", "Man City"),
        ("Celtic", "Leipzig"),
        ("Aston Villa", "Bologna"),
        ("Brugge", "Aston Villa"),
        ("Real Madrid", "Milan"),
        ("Arsenal", "Shakhtar"),
        ("Bayern", "Benfica"),
        ("Inter", "Arsenal"),
        ("Paris SG", "Atletico"),
        ("Feyenoord", "Salzburg"),
        ("Atalanta", "Celtic"),
        ("Young Boys", "Barcelona"),
        ("Crvena Zvezda", "Monaco"),
        ("Sturm Graz", "Dortmund"),
    ],
    "Journée 5": [
        ("Feyenoord", "Bayern"),
        ("Sparta Praha", "Atletico"),
        ("Inter", "Leipzig"),
        ("Man City", "Feyenoord"),
        ("Barcelona", "Brest"),
        ("Leverkusen", "Salzburg"),
        ("Young Boys", "Atalanta"),
        ("Celtic", "Brugge"),
        ("Zagreb", "Dortmund"),
        ("Liverpool", "Real Madrid"),
        ("Lille", "Bologna"),
        ("Benfica", "Monaco"),
        ("PSV", "Shakhtar"),
        ("Slovan Bratislava", "Milan"),
        ("Sporting", "Arsenal"),
        ("Sturm Graz", "Girona"),
        ("Paris SG", "Salzburg"),
        ("Crvena Zvezda", "Stuttgart"),
    ],
    "Journée 6": [
        ("Dortmund", "Barcelona"),
        ("Liverpool", "Man City"),
        ("Atalanta", "Real Madrid"),
        ("Leverkusen", "Inter"),
        ("Atletico", "Slovan Bratislava"),
        ("Brugge", "Sporting"),
        ("Benfica", "Bologna"),
        ("Arsenal", "Monaco"),
        ("Milan", "Crvena Zvezda"),
        ("Bayern", "Paris SG"),
        ("Girona", "Liverpool"),
        ("Zagreb", "Celtic"),
        ("Salzburg", "PSV"),
        ("Young Boys", "Atalanta"),
        ("Juventus", "Man City"),
        ("Feyenoord", "Sparta Praha"),
        ("Lille", "Sturm Graz"),
        ("Shakhtar", "Bayern"),
    ],
    "Journée 7": [
        ("Monaco", "Aston Villa"),
        ("Atalanta", "Sturm Graz"),
        ("Atletico", "Leverkusen"),
        ("Benfica", "Barcelona"),
        ("Bologna", "Dortmund"),
        ("Brugge", "Juventus"),
        ("Crvena Zvezda", "PSV"),
        ("Celtic", "Young Boys"),
        ("Feyenoord", "Bayern"),
        ("Lille", "Feyenoord"),
        ("Liverpool", "Lille"),
        ("Man City", "Brugge"),
        ("Paris SG", "Man City"),
        ("Real Madrid", "Salzburg"),
        ("Shakhtar", "Brest"),
        ("Slovan Bratislava", "Stuttgart"),
        ("Sparta Praha", "Inter"),
        ("Sporting", "Leipzig"),
    ],
    "Journée 8": [
        ("Aston Villa", "Celtic"),
        ("Barcelona", "Atalanta"),
        ("Bayern", "Slovan Bratislava"),
        ("Brest", "Real Madrid"),
        ("Dortmund", "Shakhtar"),
        ("Girona", "Arsenal"),
        ("Inter", "Monaco"),
        ("Juventus", "Benfica"),
        ("Leipzig", "Sporting"),
        ("Leverkusen", "Sparta Praha"),
        ("Liverpool", "PSV"),
        ("Man City", "Brugge"),
        ("Milan", "Zagreb"),
        ("Paris SG", "Stuttgart"),
        ("Salzburg", "Atletico"),
        ("Sporting", "Bologna"),
        ("Sturm Graz", "Leipzig"),
        ("Young Boys", "Crvena Zvezda"),
    ],
}

# 1. CONSTANTES ET LISTES
# -----------------------
CLUBS_SIMULATOR = [
    "Arsenal", "Aston Villa", "Atalanta", "Atletico", "Barcelona", "Bayern", "Benfica", 
    "Bologna", "Brest", "Brugge", "Celtic", "Copenhagen", "Crvena Zvezda", "Dortmund", 
    "Feyenoord", "Girona", "Inter", "Juventus", "Leipzig", "Leverkusen", "Lille", 
    "Liverpool", "Man City", "Milan", "Monaco", "Paris SG", "PSV", "Real Madrid", 
    "Salzburg", "Shakhtar", "Slovan Bratislava", "Sparta Praha", "Sporting", 
    "Sturm Graz", "Stuttgart", "Young Boys", "Zagreb"
]

MAPPING_WIKI = {
    # --- ANGLETERRE ---
    "Arsenal FC": "Arsenal",
    "Manchester City": "Man City",
    "Man City": "Man City",
    "Chelsea FC": "Chelsea",
    "Liverpool FC": "Liverpool",
    "Aston Villa": "Aston Villa",

    # --- ESPAGNE ---
    "Real Madrid": "Real Madrid",
    "Real Madrid CF": "Real Madrid",
    "Atlético de Madrid": "Atletico",
    "Atlético Madrid": "Atletico",
    "FC Barcelone": "Barcelona",
    "FC Barcelona": "Barcelona",
    "Girona FC": "Girona",

    # --- ALLEMAGNE ---
    "Bayern Munich": "Bayern",
    "Bayern München": "Bayern",
    "FC Bayern München": "Bayern",
    "Borussia Dortmund": "Dortmund",
    "Bayer Leverkusen": "Leverkusen",
    "Bayer 04 Leverkusen": "Leverkusen",
    "VfB Stuttgart": "Stuttgart",
    "RB Leipzig": "Leipzig",

    # --- FRANCE ---
    "Paris Saint-Germain": "Paris SG",
    "Paris SG": "Paris SG",
    "AS Monaco": "Monaco",
    "Stade Brestois 29": "Brest",
    "LOSC Lille": "Lille",

    # --- ITALIE ---
    "Atalanta Bergame": "Atalanta",
    "Atalanta BC": "Atalanta",
    "Atalanta": "Atalanta",
    "Inter Milan": "Inter",
    "Internazionale": "Inter",
    "Juventus FC": "Juventus",
    "AC Milan": "Milan",
    "Bologna FC": "Bologna",

    # --- PORTUGAL ---
    "Sporting CP": "Sporting",
    "SL Benfica": "Benfica",

    # --- PAYS-BAS ---
    "PSV Eindhoven": "PSV",
    "Feyenoord Rotterdam": "Feyenoord",

    # --- BELGIQUE ---
    "Club Bruges": "Brugge",
    "Club Brugge": "Brugge",

    # --- AUTRES ---
    "Celtic FC": "Celtic",
    "Celtic": "Celtic",
    "FC Copenhague": "Copenhagen",
    "F.C. Copenhagen": "Copenhagen",
    "FC Copenhagen": "Copenhagen",
    "Red Star Belgrade": "Crvena Zvezda",
    "Étoile Rouge de Belgrade": "Crvena Zvezda",
    "Crvena Zvezda": "Crvena Zvezda",
    "SK Slovan Bratislava": "Slovan Bratislava",
    "Sparta Prague": "Sparta Praha",
    "AC Sparta Praha": "Sparta Praha",
    "SK Sturm Graz": "Sturm Graz",
    "Shakhtar Donetsk": "Shakhtar",
    "Red Bull Salzburg": "Salzburg",
    "FC Red Bull Salzburg": "Salzburg",
    "Young Boys": "Young Boys",
    "BSC Young Boys": "Young Boys",
    "Dinamo Zagreb": "Zagreb",
    "GNK Dinamo Zagreb": "Zagreb",
}

# 2. MAPPING ELO (pour l'API clubelo.com)
# ----------------------------------------
MAPPING_ELO = {
    # Anglais
    "Man City": "Manchester City",
    "Arsenal": "Arsenal",
    "Liverpool": "Liverpool",
    "Aston Villa": "Aston Villa",
    
    # Allemands
    "Bayern": "Bayern Munich",
    "Leipzig": "RB Leipzig",
    "Leverkusen": "Bayer Leverkusen",
    "Dortmund": "Borussia Dortmund",
    "Stuttgart": "VfB Stuttgart",
    
    # Français
    "Paris SG": "Paris Saint Germain",
    "Lille": "LOSC Lille",
    "Brest": "Brest",
    "Monaco": "Monaco",
    
    # Italiens
    "Inter": "Inter",
    "Milan": "AC Milan",
    "Juventus": "Juventus",
    "Atalanta": "Atalanta",
    "Bologna": "Bologna",
    
    # Espagnols
    "Barcelona": "Barcelona",
    "Real Madrid": "Real Madrid",
    "Atletico": "Atletico Madrid",
    "Girona": "Girona",
    
    # Portugais
    "Benfica": "Benfica",
    "Sporting": "Sporting CP",
    
    # Néerlandais
    "PSV": "PSV Eindhoven",
    "Feyenoord": "Feyenoord",
    
    # Belges
    "Brugge": "Club Brugge",
    
    # Autres
    "Celtic": "Celtic",
    "Copenhagen": "FC Copenhagen",
    "Zagreb": "Dinamo Zagreb",
    "Salzburg": "Red Bull Salzburg",
    "Sparta Praha": "Sparta Prague",
    "Slovan Bratislava": "Slovan Bratislava",
    "Young Boys": "Young Boys",
    "Shakhtar": "Shakhtar Donetsk",
    "Crvena Zvezda": "Red Star",
    "Sturm Graz": "Sturm Graz",
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

    # D. APPEL DE LA NORMALISATION
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
    url_test = "https://fr.wikipedia.org/wiki/Phase_de_championnat_de_la_Ligue_des_champions_de_l%27UEFA_2024-2025#Classement"
    
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
    # URL 2024-2025
    url_test = "https://fr.wikipedia.org/wiki/Phase_de_championnat_de_la_Ligue_des_champions_de_l%27UEFA_2024-2025"
    
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
            # Utilise le mapping Elo
            match_name = MAPPING_ELO.get(mon_club, mon_club)
            
            if match_name in elo_database:
                elo_simulator[mon_club] = elo_database[match_name]
            elif mon_club in elo_database:
                elo_simulator[mon_club] = elo_database[mon_club]
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
            # 1. On essaie d'abord le mapping
            nom_elo = MAPPING_ELO.get(club, club)
            
            if nom_elo in elo_raw:
                elo_simu[club] = elo_raw[nom_elo]
            elif club in elo_raw:
                elo_simu[club] = elo_raw[club]
            else:
                # Recherche insensible à la casse
                found = False
                for k, v in elo_raw.items():
                    if k.lower() == club.lower() or k.lower() == nom_elo.lower():
                        elo_simu[club] = v
                        found = True
                        break
                if not found:
                    # Valeur par défaut
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

url = "https://fr.wikipedia.org/wiki/Phase_de_championnat_de_la_Ligue_des_champions_de_l%27UEFA_2024-2025"
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

"""