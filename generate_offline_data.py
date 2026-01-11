#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GÉNÉRATEUR DE DONNÉES OFFLINE POUR LE SIMULATEUR LDC
=====================================================
Ce script génère toutes les données pré-calculées nécessaires au fonctionnement
du site web, avec 1 million de simulations Monte Carlo pour une précision maximale.

Usage:
    python generate_offline_data.py [--journee J] [--simulations N]

Options:
    --journee J      : Générer uniquement pour la journée J (0-7). Sans cette option, génère tout.
    --simulations N  : Nombre de simulations (défaut: 1000000)

Fichiers générés:
    data/J0.json, data/J1.json, ..., data/J7.json
"""

import json
import os
import sys
import time
import math
import copy
import argparse
from datetime import datetime

# Import du simulateur existant (on réutilise les fonctions de base)
from simulator import (
    clubs_en_ldc, 
    calendrier,
    simulation_ligue,
    simuler_victoire,
    simuler_defaite,
    simuler_match_nul,
    etat_zero,
    données_J1, données_J2, données_J3, données_J4,
    données_J5, données_J6, données_J7, données_J8,
    update_simulation_context
)

# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_DIR = "data"
DEFAULT_SIMULATIONS = 1_000_000

# Mapping des données historiques
HISTORIQUE = {
    0: etat_zero,
    1: données_J1,
    2: données_J2,
    3: données_J3,
    4: données_J4,
    5: données_J5,
    6: données_J6,
    7: données_J7,
    8: données_J8
}

# =============================================================================
# FONCTIONS DE SIMULATION (Versions optimisées pour génération massive)
# =============================================================================

def simuler_distribution_positions(N, données, debut, fin=8):
    """
    Simule N fois et retourne la distribution des positions pour chaque club.
    Retourne: {club: {position: proba}}
    """
    # Initialisation
    d = {club: {pos: 0 for pos in range(1, 37)} for club in clubs_en_ldc}
    
    for i in range(N):
        if i % 100000 == 0 and i > 0:
            print(f"    ... {i:,} / {N:,} simulations ({100*i/N:.1f}%)")
        
        resultat = simulation_ligue(données, debut, fin)
        classement = resultat["classement"]
        
        for pos, club in enumerate(classement, 1):
            d[club][pos] += 1
    
    # Conversion en probabilités
    for club in d:
        for pos in d[club]:
            d[club][pos] = d[club][pos] / N
    
    return d


def simuler_distribution_points(N, données, debut, fin=8):
    """
    Simule N fois et retourne la distribution des points pour chaque club.
    Retourne: {club: {points: proba}}
    """
    # Points max possibles = 3 * 8 journées = 24
    d = {club: {pts: 0 for pts in range(25)} for club in clubs_en_ldc}
    
    for i in range(N):
        if i % 100000 == 0 and i > 0:
            print(f"    ... {i:,} / {N:,} simulations ({100*i/N:.1f}%)")
        
        resultat = simulation_ligue(données, debut, fin)
        points = resultat["points"]
        
        for club in clubs_en_ldc:
            pts = points[club]
            if pts in d[club]:
                d[club][pts] += 1
    
    # Conversion en probabilités
    for club in d:
        for pts in d[club]:
            d[club][pts] = d[club][pts] / N
    
    return d


def simuler_distribution_par_position(N, données, debut, fin=8):
    """
    Simule N fois et retourne la distribution des points pour chaque POSITION.
    Utilisé pour les seuils (points du 8ème, points du 24ème).
    Retourne: {position: {points: proba}}
    """
    d = {pos: {pts: 0 for pts in range(25)} for pos in range(1, 37)}
    
    for i in range(N):
        if i % 100000 == 0 and i > 0:
            print(f"    ... {i:,} / {N:,} simulations ({100*i/N:.1f}%)")
        
        resultat = simulation_ligue(données, debut, fin)
        classement = resultat["classement"]
        points = resultat["points"]
        
        for pos, club in enumerate(classement, 1):
            pts = points[club]
            if pts in d[pos]:
                d[pos][pts] += 1
    
    # Conversion en probabilités
    for pos in d:
        for pts in d[pos]:
            d[pos][pts] = d[pos][pts] / N
    
    return d


def simuler_moyennes(N, données, debut, fin=8):
    """
    Simule N fois et retourne les statistiques moyennes pour chaque club.
    Retourne: {club: {points, diff, buts, buts_ext, victoires, victoires_ext}}
    """
    totaux = {
        club: {
            "points": 0, "diff": 0, "buts": 0, 
            "buts_ext": 0, "victoires": 0, "victoires_ext": 0
        } 
        for club in clubs_en_ldc
    }
    
    for i in range(N):
        if i % 100000 == 0 and i > 0:
            print(f"    ... {i:,} / {N:,} simulations ({100*i/N:.1f}%)")
        
        resultat = simulation_ligue(données, debut, fin)
        
        for club in clubs_en_ldc:
            totaux[club]["points"] += resultat["points"][club]
            totaux[club]["diff"] += resultat["diff_buts"][club]
            totaux[club]["buts"] += resultat["buts"][club]
            totaux[club]["buts_ext"] += resultat["buts_ext"][club]
            totaux[club]["victoires"] += resultat["nb_victoires"][club]
            totaux[club]["victoires_ext"] += resultat["nb_victoires_ext"][club]
    
    # Calcul des moyennes
    moyennes = {}
    for club in clubs_en_ldc:
        moyennes[club] = {
            "points": round(totaux[club]["points"] / N, 3),
            "diff": round(totaux[club]["diff"] / N, 3),
            "buts": round(totaux[club]["buts"] / N, 3),
            "buts_ext": round(totaux[club]["buts_ext"] / N, 3),
            "victoires": round(totaux[club]["victoires"] / N, 3),
            "victoires_ext": round(totaux[club]["victoires_ext"] / N, 3)
        }
    
    return moyennes


def simuler_scenario(N, club_fixed, journee_cible, resultat, données, debut):
    """
    Simule N fois avec un résultat forcé pour un club à une journée donnée.
    Retourne: {club: {position: proba}}
    """
    d = {club: {pos: 0 for pos in range(1, 37)} for club in clubs_en_ldc}
    
    for i in range(N):
        if resultat == 'V':
            res = simuler_victoire(club_fixed, journee_cible, données=données, debut=debut)
        elif resultat == 'D':
            res = simuler_defaite(club_fixed, journee_cible, données=données, debut=debut)
        else:  # 'N'
            res = simuler_match_nul(club_fixed, journee_cible, données=données, debut=debut)
        
        classement = res["classement"]
        for pos, club in enumerate(classement, 1):
            d[club][pos] += 1
    
    # Conversion en probabilités
    for club in d:
        for pos in d[club]:
            d[club][pos] = d[club][pos] / N
    
    return d


# =============================================================================
# GÉNÉRATION PRINCIPALE
# =============================================================================

def generer_donnees_journee(journee_depart, n_simulations, generer_scenarios=True):
    """
    Génère toutes les données pour une journée de départ donnée.
    """
    print(f"\n{'='*60}")
    print(f"GÉNÉRATION JOURNÉE {journee_depart}")
    print(f"{'='*60}")
    
    # Mise à jour du contexte Elo
    update_simulation_context(journee_depart)
    
    # Récupération de l'état initial
    etat = HISTORIQUE.get(journee_depart, etat_zero)
    debut_simu = journee_depart + 1
    
    data = {
        "journee_depart": journee_depart,
        "n_simulations": n_simulations,
        "generated_at": datetime.now().isoformat(),
        "base": {},
        "scenarios": {}
    }
    
    # -------------------------------------------------------------------------
    # 1. DISTRIBUTIONS DE BASE (simulation libre jusqu'à J8)
    # -------------------------------------------------------------------------
    print(f"\n[1/4] Distribution des positions (N={n_simulations:,})...")
    t0 = time.time()
    data["base"]["positions"] = simuler_distribution_positions(n_simulations, etat, debut_simu)
    print(f"      Terminé en {time.time()-t0:.1f}s")
    
    print(f"\n[2/4] Distribution des points (N={n_simulations:,})...")
    t0 = time.time()
    data["base"]["points"] = simuler_distribution_points(n_simulations, etat, debut_simu)
    print(f"      Terminé en {time.time()-t0:.1f}s")
    
    print(f"\n[3/4] Distribution par position / seuils (N={n_simulations:,})...")
    t0 = time.time()
    data["base"]["par_position"] = simuler_distribution_par_position(n_simulations, etat, debut_simu)
    print(f"      Terminé en {time.time()-t0:.1f}s")
    
    print(f"\n[4/4] Moyennes statistiques (N={n_simulations:,})...")
    t0 = time.time()
    data["base"]["moyennes"] = simuler_moyennes(n_simulations, etat, debut_simu)
    print(f"      Terminé en {time.time()-t0:.1f}s")
    
    # -------------------------------------------------------------------------
    # 2. SCÉNARIOS (matchs fixés)
    # -------------------------------------------------------------------------
    if generer_scenarios:
        # Nombre de simulations réduit pour les scénarios (sinon trop long)
        n_scenarios = min(n_simulations, 10_000)
        
        print(f"\n[SCÉNARIOS] Génération avec N={n_scenarios:,}...")
        
        # Pour chaque journée cible possible (de debut_simu à 8)
        for journee_cible in range(debut_simu, 9):
            print(f"\n  Journée cible {journee_cible}:")
            data["scenarios"][str(journee_cible)] = {}
            
            # Pour chaque club
            for idx, club in enumerate(clubs_en_ldc):
                print(f"    [{idx+1}/36] {club}...", end=" ", flush=True)
                t0 = time.time()
                
                data["scenarios"][str(journee_cible)][club] = {}
                
                # Pour chaque résultat possible
                for resultat in ['V', 'N', 'D']:
                    distrib = simuler_scenario(
                        n_scenarios, club, journee_cible, resultat, etat, debut_simu
                    )
                    data["scenarios"][str(journee_cible)][club][resultat] = distrib
                
                print(f"({time.time()-t0:.1f}s)")
    
    return data


def compresser_donnees(data):
    """
    Nettoie les données pour réduire la taille du JSON.
    Supprime les probabilités nulles ou quasi-nulles.
    """
    seuil = 0.00001  # 0.001%
    
    def clean_dict(d):
        if isinstance(d, dict):
            return {k: clean_dict(v) for k, v in d.items() if not (isinstance(v, (int, float)) and v < seuil)}
        return d
    
    return clean_dict(data)


def sauvegarder_json(data, journee):
    """
    Sauvegarde les données dans un fichier JSON.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"J{journee}.json")
    
    # Compression des données
    data_clean = compresser_donnees(data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data_clean, f, ensure_ascii=False)
    
    # Taille du fichier
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"\n✅ Sauvegardé: {filepath} ({size_mb:.2f} MB)")
    
    return filepath


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Génère les données offline pour le simulateur LDC")
    parser.add_argument('--journee', type=int, help="Journée spécifique (0-7)")
    parser.add_argument('--max-journee', type=int, default=6, help="Dernière journée avec données réelles (défaut: 6)")
    parser.add_argument('--simulations', type=int, default=DEFAULT_SIMULATIONS, help="Nombre de simulations")
    parser.add_argument('--no-scenarios', action='store_true', help="Ne pas générer les scénarios")
    args = parser.parse_args()
    
    n_sims = args.simulations
    generer_scenarios = not args.no_scenarios
    max_j = args.max_journee
    
    print("=" * 60)
    print("GÉNÉRATEUR DE DONNÉES OFFLINE - SIMULATEUR LDC")
    print("=" * 60)
    print(f"Simulations de base: {n_sims:,}")
    print(f"Scénarios: {'Oui (100k par config)' if generer_scenarios else 'Non'}")
    print(f"Journées avec données réelles: J0 à J{max_j}")
    print(f"Dossier de sortie: {DATA_DIR}/")
    
    total_start = time.time()
    
    if args.journee is not None:
        # Génération d'une seule journée
        if args.journee > max_j:
            print(f"\n⚠️ ATTENTION: J{args.journee} n'a pas de données réelles (max = J{max_j})")
            print("   Les simulations utiliseront des données vides, ce qui est probablement faux.")
            confirm = input("   Continuer quand même ? (o/N) : ")
            if confirm.lower() != 'o':
                print("Annulé.")
                return
        journees = [args.journee]
    else:
        # Génération de J0 jusqu'à max_journee (inclus)
        journees = list(range(max_j + 1))
        print(f"\n📋 Journées à générer: {journees}")
    
    for j in journees:
        data = generer_donnees_journee(j, n_sims, generer_scenarios)
        sauvegarder_json(data, j)
    
    total_time = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"TERMINÉ en {total_time/60:.1f} minutes")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
