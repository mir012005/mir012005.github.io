import pandas as pd
import requests
import io

def get_donnees_from_wikipedia(url):
    # 1. LE DÉGUISEMENT (Contourne l'erreur 403 Forbidden)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"📡 Connexion à {url}...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Vérifie si ça a marché (200 OK)
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return None

    # 2. LECTURE DES TABLEAUX
    # On passe le texte HTML à Pandas
    try:
        tables = pd.read_html(io.StringIO(response.text))
    except ValueError:
        print("❌ Aucun tableau trouvé sur la page.")
        return None

    # 3. TROUVER LE BON TABLEAU (LE CLASSEMENT)
    # On cherche un tableau qui contient les colonnes "Team" et "Pts"
    df_classement = None
    for t in tables:
        if "Équipe" in t.columns and "Pts" in t.columns and "G" in t.columns:
            df_classement = t
            break
    
    if df_classement is None:
        print("❌ Tableau de classement introuvable.")
        return None

    print("✅ Tableau trouvé ! Transformation en format simulator.py...")

    # 4. NETTOYAGE ET FORMATAGE
    # Création des dictionnaires vides
    points = {}
    diff_buts = {}
    buts = {}
    buts_ext = {} # Wikipedia donne rarement les buts extérieurs dans le tableau principal, on mettra 0
    nb_victoires = {}
    nb_victoires_ext = {} # Idem, souvent absent, on mettra 0 ou on estimera

    # Liste ordonnée des clubs (Le classement lui-même)
    # On nettoie les noms (ex: "Real Madrid (Q)" -> "Real Madrid")
    df_classement['Équipe'] = df_classement['Équipe'].astype(str).str.replace(r'\[.*\]', '', regex=True) # Enlève les [a]
    df_classement['Équipe'] = df_classement['Équipe'].str.replace(r' \(.*\)', '', regex=True) # Enlève les (Q)
    
    classement_list = df_classement['Équipe'].tolist()

    # Remplissage des données
    for index, row in df_classement.iterrows():
        club = row['Équipe']
        
        # Récupération sécurisée des valeurs
        try:
            points[club] = int(row['Pts'])
            diff_buts[club] = int(row['diff']) 
            buts[club] = int(row['Bp'])   
            nb_victoires[club] = int(row['G'])
            
            # Valeurs par défaut car souvent absentes des tableaux résumés
            buts_ext[club] = 0 
            nb_victoires_ext[club] = 0 
            
        except KeyError as e:
            print(f"⚠️ Colonne manquante pour {club}: {e}")

    # 5. CONSTRUCTION DU DICTIONNAIRE FINAL
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

# VOTRE LISTE OFFICIELLE (Copiée de simulator.py pour référence)
CLUBS_SIMULATOR = [
    "Paris SG", "Real Madrid", "Man City", "Bayern", "Liverpool", "Inter", "Chelsea", 
    "Dortmund", "Barcelona", "Arsenal", "Leverkusen", "Atletico", "Benfica", "Atalanta", 
    "Villarreal", "Juventus", "Frankfurt", "Brugge", "Tottenham", "PSV", "Ajax", "Napoli", 
    "Sporting", "Olympiakos", "Slavia Praha", "Bodoe Glimt", "Marseille", "FC Kobenhavn", 
    "Monaco", "Galatasaray", "St Gillis", "Karabakh Agdam", "Bilbao", "Newcastle", 
    "Paphos", "Kairat"
]

# LE DICTIONNAIRE DE TRADUCTION (Wiki -> Simulator)
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

def normaliser_noms_clubs(df_classement):
    """
    Remplace les noms scrapés par les noms du projet.
    """
    # 1. Nettoyage de base (enlever les [a], (Q), espaces inutiles)
    df_classement['Équipe'] = df_classement['Team'].astype(str).str.replace(r'\[.*\]', '', regex=True)
    df_classement['Équipe'] = df_classement['Team'].str.replace(r' \(.*\)', '', regex=True)
    df_classement['Équipe'] = df_classement['Team'].str.strip()

    # 2. Application du Mapping
    # On utilise .replace() de pandas qui prend un dictionnaire
    # Si le nom n'est pas dans le dictionnaire, il reste inchangé
    df_classement['Team'] = df_classement['Team'].replace(MAPPING_WIKI)

    # 3. Vérification de sécurité (Crucial !)
    # On regarde si des clubs scrapés ne sont PAS dans notre liste officielle
    clubs_inconnus = []
    for club in df_classement['Team']:
        if club not in CLUBS_SIMULATOR:
            clubs_inconnus.append(club)
    
    if clubs_inconnus:
        print(f"⚠️ ATTENTION : Noms de clubs non reconnus détectés : {clubs_inconnus}")
        print("-> Ajoutez-les dans le dictionnaire MAPPING_WIKI.")
    else:
        print("✅ Tous les noms de clubs correspondent parfaitement !")

    return df_classement


# --- EXEMPLE D'UTILISATION (Si la page existait) ---
# url_imaginaire = "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Champions_League_league_phase"
# On utilise une vraie URL pour tester (Classement actuel de Premier League par exemple, la structure est similaire)
url_test = "https://fr.wikipedia.org/wiki/Phase_de_championnat_de_la_Ligue_des_champions_de_l%27UEFA_2025-2026#Classement"

data = get_donnees_from_wikipedia(url_test)

if data:
    print("\n🎉 VOICI LE CODE A COPIER DANS SIMULATOR.PY :\n")
    print(f"données_J_X = {data}")