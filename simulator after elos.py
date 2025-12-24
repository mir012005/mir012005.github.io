import random as rd
import math

# On importe la fonction de chargement qu'on a créée juste avant
from elo_manager import get_current_elos

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

class ChampionsLeagueSimulator:
    # On ajoute un argument optionnel 'custom_elos'
    def __init__(self, custom_elos=None):
        print("🤖 Initialisation du Simulateur...")
        
        if custom_elos:
            # Si on vous donne des données précises, on les utilise
            self.elos = custom_elos.copy() # .copy() est important pour ne pas casser l'original
            print("-> Chargement de données personnalisées/historiques.")
        else:
            # Sinon, on prend le direct par défaut
            self.elos = get_current_elos()
            print("-> Chargement des données LIVE.")

    def elo_of(self, team_name):
        """Récupère l'Elo d'une équipe (avec sécurité si inconnue)."""
        return self.elos.get(team_name, 1450.0)
    
    def win_expectation(self, club1,club2):
        e1 = self.elo_of(club1)
        e2 = self.elo_of(club2)
        assert(type(e1) != str and type(e2) != str)
        return 1/(1+10**((e2-e1-100)/400))
    
    def coeff_poisson(self, club1,club2,s):
        # retourne le coeff de la loi de poisson donnant le nb de buts marqués par club1 si s='H' - ou club2 si s='A' - 
        # club1 jouant à domicile
        assert(s == 'H' or s == 'A')
        w = self.win_expectation(club1,club2)
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

    def proba_par_but(self, k,club1,club2,s):
        # retourne la proba pour club1 si s='H' - pour club2 si s='A' - de marquer k buts dans le match se jouant chez club1
        param = self.coeff_poisson(club1,club2,s)
        return (param**k)*math.exp(-param)/math.factorial(k)
    
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

    def generate_score(self, proba_home):
        """
        Génère un score réaliste basé sur la probabilité.
        (On peut remplacer ça par une Loi de Poisson plus tard pour plus de précision)
        """
        # Logique simplifiée pour l'exemple
        rand = random.random()
        
        # Définition des seuils
        seuil_win = proba_home - 0.12 # Marge pour le nul
        seuil_draw = proba_home + 0.12
        
        if rand < seuil_win:
            # Victoire Domicile
            buts_dom = random.randint(1, 4)
            buts_ext = random.randint(0, buts_dom - 1)
            resultat_reel = 1.0 # 1 point pour Elo (Gagné)
        elif rand > seuil_draw:
            # Victoire Extérieur
            buts_ext = random.randint(1, 4)
            buts_dom = random.randint(0, buts_ext - 1)
            resultat_reel = 0.0 # 0 point pour Elo (Perdu)
        else:
            # Match Nul
            buts_dom = random.randint(0, 2)
            buts_ext = buts_dom
            resultat_reel = 0.5 # 0.5 point pour Elo (Nul)
            
        return [buts_dom, buts_ext], resultat_reel

    def play_match(self, home_team, away_team):
        """
        JOUE LE MATCH ET MET À JOUR LES ELOS.
        C'est la fonction principale.
        """
        # 1. Calcul Proba Avant Match
        proba_home = self.calculate_win_proba(home_team, away_team)
        
        # 2. Simulation du Score
        score, resultat_reel = self.generate_score(proba_home)
        
        # 3. MISE À JOUR DES ELOS (La partie dynamique)
        elo_home_old = self.get_elo(home_team)
        elo_away_old = self.get_elo(away_team)
        
        # Formule de mise à jour Elo : Nouveau = Ancien + K * (Réel - Attendu)
        delta = self.k_factor * (resultat_reel - proba_home)
        
        self.elos[home_team] = elo_home_old + delta
        self.elos[away_team] = elo_away_old - delta
        
        return {
            "match": f"{home_team} - {away_team}",
            "score": score,
            "proba_init": round(proba_home * 100, 1),
            "elo_evo": round(delta, 1) # De combien l'elo a changé
        }

    def simuler_journee(self, liste_matchs):
        """Prend une liste de matchs [[Dom, Ext], ...] et simule tout."""
        resultats_journee = []
        for match in liste_matchs:
            # On gère le format [Dom, Ext] ou [Dom, Ext, [Score...]]
            dom, ext = match[0], match[1]
            
            res = self.play_match(dom, ext)
            resultats_journee.append(res)
            
        return resultats_journee

# ==========================================
# EXEMPLE D'UTILISATION (MAIN)
# ==========================================
if __name__ == "__main__":
    # 1. On instancie la classe (Chargement des données UNE SEULE FOIS)
    simu = ChampionsLeagueSimulator()
    
    print(f"\nForce initiale PSG : {round(simu.get_elo('Paris SG'))}")
    print(f"Force initiale Man City : {round(simu.get_elo('Man City'))}")
    
    # 2. Définition d'une journée fictive
    matchs_j1 = [
        ["Paris SG", "Man City"],
        ["Real Madrid", "Brest"], # Brest n'est pas dans le top, aura 1450 par défaut
        ["Liverpool", "Milan"]
    ]
    
    print("\n--- DÉBUT SIMULATION J1 ---")
    res_j1 = simu.simuler_journee(matchs_j1)
    
    for r in res_j1:
        print(f"{r['match']} : {r['score'][0]}-{r['score'][1]} (Proba PSG: {r['proba_init']}%) [Elo: {r['elo_evo']}]")
        
    print("\n--- APRÈS J1 (Mise à jour automatique) ---")
    print(f"Nouvelle force PSG : {round(simu.get_elo('Paris SG'))}")
    print(f"Nouvelle force Man City : {round(simu.get_elo('Man City'))}")