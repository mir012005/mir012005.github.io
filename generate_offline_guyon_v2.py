#!/usr/bin/env python3
"""
Générateur de données offline - Méthode Guyon v2
=================================================
- Format JSON identique à l'ancien
- Vectorisation NumPy complète
- Multiprocessing pour fichiers intermédiaires
- ELO dynamiques par journée (API clubelo.com)
- Gestion mémoire (gc.collect)
- Calendrier VÉRIFIÉ depuis simulator.py
"""

import json
import numpy as np
import pandas as pd
import requests
import io
import os
import gc
from datetime import datetime
import time
from multiprocessing import Pool, cpu_count

# =============================================================================
# CONFIGURATION
# =============================================================================

CLUBS = sorted([
    "Ajax", "Arsenal", "Atalanta", "Atletico", "Barcelona", "Bayern",
    "Benfica", "Bilbao", "Bodoe Glimt", "Brugge", "Chelsea", "Dortmund",
    "FC Kobenhavn", "Frankfurt", "Galatasaray", "Inter", "Juventus",
    "Kairat", "Karabakh Agdam", "Leverkusen", "Liverpool", "Man City",
    "Marseille", "Monaco", "Napoli", "Newcastle", "Olympiakos", "PSV",
    "Paphos", "Paris SG", "Real Madrid", "Slavia Praha", "Sporting",
    "St Gillis", "Tottenham", "Villarreal"
])

N_CLUBS = len(CLUBS)
CLUB_TO_IDX = {club: i for i, club in enumerate(CLUBS)}
IDX_TO_CLUB = {i: club for i, club in enumerate(CLUBS)}

# =============================================================================
# CALENDRIER CORRECT - COPIÉ DEPUIS SIMULATOR.PY LE 16/01/2026
# =============================================================================

CALENDRIER = {
    1: [
        ("Bilbao", "Arsenal"), ("PSV", "St Gillis"), ("Juventus", "Dortmund"),
        ("Real Madrid", "Marseille"), ("Benfica", "Karabakh Agdam"), ("Tottenham", "Villarreal"),
        ("Olympiakos", "Paphos"), ("Slavia Praha", "Bodoe Glimt"), ("Ajax", "Inter"),
        ("Bayern", "Chelsea"), ("Liverpool", "Atletico"), ("Paris SG", "Atalanta"),
        ("Brugge", "Monaco"), ("FC Kobenhavn", "Leverkusen"), ("Frankfurt", "Galatasaray"),
        ("Man City", "Napoli"), ("Newcastle", "Barcelona"), ("Sporting", "Kairat"),
    ],
    2: [
        ("Atalanta", "Brugge"), ("Kairat", "Real Madrid"), ("Atletico", "Frankfurt"),
        ("Chelsea", "Benfica"), ("Inter", "Slavia Praha"), ("Bodoe Glimt", "Tottenham"),
        ("Galatasaray", "Liverpool"), ("Marseille", "Ajax"), ("Paphos", "Bayern"),
        ("Karabakh Agdam", "FC Kobenhavn"), ("St Gillis", "Newcastle"), ("Arsenal", "Olympiakos"),
        ("Monaco", "Man City"), ("Leverkusen", "PSV"), ("Dortmund", "Bilbao"),
        ("Barcelona", "Paris SG"), ("Napoli", "Sporting"), ("Villarreal", "Juventus"),
    ],
    3: [
        ("Barcelona", "Olympiakos"), ("Kairat", "Paphos"), ("Arsenal", "Atletico"),
        ("Leverkusen", "Paris SG"), ("FC Kobenhavn", "Dortmund"), ("Newcastle", "Benfica"),
        ("PSV", "Napoli"), ("St Gillis", "Inter"), ("Villarreal", "Man City"),
        ("Bilbao", "Karabakh Agdam"), ("Galatasaray", "Bodoe Glimt"), ("Monaco", "Tottenham"),
        ("Atalanta", "Slavia Praha"), ("Chelsea", "Ajax"), ("Frankfurt", "Liverpool"),
        ("Bayern", "Brugge"), ("Real Madrid", "Juventus"), ("Sporting", "Marseille"),
    ],
    4: [
        ("Slavia Praha", "Arsenal"), ("Napoli", "Frankfurt"), ("Atletico", "St Gillis"),
        ("Bodoe Glimt", "Monaco"), ("Juventus", "Sporting"), ("Liverpool", "Real Madrid"),
        ("Olympiakos", "PSV"), ("Paris SG", "Bayern"), ("Tottenham", "FC Kobenhavn"),
        ("Paphos", "Villarreal"), ("Karabakh Agdam", "Chelsea"), ("Ajax", "Galatasaray"),
        ("Brugge", "Barcelona"), ("Inter", "Kairat"), ("Man City", "Dortmund"),
        ("Newcastle", "Bilbao"), ("Marseille", "Atalanta"), ("Benfica", "Leverkusen"),
    ],
    5: [
        ("Ajax", "Benfica"), ("Galatasaray", "St Gillis"), ("Dortmund", "Villarreal"),
        ("Chelsea", "Barcelona"), ("Bodoe Glimt", "Juventus"), ("Man City", "Leverkusen"),
        ("Marseille", "Newcastle"), ("Slavia Praha", "Bilbao"), ("Napoli", "Karabakh Agdam"),
        ("FC Kobenhavn", "Kairat"), ("Paphos", "Monaco"), ("Arsenal", "Bayern"),
        ("Atletico", "Inter"), ("Frankfurt", "Atalanta"), ("Liverpool", "PSV"),
        ("Olympiakos", "Real Madrid"), ("Paris SG", "Tottenham"), ("Sporting", "Brugge"),
    ],
    6: [
        ("Kairat", "Olympiakos"), ("Bayern", "Sporting"), ("Monaco", "Galatasaray"),
        ("Atalanta", "Chelsea"), ("Barcelona", "Frankfurt"), ("Inter", "Liverpool"),
        ("PSV", "Atletico"), ("St Gillis", "Marseille"), ("Tottenham", "Slavia Praha"),
        ("Karabakh Agdam", "Ajax"), ("Villarreal", "FC Kobenhavn"), ("Bilbao", "Paris SG"),
        ("Leverkusen", "Newcastle"), ("Dortmund", "Bodoe Glimt"), ("Brugge", "Arsenal"),
        ("Juventus", "Paphos"), ("Real Madrid", "Man City"), ("Benfica", "Napoli"),
    ],
    7: [
        ("Kairat", "Brugge"), ("Bodoe Glimt", "Man City"), ("FC Kobenhavn", "Napoli"),
        ("Inter", "Arsenal"), ("Olympiakos", "Leverkusen"), ("Real Madrid", "Monaco"),
        ("Sporting", "Paris SG"), ("Tottenham", "Dortmund"), ("Villarreal", "Ajax"),
        ("Galatasaray", "Atletico"), ("Karabakh Agdam", "Frankfurt"), ("Atalanta", "Bilbao"),
        ("Chelsea", "Paphos"), ("Bayern", "St Gillis"), ("Juventus", "Benfica"),
        ("Newcastle", "PSV"), ("Marseille", "Liverpool"), ("Slavia Praha", "Barcelona"),
    ],
    8: [
        ("Ajax", "Olympiakos"), ("Arsenal", "Kairat"), ("Monaco", "Juventus"),
        ("Bilbao", "Sporting"), ("Atletico", "Bodoe Glimt"), ("Leverkusen", "Villarreal"),
        ("Dortmund", "Inter"), ("Brugge", "Marseille"), ("Frankfurt", "Tottenham"),
        ("Barcelona", "FC Kobenhavn"), ("Liverpool", "Karabakh Agdam"), ("Man City", "Galatasaray"),
        ("Paphos", "Slavia Praha"), ("Paris SG", "Newcastle"), ("PSV", "Bayern"),
        ("St Gillis", "Atalanta"), ("Benfica", "Real Madrid"), ("Napoli", "Chelsea"),
    ],
}

# Dates des journées LDC (pour ELO historiques)
CALENDRIER_LDC_DATES = {
    1: "2025-09-15",
    2: "2025-09-29",
    3: "2025-10-20",
    4: "2025-11-03",
    5: "2025-11-24",
    6: "2025-12-08",
    7: "2026-01-19",
    8: "2026-01-27"
}

# =============================================================================
# DONNÉES HISTORIQUES - FORMAT: (points, diff_buts, buts, buts_ext, victoires, victoires_ext)
# =============================================================================

HISTORIQUE = {
    0: {club: (0, 0, 0, 0, 0, 0) for club in CLUBS},
}

def charger_historique_depuis_simulator():
    """Charge les données historiques depuis simulator.py"""
    global HISTORIQUE
    try:
        import sys
        sys.path.insert(0, '.')
        from simulator import (
            données_J1, données_J2, données_J3, données_J4,
            données_J5, données_J6, données_J7, données_J8
        )
        
        def convertir(donnees):
            """Convertit du format simulator.py au format tuple."""
            result = {}
            # Si c'est l'état zéro (None partout)
            if donnees.get('points') is None:
                return {club: (0, 0, 0, 0, 0, 0) for club in CLUBS}
            
            for club in CLUBS:
                result[club] = (
                    donnees['points'].get(club, 0),
                    donnees['diff_buts'].get(club, 0),
                    donnees['buts'].get(club, 0),
                    donnees['buts_ext'].get(club, 0),
                    donnees['nb_victoires'].get(club, 0),
                    donnees['nb_victoires_ext'].get(club, 0)
                )
            return result
        
        HISTORIQUE[1] = convertir(données_J1)
        HISTORIQUE[2] = convertir(données_J2)
        HISTORIQUE[3] = convertir(données_J3)
        HISTORIQUE[4] = convertir(données_J4)
        HISTORIQUE[5] = convertir(données_J5)
        HISTORIQUE[6] = convertir(données_J6)
        HISTORIQUE[7] = convertir(données_J7)
        HISTORIQUE[8] = convertir(données_J8)
        print("✅ Historique chargé depuis simulator.py")
        return True
    except Exception as e:
        print(f"⚠️ Impossible de charger l'historique: {e}")
        return False

# =============================================================================
# GESTION DES ELO
# =============================================================================

CACHE_ELO = {}
ELO_RATINGS = {}

def charger_elo_depuis_csv(csv_path="Elo_rating_pré_ldc.csv"):
    """Charge les ELO depuis le fichier CSV (pour J0)."""
    try:
        elo_df = pd.read_csv(csv_path)
        elo_dict = {}
        for club in CLUBS:
            club_data = elo_df.loc[elo_df["Club"] == club, "Elo"]
            if not club_data.empty:
                elo_dict[club] = float(club_data.values[0])
            else:
                elo_dict[club] = 1600.0
        return elo_dict
    except Exception as e:
        print(f"⚠️ Erreur CSV: {e}")
        return {club: 1700.0 for club in CLUBS}

def fetch_elo_from_api(date_str=None):
    """Récupère les ELO depuis api.clubelo.com."""
    try:
        if date_str:
            url = f"http://api.clubelo.com/{date_str}"
            print(f"📡 Récupération ELO Historique ({date_str})...")
        else:
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"http://api.clubelo.com/{today}"
            print(f"📡 Récupération ELO LIVE ({today})...")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text))
        df = df[['Club', 'Elo']]
        raw_elos = dict(zip(df.Club.astype(str), df.Elo))
        
        mapped_elos = {}
        for club in CLUBS:
            if club in raw_elos:
                mapped_elos[club] = raw_elos[club]
            else:
                mapped_elos[club] = 1600.0
        return mapped_elos
    except Exception as e:
        print(f"⚠️ Erreur API ELO: {e}")
        return None

def get_elo_pour_journee(journee_depart):
    """Récupère les ELO appropriés pour une journée."""
    global ELO_RATINGS
    
    if journee_depart in CACHE_ELO:
        ELO_RATINGS = CACHE_ELO[journee_depart]
        return
    
    if journee_depart == 0:
        elos = charger_elo_depuis_csv()
        print("✅ ELO chargés depuis Elo_rating_pré_ldc.csv")
    else:
        date_cible = CALENDRIER_LDC_DATES.get(journee_depart + 1)
        if date_cible:
            target_date = datetime.strptime(date_cible, "%Y-%m-%d")
            today = datetime.now()
            if target_date > today:
                elos = fetch_elo_from_api(None)
            else:
                elos = fetch_elo_from_api(date_cible)
        else:
            elos = fetch_elo_from_api(None)
    
    if elos is None:
        elos = charger_elo_depuis_csv()
        print("⚠️ Fallback vers CSV")
    
    CACHE_ELO[journee_depart] = elos
    ELO_RATINGS = elos
    print(f"   Exemple: Liverpool={ELO_RATINGS.get('Liverpool', 0):.1f}, Marseille={ELO_RATINGS.get('Marseille', 0):.1f}")

# =============================================================================
# FONCTIONS POISSON
# =============================================================================

def win_expectation(elo_1, elo_2):
    return 1 / (1 + 10 ** ((elo_2 - elo_1) / 400))

def coeff_poisson_home(w):
    return 0.76 + 1.45 * w

def coeff_poisson_away(w):
    return 2.17 - 1.45 * w

def precalculer_lambdas():
    """Précalcule les paramètres Poisson."""
    lambda_home = np.zeros((N_CLUBS, N_CLUBS))
    lambda_away = np.zeros((N_CLUBS, N_CLUBS))
    
    for i, club1 in enumerate(CLUBS):
        for j, club2 in enumerate(CLUBS):
            if i != j:
                w = win_expectation(ELO_RATINGS.get(club1, 1700), ELO_RATINGS.get(club2, 1700))
                lambda_home[i, j] = coeff_poisson_home(w)
                lambda_away[i, j] = coeff_poisson_away(w)
    
    return lambda_home, lambda_away

# =============================================================================
# SIMULATION VECTORISÉE - MÉTHODE GUYON
# =============================================================================

def simuler_N_saisons_avec_resultats(N, donnees_initiales, journee_debut, journee_fin=8):
    """
    Simule N saisons avec stockage des résultats pour filtrage Guyon.
    Retourne les stats TOTALES (historique + simulé).
    """
    LAMBDA_HOME, LAMBDA_AWAY = precalculer_lambdas()
    
    # Initialisation avec données historiques
    points = np.zeros((N, N_CLUBS), dtype=np.int32)
    diff_buts = np.zeros((N, N_CLUBS), dtype=np.int32)
    buts = np.zeros((N, N_CLUBS), dtype=np.int32)
    buts_ext = np.zeros((N, N_CLUBS), dtype=np.int32)
    victoires = np.zeros((N, N_CLUBS), dtype=np.int32)
    victoires_ext = np.zeros((N, N_CLUBS), dtype=np.int32)
    
    # Charger l'historique
    for club, stats_club in donnees_initiales.items():
        if club in CLUB_TO_IDX:
            idx = CLUB_TO_IDX[club]
            points[:, idx] = stats_club[0]
            diff_buts[:, idx] = stats_club[1]
            buts[:, idx] = stats_club[2]
            buts_ext[:, idx] = stats_club[3]
            victoires[:, idx] = stats_club[4]
            victoires_ext[:, idx] = stats_club[5]
    
    # Liste des matchs à simuler
    matchs_info = []
    for j in range(journee_debut, journee_fin + 1):
        for home, away in CALENDRIER[j]:
            matchs_info.append((j, CLUB_TO_IDX[home], CLUB_TO_IDX[away], home, away))
    
    n_matchs = len(matchs_info)
    if n_matchs == 0:
        return None, None, None, None
    
    # Préparer les lambdas
    home_indices = np.array([m[1] for m in matchs_info])
    away_indices = np.array([m[2] for m in matchs_info])
    lambdas_home = LAMBDA_HOME[home_indices, away_indices]
    lambdas_away = LAMBDA_AWAY[home_indices, away_indices]
    
    # Simulation vectorisée
    scores_home = np.random.poisson(lambdas_home, size=(N, n_matchs))
    scores_away = np.random.poisson(lambdas_away, size=(N, n_matchs))
    
    # Résultats: 1=dom gagne, -1=ext gagne, 0=nul
    resultats_matchs = np.sign(scores_home - scores_away).astype(np.int8)
    
    # Mise à jour des stats
    for m in range(n_matchs):
        h_idx = home_indices[m]
        a_idx = away_indices[m]
        
        s_home = scores_home[:, m]
        s_away = scores_away[:, m]
        
        diff_buts[:, h_idx] += s_home - s_away
        diff_buts[:, a_idx] += s_away - s_home
        
        buts[:, h_idx] += s_home
        buts[:, a_idx] += s_away
        buts_ext[:, a_idx] += s_away
        
        home_win = resultats_matchs[:, m] == 1
        away_win = resultats_matchs[:, m] == -1
        draw = resultats_matchs[:, m] == 0
        
        points[:, h_idx] += 3 * home_win + draw
        points[:, a_idx] += 3 * away_win + draw
        
        victoires[:, h_idx] += home_win
        victoires[:, a_idx] += away_win
        victoires_ext[:, a_idx] += away_win
    
    # Calcul des positions (VECTORISÉ)
    score_tri = (
        points.astype(np.int64) * 1000000000000 +
        (diff_buts.astype(np.int64) + 1000) * 10000000 +
        buts.astype(np.int64) * 100000 +
        buts_ext.astype(np.int64) * 1000 +
        victoires.astype(np.int64) * 10 +
        victoires_ext.astype(np.int64)
    )
    
    ordre = np.argsort(-score_tri, axis=1)
    positions = np.zeros((N, N_CLUBS), dtype=np.int32)
    rows = np.arange(N)[:, np.newaxis]
    positions[rows, ordre] = np.arange(1, N_CLUBS + 1)
    
    # Index des matchs pour filtrage
    index_matchs = {}
    for m, (journee, h_idx, a_idx, home, away) in enumerate(matchs_info):
        if journee not in index_matchs:
            index_matchs[journee] = {}
        index_matchs[journee][home] = (m, True)
        index_matchs[journee][away] = (m, False)
    
    return positions, resultats_matchs, index_matchs, {
        'points': points,
        'diff_buts': diff_buts,
        'buts': buts,
        'buts_ext': buts_ext,
        'victoires': victoires,
        'victoires_ext': victoires_ext
    }

# =============================================================================
# CALCUL DES DISTRIBUTIONS (FORMAT ANCIEN)
# =============================================================================

def calculer_distribution_positions(positions, mask=None):
    """Calcule {club: {position: proba}} - VERSION OPTIMISÉE"""
    if mask is not None:
        indices = np.where(mask)[0]
        N = len(indices)
        if N == 0:
            return {club: {} for club in CLUBS}
    else:
        indices = None
        N = positions.shape[0]
    
    distribution = {}
    for club_idx, club in enumerate(CLUBS):
        if indices is not None:
            col = positions[indices, club_idx]
        else:
            col = positions[:, club_idx]
        
        # bincount est BEAUCOUP plus rapide que sum(==p) en boucle
        counts = np.bincount(col, minlength=N_CLUBS + 1)
        
        distribution[club] = {}
        for p in range(1, N_CLUBS + 1):
            if counts[p] > 0:
                distribution[club][p] = counts[p] / N
    
    return distribution

def calculer_distribution_points(stats, mask=None):
    """Calcule {club: {nb_points: proba}} - VERSION OPTIMISÉE"""
    if mask is not None:
        indices = np.where(mask)[0]
        N = len(indices)
        if N == 0:
            return {club: {} for club in CLUBS}
    else:
        indices = None
        N = stats['points'].shape[0]
    
    distribution = {}
    for club_idx, club in enumerate(CLUBS):
        if indices is not None:
            col = stats['points'][indices, club_idx]
        else:
            col = stats['points'][:, club_idx]
        
        # bincount pour comptage rapide
        counts = np.bincount(col)
        
        distribution[club] = {}
        for val, cnt in enumerate(counts):
            if cnt > 0:
                distribution[club][int(val)] = cnt / N
    
    return distribution

def calculer_par_position(positions, stats, mask=None):
    """Calcule {position: {nb_points: proba}} - VERSION OPTIMISÉE"""
    if mask is not None:
        indices = np.where(mask)[0]
        pos = positions[indices]
        pts = stats['points'][indices]
    else:
        pos = positions
        pts = stats['points']
    
    N = pos.shape[0]
    if N == 0:
        return {}
    
    par_position = {}
    for p in range(1, N_CLUBS + 1):
        par_position[p] = {}
        # Masque pour cette position (sur toutes les colonnes)
        mask_pos = pos == p
        points_at_pos = pts[mask_pos]
        
        if len(points_at_pos) > 0:
            counts = np.bincount(points_at_pos)
            total = counts.sum()
            for val, cnt in enumerate(counts):
                if cnt > 0:
                    par_position[p][int(val)] = cnt / total
    
    return par_position

def calculer_moyennes(stats, mask=None):
    """Calcule les moyennes avec TOUS les champs - VERSION OPTIMISÉE."""
    if mask is not None:
        indices = np.where(mask)[0]
        N = len(indices)
        if N == 0:
            return {club: {} for club in CLUBS}
    else:
        indices = None
        N = stats['points'].shape[0]
    
    moyennes = {}
    for club_idx, club in enumerate(CLUBS):
        if indices is not None:
            moyennes[club] = {
                'points': float(np.mean(stats['points'][indices, club_idx])),
                'diff': float(np.mean(stats['diff_buts'][indices, club_idx])),
                'buts': float(np.mean(stats['buts'][indices, club_idx])),
                'buts_ext': float(np.mean(stats['buts_ext'][indices, club_idx])),
                'victoires': float(np.mean(stats['victoires'][indices, club_idx])),
                'victoires_ext': float(np.mean(stats['victoires_ext'][indices, club_idx]))
            }
        else:
            moyennes[club] = {
                'points': float(np.mean(stats['points'][:, club_idx])),
                'diff': float(np.mean(stats['diff_buts'][:, club_idx])),
                'buts': float(np.mean(stats['buts'][:, club_idx])),
                'buts_ext': float(np.mean(stats['buts_ext'][:, club_idx])),
                'victoires': float(np.mean(stats['victoires'][:, club_idx])),
                'victoires_ext': float(np.mean(stats['victoires_ext'][:, club_idx]))
            }
    
    return moyennes

# =============================================================================
# GÉNÉRATION DES DONNÉES
# =============================================================================

def generer_donnees_guyon(journee_depart, journee_fin, n_simulations, generer_scenarios=True):
    """Génère les données avec la méthode Guyon."""
    print(f"\n{'='*60}")
    print(f"GÉNÉRATION J{journee_depart} → J{journee_fin} (N={n_simulations:,})")
    print(f"Méthode: GUYON (probabilités conditionnelles)")
    print(f"{'='*60}")
    
    # Charger les ELO
    get_elo_pour_journee(journee_depart)
    
    donnees_init = HISTORIQUE.get(journee_depart, HISTORIQUE[0])
    debut_simu = journee_depart + 1
    
    # Structure JSON identique à l'ancien
    data = {
        "journee_depart": journee_depart,
        "n_simulations": n_simulations,
        "generated_at": datetime.now().isoformat(),
        "base": {},
        "scenarios": {}
    }
    
    # Simulation
    print(f"\n[SIMULATION] {n_simulations:,} trajectoires...")
    t0 = time.time()
    
    positions, resultats_matchs, index_matchs, stats = simuler_N_saisons_avec_resultats(
        n_simulations, donnees_init, debut_simu, journee_fin
    )
    
    print(f"             Terminé en {time.time()-t0:.1f}s")
    
    if positions is None:
        print("⚠️ Aucun match à simuler")
        return data
    
    # Calcul des distributions de base
    print(f"\n[BASE] Calcul des distributions...")
    data["base"]["positions"] = calculer_distribution_positions(positions)
    data["base"]["points"] = calculer_distribution_points(stats)
    data["base"]["par_position"] = calculer_par_position(positions, stats)
    data["base"]["moyennes"] = calculer_moyennes(stats)
    
    # Scénarios par filtrage
    if generer_scenarios and journee_fin == 8:
        print(f"\n[SCÉNARIOS] Extraction par filtrage...")
        
        for journee_cible in range(debut_simu, journee_fin + 1):
            t_j = time.time()
            data["scenarios"][str(journee_cible)] = {}
            
            for club in CLUBS:
                if journee_cible not in index_matchs or club not in index_matchs[journee_cible]:
                    continue
                
                match_idx, is_home = index_matchs[journee_cible][club]
                
                if is_home:
                    mask_V = resultats_matchs[:, match_idx] == 1
                    mask_N = resultats_matchs[:, match_idx] == 0
                    mask_D = resultats_matchs[:, match_idx] == -1
                else:
                    mask_V = resultats_matchs[:, match_idx] == -1
                    mask_N = resultats_matchs[:, match_idx] == 0
                    mask_D = resultats_matchs[:, match_idx] == 1
                
                data["scenarios"][str(journee_cible)][club] = {}
                
                for resultat, mask in [('V', mask_V), ('N', mask_N), ('D', mask_D)]:
                    if np.sum(mask) > 0:
                        data["scenarios"][str(journee_cible)][club][resultat] = \
                            calculer_distribution_positions(positions, mask)
            
            print(f"  Journée {journee_cible}:")
            print(f"    → {time.time()-t_j:.1f}s")
    
    # Libérer la mémoire
    del positions, resultats_matchs, stats
    gc.collect()
    
    return data

# =============================================================================
# COMPRESSION ET SAUVEGARDE
# =============================================================================

def compresser_donnees(data, seuil=0.00001):
    """Supprime les probabilités < seuil et convertit les clés int en str."""
    def clean(obj, depth=0):
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                # Convertir clés int en str pour JSON
                key = str(k) if isinstance(k, int) else k
                cleaned = clean(v, depth + 1)
                # Filtrer les probas nulles
                if isinstance(cleaned, (int, float)):
                    if cleaned >= seuil:
                        result[key] = cleaned
                elif cleaned:  # dict non vide ou autre
                    result[key] = cleaned
            return result
        return obj
    return clean(data)

def sauvegarder_json(data, journee_depart, journee_fin, output_dir="data"):
    """Sauvegarde en JSON."""
    os.makedirs(output_dir, exist_ok=True)
    
    if journee_fin == 8:
        filename = f"J{journee_depart}.json"
    else:
        filename = f"J{journee_depart}_to_J{journee_fin}.json"
    
    filepath = os.path.join(output_dir, filename)
    
    data_compressed = compresser_donnees(data)
    
    with open(filepath, 'w') as f:
        json.dump(data_compressed, f)
    
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"\n💾 Sauvegardé: {filepath} ({size_mb:.1f} MB)")
    
    return filepath

# =============================================================================
# MAIN AVEC MULTIPROCESSING
# =============================================================================

def generer_fichier_intermediaire(args):
    """Worker pour multiprocessing."""
    j_depart, j_fin, n_simus = args
    try:
        # Recharger l'historique dans le worker
        charger_historique_depuis_simulator()
        data = generer_donnees_guyon(j_depart, j_fin, n_simus, generer_scenarios=False)
        filepath = sauvegarder_json(data, j_depart, j_fin)
        
        # Libérer mémoire
        del data
        gc.collect()
        
        return (j_depart, j_fin, True)
    except Exception as e:
        print(f"❌ Erreur J{j_depart}→J{j_fin}: {e}")
        return (j_depart, j_fin, False)

def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("GÉNÉRATEUR OFFLINE - MÉTHODE GUYON v2")
    print(f"CPUs: {cpu_count()} | RAM: Gestion active (gc.collect)")
    print("=" * 60)
    
    # Charger l'historique
    if not charger_historique_depuis_simulator():
        print("❌ Impossible de continuer sans historique")
        return
    
    N_SIMULATIONS = 1_000_000
    USE_MULTIPROCESSING = True
    
    t_total = time.time()
    
    # =========================================================================
    # PHASE 1: Fichiers principaux (avec scénarios) - SÉQUENTIEL
    # =========================================================================
    print("\n" + "=" * 60)
    print("PHASE 1: Fichiers principaux (Jx → J8 avec scénarios)")
    print("=" * 60)
    
    for j_depart in range(0, 7):
        t0 = time.time()
        data = generer_donnees_guyon(j_depart, 8, N_SIMULATIONS, generer_scenarios=True)
        sauvegarder_json(data, j_depart, 8)
        print(f"    Temps J{j_depart}: {time.time()-t0:.1f}s")
        
        # Libérer mémoire entre chaque fichier
        del data
        gc.collect()
    
    # =========================================================================
    # PHASE 2: Fichiers intermédiaires (sans scénarios) - PARALLÈLE
    # =========================================================================
    print("\n" + "=" * 60)
    print("PHASE 2: Fichiers intermédiaires (Jx → Jy)")
    print("=" * 60)
    
    combinaisons = []
    for j_depart in range(0, 6):
        for j_fin in range(j_depart + 1, 8):
            combinaisons.append((j_depart, j_fin, N_SIMULATIONS))
    
    print(f"    {len(combinaisons)} fichiers à générer")
    
    if USE_MULTIPROCESSING and len(combinaisons) > 1:
        n_workers = min(cpu_count(), 3)  # Max 3 pour limiter RAM
        print(f"    Mode: PARALLÈLE ({n_workers} workers)")
        
        with Pool(n_workers) as pool:
            results = pool.map(generer_fichier_intermediaire, combinaisons)
        
        success = sum(1 for r in results if r[2])
        print(f"\n    Résultat: {success}/{len(combinaisons)} fichiers")
    else:
        print(f"    Mode: SÉQUENTIEL")
        for args in combinaisons:
            generer_fichier_intermediaire(args)
    
    # =========================================================================
    # RÉSUMÉ
    # =========================================================================
    print("\n" + "=" * 60)
    duree = time.time() - t_total
    print(f"✅ TERMINÉ en {duree:.0f}s ({duree/60:.1f} min)")
    print("=" * 60)

if __name__ == "__main__":
    main()
