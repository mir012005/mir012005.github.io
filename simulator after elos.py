import random as rd
import math
import copy

# On importe la fonction de chargement qu'on a créée juste avant
from elo_manager import get_current_elos
from scraper import calendrier, clubs_en_ldc

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

def dico_de_données(classement,points,diff_buts,buts,buts_ext,nb_victoires,nb_victoires_ext):
    return {"classement" : classement , "points" : points , "diff_buts" : diff_buts , "buts" : buts ,
            "buts_ext" : buts_ext , "nb_victoires" : nb_victoires , "nb_victoires_ext" : nb_victoires_ext}

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
        
        self.probas_par_matchs = {}

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
    
    def dico_de_proba(self, N=3):  # N représente le nombre de proba par buts que l'on stocke pour chaque match (on commence par N=3 
        # car on est à peu près sûrs que les probas de marquer 0,1 ou 2 buts seront utiles quels que soient le match et l'équipe)
        # retourne un dictionnaire ayant pour clés les matchs possibles et comme valeurs associées deux listes correspondant
        # aux probas pour l'équipe à domicile, et pour celle à l'extérieur
        d = {}
        for club1 in clubs_en_ldc:
            for club2 in clubs_en_ldc:
                if club2 != club1:
                    d[(club1,club2)] = [[self.proba_par_but(k,club1,club2,'H') for k in range(N)]
                                        ,[self.proba_par_but(k,club1,club2,'A') for k in range(N)]]
                    
        self.probas_par_matchs = d
        return d
            
    

    def simule_nb_buts(self, club1,club2,s):
        # retourne un tirage du nb de buts marqués par club1 si s='H' - par club2 si s='A' - le match se jouant chez club1
        assert(s == 'H' or s == 'A')
        if s == 'H':
            b = 0
        else:
            b = 1
        probas = self.probas_par_matchs[(club1,club2)][b]
        u = rd.random()
        k = 0 ; t = probas[0]
        while t < u:
            k += 1
            if k < len(probas):
                t += probas[k]
            else:
                p = self.proba_par_but(k,club1,club2,s)
                t += p
                probas = probas + [p]
                self.probas_par_matchs[(club1,club2)][b] = probas
                # On ajoute la valeur au dictionnaire si on en a eu besoin
        return k

    def retourne_score(self, club1,club2):
        # retourne une simulation du score du match entre club1 et club2, club1 jouant à domicile
        return (self.simule_nb_buts(club1,club2,'H'), self.simule_nb_buts(club1,club2,'A'))

    def simuler_match(self, club1,club2,points,diff_buts,buts,buts_exterieur,nb_victoires,nb_victoires_ext,resultats):
        (i,j) = self.retourne_score(club1,club2)
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

    def simulation_ligue(self, données={"classement" : None, "points" : None, "diff_buts" : None, "buts" : None, "buts_ext" : None,
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
                self.simuler_match(matchs[i][0],matchs[i][1],points,diff_buts,buts,buts_exterieur,nb_victoires,nb_victoires_ext,resultats)
        
        nclassement = sorted(classement, key = lambda x: (points[x],diff_buts[x],buts[x],buts_exterieur[x],nb_victoires[x],nb_victoires_ext[x]),
                            reverse=True)

        d = dico_de_données(nclassement, points , diff_buts , buts , buts_exterieur , nb_victoires , nb_victoires_ext)
        return d | {"résultats" : resultats}

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