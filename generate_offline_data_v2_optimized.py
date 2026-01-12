#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GÉNÉRATEUR DE DONNÉES OFFLINE V2 - VERSION OPTIMISÉE
=====================================================
Utilise NumPy pour vectoriser les simulations Monte Carlo.
Génère TOUTES les combinaisons (start → end) possibles.

Usage:
    python generate_offline_data.py [--simulations N] [--skip-to-j8]

Options:
    --start X        : Générer uniquement à partir de Jx
    --end Y          : Générer uniquement jusqu'à Jy  
    --max-journee M  : Dernière journée avec données réelles (défaut: 6)
    --simulations N  : Nombre de simulations (défaut: 1000000)
    --skip-to-j8     : Ne pas générer les combinaisons →J8 (si déjà faites)
    --no-scenarios   : Ne pas générer les scénarios

Fichiers générés:
    data/J0_to_J1.json, data/J0_to_J8.json, ..., data/J6_to_J7.json
"""

import json
import os
import sys
import time
import math
import argparse
import numpy as np
from datetime import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_DIR = "data"
DEFAULT_SIMULATIONS = 1_000_000

# Liste des clubs (doit correspondre à simulator.py)
CLUBS = sorted([
    "Paris SG", "Real Madrid", "Man City", "Bayern", "Liverpool", "Inter",
    "Chelsea", "Dortmund", "Barcelona", "Arsenal", "Leverkusen", "Atletico",
    "Benfica", "Atalanta", "Villarreal", "Juventus", "Frankfurt", "Brugge",
    "Tottenham", "PSV", "Ajax", "Napoli", "Sporting", "Olympiakos",
    "Slavia Praha", "Bodoe Glimt", "Marseille", "FC Kobenhavn", "Monaco",
    "Galatasaray", "St Gillis", "Karabakh Agdam", "Bilbao", "Newcastle",
    "Paphos", "Kairat"
])

N_CLUBS = len(CLUBS)
CLUB_TO_IDX = {club: i for i, club in enumerate(CLUBS)}
IDX_TO_CLUB = {i: club for i, club in enumerate(CLUBS)}

# Calendrier complet
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
        ("Slavia Praha", "Arsenal"), ("Karabakh Agdam", "Monaco"), ("Bodoe Glimt", "Man City"),
        ("Ajax", "Galatasaray"), ("Benfica", "Barcelona"), ("Brugge", "Sporting"),
        ("Dortmund", "Atalanta"), ("Inter", "Kairat"), ("Juventus", "Bilbao"),
        ("Liverpool", "Villarreal"), ("Napoli", "Chelsea"), ("Olympiakos", "St Gillis"),
        ("Paphos", "Leverkusen"), ("Paris SG", "Newcastle"), ("Atletico", "PSV"),
        ("Marseille", "Bayern"), ("Tottenham", "Frankfurt"), ("Real Madrid", "FC Kobenhavn"),
    ],
    5: [
        ("Arsenal", "Monaco"), ("Barcelona", "Tottenham"), ("Bayern", "Olympiakos"),
        ("Bilbao", "Atalanta"), ("Chelsea", "Galatasaray"), ("FC Kobenhavn", "Bodoe Glimt"),
        ("Frankfurt", "Inter"), ("Karabakh Agdam", "Marseille"), ("Kairat", "Napoli"),
        ("Leverkusen", "Benfica"), ("Man City", "Ajax"), ("Newcastle", "Slavia Praha"),
        ("Paris SG", "Brugge"), ("PSV", "Dortmund"), ("Sporting", "Real Madrid"),
        ("St Gillis", "Juventus"), ("Villarreal", "Atletico"), ("Paphos", "Liverpool"),
    ],
    6: [
        ("Ajax", "Paphos"), ("Atalanta", "Leverkusen"), ("Atletico", "Karabakh Agdam"),
        ("Benfica", "PSV"), ("Bodoe Glimt", "Bilbao"), ("Brugge", "Newcastle"),
        ("Dortmund", "Chelsea"), ("Galatasaray", "Kairat"), ("Inter", "Monaco"),
        ("Juventus", "Bayern"), ("Marseille", "Villarreal"), ("Napoli", "Paris SG"),
        ("Olympiakos", "FC Kobenhavn"), ("Real Madrid", "Arsenal"), ("Slavia Praha", "Barcelona"),
        ("Sporting", "Frankfurt"), ("St Gillis", "Man City"), ("Tottenham", "Liverpool"),
    ],
    7: [
        ("Arsenal", "Sporting"), ("Atalanta", "Real Madrid"), ("Atletico", "Inter"),
        ("Bayern", "Karabakh Agdam"), ("Benfica", "Tottenham"), ("Bilbao", "Olympiakos"),
        ("Brugge", "Bodoe Glimt"), ("Chelsea", "St Gillis"), ("FC Kobenhavn", "Galatasaray"),
        ("Frankfurt", "Paphos"), ("Leverkusen", "Slavia Praha"), ("Liverpool", "Kairat"),
        ("Man City", "Barcelona"), ("Monaco", "Marseille"), ("Napoli", "Ajax"),
        ("Newcastle", "Villarreal"), ("Paris SG", "Dortmund"), ("PSV", "Juventus"),
    ],
    8: [
        ("Ajax", "Bilbao"), ("Barcelona", "Leverkusen"), ("Bodoe Glimt", "Benfica"),
        ("Dortmund", "Napoli"), ("Galatasaray", "Brugge"), ("Inter", "Bayern"),
        ("Juventus", "Chelsea"), ("Karabakh Agdam", "Newcastle"), ("Kairat", "Arsenal"),
        ("Liverpool", "Monaco"), ("Man City", "Real Madrid"), ("Marseille", "PSV"),
        ("Olympiakos", "Atalanta"), ("Paphos", "Atletico"), ("Slavia Praha", "Sporting"),
        ("St Gillis", "FC Kobenhavn"), ("Tottenham", "Paris SG"), ("Villarreal", "Frankfurt"),
    ],
}

# =============================================================================
# DONNÉES HISTORIQUES - IMPORTÉES DIRECTEMENT DE SIMULATOR.PY
# =============================================================================

def charger_donnees_depuis_simulator():
    """
    Charge les données historiques depuis simulator.py et les convertit au format attendu.
    Format simulator.py: {'points': {club: pts}, 'diff_buts': {...}, ...}
    Format attendu ici: {club: [pts, diff, buts, buts_ext, vic, vic_ext]}
    """
    from simulator import (
        données_J1, données_J2, données_J3, données_J4, 
        données_J5, données_J6, données_J7, données_J8,
        clubs_en_ldc
    )
    
    def convertir(donnees_sim):
        """Convertit du format simulator au format liste."""
        if donnees_sim.get('points') is None:
            # C'est un etat_zero
            return {club: [0, 0, 0, 0, 0, 0] for club in CLUBS}
        
        result = {}
        for club in CLUBS:
            result[club] = [
                donnees_sim['points'].get(club, 0),
                donnees_sim['diff_buts'].get(club, 0),
                donnees_sim['buts'].get(club, 0),
                donnees_sim['buts_ext'].get(club, 0),
                donnees_sim['nb_victoires'].get(club, 0),
                donnees_sim['nb_victoires_ext'].get(club, 0)
            ]
        return result
    
    return {
        0: {club: [0, 0, 0, 0, 0, 0] for club in CLUBS},
        1: convertir(données_J1),
        2: convertir(données_J2),
        3: convertir(données_J3),
        4: convertir(données_J4),
        5: convertir(données_J5),
        6: convertir(données_J6),
        7: convertir(données_J7),
        8: convertir(données_J8)
    }

# Chargement au démarrage
HISTORIQUE = charger_donnees_depuis_simulator()

# =============================================================================
# CHARGEMENT DES ELO
# =============================================================================

def charger_elo():
    """Charge les ratings ELO depuis le CSV."""
    base_dir = Path(__file__).parent
    elo_file = base_dir / "Elo_rating_pré_ldc.csv"
    
    import pandas as pd
    elo_df = pd.read_csv(elo_file)
    elo_dict = {}
    for club in CLUBS:
        row = elo_df[elo_df["Club"] == club]
        if len(row) > 0:
            elo_dict[club] = row["Elo"].values[0]
        else:
            elo_dict[club] = 1500  # Valeur par défaut
    return elo_dict

ELO_RATINGS = charger_elo()

# =============================================================================
# CALCUL DES PARAMÈTRES POISSON (PRÉ-CALCULÉS)
# =============================================================================

def win_expectation(elo1, elo2):
    """Probabilité de victoire basée sur ELO."""
    return 1 / (1 + 10 ** ((elo2 - elo1 - 100) / 400))

def coeff_poisson_home(w):
    """Coefficient Poisson pour l'équipe à domicile."""
    if w <= 0.9:
        return -5.42301*(w**4) + 15.49728*(w**3) - 12.6499*(w**2) + 5.36198*w + 0.22862
    else:
        return 231098.16153*((w-0.9)**4) - 30953.10199*((w-0.9)**3) + 1347.51495*((w-0.9)**2) - 1.63074*(w-0.9) + 2.54747

def coeff_poisson_away(w):
    """Coefficient Poisson pour l'équipe à l'extérieur."""
    if w >= 0.1:
        return -1.25010*(w**4) - 1.99984*(w**3) + 6.54946*(w**2) - 5.83979*w + 2.80352
    else:
        return 90173.57949*((w-0.1)**4) + 10064.38612*((w-0.1)**3) + 218.6628*((w-0.1)**2) - 11.06198*(w-0.1) + 2.28291

def precalculer_lambdas():
    """
    Pré-calcule tous les paramètres lambda (Poisson) pour chaque match possible.
    Retourne deux matrices N_CLUBS x N_CLUBS pour lambda_home et lambda_away.
    """
    lambda_home = np.zeros((N_CLUBS, N_CLUBS))
    lambda_away = np.zeros((N_CLUBS, N_CLUBS))
    
    for i, club1 in enumerate(CLUBS):
        for j, club2 in enumerate(CLUBS):
            if i != j:
                w = win_expectation(ELO_RATINGS[club1], ELO_RATINGS[club2])
                lambda_home[i, j] = coeff_poisson_home(w)
                lambda_away[i, j] = coeff_poisson_away(w)
    
    return lambda_home, lambda_away

LAMBDA_HOME, LAMBDA_AWAY = precalculer_lambdas()

# =============================================================================
# SIMULATION VECTORISÉE
# =============================================================================

def convertir_calendrier_indices(journee_debut, journee_fin):
    """
    Convertit le calendrier en indices numpy pour les journées spécifiées.
    Retourne: (home_indices, away_indices) - arrays de shape (n_matchs,)
    """
    home_indices = []
    away_indices = []
    
    for j in range(journee_debut, journee_fin + 1):
        for home, away in CALENDRIER[j]:
            home_indices.append(CLUB_TO_IDX[home])
            away_indices.append(CLUB_TO_IDX[away])
    
    return np.array(home_indices), np.array(away_indices)

def simuler_N_saisons(N, donnees_initiales, journee_debut, journee_fin=8):
    """
    Simule N saisons en parallèle avec NumPy.
    
    Retourne:
        positions: array (N, N_CLUBS) - position finale de chaque club dans chaque simulation
        points: array (N, N_CLUBS) - points finaux
        stats: dict avec diff_buts, buts, buts_ext, victoires, victoires_ext
    """
    # Initialisation des stats pour N simulations
    points = np.zeros((N, N_CLUBS), dtype=np.int32)
    diff_buts = np.zeros((N, N_CLUBS), dtype=np.int32)
    buts = np.zeros((N, N_CLUBS), dtype=np.int32)
    buts_ext = np.zeros((N, N_CLUBS), dtype=np.int32)
    victoires = np.zeros((N, N_CLUBS), dtype=np.int32)
    victoires_ext = np.zeros((N, N_CLUBS), dtype=np.int32)
    
    # Charger les données initiales
    for club, stats in donnees_initiales.items():
        idx = CLUB_TO_IDX[club]
        points[:, idx] = stats[0]
        diff_buts[:, idx] = stats[1]
        buts[:, idx] = stats[2]
        buts_ext[:, idx] = stats[3]
        victoires[:, idx] = stats[4]
        victoires_ext[:, idx] = stats[5]
    
    # Récupérer les matchs à simuler
    home_idx, away_idx = convertir_calendrier_indices(journee_debut, journee_fin)
    n_matchs = len(home_idx)
    
    # Récupérer les lambdas pour chaque match
    lambdas_home = LAMBDA_HOME[home_idx, away_idx]  # (n_matchs,)
    lambdas_away = LAMBDA_AWAY[home_idx, away_idx]  # (n_matchs,)
    
    # Simuler tous les scores en une fois : (N, n_matchs)
    scores_home = np.random.poisson(lambdas_home, size=(N, n_matchs))
    scores_away = np.random.poisson(lambdas_away, size=(N, n_matchs))
    
    # Mettre à jour les stats pour chaque match
    for m in range(n_matchs):
        h_idx = home_idx[m]
        a_idx = away_idx[m]
        
        s_home = scores_home[:, m]  # (N,)
        s_away = scores_away[:, m]  # (N,)
        
        # Différence de buts
        diff_buts[:, h_idx] += s_home - s_away
        diff_buts[:, a_idx] += s_away - s_home
        
        # Buts marqués
        buts[:, h_idx] += s_home
        buts[:, a_idx] += s_away
        buts_ext[:, a_idx] += s_away
        
        # Points et victoires
        home_win = s_home > s_away
        away_win = s_away > s_home
        draw = s_home == s_away
        
        points[:, h_idx] += 3 * home_win + draw
        points[:, a_idx] += 3 * away_win + draw
        
        victoires[:, h_idx] += home_win
        victoires[:, a_idx] += away_win
        victoires_ext[:, a_idx] += away_win
    
    # Calculer les positions (tri multi-critères)
    # Créer un score composite pour le tri
    # On utilise des puissances de 1000 pour garantir l'ordre des critères
    score_tri = (
        points.astype(np.int64) * 1000000000000 +
        (diff_buts.astype(np.int64) + 1000) * 10000000 +  # +1000 pour éviter les négatifs
        buts.astype(np.int64) * 100000 +
        buts_ext.astype(np.int64) * 1000 +
        victoires.astype(np.int64) * 10 +
        victoires_ext.astype(np.int64)
    )
    
    # Trier et obtenir les positions
    positions = np.zeros((N, N_CLUBS), dtype=np.int32)
    for i in range(N):
        ordre = np.argsort(-score_tri[i])  # Tri décroissant
        for pos, club_idx in enumerate(ordre):
            positions[i, club_idx] = pos + 1  # Position 1-indexed
    
    return positions, {
        'points': points,
        'diff_buts': diff_buts,
        'buts': buts,
        'buts_ext': buts_ext,
        'victoires': victoires,
        'victoires_ext': victoires_ext
    }

def simuler_N_saisons_avec_match_fixe(N, donnees_initiales, journee_debut, journee_fin, 
                                       club_fixe, journee_match, resultat):
    """
    Simule N saisons avec un résultat forcé pour un club à une journée donnée.
    resultat: 'V' (victoire), 'N' (nul), 'D' (défaite)
    """
    # Initialisation
    points = np.zeros((N, N_CLUBS), dtype=np.int32)
    diff_buts = np.zeros((N, N_CLUBS), dtype=np.int32)
    buts = np.zeros((N, N_CLUBS), dtype=np.int32)
    buts_ext = np.zeros((N, N_CLUBS), dtype=np.int32)
    victoires = np.zeros((N, N_CLUBS), dtype=np.int32)
    victoires_ext = np.zeros((N, N_CLUBS), dtype=np.int32)
    
    # Charger données initiales
    for club, stats in donnees_initiales.items():
        idx = CLUB_TO_IDX[club]
        points[:, idx] = stats[0]
        diff_buts[:, idx] = stats[1]
        buts[:, idx] = stats[2]
        buts_ext[:, idx] = stats[3]
        victoires[:, idx] = stats[4]
        victoires_ext[:, idx] = stats[5]
    
    club_fixe_idx = CLUB_TO_IDX[club_fixe]
    
    # Trouver le match du club à la journée spécifiée
    match_fixe = None
    is_home = None
    for home, away in CALENDRIER[journee_match]:
        if home == club_fixe:
            match_fixe = (home, away)
            is_home = True
            break
        elif away == club_fixe:
            match_fixe = (home, away)
            is_home = False
            break
    
    if match_fixe is None:
        raise ValueError(f"Club {club_fixe} n'a pas de match en J{journee_match}")
    
    adversaire = match_fixe[1] if is_home else match_fixe[0]
    adversaire_idx = CLUB_TO_IDX[adversaire]
    
    # Simuler journée par journée
    for j in range(journee_debut, journee_fin + 1):
        for home, away in CALENDRIER[j]:
            h_idx = CLUB_TO_IDX[home]
            a_idx = CLUB_TO_IDX[away]
            
            # Vérifier si c'est le match fixé
            is_fixed_match = (j == journee_match and 
                              (home == club_fixe or away == club_fixe))
            
            if is_fixed_match:
                # Générer des scores qui respectent le résultat
                if resultat == 'V':
                    if is_home:
                        # Club gagne à domicile
                        s_home = np.random.poisson(2.0, N)  # Score typique gagnant
                        s_away = np.random.poisson(0.5, N)
                        # Forcer victoire
                        mask = s_home <= s_away
                        s_home[mask] = s_away[mask] + 1
                    else:
                        # Club gagne à l'extérieur
                        s_home = np.random.poisson(0.5, N)
                        s_away = np.random.poisson(2.0, N)
                        mask = s_away <= s_home
                        s_away[mask] = s_home[mask] + 1
                        
                elif resultat == 'D':
                    if is_home:
                        # Club perd à domicile
                        s_home = np.random.poisson(0.5, N)
                        s_away = np.random.poisson(2.0, N)
                        mask = s_home >= s_away
                        s_away[mask] = s_home[mask] + 1
                    else:
                        # Club perd à l'extérieur
                        s_home = np.random.poisson(2.0, N)
                        s_away = np.random.poisson(0.5, N)
                        mask = s_away >= s_home
                        s_home[mask] = s_away[mask] + 1
                        
                else:  # 'N' - Nul
                    s_home = np.random.poisson(1.2, N)
                    s_away = s_home.copy()  # Forcer l'égalité
            else:
                # Match normal
                lambda_h = LAMBDA_HOME[h_idx, a_idx]
                lambda_a = LAMBDA_AWAY[h_idx, a_idx]
                s_home = np.random.poisson(lambda_h, N)
                s_away = np.random.poisson(lambda_a, N)
            
            # Mise à jour des stats
            diff_buts[:, h_idx] += s_home - s_away
            diff_buts[:, a_idx] += s_away - s_home
            buts[:, h_idx] += s_home
            buts[:, a_idx] += s_away
            buts_ext[:, a_idx] += s_away
            
            home_win = s_home > s_away
            away_win = s_away > s_home
            draw = s_home == s_away
            
            points[:, h_idx] += 3 * home_win + draw
            points[:, a_idx] += 3 * away_win + draw
            victoires[:, h_idx] += home_win
            victoires[:, a_idx] += away_win
            victoires_ext[:, a_idx] += away_win
    
    # Calculer les positions
    score_tri = (
        points.astype(np.int64) * 1000000000000 +
        (diff_buts.astype(np.int64) + 1000) * 10000000 +
        buts.astype(np.int64) * 100000 +
        buts_ext.astype(np.int64) * 1000 +
        victoires.astype(np.int64) * 10 +
        victoires_ext.astype(np.int64)
    )
    
    positions = np.zeros((N, N_CLUBS), dtype=np.int32)
    for i in range(N):
        ordre = np.argsort(-score_tri[i])
        for pos, club_idx in enumerate(ordre):
            positions[i, club_idx] = pos + 1
    
    return positions

# =============================================================================
# CALCUL DES DISTRIBUTIONS
# =============================================================================

def calculer_distribution_positions(positions):
    """
    Calcule la distribution des positions pour chaque club.
    positions: array (N, N_CLUBS)
    Retourne: dict {club: {position: proba}}
    """
    N = positions.shape[0]
    distribution = {}
    
    for club_idx, club in enumerate(CLUBS):
        distribution[club] = {}
        for pos in range(1, N_CLUBS + 1):
            count = np.sum(positions[:, club_idx] == pos)
            if count > 0:
                distribution[club][pos] = count / N
    
    return distribution

def calculer_distribution_points(stats):
    """
    Calcule la distribution des points pour chaque club.
    Retourne: dict {club: {points: proba}}
    """
    points = stats['points']
    N = points.shape[0]
    distribution = {}
    
    for club_idx, club in enumerate(CLUBS):
        distribution[club] = {}
        club_points = points[:, club_idx]
        unique, counts = np.unique(club_points, return_counts=True)
        for pts, cnt in zip(unique, counts):
            distribution[club][int(pts)] = cnt / N
    
    return distribution

def calculer_distribution_par_position(positions, stats):
    """
    Calcule la distribution des points pour chaque POSITION (pour les seuils).
    Retourne: dict {position: {points: proba}}
    """
    points = stats['points']
    N = positions.shape[0]
    distribution = {}
    
    for pos in range(1, N_CLUBS + 1):
        distribution[pos] = {}
        points_at_pos = []
        
        for i in range(N):
            # Trouver le club à cette position
            club_idx = np.where(positions[i] == pos)[0][0]
            points_at_pos.append(points[i, club_idx])
        
        points_at_pos = np.array(points_at_pos)
        unique, counts = np.unique(points_at_pos, return_counts=True)
        for pts, cnt in zip(unique, counts):
            distribution[pos][int(pts)] = cnt / N
    
    return distribution

def calculer_moyennes(stats):
    """
    Calcule les moyennes pour chaque club.
    Retourne: dict {club: {stat: moyenne}}
    """
    N = stats['points'].shape[0]
    moyennes = {}
    
    for club_idx, club in enumerate(CLUBS):
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
# GÉNÉRATION PRINCIPALE
# =============================================================================

def generer_donnees_combinaison(journee_depart, journee_fin, n_simulations, generer_scenarios=True):
    """
    Génère toutes les données pour une combinaison (start → end).
    """
    print(f"\n{'='*60}")
    print(f"GÉNÉRATION J{journee_depart} → J{journee_fin} (N={n_simulations:,})")
    print(f"{'='*60}")
    
    donnees_init = HISTORIQUE.get(journee_depart, HISTORIQUE[0])
    debut_simu = journee_depart + 1
    
    data = {
        "journee_depart": journee_depart,
        "journee_fin": journee_fin,
        "n_simulations": n_simulations,
        "generated_at": datetime.now().isoformat(),
        "base": {},
        "scenarios": {}
    }
    
    # -------------------------------------------------------------------------
    # 1. SIMULATIONS DE BASE
    # -------------------------------------------------------------------------
    print(f"\n[BASE] Simulation de {n_simulations:,} saisons...")
    t0 = time.time()
    
    positions, stats = simuler_N_saisons(n_simulations, donnees_init, debut_simu, journee_fin)
    
    print(f"       Simulation terminée en {time.time()-t0:.1f}s")
    
    # Calcul des distributions
    print("       Calcul des distributions...")
    data["base"]["positions"] = calculer_distribution_positions(positions)
    data["base"]["points"] = calculer_distribution_points(stats)
    data["base"]["par_position"] = calculer_distribution_par_position(positions, stats)
    data["base"]["moyennes"] = calculer_moyennes(stats)
    
    print(f"       Total base: {time.time()-t0:.1f}s")
    
    # -------------------------------------------------------------------------
    # 2. SCÉNARIOS (seulement pour journee_fin=8)
    # -------------------------------------------------------------------------
    if generer_scenarios and journee_fin == 8:
        n_scenarios = min(n_simulations, 100_000)  # Limiter pour les scénarios
        
        print(f"\n[SCÉNARIOS] N={n_scenarios:,} par configuration")
        
        for journee_cible in range(debut_simu, journee_fin + 1):
            print(f"\n  Journée cible {journee_cible}:")
            data["scenarios"][str(journee_cible)] = {}
            
            for club_idx, club in enumerate(CLUBS):
                t0 = time.time()
                data["scenarios"][str(journee_cible)][club] = {}
                
                for resultat in ['V', 'N', 'D']:
                    positions = simuler_N_saisons_avec_match_fixe(
                        n_scenarios, donnees_init, debut_simu, journee_fin,
                        club, journee_cible, resultat
                    )
                    data["scenarios"][str(journee_cible)][club][resultat] = \
                        calculer_distribution_positions(positions)
                
                elapsed = time.time() - t0
                if (club_idx + 1) % 6 == 0:
                    print(f"    [{club_idx+1}/36] {club}... ({elapsed:.1f}s)")
    
    return data

def compresser_donnees(data, seuil=0.00001):
    """Supprime les probabilités quasi-nulles pour réduire la taille."""
    def clean(obj):
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items() 
                    if not (isinstance(v, (int, float)) and v < seuil)}
        return obj
    return clean(data)

def sauvegarder_json(data, journee_depart, journee_fin):
    """Sauvegarde les données en JSON avec le nouveau format de nom."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"J{journee_depart}_to_J{journee_fin}.json")
    
    data_clean = compresser_donnees(data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data_clean, f, ensure_ascii=False)
    
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"\n✅ Sauvegardé: {filepath} ({size_mb:.2f} MB)")

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Génère les données offline V2 optimisé (toutes combinaisons)")
    parser.add_argument('--start', type=int, help="Générer uniquement à partir de cette journée")
    parser.add_argument('--end', type=int, help="Générer uniquement jusqu'à cette journée")
    parser.add_argument('--max-journee', type=int, default=6, help="Dernière journée avec données réelles")
    parser.add_argument('--simulations', type=int, default=DEFAULT_SIMULATIONS, help="Nombre de simulations")
    parser.add_argument('--no-scenarios', action='store_true', help="Ne pas générer les scénarios")
    parser.add_argument('--skip-to-j8', action='store_true', help="Ne pas générer les combinaisons →J8 (déjà faites)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("GÉNÉRATEUR OPTIMISÉ V2 (NumPy) - TOUTES COMBINAISONS")
    print("=" * 60)
    print(f"Simulations: {args.simulations:,}")
    print(f"Scénarios: {'Non' if args.no_scenarios else 'Oui (pour end=8 uniquement)'}")
    print(f"Journées avec données: J0 à J{args.max_journee}")
    print(f"Skip →J8: {'Oui' if args.skip_to_j8 else 'Non'}")
    
    # Construire la liste des combinaisons
    combinaisons = []
    
    if args.start is not None and args.end is not None:
        # Une seule combinaison spécifique
        combinaisons = [(args.start, args.end)]
    else:
        # Toutes les combinaisons possibles
        for start in range(args.max_journee + 1):  # 0 à max_journee
            for end in range(start + 1, 9):  # start+1 à 8
                # Skip les combinaisons →J8 si demandé
                if args.skip_to_j8 and end == 8:
                    continue
                combinaisons.append((start, end))
    
    print(f"\n📋 Combinaisons à générer: {len(combinaisons)}")
    for s, e in combinaisons[:5]:
        print(f"   J{s} → J{e}")
    if len(combinaisons) > 5:
        print(f"   ... et {len(combinaisons) - 5} autres")
    
    # Estimation du temps
    n_avec_scenarios = sum(1 for _, end in combinaisons if end == 8 and not args.no_scenarios)
    n_sans_scenarios = len(combinaisons) - n_avec_scenarios
    # Temps estimé basé sur les benchmarks : ~5min avec scénarios, ~20s sans
    temps_estime_min = (n_avec_scenarios * 5 + n_sans_scenarios * 0.3)
    print(f"\n⏱️  Temps estimé: ~{temps_estime_min:.0f} minutes ({temps_estime_min/60:.1f}h)")
    
    input("\nAppuyez sur Entrée pour commencer...")
    
    total_start = time.time()
    
    for idx, (start, end) in enumerate(combinaisons):
        print(f"\n[{idx+1}/{len(combinaisons)}]")
        data = generer_donnees_combinaison(start, end, args.simulations, not args.no_scenarios)
        sauvegarder_json(data, start, end)
    
    total_time = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"✅ TERMINÉ en {total_time/60:.1f} minutes ({total_time/3600:.2f} heures)")
    print(f"   {len(combinaisons)} fichiers générés dans {DATA_DIR}/")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
