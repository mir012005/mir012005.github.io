#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GÉNÉRATEUR DE DONNÉES OFFLINE V2 - TOUTES COMBINAISONS
=======================================================
Ce script génère les données pré-calculées pour TOUTES les combinaisons
de journées (start → end), permettant un mode offline complet.

Usage:
    python generate_offline_data_v2.py [--simulations N] [--start X] [--end Y]

Fichiers générés:
    data/J0_to_J1.json, data/J0_to_J2.json, ..., data/J7_to_J8.json
    Total: 36 fichiers pour toutes les combinaisons possibles
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime

# Import du simulateur existant
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
# FONCTIONS DE SIMULATION
# =============================================================================

def simuler_distribution_positions(N, données, debut, fin):
    """
    Simule N fois et retourne la distribution des positions pour chaque club.
    """
    d = {club: {pos: 0 for pos in range(1, 37)} for club in clubs_en_ldc}
    
    for i in range(N):
        if i % 100000 == 0 and i > 0:
            print(f"    ... {i:,} / {N:,} ({100*i/N:.0f}%)")
        
        resultat = simulation_ligue(données, debut, fin)
        classement = resultat["classement"]
        
        for pos, club in enumerate(classement, 1):
            d[club][pos] += 1
    
    # Conversion en probabilités
    for club in d:
        for pos in d[club]:
            d[club][pos] = d[club][pos] / N
    
    return d


def simuler_distribution_points(N, données, debut, fin):
    """
    Simule N fois et retourne la distribution des points pour chaque club.
    """
    d = {club: {pts: 0 for pts in range(25)} for club in clubs_en_ldc}
    
    for i in range(N):
        if i % 100000 == 0 and i > 0:
            print(f"    ... {i:,} / {N:,} ({100*i/N:.0f}%)")
        
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


def simuler_distribution_par_position(N, données, debut, fin):
    """
    Simule N fois et retourne la distribution des points pour chaque POSITION.
    """
    d = {pos: {pts: 0 for pts in range(25)} for pos in range(1, 37)}
    
    for i in range(N):
        if i % 100000 == 0 and i > 0:
            print(f"    ... {i:,} / {N:,} ({100*i/N:.0f}%)")
        
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


def simuler_moyennes(N, données, debut, fin):
    """
    Simule N fois et retourne les statistiques moyennes pour chaque club.
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
            print(f"    ... {i:,} / {N:,} ({100*i/N:.0f}%)")
        
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


def simuler_scenario(N, club_fixed, journee_cible, resultat, données, debut, fin):
    """
    Simule N fois avec un résultat forcé pour un club à une journée donnée.
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

def generer_donnees_combinaison(journee_depart, journee_fin, n_simulations, generer_scenarios=True):
    """
    Génère toutes les données pour une combinaison (start → end).
    """
    print(f"\n{'='*60}")
    print(f"GÉNÉRATION J{journee_depart} → J{journee_fin} (N={n_simulations:,})")
    print(f"{'='*60}")
    
    # Mise à jour du contexte Elo
    update_simulation_context(journee_depart)
    
    # Récupération de l'état initial
    etat = HISTORIQUE.get(journee_depart, etat_zero)
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
    # 1. DISTRIBUTIONS DE BASE
    # -------------------------------------------------------------------------
    print(f"\n[1/4] Distribution des positions...")
    t0 = time.time()
    data["base"]["positions"] = simuler_distribution_positions(n_simulations, etat, debut_simu, journee_fin)
    print(f"      Terminé en {time.time()-t0:.1f}s")
    
    print(f"\n[2/4] Distribution des points...")
    t0 = time.time()
    data["base"]["points"] = simuler_distribution_points(n_simulations, etat, debut_simu, journee_fin)
    print(f"      Terminé en {time.time()-t0:.1f}s")
    
    print(f"\n[3/4] Distribution par position / seuils...")
    t0 = time.time()
    data["base"]["par_position"] = simuler_distribution_par_position(n_simulations, etat, debut_simu, journee_fin)
    print(f"      Terminé en {time.time()-t0:.1f}s")
    
    print(f"\n[4/4] Moyennes statistiques...")
    t0 = time.time()
    data["base"]["moyennes"] = simuler_moyennes(n_simulations, etat, debut_simu, journee_fin)
    print(f"      Terminé en {time.time()-t0:.1f}s")
    
    # -------------------------------------------------------------------------
    # 2. SCÉNARIOS (matchs fixés) - seulement si journee_fin = 8
    # -------------------------------------------------------------------------
    if generer_scenarios and journee_fin == 8:
        n_scenarios = min(n_simulations, 100_000)
        
        print(f"\n[SCÉNARIOS] Génération avec N={n_scenarios:,}...")
        
        # Pour chaque journée cible possible (de debut_simu à journee_fin)
        for journee_cible in range(debut_simu, journee_fin + 1):
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
                        n_scenarios, club, journee_cible, resultat, etat, debut_simu, journee_fin
                    )
                    data["scenarios"][str(journee_cible)][club][resultat] = distrib
                
                print(f"({time.time()-t0:.1f}s)")
    
    return data


def compresser_donnees(data):
    """
    Nettoie les données pour réduire la taille du JSON.
    """
    seuil = 0.00001  # 0.001%
    
    def clean_dict(d):
        if isinstance(d, dict):
            return {k: clean_dict(v) for k, v in d.items() if not (isinstance(v, (int, float)) and v < seuil)}
        return d
    
    return clean_dict(data)


def sauvegarder_json(data, journee_depart, journee_fin):
    """
    Sauvegarde les données dans un fichier JSON.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"J{journee_depart}_to_J{journee_fin}.json")
    
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
    parser = argparse.ArgumentParser(description="Génère les données offline V2 (toutes combinaisons)")
    parser.add_argument('--simulations', type=int, default=DEFAULT_SIMULATIONS, help="Nombre de simulations")
    parser.add_argument('--max-journee', type=int, default=6, help="Dernière journée avec données réelles (défaut: 6)")
    parser.add_argument('--start', type=int, help="Générer uniquement à partir de cette journée")
    parser.add_argument('--end', type=int, help="Générer uniquement jusqu'à cette journée")
    parser.add_argument('--no-scenarios', action='store_true', help="Ne pas générer les scénarios")
    parser.add_argument('--skip-to-j8', action='store_true', help="Ne pas générer les combinaisons →J8 (déjà faites)")
    args = parser.parse_args()
    
    n_sims = args.simulations
    generer_scenarios = not args.no_scenarios
    max_j = args.max_journee
    
    print("=" * 60)
    print("GÉNÉRATEUR DE DONNÉES OFFLINE V2 - TOUTES COMBINAISONS")
    print("=" * 60)
    print(f"Simulations: {n_sims:,}")
    print(f"Scénarios: {'Oui (pour end=8 uniquement)' if generer_scenarios else 'Non'}")
    print(f"Journées avec données réelles: J0 à J{max_j}")
    print(f"Skip →J8: {'Oui' if args.skip_to_j8 else 'Non'}")
    print(f"Dossier de sortie: {DATA_DIR}/")
    
    # Construire la liste des combinaisons à générer
    combinaisons = []
    
    if args.start is not None and args.end is not None:
        # Une seule combinaison spécifique
        combinaisons = [(args.start, args.end)]
    else:
        # Toutes les combinaisons possibles
        for start in range(max_j + 1):  # 0 à max_j
            for end in range(start + 1, 9):  # start+1 à 8
                # Skip les combinaisons →J8 si demandé
                if args.skip_to_j8 and end == 8:
                    continue
                combinaisons.append((start, end))
    
    print(f"\n📋 Combinaisons à générer: {len(combinaisons)}")
    for start, end in combinaisons[:5]:
        print(f"   J{start} → J{end}")
    if len(combinaisons) > 5:
        print(f"   ... et {len(combinaisons) - 5} autres")
    
    # Estimation du temps
    n_avec_scenarios = sum(1 for _, end in combinaisons if end == 8)
    n_sans_scenarios = len(combinaisons) - n_avec_scenarios
    temps_estime = (n_avec_scenarios * 6 + n_sans_scenarios * 1.5)  # minutes approximatives
    print(f"\n⏱️  Temps estimé: ~{temps_estime:.0f} minutes ({temps_estime/60:.1f}h)")
    
    input("\nAppuyez sur Entrée pour commencer...")
    
    total_start = time.time()
    
    for idx, (start, end) in enumerate(combinaisons):
        print(f"\n[{idx+1}/{len(combinaisons)}] Génération J{start} → J{end}...")
        
        data = generer_donnees_combinaison(start, end, n_sims, generer_scenarios)
        sauvegarder_json(data, start, end)
    
    total_time = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"✅ TERMINÉ en {total_time/60:.1f} minutes ({total_time/3600:.2f}h)")
    print(f"   {len(combinaisons)} fichiers générés dans {DATA_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
