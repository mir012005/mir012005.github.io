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


