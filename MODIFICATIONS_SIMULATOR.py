"""
=============================================================================
MODIFICATIONS À APPORTER À simulator.py
=============================================================================

INSTRUCTIONS :
1. Ajouter l'import en haut du fichier simulator.py (après les autres imports)
2. Remplacer les fonctions existantes par les nouvelles versions ci-dessous

=============================================================================
"""

# =============================================================================
# ÉTAPE 1 : AJOUTER CET IMPORT EN HAUT DE simulator.py (après "from pathlib import Path")
# =============================================================================

# --- COPIER CECI EN HAUT DU FICHIER ---
"""
# Import du module de données offline
try:
    import offline_data
    offline_data.charger_toutes_les_donnees()
    OFFLINE_DISPONIBLE = offline_data.donnees_disponibles()
    print(f"✅ Mode OFFLINE activé" if OFFLINE_DISPONIBLE else "⚠️ Mode LIVE (pas de données offline)")
except ImportError:
    OFFLINE_DISPONIBLE = False
    print("⚠️ Module offline_data non trouvé - Mode LIVE")
"""


# =============================================================================
# ÉTAPE 2 : REMPLACER LES FONCTIONS SUIVANTES
# =============================================================================

# -----------------------------------------------------------------------------
# FONCTION 1 : get_web_simulation (remplace lignes ~1123-1191)
# -----------------------------------------------------------------------------

def get_web_simulation(club_cible, nb_simulations=1000, journee_depart=0):
    """
    Fonction optimisée pour le web.
    Utilise les données OFFLINE si disponibles, sinon fait une simulation LIVE.
    """
    if club_cible not in clubs_en_ldc:
        return {"error": f"Le club '{club_cible}' n'est pas dans la liste."}

    try:
        j_dep = int(journee_depart)
    except:
        j_dep = 0

    # =========================================================================
    # MODE OFFLINE (Données pré-calculées)
    # =========================================================================
    if OFFLINE_DISPONIBLE:
        distrib_rank = offline_data.get_distribution_positions(j_dep)
        distrib_points = offline_data.get_distribution_points(j_dep)
        
        if distrib_rank and distrib_points:
            # Extraction des stats pour le club
            stats_rank = distrib_rank.get(club_cible, {})
            stats_points = distrib_points.get(club_cible, {})
            
            # Conversion des clés string en int si nécessaire
            stats_rank = {int(k): v for k, v in stats_rank.items()}
            stats_points = {int(k): v for k, v in stats_points.items()}
            
            # Calculs
            p_top8 = sum(stats_rank.get(r, 0) for r in range(1, 9))
            p_qualif = sum(stats_rank.get(r, 0) for r in range(1, 25))
            p_barrage = p_qualif - p_top8
            p_elimine = 1 - p_qualif
            pts_moyen = sum(pt * prob for pt, prob in stats_points.items())
            
            # Nettoyage pour alléger le JSON
            clean_points = {k: v for k, v in stats_points.items() if v > 0.001}
            clean_ranks = {k: v for k, v in stats_rank.items() if v > 0.001}
            
            return {
                "club": club_cible,
                "day_used": j_dep,
                "mode": "OFFLINE",
                "points_moyens": round(pts_moyen, 2),
                "proba_top_8": round(min(p_top8, 1.0) * 100, 1),
                "proba_barrage": round(max(min(p_barrage, 1.0), 0) * 100, 1),
                "proba_elimine": round(max(min(p_elimine, 1.0), 0) * 100, 1),
                "distribution_points": clean_points,
                "distribution_rangs": clean_ranks
            }

    # =========================================================================
    # MODE LIVE (Fallback - Simulation en temps réel)
    # =========================================================================
    update_simulation_context(j_dep)
    
    historique_donnees = {
        0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    etat_actuel = historique_donnees.get(j_dep, etat_zero)
    debut_simulation = j_dep + 1
    
    distrib_points = distribution_points_par_club(N=nb_simulations, données=etat_actuel, debut=debut_simulation, fin=8)
    distrib_rank = distribution_position_par_club(N=nb_simulations, données=etat_actuel, debut=debut_simulation, fin=8)
    
    stats_points = distrib_points[club_cible]
    stats_rank = distrib_rank[club_cible]
    
    p_top8 = proba_top_8(club_cible, distrib_rank)
    p_qualif = proba_qualification(club_cible, distrib_rank)
    p_barrage = p_qualif - p_top8
    p_elimine = 1 - p_qualif
    pts_moyen = sum(pt * prob for pt, prob in stats_points.items())
    
    clean_points = {k: v for k, v in stats_points.items() if v > 0.001}
    clean_ranks = {k: v for k, v in stats_rank.items() if v > 0.001}

    return {
        "club": club_cible,
        "day_used": j_dep,
        "mode": "LIVE",
        "points_moyens": round(pts_moyen, 2),
        "proba_top_8": round(min(p_top8, 1.0) * 100, 1),
        "proba_barrage": round(max(min(p_barrage, 1.0), 0) * 100, 1),
        "proba_elimine": round(max(min(p_elimine, 1.0), 0) * 100, 1),
        "distribution_points": clean_points,
        "distribution_rangs": clean_ranks
    }


# -----------------------------------------------------------------------------
# FONCTION 2 : get_web_seuils (remplace lignes ~1037-1085)
# -----------------------------------------------------------------------------

def get_web_seuils(nb_simulations=1000, journee_depart=0):
    """
    Calcule la distribution des points du 8ème et du 24ème.
    Utilise les données OFFLINE si disponibles.
    """
    try:
        j_dep = int(journee_depart)
    except:
        j_dep = 0

    # =========================================================================
    # MODE OFFLINE
    # =========================================================================
    if OFFLINE_DISPONIBLE:
        distrib_pos = offline_data.get_distribution_par_position(j_dep)
        
        if distrib_pos:
            # Conversion des clés string en int
            stats_8 = {int(k): v for k, v in distrib_pos.get("8", distrib_pos.get(8, {})).items()}
            stats_24 = {int(k): v for k, v in distrib_pos.get("24", distrib_pos.get(24, {})).items()}
            
            def clean_dict(d):
                return {k: v for k, v in d.items() if v > 0.005}
            
            return {
                "journee_utilisee": j_dep,
                "mode": "OFFLINE",
                "seuil_top8": clean_dict(stats_8),
                "seuil_barrage": clean_dict(stats_24)
            }

    # =========================================================================
    # MODE LIVE
    # =========================================================================
    update_simulation_context(j_dep)
    
    map_historique = {
        0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    etat = map_historique.get(journee_depart, etat_zero)
    debut_simu = journee_depart + 1
    
    distrib_pos = distribution_par_position(N=nb_simulations, données=etat, debut=debut_simu, fin=8)
    
    stats_8 = distrib_pos.get(8, {})
    stats_24 = distrib_pos.get(24, {})
    
    def clean_dict(d):
        return {k: v for k, v in d.items() if v > 0.005}

    return {
        "journee_utilisee": journee_depart,
        "mode": "LIVE",
        "seuil_top8": clean_dict(stats_8),
        "seuil_barrage": clean_dict(stats_24)
    }


# -----------------------------------------------------------------------------
# FONCTION 3 : get_simulation_flexible (remplace lignes ~1306-1394)
# -----------------------------------------------------------------------------

def get_simulation_flexible(n_simulations=1000, start_day=0, end_day=8):
    """
    Génère le classement projeté avec moyennes.
    Utilise les données OFFLINE si disponibles ET si end_day=8.
    """
    try:
        sd = int(start_day)
    except:
        sd = 0

    # =========================================================================
    # MODE OFFLINE (seulement si on simule jusqu'à J8)
    # =========================================================================
    if OFFLINE_DISPONIBLE and int(end_day) == 8:
        moyennes = offline_data.get_moyennes(sd)
        
        if moyennes:
            ranking_data = []
            
            for club, stats in moyennes.items():
                ranking_data.append({
                    "club": club,
                    "points": round(stats.get("points", 0), 1),
                    "diff": round(stats.get("diff", 0), 1),
                    "buts": round(stats.get("buts", 0), 1),
                    "buts_ext": round(stats.get("buts_ext", 0), 1),
                    "victoires": round(stats.get("victoires", 0), 1),
                    "victoires_ext": round(stats.get("victoires_ext", 0), 1),
                })
            
            # Tri UEFA
            ranking_data.sort(key=lambda x: (
                x['points'], x['diff'], x['buts'], 
                x['buts_ext'], x['victoires'], x['victoires_ext']
            ), reverse=True)
            
            for i, row in enumerate(ranking_data):
                row['rank'] = i + 1
                row['mode'] = 'OFFLINE'
            
            return ranking_data

    # =========================================================================
    # MODE LIVE
    # =========================================================================
    update_simulation_context(sd)
    
    if start_day == 0:
        etat_initial = {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, "nb_victoires_ext": None
        }
    else:
        map_historique = {
            1: données_J1, 2: données_J2, 3: données_J3, 4: données_J4,
            5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
        }
        etat_initial = map_historique.get(start_day, {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, "nb_victoires_ext": None
        })

    total_stats = {
        club: {"points": 0, "diff_buts": 0, "buts": 0, "buts_ext": 0, "nb_victoires": 0, "nb_victoires_ext": 0} 
        for club in clubs_en_ldc
    }

    for _ in range(n_simulations):
        resultats_simu = simulation_ligue(données=etat_initial, debut=start_day + 1, fin=end_day)
        for club in clubs_en_ldc:
            total_stats[club]["points"] += resultats_simu["points"][club]
            total_stats[club]["diff_buts"] += resultats_simu["diff_buts"][club]
            total_stats[club]["buts"] += resultats_simu["buts"][club]
            total_stats[club]["buts_ext"] += resultats_simu["buts_ext"][club]
            total_stats[club]["nb_victoires"] += resultats_simu["nb_victoires"][club]
            total_stats[club]["nb_victoires_ext"] += resultats_simu["nb_victoires_ext"][club]

    ranking_data = []
    for club, stats in total_stats.items():
        ranking_data.append({
            "club": club,
            "points": round(stats["points"] / n_simulations, 1),
            "diff": round(stats["diff_buts"] / n_simulations, 1),
            "buts": round(stats["buts"] / n_simulations, 1),
            "buts_ext": round(stats["buts_ext"] / n_simulations, 1),
            "victoires": round(stats["nb_victoires"] / n_simulations, 1),
            "victoires_ext": round(stats["nb_victoires_ext"] / n_simulations, 1),
        })

    ranking_data.sort(key=lambda x: (
        x['points'], x['diff'], x['buts'], x['buts_ext'], x['victoires'], x['victoires_ext']
    ), reverse=True)

    for i, row in enumerate(ranking_data):
        row['rank'] = i + 1
        row['mode'] = 'LIVE'

    return ranking_data


# -----------------------------------------------------------------------------
# FONCTION 4 : get_probas_top8_qualif (remplace lignes ~1396-1474)
# -----------------------------------------------------------------------------

def get_probas_top8_qualif(nb_simulations=1000, journee_depart=0):
    """
    Génère les tableaux de probabilités Top 8 et Top 24.
    Utilise les données OFFLINE si disponibles.
    """
    try:
        jd = int(journee_depart)
    except:
        jd = 0

    # =========================================================================
    # MODE OFFLINE
    # =========================================================================
    if OFFLINE_DISPONIBLE:
        distrib_clubs = offline_data.get_distribution_positions(jd)
        
        if distrib_clubs:
            liste_qualif = []
            liste_top8 = []
            
            for club in clubs_en_ldc:
                distrib = distrib_clubs.get(club, {})
                # Conversion clés string -> int
                distrib = {int(k): v for k, v in distrib.items()}
                
                p_qualif = sum(distrib.get(r, 0) for r in range(1, 25))
                p_top8 = sum(distrib.get(r, 0) for r in range(1, 9))
                
                if p_qualif > 0.001:
                    liste_qualif.append({"club": club, "proba": round(min(p_qualif, 1.0) * 100, 1)})
                if p_top8 > 0.001:
                    liste_top8.append({"club": club, "proba": round(min(p_top8, 1.0) * 100, 1)})
            
            liste_qualif.sort(key=lambda x: x["proba"], reverse=True)
            liste_top8.sort(key=lambda x: x["proba"], reverse=True)
            
            return {
                "day_used": jd,
                "mode": "OFFLINE",
                "ranking_qualif": liste_qualif,
                "ranking_top8": liste_top8
            }

    # =========================================================================
    # MODE LIVE
    # =========================================================================
    update_simulation_context(jd)
    
    if journee_depart == 0:
        etat_initial = {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, "nb_victoires_ext": None
        }
    else:
        map_historique = {
            1: données_J1, 2: données_J2, 3: données_J3, 4: données_J4,
            5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
        }
        etat_initial = map_historique.get(journee_depart, {
            "classement": None, "points": None, "diff_buts": None, 
            "buts": None, "buts_ext": None, "nb_victoires": None, "nb_victoires_ext": None
        })

    debut_simu = journee_depart + 1
    distrib_clubs = distribution_position_par_club(N=nb_simulations, données=etat_initial, debut=debut_simu, fin=8)
    
    liste_qualif = []
    liste_top8 = []
    
    for club in clubs_en_ldc:
        p_qualif = proba_qualification(club, distrib_clubs)
        p_top8 = proba_top_8(club, distrib_clubs)
        
        if p_qualif > 0.001:
            liste_qualif.append({"club": club, "proba": round(p_qualif * 100, 1)})
        if p_top8 > 0.001:
            liste_top8.append({"club": club, "proba": round(p_top8 * 100, 1)})
    
    liste_qualif.sort(key=lambda x: x["proba"], reverse=True)
    liste_top8.sort(key=lambda x: x["proba"], reverse=True)
    
    return {
        "day_used": journee_depart,
        "mode": "LIVE",
        "ranking_qualif": liste_qualif,
        "ranking_top8": liste_top8
    }


# -----------------------------------------------------------------------------
# FONCTION 5 : get_scenario_analysis (remplace lignes ~1495-1577)
# -----------------------------------------------------------------------------

def get_scenario_analysis(club_cible, journee_cible, resultat_fixe, journee_depart=6, n_simulations=500):
    """
    Simule la différence avant/après un résultat fixé.
    Utilise les données OFFLINE si disponibles.
    """
    try:
        jd = int(journee_depart)
        jc = int(journee_cible)
    except:
        jd = 6
        jc = 7

    # =========================================================================
    # MODE OFFLINE
    # =========================================================================
    if OFFLINE_DISPONIBLE:
        # Distribution AVANT (simulation libre)
        distrib_avant = offline_data.get_distribution_positions(jd)
        # Distribution APRÈS (scénario fixé)
        distrib_apres = offline_data.get_scenario_distribution(jd, jc, club_cible, resultat_fixe)
        
        if distrib_avant and distrib_apres:
            # Stats AVANT
            stats_avant = distrib_avant.get(club_cible, {})
            stats_avant = {int(k): v for k, v in stats_avant.items()}
            top8_avant = sum(stats_avant.get(r, 0) for r in range(1, 9))
            qualif_avant = sum(stats_avant.get(r, 0) for r in range(1, 25))
            
            # Stats APRÈS
            stats_apres = distrib_apres.get(club_cible, {})
            stats_apres = {int(k): v for k, v in stats_apres.items()}
            top8_apres = sum(stats_apres.get(r, 0) for r in range(1, 9))
            qualif_apres = sum(stats_apres.get(r, 0) for r in range(1, 25))
            
            return {
                "club": club_cible,
                "scenario": resultat_fixe,
                "journee": jc,
                "mode": "OFFLINE",
                "avant": {
                    "top8": round(min(top8_avant, 1.0) * 100, 1),
                    "qualif": round(min(qualif_avant, 1.0) * 100, 1)
                },
                "apres": {
                    "top8": round(min(top8_apres, 1.0) * 100, 1),
                    "qualif": round(min(qualif_apres, 1.0) * 100, 1)
                },
                "delta": {
                    "top8": round((top8_apres - top8_avant) * 100, 1),
                    "qualif": round((qualif_apres - qualif_avant) * 100, 1)
                }
            }

    # =========================================================================
    # MODE LIVE
    # =========================================================================
    update_simulation_context(jd)
    
    map_historique = {
        0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    etat_initial = map_historique.get(jd, etat_zero)
    debut_simu = jd + 1
    if debut_simu > jc:
        debut_simu = jc

    # AVANT
    distrib_avant = distribution_position_par_club(N=n_simulations, données=etat_initial, debut=debut_simu, fin=8)
    stats_avant = distrib_avant.get(club_cible, {})
    top8_avant = sum(stats_avant.get(r, 0) for r in range(1, 9))
    qualif_avant = sum(stats_avant.get(r, 0) for r in range(1, 25))

    # APRÈS
    distrib_apres = distribution_position_par_club_match_fixe(
        N=n_simulations, club_fixed=club_cible, journee=jc, result_fixed=resultat_fixe,
        données=etat_initial, debut=debut_simu, fin=8
    )
    stats_apres = distrib_apres.get(club_cible, {})
    top8_apres = sum(stats_apres.get(r, 0) for r in range(1, 9))
    qualif_apres = sum(stats_apres.get(r, 0) for r in range(1, 25))

    return {
        "club": club_cible,
        "scenario": resultat_fixe,
        "journee": jc,
        "mode": "LIVE",
        "avant": {
            "top8": round(min(top8_avant, 1.0) * 100, 1),
            "qualif": round(min(qualif_avant, 1.0) * 100, 1)
        },
        "apres": {
            "top8": round(min(top8_apres, 1.0) * 100, 1),
            "qualif": round(min(qualif_apres, 1.0) * 100, 1)
        },
        "delta": {
            "top8": round((top8_apres - top8_avant) * 100, 1),
            "qualif": round((qualif_apres - qualif_avant) * 100, 1)
        }
    }


# -----------------------------------------------------------------------------
# FONCTION 6 : get_web_hypometre (remplace lignes ~1579-1657)
# -----------------------------------------------------------------------------

def get_web_hypometre(club_cible, nb_simulations=300, journee_depart=6):
    """
    Analyse quels matchs de la prochaine journée impactent le plus la qualification.
    Utilise les données OFFLINE si disponibles.
    """
    try:
        jd = int(journee_depart)
    except:
        jd = 0

    if club_cible not in clubs_en_ldc:
        return {"error": f"Club {club_cible} introuvable"}
    
    journee_suivante = jd + 1
    
    matchs_a_tester = calendrier.get(f"Journée {journee_suivante}", [])
    if not matchs_a_tester:
        matchs_a_tester = calendrier.get(journee_suivante, [])
    if not matchs_a_tester:
        return {"error": f"Pas de matchs trouvés pour J{journee_suivante}"}

    resultats_impact = []
    
    # =========================================================================
    # MODE OFFLINE
    # =========================================================================
    if OFFLINE_DISPONIBLE:
        for (dom, ext) in matchs_a_tester:
            # MONDE A : Domicile gagne
            distrib_dom_V = offline_data.get_scenario_distribution(jd, journee_suivante, dom, 'V')
            # MONDE B : Extérieur gagne (= Domicile perd)
            distrib_dom_D = offline_data.get_scenario_distribution(jd, journee_suivante, dom, 'D')
            
            if distrib_dom_V and distrib_dom_D:
                # Proba qualif dans chaque monde pour NOTRE club
                stats_A = distrib_dom_V.get(club_cible, {})
                stats_A = {int(k): v for k, v in stats_A.items()}
                p_qualif_A = sum(stats_A.get(r, 0) for r in range(1, 25))
                
                stats_B = distrib_dom_D.get(club_cible, {})
                stats_B = {int(k): v for k, v in stats_B.items()}
                p_qualif_B = sum(stats_B.get(r, 0) for r in range(1, 25))
                
                impact = abs(p_qualif_A - p_qualif_B) * 100
                is_own = (dom == club_cible or ext == club_cible)
                
                if impact > 0.5 or is_own:
                    resultats_impact.append({
                        "match": f"{dom} vs {ext}",
                        "dom": dom, "ext": ext,
                        "score": round(impact, 1),
                        "is_my_match": is_own
                    })
        
        if resultats_impact:
            resultats_impact.sort(key=lambda x: (x['is_my_match'], x['score']), reverse=True)
            return {"club": club_cible, "journee": journee_suivante, "mode": "OFFLINE", "liste": resultats_impact}

    # =========================================================================
    # MODE LIVE
    # =========================================================================
    update_simulation_context(jd)
    
    map_historique = {
        0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
        4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
    }
    etat_actuel = map_historique.get(jd, données_J6)
    
    for (dom, ext) in matchs_a_tester:
        distrib_dom = distribution_position_par_club_match_fixe(
            N=nb_simulations, club_fixed=dom, journee=journee_suivante, result_fixed='V',
            données=etat_actuel, debut=journee_suivante, fin=8
        )
        p_qualif_1 = proba_qualification(club_cible, distrib_dom)
        
        distrib_ext = distribution_position_par_club_match_fixe(
            N=nb_simulations, club_fixed=dom, journee=journee_suivante, result_fixed='D',
            données=etat_actuel, debut=journee_suivante, fin=8
        )
        p_qualif_2 = proba_qualification(club_cible, distrib_ext)
        
        impact = abs(p_qualif_1 - p_qualif_2) * 100
        is_own = (dom == club_cible or ext == club_cible)
        
        if impact > 0.5 or is_own:
            resultats_impact.append({
                "match": f"{dom} vs {ext}",
                "dom": dom, "ext": ext,
                "score": round(impact, 1),
                "is_my_match": is_own
            })

    resultats_impact.sort(key=lambda x: (x['is_my_match'], x['score']), reverse=True)
    return {"club": club_cible, "journee": journee_suivante, "mode": "LIVE", "liste": resultats_impact}


# -----------------------------------------------------------------------------
# FONCTION 7 : get_web_evolution (remplace lignes ~1659-1699)
# -----------------------------------------------------------------------------

def get_web_evolution(club, journee_max=8, n_simulations=300):
    """
    Calcule l'historique des chances pour le graphique d'évolution.
    Utilise les données OFFLINE si disponibles.
    """
    historique = []
    
    for j in range(int(journee_max) + 1):
        # =====================================================================
        # MODE OFFLINE
        # =====================================================================
        if OFFLINE_DISPONIBLE:
            distrib = offline_data.get_distribution_positions(j)
            
            if distrib and club in distrib:
                stats = distrib[club]
                stats = {int(k): v for k, v in stats.items()}
                p_top8 = sum(stats.get(r, 0) for r in range(1, 9))
                p_qualif = sum(stats.get(r, 0) for r in range(1, 25))
                
                historique.append({
                    "journee": f"J{j}",
                    "top8": round(min(p_top8, 1.0) * 100, 1),
                    "qualif": round(min(p_qualif, 1.0) * 100, 1)
                })
                continue

        # =====================================================================
        # MODE LIVE (fallback)
        # =====================================================================
        update_simulation_context(j)
        
        map_historique = {
            0: etat_zero, 1: données_J1, 2: données_J2, 3: données_J3, 
            4: données_J4, 5: données_J5, 6: données_J6, 7: données_J7, 8: données_J8
        }
        etat = map_historique.get(j, etat_zero)
        
        distrib = distribution_position_par_club(N=n_simulations, données=etat, debut=j + 1, fin=8)
        stats = distrib.get(club, {})
        p_top8 = sum(stats.get(r, 0) for r in range(1, 9))
        p_qualif = sum(stats.get(r, 0) for r in range(1, 25))
        
        historique.append({
            "journee": f"J{j}",
            "top8": round(p_top8 * 100, 1),
            "qualif": round(p_qualif * 100, 1)
        })
    
    return historique
