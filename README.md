# Champions_league_TDLOG_-website

On a 36 équipes issues de 55 ligues (associations), réparties en 4 châpeaux de 9 équipes chacune.

Chaque équipe est définie par son classement UEFA et la ligue auquelle elle appartient.

Chaque match a son importance auquel on associera un indicateur.

On pourra comparer plusieurs modèles probabilistes pour la simulation de résultats de matchs de football.
Typiquement des lois de Poisson sont utilisées pour modéliser le nombre de buts marqués par chaque équipe,
dont les paramètres dépendent de la force de l'équipe.

La force d'une équipe est définie par son coefficient Elo (déjà simulé), de la force offensive, de la qualité défensive (estimées sur un historique de résultats), ainsi que du lieu du match (à domicile ou à l’extérieur).

Objectifs: 
    quantifier la probabilité pour chaque équipe de se qualifier directement pour les 8emes de finale / de
    se qualifier pour les barrages, avant le début de la phase de ligue, et après chaque journée de phase
    de ligue, en mettant à jour le classement avec les vrais résultats des matchs. 
        Pour chaque équipe, on affichera:
            la distribution de probabilité,
            le nombre de points final,
            la place finale au classement.
    
    quantifier le nombre de points nécessaires pour finir dans le top 8/16/24. On affichera la distribution
    du nombre de points du club qui finit en position 8/9/16/17/24/25.
    
    proposer un classement alternatif plus juste qui prend en compte la force des adversaires rencontrés.