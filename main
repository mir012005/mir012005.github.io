import Modele_elo_rating
## Générer les distributions
distribution_probas_classement_from_J6 = distribution_position_par_club(
    N=100000,
    classement=classement_J6,
    points=points_J6,
    diff_buts=diff_buts_J6,
    buts=buts_J6,
    buts_exterieur=buts_ext_J6,
    nb_victoires=nb_v_J6,
    nb_victoires_ext=nb_v_ext_J6,
    debut=7,
)
distribution_probas_points_from_J6 = distribution_points_par_club(
    N=100000,
    classement=classement_J6,
    points=points_J6,
    diff_buts=diff_buts_J6,
    buts=buts_J6,
    buts_exterieur=buts_ext_J6,
    nb_victoires=nb_v_J6,
    nb_victoires_ext=nb_v_ext_J6,
    debut=7,
)


## Afficher plein d'infos sur les clubs français
print("RESULTATS SUR LA BASE DE N = 100 000 SIMULATIONS :")
print()
for club in ["Brest", "Lille", "Monaco", "Paris SG"]:
    print(club, ":")
    print()

    d = {
        pos: round(distribution_probas_classement_from_J5[club][pos], 5)
        for pos in distribution_probas_classement_from_J5[club]
    }
    print(
        "La distribution de probabilités sur le classement de",
        club,
        "après les 8 journées est :",
        d,
    )
    moy, ecart = moyenne_et_ecart_type(club, distribution_probas_classement_from_J5)
    print("Sa position moyenne est", moy, "avec un écart-type de", ecart)
    L = [0, 0, 0, 0]
    for pos in range(1, 25):
        L[(pos - 1) // 8] += d[pos]
    L[-1] = 1 - proba_qualification(club, distribution_probas_classement_from_J5)
    print(
        "La proba pour",
        club,
        "de finir entre les positions 1 et 8 est de",
        round(L[0], 3),
    )
    print(
        "La proba pour",
        club,
        "de finir entre les positions 9 et 16 est de",
        round(L[1], 3),
    )
    print(
        "La proba pour",
        club,
        "de finir entre les positions 17 et 24 est de",
        round(L[2], 3),
    )
    print(
        "La proba pour",
        club,
        "de finir entre les positions 25 et 36 est de",
        round(L[3], 3),
    )

    d = {
        points: round(distribution_probas_points_from_J5[club][points], 5)
        for points in distribution_probas_points_from_J5[club]
    }
    print(
        "Le nombre de points inscrit par",
        club,
        "suit la distribution suivante :",
        d,
    )
    moy, ecart = moyenne_et_ecart_type(club, distribution_probas_points_from_J5)
    print("En moyenne,", club, "a inscrit", moy, "points, avec un écart-type de", ecart)

    print()

for club in ["Brest", "Lille", "Monaco", "Paris SG"]:
    afficher_distribution_classement_club(club, distribution_probas_classement_from_J5)
    afficher_distribution_points_club(club, distribution_probas_points_from_J5)


#NOMBRE DE POINTS POSITIONS CLES:
distribution_probas = distribution_par_position(
    N=100000,
    données=données_J6,
    demi=False,
    debut=7,
)
for position in [25,24,9,8]:
    distribution = distribution_probas[position]
    positions = [p for p, prob in distribution.items() if prob > 0]
    probabilities = [100 * prob for prob in distribution.values() if prob > 0]

    # Création du graphique
    plt.figure(figsize=(8, 4.5))
    plt.bar(positions, probabilities, color="skyblue", edgecolor="black")

    # Ajouter des étiquettes
    plt.xlabel("Nombre de points", fontsize=14)
    plt.ylabel("Probabilités (%)", fontsize=14)
    plt.title(f"Nombre de points de l'équipe en {position}è place", fontsize=16)
    plt.xticks(positions, fontsize=12)
    plt.yticks(fontsize=12)

    moyenne, ecart_type = moyenne_et_ecart_type(position, distribution_probas)

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


## Mettre dans un PDF toutes les distributions
clubs_triés = sorted(clubs_en_ldc)

with PdfPages(
    "C:\\Users\\Oscar\\OneDrive\\Documents\\2A\\Projet_IMI_ldc\\Résultats\\Tous_les_clubs_J6.pdf"
) as pdf:
    for club in clubs_triés:
        affichage_simplifié_pdf(club, distribution_probas_classement_from_J6)
        affichage_simplifié_pdf(club, distribution_probas_points_from_J6, points=True)


## Mettre dans un PDF les distributions initiales pour les clubs français
elo_ldc = elo_pre_ldc
probas_par_matchs = dico_de_proba()

distribution_position = distribution_position_par_club(N=100000)
distribution_points = distribution_points_par_club(N=100000)

with PdfPages(
    "C:\\Users\\Oscar\\OneDrive\\Documents\\2A\\Projet_IMI_ldc\\Résultats\\Clubs français\\Images_distributions_initiales.pdf"
) as pdf:
    for club in ["Brest", "Lille", "Monaco", "Paris SG"]:
        affichage_simplifié_pdf(club, distribution_position)
        affichage_simplifié_pdf(club, distribution_points, points=True)




IMPORTANCE DES MATCHS : 

print("IMPORTANCE DES MATCHS : \n\n")
for journee in ['Journée 7','Journée 8']:
    print(journee, ":\n")
    enjeux_ = [[],[],[]]
    for match in calendrier[journee]:
        j = int(journee[-1])
        max1 , moy1, diff1 = enjeux(match[0],j,données_J6,
                  debut=7)
        max2 , moy2, diff2 = enjeux(match[1],j,données_J6,
                  debut=7)
        enjeux_[0].append([match,max1,max2,(max1+max2)/2])
        enjeux_[1].append([match,moy1,moy2,(moy1+moy2)/2])
        enjeux_[2].append([match,diff1,diff2,(diff1+diff2)/2])
    for enjeu in range(3):
        if enjeu == 0:
            print("Enjeu au sens du max entre qualif et top 8: \n")
        elif enjeu == 1:
            print("Enjeu au sens de la somme de qualif et top 8: \n")
        else:
            print("Gain moyen de places au classement: \n")
        df = pd.DataFrame({
            "Match": [enjeux_[enjeu][i][0] for i in range(len(enjeux_[enjeu]))],
            "Club 1": [enjeux_[enjeu][i][1] for i in range(len(enjeux_[enjeu]))],
            "Club 2": [enjeux_[enjeu][i][2] for i in range(len(enjeux_[enjeu]))],
            "Enjeu": [enjeux_[enjeu][i][-1] for i in range(len(enjeux_[enjeu]))]
            })

        df = df.sort_values(by=["Enjeu"], ascending=[False]).reset_index(drop=True)
        df['Enjeu'] = df['Enjeu'].round(3)

        print(df,"\n\n")


SCENARIO ELIMINATION BREST :

def issue(club1,club2):
    i,j = retourne_score(club1,club2)
    if i>j:
        return 1
    elif i<j:
        return -1
    else:
        return 0

N = 1000000
p1=0 ; p2=0 ; p3=0 ; p4=0 ; p5=0 ; p6=0 ; p7=0 ; p8 = 0 ; p9 = 0 ; p10 = 0 ; p11 = 0 ; p12 = 0
for _ in range(N):
    if issue("Shakhtar","Brest") == 1 and issue("Brest","Real Madrid") == -1:
        p1 += 1/N
    if issue("Arsenal","Dinamo Zagreb") == -1 and issue("Dinamo Zagreb","Milan") == 1:
        p2 += 1/N
    if issue("Slovan Bratislava","Stuttgart") == -1 and issue("Stuttgart","Paris SG") == 1:
        p3 += 1/N
    if issue("Benfica","Barcelona") == 1:
        p4 += 1/N
    if issue("Juventus","Benfica") == 1:
        p5 += 1/N
    if issue("Paris SG","Man City") == -1 and issue("Man City","Brugge") == 1:
        p6 += 1/N
    if issue("PSV","Liverpool") == 1 and issue("Crvena Zvezda","PSV") == -1:
        p7 += 1/N
    issue1 = issue("Celtic","Young Boys") ; issue2 = issue("Aston Villa","Young Boys")
    if (issue1 == 1 and issue2 != 1) or (issue1 != -1 and issue2 == -1):
        p8 += 1/N
    if issue("Real Madrid","Salzburg") != -1:
        p9 += 1/N
    if issue("Feyenoord","Bayern") == 1 or issue("Lille","Feyenoord") == -1:
        p10 += 1/N
    if issue("RB Leipzig","Sporting") == -1 or issue("Sporting","Bologna") == 1:
        p11 += 1/N
    if issue("Monaco","Aston Villa") == 1 or issue("Inter","Monaco") == -1:
        p12 += 1/N

print("La proba que Brest perde ses deux matchs est de", round(p1,3))
print("La proba que le Dinamo Zagreb gagne ses deux matchs est de", round(p2,3))
print("La proba que Stuttgart gagne ses deux matchs est de", round(p3,3))
print("La proba que Benfica batte Barcelone est de", round(p4,3))
print("La proba que la Juventus batte Benfica est de", round(p5,3))
print("La proba que Man City gagne ses deux matchs est de", round(p6,3))
print("La proba que le PSV gagne ses deux matchs est de", round(p7,3))
print("La proba que le Celtic prenne au moins 4 points sur ses deux matchs est de", round(p8,3))
print("La proba que le Real ne perde pas contre Salzbourg est de", round(p9,3))
print("La proba que Feyenoord gagne au moins un match est de", round(p10,3))
print("La proba que le Sporting gagne au moins un match est de", round(p11,3))
print("La proba que Monaco gagne au moins un match est de", round(p12,3))
print()
print("La probabilité de tout le scénario est de", p1*p2*p3*p4*p5*p6*p7*p8*p9*p10*p11*p12)


ENJEUX MATCHS POUR AUTRES CLUBS :

enjeux_ = {club : {match : [0,0] for match in 
                   [match for match in calendrier["Journée 7"] if (match[0] != club and match[1] != club)]}
            for club in clubs_en_ldc}
for club in enjeux_.keys():
    print(club)
    for match in [match for match in calendrier["Journée 7"] if (match[0] != club and match[1] != club)]:
        moy, diff = enjeux_pour(club,match,7,données_J6,debut=7,N=10000)
        if moy>=0:
            sens = "Domicile"
            val = moy
        else:
            sens = "Exterieur"
            val = -moy
        enjeux_[club][match] = [val,sens]


AFFICHAGE DE TOUS LES ENJEUX:
N = 10000
enjeux_ = simulation_pour_enjeux(journee=7,données=données_J6,debut=7,demi=True,N=N)

matchs_a_estimer = calendrier["Journée 7"][9:] + calendrier["Journée 8"]

pd.set_option('display.width', 1000)  # Largeur totale de l'affichage
pd.set_option('display.max_colwidth', None)  # Largeur maximale des colonnes

for critere in ["classement","proba_qualif","proba_top8"]:
    print(critere,"\n\n")
    for club in clubs_en_ldc:
        print(club,"\n")
        d = enjeux_[club] ; L = list(d.keys())
        journée = [7 if x in calendrier["Journée 7"] else 8 for x in L]
        df = pd.DataFrame({
            "Match" : L,
            "Journée" : journée,
            "Domicile" : [d[match]["domicile"][critere] for match in d.keys()],
            "Nul" : [d[match]["nul"][critere] for match in d.keys()],
            "Exterieur" : [d[match]["exterieur"][critere] for match in d.keys()],
            "Importance" : [abs(d[match]["domicile"][critere] - d[match]["exterieur"][critere]) for match in d.keys()],
            "Occurences" : [(round(d[match]["domicile"]["nb_occurences"]/N,2),round(d[match]["nul"]["nb_occurences"]/N,2),round(d[match]["exterieur"]["nb_occurences"]/N,2)) for match in d.keys()]
        })
        df = df.sort_values(by=["Importance"], ascending=[False]).reset_index(drop=True)
        df['Domicile'] = df['Domicile'].round(3)
        df['Nul'] = df['Nul'].round(3)
        df['Exterieur'] = df['Exterieur'].round(3)
        df['Importance'] = df['Importance'].round(4)
        print(df,"\n\n")


enjeux_matchs_probas = {match : {"domicile" : enjeux_[match[0]][match]["domicile"]["proba_qualif"] - enjeux_[match[0]][match]["exterieur"]["proba_qualif"] + enjeux_[match[0]][match]["domicile"]["proba_top8"] - enjeux_[match[0]][match]["exterieur"]["proba_top8"],
                                 "exterieur" : -(enjeux_[match[1]][match]["domicile"]["proba_qualif"] - enjeux_[match[1]][match]["exterieur"]["proba_qualif"] + enjeux_[match[1]][match]["domicile"]["proba_top8"] - enjeux_[match[1]][match]["exterieur"]["proba_top8"])}
                                   for match in matchs_a_estimer}
df = pd.DataFrame({
    "Match" : enjeux_matchs_probas.keys(),
    "Journée" : journée,
    "Enjeu Club1" : [enjeux_matchs_probas[match]["domicile"] for match in enjeux_matchs_probas.keys()],
    "Enjeu Club2" : [enjeux_matchs_probas[match]["exterieur"] for match in enjeux_matchs_probas.keys()],
    "Enjeu Moyen" : [(enjeux_matchs_probas[match]["domicile"] + enjeux_matchs_probas[match]["exterieur"])/2 for match in enjeux_matchs_probas.keys()]
}).sort_values(by=["Enjeu Moyen"], ascending=[False]).reset_index(drop=True)
for colonne in ["Enjeu Club1", "Enjeu Club2", "Enjeu Moyen"]:
    df[colonne] = df[colonne].round(3)
print("Enjeu des matchs pour les clubs eux-mêmes, au sens de la somme de la différence de proba de qualif et de celle de proba de top8 :\n\n",df,"\n\n")

enjeux_autres_probas = {
    match: sum(
        [
            abs(enjeux_[club][match]["domicile"]["proba_qualif"] - enjeux_[club][match]["exterieur"]["proba_qualif"]) +
            abs(enjeux_[club][match]["domicile"]["proba_top8"] - enjeux_[club][match]["exterieur"]["proba_top8"])
            for club in clubs_en_ldc if club not in match
        ]
    )
    for match in matchs_a_estimer
}
df = pd.DataFrame({
    "Match" : enjeux_autres_probas.keys(),
    "Journée" : journée,
    "Enjeu pour autres clubs" : [enjeux_autres_probas[match] for match in enjeux_autres_probas.keys()]
}).sort_values(by=["Enjeu pour autres clubs"], ascending=[False]).reset_index(drop=True)
df["Enjeu pour autres clubs"] = df["Enjeu pour autres clubs"].round(3)
print("Enjeu des matchs pour les autres clubs, au sens de la somme de la différence de proba de qualif et de celle de proba de top8 :\n\n",df,"\n\n")



AFFICHAGE DES ENJEUX CONDITIONNES :

N = 1000000
enjeux_ = simulation_pour_enjeux_si_issue([8],données_J7,debut=8,N=N)

matchs_a_estimer = calendrier["Journée 8"]

pd.set_option('display.width', 1000)  # Largeur totale de l'affichage
pd.set_option('display.max_colwidth', None)  # Largeur maximale des colonnes

for critere in ["classement","proba_qualif","proba_top8"]:
    print(critere,"\n\n")
    for club in clubs_en_ldc:
        for issue in ["victoire","nul","défaite"]:
            d = enjeux_[issue][club] ; L = list(d.keys())
            #journée = [7 if x in calendrier["Journée 7"] else 8 for x in L]
            df = pd.DataFrame({
                "Match" : L,
                "Journée" : journée,
                "Domicile" : [d[match]["domicile"][critere] for match in d.keys()],
                "Nul" : [d[match]["nul"][critere] for match in d.keys()],
                "Exterieur" : [d[match]["exterieur"][critere] for match in d.keys()],
                "Importance" : [max(d[match]["domicile"][critere],d[match]["nul"][critere],d[match]["exterieur"][critere])-min(d[match]["domicile"][critere],d[match]["nul"][critere],d[match]["exterieur"][critere]) for match in d.keys()],
                "Occurences" : [(round(d[match]["domicile"]["nb_occurences"]/N,2),round(d[match]["nul"]["nb_occurences"]/N,2),round(d[match]["exterieur"]["nb_occurences"]/N,2)) for match in d.keys()]
            })
            df = df.sort_values(by=["Importance"], ascending=[False]).reset_index(drop=True)
            df['Domicile'] = df['Domicile'].round(3)
            df['Nul'] = df['Nul'].round(3)
            df['Exterieur'] = df['Exterieur'].round(3)
            df['Importance'] = df['Importance'].round(4)
            if df['Importance'][0] > 0:
                print(club, ": proba de", issue, "=", round((d[match]["domicile"]["nb_occurences"]+d[match]["nul"]["nb_occurences"]+d[match]["domicile"]["nb_occurences"])/N,4)*100,"%")
                print(df,"\n\n")