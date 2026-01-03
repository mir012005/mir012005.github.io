import pandas as pd
import math
import random as rd
import copy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages as pdf
from IPython.display import FileLink


#ligne 461 en dessous de: def distribution_position_par_club

#distribution_probas_classement = distribution_position_par_club()

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


#=========================================================================================================================
#en dessous de: def distribution_points_par_club

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


#======================================================================================================================
#en dessous de: def distribution_par_position

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
"""

#============================================================================================================================
#En dessous de: def ajouter_matchs_donnés

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
"""

#======================================================================================================================
#en dessouis de def: enjeux_pour

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

#===============================================================================================================================
#En dessous de def get_web_importance_matchs

        # =============================================================================
        #  PONT API (A RAJOUTER A LA FIN DE SIMULATION.PY)


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

#===============================================================================================================================
#En dessous de def get_web_isimulation

"""
A supprimer plus tard

def get_probas_top8_qualif(nb_simulations=1000, journee_depart=6):
    # 1. MAPPING TEMPOREL (Comme pour la simulation club)
    historique_donnees = {
        5: données_J5,
        6: données_J6,
        7: données_J7
        # Ajoutez 8: données_J8 si disponible
    }
    
    # On récupère les données correspondantes (par défaut J6)
    etat = historique_donnees.get(journee_depart, données_J6)
    
    # Si on part de la J5, on doit simuler à partir de la J6 (donc debut=6)
    # ATTENTION : Dans votre code, debut est inclusif.
    debut_simu = journee_depart + 1
    
    # 2. Simulation
    # Si on est déjà à la fin (ex: départ J8), la simulation ne fait rien, ce qui est logique.
    distrib_clubs = distribution_position_par_club(N=nb_simulations, données=etat, debut=debut_simu, fin=8)
    
    # 3. Préparation des listes
    liste_qualif = []
    liste_top8 = []
    
    for club in clubs_en_ldc:
        p_qualif = proba_qualification(club, distrib_clubs)
        p_top8 = proba_top_8(club, distrib_clubs)
        
        if p_qualif > 0.001:
            liste_qualif.append({"club": club, "proba": round(p_qualif * 100, 1)})
            
        if p_top8 > 0.001:
            liste_top8.append({"club": club, "proba": round(p_top8 * 100, 1)})
            
    # 4. Tri décroissant
    liste_qualif.sort(key=lambda x: x["proba"], reverse=True)
    liste_top8.sort(key=lambda x: x["proba"], reverse=True)
    
    return {
        "day_used": journee_depart,
        "ranking_qualif": liste_qualif,
        "ranking_top8": liste_top8
    }

"""
#===============================================================================================================================
#En dessous de def get_match prediction

"""
def get_global_ranking_detailed(n_simulations=1000, start_day=7, end_day=8):
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
"""

"""
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
"""

#===============================================================================================================================
#En dessous de def get_probas_top8_qualif



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

for j in range(1, 5):
    matchs_j = matchs_par_journee.get(j, [])
    if matchs_j:
        états[j] = ajouter_matchs_donnés(états[j-1], matchs_j)

with open('CODE_A_COPIER.py', 'w', encoding='utf-8') as f:
    for j in range(1, 5):
        if j in matchs_par_journee and matchs_par_journee[j]:
            f.write(f"matchs_J{j} = [\n")
            for m in matchs_par_journee[j]:
                f.write(f"    {m},\n")
            f.write("]\n\n")
    for j in range(1, 5):
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

#==================================================================================================================
#Dans App.py

"""
@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    try:
        data = request.json
        club = data.get('club')
        
        print(f"--> Simulation demandée pour : {club}")
        
        if not club:
            return jsonify({"error": "Nom de club manquant"}), 400

        # Appel avec "simulator."
        resultats = simulator.get_web_simulation(club)
        
        if "error" in resultats:
            return jsonify(resultats), 404
            
        return jsonify(resultats)
        
    except Exception as e:
        print(f"ERREUR : {e}")
        return jsonify({"error": str(e)}), 500

"""
"""
<section id="ranking" class="page" style="display:none;">
            <h2>🏆 Classement Projeté (Moyenne)</h2>
            
            <div class="controls-bar">
                <div class="control-group">
                    <label>De :</label>
                    <select id="startDay">
                        <option value="1" selected>J0</option><option value="1">J1</option><option value="2">J2</option>
                        <option value="3">J3</option><option value="4">J4</option>
                        <option value="5">J5</option><option value="6">J6</option>
                        <option value="7">J7</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>À :</label>
                    <select id="endDay">
                        <option value="1">J1</option><option value="2">J2</option>
                        <option value="3">J3</option><option value="4">J4</option>
                        <option value="5">J5</option><option value="6">J6</option>
                        <option value="7">J7</option><option value="8" selected>J8</option>
                    </select>
                </div>
                <button class="action-btn" onclick="chargerClassement()">🔄 Calculer</button>
            </div>

            <div class="table-container">
                <table class="ranking-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th style="text-align:left;">Club</th>
                            <th>Points</th>
                            <th>Diff. Buts</th>
                            <th>Buts</th>
                            <th class="secondary-stat">Buts Ext.</th>
                            <th>Victoires</th>
                            <th class="secondary-stat">Vict. Ext.</th>
                        </tr>
                    </thead>
                    <tbody id="rankingBody">
                        <tr><td colspan="8">Cliquez sur Calculer...</td></tr>
                    </tbody>
                </table>
            </div>
            
            <div class="legend">
                <span class="dot green"></span> Qualif Directe (1-8)
                <span class="dot orange"></span> Barrages (9-24)
                <span class="dot red"></span> Éliminé (25-36)
            </div>
        </section>
"""

"""
@app.route('/api/ranking', methods=['POST'])
def get_ranking():
    try:
        # Récupération des données JSON envoyées par le site
        data = request.json
        
        # Par défaut : Simulation complète (J1 à J8) si rien n'est précisé
        start = int(data.get('start', 1))
        end = int(data.get('end', 8))

        # Appel de la nouvelle fonction wrapper
        result = simulator.get_simulation_flexible(n_simulations=1000, start_day=start, end_day=end)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
"""
#==================================================================================================================================
#App.py avant nettoyage
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

import simulator 

app = Flask(__name__, static_folder='.')
CORS(app) 

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/clubs', methods=['GET'])
def get_clubs():
    try:
        clubs = simulator.get_clubs_list()
        return jsonify(clubs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    try:
        data = request.json or {}
        club = data.get('club')
        day = int(data.get('day', 6)) # On récupère le jour
        
        if not club:
            return jsonify({"error": "Club manquant"}), 400

        # Appel de la fonction web simulation
        resultats = simulator.get_web_simulation(club, journee_depart=day)
        
        if "error" in resultats:
            return jsonify(resultats), 404
            
        return jsonify(resultats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/seuils', methods=['GET'])
def get_seuils():
    try:
        print("--> Calcul des seuils globaux...")
        # Appel avec "simulator."
        data = simulator.get_web_seuils(nb_simulations=1000)
        return jsonify(data)
    except Exception as e:
        print(f"ERREUR : {e}")
        return jsonify({"error": str(e)}), 500

#============ 19/12/2025===============================
@app.route('/api/predict-match', methods=['POST'])
def predict_match():
    try:
        data = request.json
        home = data.get('home')
        away = data.get('away')
        
        # Appel de la fonction du simulateur
        result = simulator.get_match_prediction(home, away)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rankings', methods=['POST'])
def get_rankings():
    try:
        data = request.json or {}
        
        # On récupère le début et la fin demandés
        # Par défaut : du début (0) à la fin (8)
        start = int(data.get('start', 0))
        end = int(data.get('end', 8))
        
        print(f"--> Simulation de J{start} jusqu'à J{end}...")
        
        # Appel de la fonction flexible avec les deux bornes
        results = simulator.get_simulation_flexible(n_simulations=1000, start_day=start, end_day=end)
        
        return jsonify(results)
        
    except Exception as e:
        print(f"ERREUR RANKING: {e}")
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------
# 2. Route pour les PROBABILITÉS (Top 8 / Qualif)
# -----------------------------------------------------
@app.route('/api/rankings_top8_qualif', methods=['POST']) # Changé en POST
def get_probas_api():
    try:
        data = request.json or {}
        day = int(data.get('day', 6))
        
        print(f"--> Calcul Probas (Base J{day})...")
        
        # Appel de la fonction probas
        results = simulator.get_probas_top8_qualif(nb_simulations=1000, journee_depart=day)
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/probas', methods=['POST'])
def get_probas():
    try:
        data = request.json or {}
        # On récupère la journée demandée (par défaut 0 ou 6 selon votre préférence)
        day = int(data.get('day', 6))
        
        # Appel de votre fonction
        results = simulator.get_probas_top8_qualif(nb_simulations=1000, journee_depart=day)
        
        return jsonify(results)
    except Exception as e:
        print(f"Erreur Probas: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/match-impact', methods=['POST'])
def get_match_impact():
    try:
        data = request.json or {}
        club = data.get('club')
        journee = int(data.get('journee', 7))
        journee_donnees = int(data.get('journee_donnees', 6))
        
        if not club:
            return jsonify({"error": "Club manquant"}), 400
        
        result = simulator.get_web_match_impact(club, journee, nb_simulations=1000, journee_donnees=journee_donnees)
        
        if "error" in result:
            return jsonify(result), 404
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/all-matches-impact', methods=['POST'])
def get_all_matches_impact():
    try:
        data = request.json or {}
        journee = int(data.get('journee', 7))
        journee_donnees = int(data.get('journee_donnees', 6))
        
        result = simulator.get_web_all_matches_impact(journee, nb_simulations=500, journee_donnees=journee_donnees)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/next-match-scenarios', methods=['POST'])
def get_next_match_scenarios():
    try:
        data = request.json or {}
        club = data.get('club')
        journee_donnees = int(data.get('journee_donnees', 6))
        
        if not club:
            return jsonify({"error": "Club manquant"}), 400
        
        result = simulator.get_web_club_next_match_scenarios(club, nb_simulations=1000, journee_donnees=journee_donnees)
        
        if "error" in result:
            return jsonify(result), 404
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#moi
# Route pour le Tableau de Bord Scénario
@app.route('/api/scenario', methods=['POST'])
def run_scenario():
    try:
        data = request.json
        # Paramètres envoyés par le JS
        club = data.get('club')
        result = data.get('result') # V, N ou D
        target_day = int(data.get('day', 7))      # Journée du match
        start_day = int(data.get('start_day', 6)) # Journée de départ de la simu
        
        if not club or not result: return jsonify({"error": "Données incomplètes"}), 400

        # Appel du wrapper
        analysis = simulator.get_scenario_analysis(
            club_cible=club, journee_cible=target_day, resultat_fixe=result, 
            journee_depart=start_day, n_simulations=500
        )
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route pour la Liste d'Importance
@app.route('/api/importance', methods=['POST'])
def get_importance_route():
    try:
        data = request.json
        target = int(data.get('target', 7))
        start = int(data.get('start', 6))
        
        # Appel du wrapper
        results = simulator.get_web_importance(
            journee_cible=target, journee_depart=start, n_simulations=300
        )
        if isinstance(results, dict) and "error" in results: return jsonify(results), 400
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#===============================================================================================

if __name__ == '__main__':
    print("Serveur lancé sur http://127.0.0.1:5000")
    app.run(debug=True)

"""

#========================================================================================================================
# script.js avant nettoyage

"""
// Variable globale pour stocker les instances de graphiques et éviter les bugs de superposition
let charts = {};

function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.style.display = 'none');
    document.getElementById(pageId).style.display = 'block';
}

// ==========================================
// 1. SIMULATION INDIVIDUELLE
// ==========================================
/*
//je step un peu sur houssam
async function simulate() {
    const clubInput = document.getElementById('club');
    const club = clubInput.value.trim();
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (club === "") {
        alert("Veuillez entrer un nom de club !");
        return;
    }

    showPage('results');
    resultsContainer.innerHTML = `
        <div class="loading-container">
            <div class="loader"></div>
            <p>Simulation de 1000 saisons pour ${club}...</p>
        </div>`;

    try {
        // Appel à l'API Python
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ club: club })
        });

        const data = await response.json();

        if (data.error) {
            resultsContainer.innerHTML = `<div class="error-msg">❌ Erreur : ${data.error} <br> Vérifiez l'orthographe (ex: "Paris SG", "Man City").</div>`;
            return;
        }

        // Construction de l'affichage
        resultsContainer.innerHTML = `
            <div class="club-header">
                <h3>${data.club}</h3>
                <span class="avg-points">Points moyens estimés : <strong>${data.points_moyens}</strong></span>
            </div>

            <div class="stats-grid">
                <div class="stat-box green">
                    <h4>Top 8 (Direct)</h4>
                    <span class="percentage">${data.proba_top_8}%</span>
                </div>
                <div class="stat-box yellow">
                    <h4>Barrages</h4>
                    <span class="percentage">${data.proba_barrage}%</span>
                </div>
                <div class="stat-box red">
                    <h4>Éliminé</h4>
                    <span class="percentage">${data.proba_elimine}%</span>
                </div>
            </div>

            <div class="main-chart-container">
                <canvas id="probaChart"></canvas>
            </div>
        `;

        // Dessiner le graphique
        creerGraphique('probaChart', data.distribution, `Distribution des points - ${data.club}`, '#0066cc');

    } catch (error) {
        console.error(error);
        resultsContainer.innerHTML = `<div class="error-msg">❌ Impossible de contacter le serveur Python. Vérifiez qu'il est lancé.</div>`;
    }
}

*/
// ==========================================
// 1. SIMULATION INDIVIDUELLE (MISE A JOUR)
// ==========================================
// ==========================================
// 1. SIMULATION INDIVIDUELLE (MISE A JOUR)
// ==========================================
async function simulate() {
    const clubInput = document.getElementById('club');
    const club = clubInput.value.trim();
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (club === "") {
        alert("Veuillez entrer un nom de club !");
        return;
    }

    showPage('results');
    resultsContainer.innerHTML = `
        <div class="loading-container">
            <div class="loader"></div>
            <p>Simulation de 1000 saisons pour ${club}...</p>
        </div>`;

    try {
        // Appel API
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ club: club })
        });

        const data = await response.json();

        if (data.error) {
            resultsContainer.innerHTML = `<div class="error-msg">❌ Erreur : ${data.error}</div>`;
            return;
        }

        // Construction de l'affichage
        // Notez la nouvelle div "charts-column" pour empiler les graphes
        resultsContainer.innerHTML = `
            <div class="club-header">
                <h3>${data.club}</h3>
                <span class="avg-points">Points moyens estimés : <strong>${data.points_moyens}</strong></span>
            </div>

            <div class="stats-grid">
                <div class="stat-box green">
                    <h4>Top 8 (Direct)</h4>
                    <span class="percentage">${data.proba_top_8}%</span>
                </div>
                <div class="stat-box yellow">
                    <h4>Barrages</h4>
                    <span class="percentage">${data.proba_barrage}%</span>
                </div>
                <div class="stat-box red">
                    <h4>Éliminé</h4>
                    <span class="percentage">${data.proba_elimine}%</span>
                </div>
            </div>

            <div class="charts-column">
                
                <div class="chart-box">
                    <h4>📊 Distribution des Points Finaux</h4>
                    <div class="chart-area">
                        <canvas id="pointsChart"></canvas>
                    </div>
                </div>

                <div class="chart-box">
                    <h4>🏆 Distribution du Classement Final</h4>
                    <div class="chart-area">
                        <canvas id="rankChart"></canvas>
                    </div>
                </div>

            </div>
        `;

        // Génération des graphiques
        // Graphe Points (Bleu)
        creerGraphique('pointsChart', data.distribution_points, 'Probabilité (%)', '#0066cc');
        
        // Graphe Classement (Violet pour différencier)
        creerGraphique('rankChart', data.distribution_rangs, 'Probabilité (%)', '#9b59b6');

    } catch (error) {
        console.error(error);
        resultsContainer.innerHTML = `<div class="error-msg">❌ Erreur de communication avec le serveur.</div>`;
    }
}

// ==========================================
// 2. ANALYSES GLOBALES
// ==========================================
async function chargerAnalysesGlobales() {
    // On charge les seuils
    try {
        const response = await fetch('/api/seuils');
        const data = await response.json();
        
        creerGraphique('chartTop8', data.seuil_top8, 'Points du 8ème', '#4bc0c0');
        creerGraphique('chartBarrage', data.seuil_barrage, 'Points du 24ème', '#ffcd56');
    } catch (e) {
        console.error("Erreur seuils", e);
    }

    // On charge l'importance des matchs
    try {
        const list = document.getElementById('listeImportance');
        list.innerHTML = '<div class="loader small"></div> Calcul des impacts...';
        
        const response2 = await fetch('/api/importance');
        const data2 = await response2.json();

        list.innerHTML = "";
        data2.forEach((item, index) => {
            list.innerHTML += `
                <li>
                    <span class="rank">#${index + 1}</span>
                    <span class="match-name">${item.match}</span>
                    <span class="score">Impact: <strong>${item.score}</strong></span>
                </li>`;
        });
    } catch (e) {
        console.error("Erreur importance", e);
    }
}

// ==========================================
// 3. FONCTION UTILITAIRE GRAPHIQUE
// ==========================================
function creerGraphique(canvasId, distribution, label, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Si un graphique existe déjà sur ce canvas, on le détruit proprement
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    // Trier les clés (points) par ordre croissant
    const labels = Object.keys(distribution).sort((a, b) => parseInt(a) - parseInt(b));
    // Récupérer les valeurs correspondantes et convertir en pourcentage si nécessaire
    const dataValues = labels.map(k => distribution[k] * 100); 

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels, // ex: ["10 pts", "11 pts"...]
            datasets: [{
                label: label + ' (%)',
                data: dataValues,
                backgroundColor: color,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (context) => context.raw.toFixed(1) + '%' } }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Probabilité (%)' } }
            }
        }
    });
}

// =========== 19/12/2025 16:42 début MIR ===============================
// 4. GESTION DES LOGOS ET DE LA GRILLE
// ==========================================

// Lancer le chargement dès que la page s'ouvre
document.addEventListener('DOMContentLoaded', () => {
    chargerListeClubs();
    // Si vous aviez d'autres inits, gardez-les
});

async function chargerListeClubs() {
    const grid = document.getElementById('clubsGrid');
    
    try {
        const response = await fetch('/api/clubs');
        const clubs = await response.json();
        
        // Si erreur
        if (clubs.error) {
            grid.innerHTML = `<p style="color:red">Erreur: ${clubs.error}</p>`;
            return;
        }

        // On vide le "Chargement..."
        grid.innerHTML = ''; 

        clubs.forEach(club => {
            // Création de la carte (div)
            const card = document.createElement('div');
            card.className = 'club-card';
            
            // Chemin de l'image : on suppose que c'est le nom exact + .png
            // On ajoute un timestamp ?v=1 pour éviter les soucis de cache si vous changez l'image
            const logoPath = `logos/${club}.png`; 
            
            // On construit le HTML de la carte
            // onerror : si l'image n'existe pas, on met une image par défaut
            card.innerHTML = `
                <div class="club-logo-wrapper">
                    <img src="${logoPath}" 
                         alt="${club}" 
                         onerror="this.onerror=null; this.src='logos/default.png';">
                </div>
                <span class="club-name">${club}</span>
            `;

            // RENDRE CLIQUABLE
            // Quand on clique, ça remplit le champ caché et ça lance la simulation
            card.onclick = () => {
                // 1. Remplir l'input (même s'il est caché ou sur l'autre page)
                const input = document.getElementById('club');
                if(input) input.value = club;

                // 2. Changer de page
                showPage('simulate');

                // 3. Lancer la fonction existante simulate()
                simulate();
            };

            grid.appendChild(card);
        });

    } catch (error) {
        console.error("Erreur JS:", error);
        grid.innerHTML = '<p>Impossible de charger les équipes.</p>';
    }
}
// =========== 19/12/2025 16:42 fin MIR ===============================

// ==========================================
// 5. GESTION DU DUEL (MATCH PREDICTOR)
// ==========================================

// A. AU CHARGEMENT DE LA PAGE
// On écoute l'événement "DOMContentLoaded" (quand la page est prête)
document.addEventListener('DOMContentLoaded', () => {
    // On lance la fonction qui remplit les listes
    remplirListesDuel();
});

// Fonction pour récupérer les clubs et remplir les <select>
async function remplirListesDuel() {
    try {
        // 1. On demande la liste des clubs à Python
        const res = await fetch('/api/clubs');
        const clubs = await res.json();
        
        // 2. On cible les deux menus déroulants HTML par leur ID
        const selHome = document.getElementById('selHome');
        const selAway = document.getElementById('selAway');
        
        // 3. Pour chaque club, on crée une option
        clubs.forEach(clubName => {
            // new Option(texte_visible, valeur_interne)
            selHome.add(new Option(clubName, clubName));
            selAway.add(new Option(clubName, clubName));
        });
        
        // Petite astuce : on sélectionne par défaut le 2ème club pour l'équipe extérieure
        // pour ne pas avoir "Arsenal vs Arsenal" au début.
        selAway.selectedIndex = 1; 

    } catch (err) {
        console.error("Erreur chargement liste duel:", err);
    }
}

// B. QUAND ON CLIQUE SUR "SIMULER LE MATCH"
async function lancerDuel() {
    // 1. Récupérer les valeurs choisies par l'utilisateur
    const homeTeam = document.getElementById('selHome').value;
    const awayTeam = document.getElementById('selAway').value;
    
    // 2. Vérification de sécurité
    if(homeTeam === awayTeam) {
        alert("Une équipe ne peut pas jouer contre elle-même !");
        return; // On arrête tout ici
    }

    // 3. On cache le résultat précédent (si existant) pour faire propre
    const resultBox = document.getElementById('duelResult');
    resultBox.style.display = 'none';

    try {
        // 4. On appelle le serveur Python (C'est le coup de téléphone)
        const response = await fetch('/api/predict-match', {
            method: 'POST', // On envoie des données
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ home: homeTeam, away: awayTeam })
        });
        
        // 5. On récupère la réponse de Python (le dictionnaire JSON)
        const data = await response.json();
        
        // Si Python renvoie une erreur, on l'affiche
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // 6. MISE A JOUR DE L'INTERFACE (On remplit les trous du HTML)
        
        // Noms des équipes
        document.getElementById('resHomeName').innerText = data.home_team;
        document.getElementById('resAwayName').innerText = data.away_team;
        
        // Scores prédits (moyennes)
        document.getElementById('resHomeScore').innerText = data.score_avg_home;
        document.getElementById('resAwayScore').innerText = data.score_avg_away;

        // Barres de probabilités (Largeur en % + Texte)
        // Victoire Domicile
        const bWin = document.getElementById('barWin');
        bWin.style.width = data.proba_win + '%';
        bWin.innerText = data.proba_win + '%';
        
        // Match Nul
        const bDraw = document.getElementById('barDraw');
        bDraw.style.width = data.proba_draw + '%';
        bDraw.innerText = data.proba_draw + '%';
        
        // Victoire Extérieur
        const bLoss = document.getElementById('barLoss');
        bLoss.style.width = data.proba_loss + '%';
        bLoss.innerText = data.proba_loss + '%';

        // 7. Tout est prêt, on affiche la boite de résultat !
        resultBox.style.display = 'block';

    } catch (err) {
        console.error("Erreur duel:", err);
        alert("Erreur lors de la simulation du match.");
    }
}

// =========== 20/12/2025 MIR ===============================

// ==========================================
// 6. CLASSEMENT
// ==========================================
/*
async function chargerClassement() {
    const tbody = document.getElementById('rankingBody');
    const startSelect = document.getElementById('startDay');
    const endSelect = document.getElementById('endDay');
    
    const startVal = startSelect ? startSelect.value : 1;
    const endVal = endSelect ? endSelect.value : 8;

    if (parseInt(startVal) > parseInt(endVal)) {
        alert("La journée de début doit être <= à la fin !"); return;
    }

    tbody.innerHTML = '<tr><td colspan="8" class="loading-cell">Calcul en cours...</td></tr>';

    try {
        const response = await fetch('/api/ranking', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start: startVal, end: endVal })
        });
        const data = await response.json();

        if (data.error) {
            tbody.innerHTML = `<tr><td colspan="8" style="color:red">Erreur: ${data.error}</td></tr>`; return;
        }

        tbody.innerHTML = ''; 

        data.forEach(row => {
            const tr = document.createElement('tr');
            
            // Définition de la couleur de la ligne (Zone)
            let rowClass = '';
            if (row.rank <= 8) rowClass = 'zone-top8';
            else if (row.rank <= 24) rowClass = 'zone-barrage';
            else rowClass = 'zone-elim';

            tr.className = rowClass;
            
            // Injection des 8 colonnes (Pas de colonne Zone texte, pas d'Elo)
            tr.innerHTML = `
                <td class="rank-cell"><b>${row.rank}</b></td>
                <td class="club-cell" style="text-align:left;">
                    <div class="club-flex">
                        <img src="logos/${row.club}.png" onerror="this.src='logos/default.png'" class="mini-logo">
                        <span>${row.club}</span>
                    </div>
                </td>
                <td class="points-cell"><b>${row.points}</b></td>
                <td>${row.diff > 0 ? '+' : ''}${row.diff}</td>
                <td>${row.buts}</td>
                <td class="secondary-stat">${row.buts_ext}</td>
                <td>${row.victoires}</td>
                <td class="secondary-stat">${row.victoires_ext}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="8">Erreur connexion.</td></tr>';
    }
}
*/
async function chargerClassement() {
    const tbody = document.getElementById('rankingBody');
    
    // 1. Récupération des valeurs
    const startSelect = document.getElementById('startDay');
    const endSelect = document.getElementById('endDay');
    
    const startVal = parseInt(startSelect.value);
    const endVal = parseInt(endSelect.value);

    // 2. Sécurité : Vérifier l'ordre chronologique
    if (startVal >= endVal) {
        alert(`Impossible de simuler : La journée de fin (J${endVal}) doit être après le départ (J${startVal}).`);
        return;
    }

    tbody.innerHTML = '<tr><td colspan="8" class="loading"><div class="loader small"></div> Calcul en cours...</td></tr>';

    try {
        // 3. Appel API avec les DEUX paramètres
        const response = await fetch('/api/rankings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                start: startVal, 
                end: endVal 
            }) 
        });

        const data = await response.json();
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8">Aucune donnée disponible.</td></tr>';
            return;
        }

        // 4. Affichage du tableau
        data.forEach(row => {
            let rowClass = "";
            if (row.rank <= 8) rowClass = "qualif-direct";
            else if (row.rank <= 24) rowClass = "barrage";
            else rowClass = "elimine";

            tbody.innerHTML += `
                <tr class="${rowClass}">
                    <td>${row.rank}</td>
                    <td class="club-cell">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <img src="logos/${row.club}.png" class="mini-logo" onerror="this.src='logos/default.png'">
                            <strong>${row.club}</strong>
                        </div>
                    </td>
                    <td><strong>${row.points}</strong></td>
                    <td>${row.diff}</td>
                    <td>${row.buts}</td>
                    <td class="secondary-stat">${row.buts_ext}</td>
                    <td>${row.victoires}</td>
                    <td class="secondary-stat">${row.victoires_ext}</td>
                </tr>
            `;
        });
    } catch (error) {
        console.error('Erreur:', error);
        tbody.innerHTML = '<tr><td colspan="8" style="color:red; text-align:center;">Erreur serveur</td></tr>';
    }
}

// ==========================================
// ANALYSE D'IMPACT DES MATCHS
// ==========================================

function switchImpactTab(tabName) {
    // Cacher tous les onglets DE LA SECTION match-impact UNIQUEMENT
    document.querySelectorAll('#match-impact .impact-tab-content').forEach(tab => tab.style.display = 'none');
    document.querySelectorAll('#match-impact .tab-btn').forEach(btn => btn.classList.remove('active'));
    
    // Afficher le bon onglet
    if (tabName === 'specific') {
        document.getElementById('impact-specific').style.display = 'block';
        document.querySelectorAll('#match-impact .tab-btn')[0].classList.add('active');
    } else if (tabName === 'qualif') {
        document.getElementById('impact-qualif').style.display = 'block';
        document.querySelectorAll('#match-impact .tab-btn')[1].classList.add('active');
    } else if (tabName === 'top8') {
        document.getElementById('impact-top8').style.display = 'block';
        document.querySelectorAll('#match-impact .tab-btn')[2].classList.add('active');
    }
}

function switchScenarioTab(tabName) {
    // Cacher tous les onglets de la section impact-zone
    document.querySelectorAll('#impact-zone .impact-tab-content').forEach(tab => tab.style.display = 'none');
    document.querySelectorAll('#impact-zone .tab-btn').forEach(btn => btn.classList.remove('active'));
    
    // Afficher le bon onglet
    if (tabName === 'scenario') {
        document.getElementById('scenario-tab').style.display = 'block';
        document.querySelectorAll('#impact-zone .tab-btn')[0].classList.add('active');
    } else if (tabName === 'hype') {
        document.getElementById('hype-tab').style.display = 'block';
        document.querySelectorAll('#impact-zone .tab-btn')[1].classList.add('active');
    }
}


async function analyserImpactMatch() {
    const club = document.getElementById('impactClub').value.trim();
    const journee = parseInt(document.getElementById('impactJournee').value);
    const container = document.getElementById('impactResults');
    
    if (!club) {
        alert('Entrez un nom de club');
        return;
    }
    
    container.innerHTML = '<div class="loading-container"><div class="loader"></div><p>Analyse en cours...</p></div>';
    
    try {
        const response = await fetch('/api/match-impact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ club, journee, journee_donnees: 6 })
        });
        
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<div class="error-msg">❌ ${data.error}</div>`;
            return;
        }
        
        const domicileText = data.domicile ? '🏠 Domicile' : '✈️ Extérieur';
        
        container.innerHTML = `
            <div class="impact-card">
                <h3>${club} vs ${data.adversaire}</h3>
                <p class="match-info">${domicileText} - Journée ${journee}</p>
                
                <div class="scenarios-grid">
                    <div class="scenario-box victoire">
                        <h4>✅ Victoire</h4>
                        <div class="stat-line">
                            <span>Qualification :</span>
                            <strong>${data.impact_victoire.proba_qualif}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Top 8 :</span>
                            <strong>${data.impact_victoire.proba_top8}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Classement moyen :</span>
                            <strong>${data.impact_victoire.classement_moyen}</strong>
                        </div>
                    </div>
                    
                    <div class="scenario-box nul">
                        <h4>⚖️ Match Nul</h4>
                        <div class="stat-line">
                            <span>Qualification :</span>
                            <strong>${data.impact_nul.proba_qualif}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Top 8 :</span>
                            <strong>${data.impact_nul.proba_top8}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Classement moyen :</span>
                            <strong>${data.impact_nul.classement_moyen}</strong>
                        </div>
                    </div>
                    
                    <div class="scenario-box defaite">
                        <h4>❌ Défaite</h4>
                        <div class="stat-line">
                            <span>Qualification :</span>
                            <strong>${data.impact_defaite.proba_qualif}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Top 8 :</span>
                            <strong>${data.impact_defaite.proba_top8}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Classement moyen :</span>
                            <strong>${data.impact_defaite.classement_moyen}</strong>
                        </div>
                    </div>
                </div>
                
                <div class="gains-box">
                    <h4>📊 Enjeux</h4>
                    <p><strong>Victoire vs Nul :</strong> +${data.gain_victoire_vs_nul.qualif}% qualif, +${data.gain_victoire_vs_nul.top8}% top8</p>
                    <p><strong>Nul vs Défaite :</strong> +${data.gain_nul_vs_defaite.qualif}% qualif, +${data.gain_nul_vs_defaite.top8}% top8</p>
                    <p><strong>Places gagnées (victoire) :</strong> ${data.gain_victoire_vs_nul.classement} places en moyenne</p>
                </div>
            </div>
        `;
        
    } catch (error) {
        container.innerHTML = '<div class="error-msg">❌ Erreur serveur</div>';
    }
}

async function chargerMatchsImportants(type) {
    const container = type === 'qualif' 
        ? document.getElementById('tableQualif') 
        : document.getElementById('tableTop8');
    
    container.innerHTML = '<div class="loading-container"><div class="loader"></div><p>Calcul en cours...</p></div>';
    
    try {
        const response = await fetch('/api/all-matches-impact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ journee: 7, journee_donnees: 6 })
        });
        
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<div class="error-msg">❌ ${data.error}</div>`;
            return;
        }
        
        // Choisir le bon classement
        const matchs = type === 'qualif' ? data.par_qualif : data.par_top8;
        const metrique = type === 'qualif' ? 'impact_qualif' : 'impact_top8';
        const titre = type === 'qualif' ? 'Qualification' : 'Top 8';
        
        let html = `
            <table class="ranking-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Match</th>
                        <th>Impact Global ${titre}</th>
                        <th>Club le + Impacté</th>
                        <th>Impact Max</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        matchs.forEach((match, idx) => {
            html += `
                <tr>
                    <td>${idx + 1}</td>
                    <td style="text-align:left;">${match.match}</td>
                    <td>${match[metrique].global}</td>
                    <td>${match[metrique].club_max}</td>
                    <td>${match[metrique].max}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
        
    } catch (error) {
        container.innerHTML = '<div class="error-msg">❌ Erreur serveur</div>';
    }
}

// --- FONCTION POUR CHARGER LES PROBAS ---
async function chargerProbas() {
    const day = document.getElementById('probaStartDay').value;
    const tbodyTop8 = document.getElementById('tbodyTop8');
    const tbodyQualif = document.getElementById('tbodyQualif');

    // Afficher le chargement
    const loadingRow = '<tr><td colspan="3" style="text-align:center;"><div class="loader"></div> Calcul...</td></tr>';
    tbodyTop8.innerHTML = loadingRow;
    tbodyQualif.innerHTML = loadingRow;

    try {
        const response = await fetch('/api/probas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ day: parseInt(day) })
        });

        const data = await response.json();

        if (data.error) {
            tbodyTop8.innerHTML = `<tr><td colspan="3" style="color:red">${data.error}</td></tr>`;
            tbodyQualif.innerHTML = `<tr><td colspan="3" style="color:red">${data.error}</td></tr>`;
            return;
        }

        // Fonction utilitaire pour générer les lignes
        const generateRows = (list, colorClass) => {
            if (list.length === 0) return '<tr><td colspan="3">Aucune donnée</td></tr>';
            
            return list.map((item, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td style="text-align:left; display:flex; align-items:center; gap:10px;">
                        <img src="logos/${item.club}.png" class="mini-logo" onerror="this.src='logos/default.png'">
                        ${item.club}
                    </td>
                    <td>
                        <span class="score-badge ${colorClass}" style="width:50px; display:inline-block;">
                            ${item.proba}%
                        </span>
                    </td>
                </tr>
            `).join('');
        };

        // Remplissage des tableaux
        tbodyTop8.innerHTML = generateRows(data.ranking_top8, 'green-bg');
        tbodyQualif.innerHTML = generateRows(data.ranking_qualif, 'orange-bg');

    } catch (error) {
        console.error(error);
        tbodyTop8.innerHTML = '<tr><td colspan="3">Erreur serveur</td></tr>';
        tbodyQualif.innerHTML = '<tr><td colspan="3">Erreur serveur</td></tr>';
    }
}

//c'est moi ca
// --- FONCTION SCENARIO (DASHBOARD) ---
// GESTION DES ONGLETS
function switchImpactTab(tabName) {
    document.getElementById('impact-specific').style.display = 'none';
    document.getElementById('impact-ranking').style.display = 'none';
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

    if (tabName === 'specific') {
        document.getElementById('impact-specific').style.display = 'block';
        document.querySelector("button[onclick*='specific']").classList.add('active');
    } else {
        document.getElementById('impact-ranking').style.display = 'block';
        document.querySelector("button[onclick*='ranking']").classList.add('active');
    }
}

// FONCTION SCENARIO
async function lancerScenario() {
    const club = document.getElementById('scenarioClub').value;
    const start = document.getElementById('scenarioStartDay').value;
    const target = document.getElementById('scenarioTargetDay').value;
    const res = document.getElementById('scenarioResult').value;
    const box = document.getElementById('scenarioResultBox');

    if(!club) return alert("Club?");
    box.style.display = 'block';
    document.getElementById('scenarioVerdict').innerText = "Simulation...";

    try {
        const rep = await fetch('/api/scenario', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({club:club, start_day:start, day:target, result:res})
        });
        const data = await rep.json();
        if(data.error) return alert(data.error);

        // Mise à jour UI
        document.getElementById('scenarioTitle').innerHTML = `Si <strong>${data.club}</strong> fait <strong>${res}</strong>`;
        document.getElementById('dispTop8').innerText = data.proba_top8+"%";
        document.getElementById('barTop8').style.width = data.proba_top8+"%";
        document.getElementById('dispQualif').innerText = data.proba_qualif+"%";
        document.getElementById('barQualif').style.width = data.proba_qualif+"%";
        
        let v = "❌ Éliminé"; let c = "red";
        if(data.proba_qualif > 99) { v="✅ Qualifié"; c="green"; }
        else if(data.proba_qualif > 50) { v="⚖️ Incertain"; c="orange"; }
        
        const vb = document.getElementById('scenarioVerdict');
        vb.innerText = v; vb.style.borderLeftColor = c;

    } catch(e) { alert(e); }
}

// FONCTION IMPORTANCE
// --- FONCTION IMPORTANCE (HYPE) CORRIGÉE ---
async function chargerImportance() {
    // 1. Récupération des éléments par ID
    const startSelect = document.getElementById('impStartDay');
    const targetSelect = document.getElementById('impTargetDay');
    const list = document.getElementById('importanceList');

    // 2. Sécurité : Si les éléments n'existent pas dans le HTML, on arrête
    if (!startSelect || !targetSelect || !list) {
        console.error("Erreur : Impossible de trouver les éléments HTML (impStartDay, impTargetDay ou importanceList).");
        return;
    }

    const start = parseInt(startSelect.value);
    const target = parseInt(targetSelect.value);

    // 3. Vérification logique
    if (start >= target) {
        alert("La journée à analyser (Cible) doit être après le point de départ (Contexte).");
        return;
    }

    // 4. Affichage du chargement
    list.innerHTML = '<div class="loader"></div><p style="text-align:center">Calcul de l\'importance de tous les matchs...</p>';

    try {
        // 5. Appel au serveur
        const response = await fetch('/api/importance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start: start, target: target })
        });

        const data = await response.json();
        
        // 6. Gestion d'erreur renvoyée par Python
        if (data.error) {
            list.innerHTML = `<div style="color:red; text-align:center; padding:20px;">❌ Erreur : ${data.error}</div>`;
            return;
        }

        // 7. Affichage des résultats
        list.innerHTML = ""; // On vide le chargement
        
        if (data.length === 0) {
            list.innerHTML = `<div style="text-align:center; padding:20px;">Aucun match trouvé pour cette journée.</div>`;
            return;
        }

        data.forEach((m, i) => {
            // Calcul couleur (Rouge = Important, Gris = Pas important)
            let cls = 'low';
            if (m.score > 50) cls = 'high';
            else if (m.score > 20) cls = 'medium';
            
            // HTML de la carte
            list.innerHTML += `
                <div class="match-card">
                    <div class="match-info">
                        <span class="rank">#${i+1}</span>
                        <div class="teams">
                            <img src="logos/${m.dom}.png" class="mini-logo" onerror="this.src='logos/default.png'"> 
                            ${m.dom} 
                            <span class="vs">vs</span> 
                            ${m.ext} 
                            <img src="logos/${m.ext}.png" class="mini-logo" onerror="this.src='logos/default.png'">
                        </div>
                        <div class="score-badge ${cls}">${m.score}</div>
                    </div>
                    
                    <div class="hype-bar-bg">
                        <div class="hype-bar-fill ${cls}" style="width:${Math.min(m.score, 100)}%"></div>
                    </div>
                    
                    <div class="match-details-text">
                        Enjeu ${m.dom}: <strong>${m.details.dom_val}</strong> | 
                        Enjeu ${m.ext}: <strong>${m.details.ext_val}</strong>
                    </div>
                </div>`;
        });

    } catch (e) {
        console.error(e);
        list.innerHTML = `<div style="color:red; text-align:center;">❌ Erreur technique (Voir console F12)</div>`;
    }
}

"""


#===============================================================================================================================
#style.css avant nettoyage

"""
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f7f6;
    color: #333;
}

header {
    background-color: #002f5f; /* Bleu nuit LDC */
    color: white;
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

h1 { margin: 0; font-size: 1.5rem; }

nav button {
    margin-left: 10px;
    padding: 10px 15px;
    cursor: pointer;
    background-color: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 5px;
    color: white;
    transition: background 0.3s;
}

nav button:hover { background-color: rgba(255,255,255,0.25); }

.page {
    max-width: 1000px;
    margin: 30px auto;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

/* Accueil */
.hero { text-align: center; padding: 40px 0; }
.actions { margin-top: 30px; }
.big-btn {
    padding: 15px 30px;
    font-size: 1.1rem;
    background-color: #0066cc;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin: 0 10px;
}
.big-btn.secondary { background-color: #6c757d; }

/* Formulaire */
.search-box { text-align: center; margin: 40px 0; }
input[type="text"] {
    padding: 10px;
    width: 250px;
    border: 1px solid #ccc;
    border-radius: 4px;
}
button[type="submit"] {
    padding: 10px 20px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

/* Résultats Stats Grid */
.stats-grid {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    margin: 20px 0;
}
.stat-box {
    flex: 1;
    padding: 20px;
    text-align: center;
    border-radius: 8px;
    color: white;
}
.stat-box h4 { margin: 0 0 10px 0; opacity: 0.9; }
.stat-box .percentage { font-size: 2rem; font-weight: bold; }
.green { background-color: #28a745; }
.yellow { background-color: #ffc107; color: #333; }
.red { background-color: #dc3545; }

/* Graphiques */
.main-chart-container { position: relative; height: 400px; width: 100%; margin-top: 30px; }
.charts-row { display: flex; flex-wrap: wrap; gap: 20px; }
.chart-wrapper { flex: 1; min-width: 300px; background: #f9f9f9; padding: 15px; border-radius: 8px; height: 300px; }

/* Liste Importance */
.importance-list { list-style: none; padding: 0; }
.importance-list li {
    background: #fff;
    border-bottom: 1px solid #eee;
    padding: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.rank { background: #002f5f; color: white; padding: 5px 10px; border-radius: 50%; font-size: 0.8rem; }
.match-name { font-weight: bold; }
.score { color: #555; }

/* Loader */
.loader {
    border: 5px solid #f3f3f3;
    border-top: 5px solid #0066cc;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 20px auto;
}
.loader.small { width: 20px; height: 20px; border-width: 3px; display: inline-block; vertical-align: middle; margin: 0 10px 0 0;}

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.error-msg { color: #dc3545; text-align: center; padding: 20px; font-weight: bold; background: #ffe6e6; border-radius: 5px;}
nav button:hover {
    background-color: #0055aa;
}

.page {
    padding: 20px;
}

form input {
    padding: 5px;
    margin-right: 10px;
}



/* --- GRILLE DES CLUBS: 19/12/2025 16:42 début MIR --- */

.clubs-container {
    margin-top: 40px;
    text-align: center;
    padding: 0 20px 40px 20px;
}

.clubs-container h3 {
    color: #555;
    margin-bottom: 20px;
}

.clubs-grid {
    display: grid;
    /* Magie CSS : remplit la ligne avec autant de cartes que possible (min 110px de large) */
    grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
    gap: 15px;
    max-width: 1000px;
    margin: 0 auto;
}

.club-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 15px 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 120px; /* Hauteur fixe pour uniformité */
}

.club-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    border-color: #002f5f;
}

.club-logo-wrapper {
    height: 60px;
    width: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
}

.club-logo-wrapper img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain; /* L'image ne sera pas déformée */
}

.club-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #333;
    line-height: 1.2;
    overflow: hidden;
    text-overflow: ellipsis; /* ... si le nom est trop long */
    display: -webkit-box;
    -webkit-line-clamp: 2; /* Max 2 lignes de texte */
    line-clamp: 2;
    -webkit-box-orient: vertical;
}

/* --- GRILLE DES CLUBS: 19/12/2025 16:42 fin MIR --- */


/* --- SECTION DUEL: 19/12/2025 16:42 début MIR --- */
.duel-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin: 40px 0;
}

.team-selector {
    display: flex;
    flex-direction: column;
    text-align: center;
}

.team-selector select {
    padding: 10px;
    font-size: 1.1rem;
    border-radius: 8px;
    border: 1px solid #ddd;
    width: 200px;
}

.vs-badge {
    background: #002f5f;
    color: white;
    padding: 10px;
    border-radius: 50%;
    font-weight: bold;
}

/* SCORE BOARD */
.score-board {
    background: #222;
    color: #fff;
    padding: 20px;
    border-radius: 12px;
    display: flex;
    justify-content: space-around;
    align-items: center;
    font-family: 'Courier New', monospace; /* Style tableau d'affichage */
    margin-top: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.score-digit {
    font-size: 3rem;
    color: #f1c40f; /* Jaune LED */
    display: block;
    font-weight: bold;
}

/* BARRE DE PROBAS */
.proba-bar-container {
    display: flex;
    height: 30px;
    margin-top: 20px;
    border-radius: 15px;
    overflow: hidden;
    font-size: 0.8rem;
    color: white;
    line-height: 30px;
    text-align: center;
}

.p-bar.win { background: #28a745; }
.p-bar.draw { background: #6c757d; }
.p-bar.loss { background: #dc3545; }


/* --- SECTION CLASSEMENT 19/12/2025 MIR --- */

/* La barre de choix J1 -> J8 */
.controls-bar {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    border: 1px solid #dee2e6;
}

.control-group {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: bold;
    color: #333;
}

.control-group select {
    padding: 5px 10px;
    border-radius: 4px;
    border: 1px solid #ccc;
    font-size: 1rem;
}

.action-btn {
    background-color: #002f5f; /* Bleu LDC */
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.3s;
}
.action-btn:hover {
    background-color: #004a93;
}



/* Le Tableau */
.table-container {
    overflow-x: auto; /* Permet de scroller si l'écran est petit */
}

.ranking-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    background: white;
}

.ranking-table th {
    background-color: #002f5f;
    color: white;
    padding: 12px 8px;
    text-align: center;
    white-space: nowrap;
}

.ranking-table td {
    padding: 8px;
    border-bottom: 1px solid #eee;
    text-align: center;
}


/* Style spécifique pour les stats secondaires (Extérieur) pour qu'elles soient moins voyantes */
.secondary-stat {
    color: #777;
    font-size: 0.85rem;
    background-color: #fcfcfc;
}

.points-cell {
    font-weight: bold;
    color: #002f5f;
    font-size: 1.1rem;
    background-color: #f0f8ff;
}

.mini-logo {
    width: 20px;
    height: 20px;
    vertical-align: middle;
    margin-right: 8px;
}

/* Zones de qualification */
.zone-top8 { background-color: rgba(46, 204, 113, 0.1); border-left: 4px solid #2ecc71; }
.zone-barrage { background-color: rgba(243, 156, 18, 0.1); border-left: 4px solid #f39c12; }
.zone-elim { background-color: rgba(231, 76, 60, 0.05); border-left: 4px solid #e74c3c; }

/* Badges (Étiquettes colorées) */
.badge {
    padding: 3px 8px;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
}
.badge.zone-top8 { background: #d4edda; color: #155724; }
.badge.zone-barrage { background: #fff3cd; color: #856404; }
.badge.zone-elim { background: #f8d7da; color: #721c24; }


/* --- GRAPHIQUES SIMULATION CLUB (VERTICAL & AÉRÉ) --- */

.charts-column {
    display: flex;
    flex-direction: column; /* Empile les éléments verticalement */
    gap: 50px; /* Grand espace entre les deux graphiques */
    margin-top: 40px;
}

.chart-box {
    background: white;
    padding: 25px;       /* Espace interne confortable */
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05); /* Ombre douce */
    border: 1px solid #eee;
    width: 100%;         /* Prend toute la largeur */
    box-sizing: border-box; /* Empêche de dépasser */
}

.chart-box h4 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #002f5f;
    font-size: 1.2rem;
    text-align: center;
    border-bottom: 2px solid #f4f7f6;
    padding-bottom: 10px;
}

.chart-area {
    position: relative;
    height: 350px; /* Hauteur fixe confortable pour éviter l'écrasement */
    width: 100%;
}

/* =========================================
   BARRE DE CONTRÔLE (Date Selector)
   ========================================= */
.controls-bar {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    border: 1px solid #e9ecef;
    display: flex;
    align-items: center;
    gap: 15px;
    flex-wrap: wrap; /* Pour mobile */
}

.controls-bar label {
    font-weight: 600;
    color: #495057;
}

.controls-bar select {
    padding: 8px 12px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    background-color: white;
    font-size: 1rem;
    cursor: pointer;
    min-width: 200px;
}

.controls-bar .action-btn {
    padding: 8px 15px;
    background-color: #007bff; /* Bleu */
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background 0.2s;
}

.controls-bar .action-btn:hover {
    background-color: #0056b3;
}

/* Petit style pour le chargement dans le tableau */
.loading {
    text-align: center;
    font-style: italic;
    color: #666;
    padding: 20px;
}

/* --- BARRE DE CONTRÔLES (Double Select) --- */
.control-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.controls-bar {
    display: flex;
    flex-wrap: wrap; /* Passe à la ligne sur mobile */
    gap: 20px;
    align-items: center;
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
    margin-bottom: 20px;
}

/* --- TABLEAU --- */
.ranking-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
}
.ranking-table th {
    background: #343a40;
    color: white;
    padding: 12px;
    text-align: center;
}
.ranking-table td {
    padding: 10px;
    border-bottom: 1px solid #eee;
    text-align: center;
}
/* Aligner le nom du club à gauche */
.ranking-table td.club-cell {
    text-align: left;
}

/* --- COULEURS DE RANG --- */
tr.qualif-direct { border-left: 5px solid #28a745; background: rgba(40, 167, 69, 0.05); }
tr.barrage { border-left: 5px solid #ffc107; background: rgba(255, 193, 7, 0.05); }
tr.elimine { border-left: 5px solid #dc3545; background: rgba(220, 53, 69, 0.05); }

/* --- LÉGENDE --- */
.legend {
    margin-top: 15px;
    display: flex;
    gap: 20px;
    font-size: 0.9rem;
    justify-content: center;
}
.dot {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 5px;
}
.dot.green { background: #28a745; }
.dot.orange { background: #ffc107; }
.dot.red { background: #dc3545; }

/* --- RESPONSIVE : Cacher les stats secondaires sur mobile --- */
@media (max-width: 768px) {
    .secondary-stat {
        display: none;
    }
}

/* ========================================
   STYLES IMPACT DES MATCHS
   ======================================== */

.impact-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.tab-btn {
    padding: 10px 20px;
    background: #2c2c2c;
    border: 2px solid #444;
    color: white;
    cursor: pointer;
    border-radius: 8px;
    transition: all 0.3s;
}

.tab-btn.active {
    background: #0066cc;
    border-color: #0066cc;
}

.tab-btn:hover {
    background: #444;
}

.impact-card {
    background: #1a1a1a;
    border-radius: 12px;
    padding: 25px;
    margin-top: 20px;
}

.impact-card h3 {
    color: #0066cc;
    margin-bottom: 5px;
}

.match-info {
    color: #888;
    margin-bottom: 20px;
}

.scenarios-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
}

.scenario-box {
    background: #2c2c2c;
    padding: 20px;
    border-radius: 10px;
    border: 2px solid;
}

.scenario-box.victoire {
    border-color: #22c55e;
}

.scenario-box.nul {
    border-color: #fbbf24;
}

.scenario-box.defaite {
    border-color: #ef4444;
}

.scenario-box h4 {
    margin-bottom: 15px;
    font-size: 1.1em;
}

.stat-line {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #444;
}

.stat-line:last-child {
    border-bottom: none;
}

.gains-box {
    background: #2c2c2c;
    padding: 20px;
    border-radius: 10px;
    border-left: 4px solid #0066cc;
}

.gains-box h4 {
    margin-bottom: 10px;
    color: #0066cc;
}

.gains-box p {
    margin: 8px 0;
}
/* Info box pour les onglets */
.info-box {
    background: #1a1a1a;
    border-left: 4px solid #0066cc;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 8px;
}

.info-box p {
    margin: 5px 0;
    color: #ccc;
}

.info-box strong {
    color: #0066cc;
}

/* --- PROBAS SECTION --- */
.probas-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: space-between;
    margin-top: 20px;
}

.proba-column {
    flex: 1;
    min-width: 300px; /* Pour mobile */
    background: white;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.proba-column h3 {
    text-align: center;
    margin-bottom: 15px;
    font-size: 1.2rem;
}

.green-text { color: #28a745; }
.orange-text { color: #fd7e14; }

/* Badges de pourcentage */
.score-badge.green-bg { background-color: #28a745; color: white; }
.score-badge.orange-bg { background-color: #fd7e14; color: white; }

/* Scroll si la liste est longue */
.table-wrapper {
    max-height: 500px;
    overflow-y: auto;
}

/* --- SCENARIO DASHBOARD --- */
.scenario-dashboard { display: flex; justify-content: space-around; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.stat-card { background: white; border: 1px solid #eee; border-radius: 10px; padding: 15px; width: 30%; min-width: 150px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.stat-icon { font-size: 1.5rem; }
.stat-big-number { font-size: 2rem; font-weight: bold; margin: 10px 0; }
.green-text { color: #28a745; } .orange-text { color: #fd7e14; } .red-text { color: #dc3545; }
.progress-bg { background: #eee; height: 6px; border-radius: 3px; overflow: hidden; }
.progress-bar { height: 100%; transition: width 0.5s; }
.progress-bar.green { background: #28a745; } .progress-bar.orange { background: #fd7e14; } .progress-bar.red { background: #dc3545; }
.verdict-box { background: #f8f9fa; border-left: 5px solid #333; padding: 15px; text-align: center; font-weight: bold; }

/* --- IMPORTANCE LIST --- */
.matches-list { display: flex; flex-direction: column; gap: 10px; margin-top: 15px; }
.match-card { background: white; padding: 12px; border-radius: 8px; border: 1px solid #ddd; }
.match-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.score-badge { padding: 4px 8px; border-radius: 12px; color: white; font-weight: bold; font-size: 0.9rem; }
.score-badge.high { background: #dc3545; } .score-badge.medium { background: #17a2b8; } .score-badge.low { background: #6c757d; }
.hype-bar-bg { height: 6px; background: #eee; border-radius: 3px; overflow: hidden; margin-bottom: 5px; }
.hype-bar-fill { height: 100%; }
.hype-bar-fill.high { background: linear-gradient(90deg, #ffc107, #dc3545); }
.hype-bar-fill.medium { background: #17a2b8; } .hype-bar-fill.low { background: #adb5bd; }
.match-details-text { font-size: 0.8rem; color: #777; text-align: right; }
"""