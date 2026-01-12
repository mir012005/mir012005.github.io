#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE DE DONNÉES OFFLINE V2
============================
Ce module charge les données pré-calculées pour TOUTES les combinaisons
de journées (start → end) et fournit des fonctions d'accès rapide.

Format des fichiers: data/J{start}_to_J{end}.json
Exemple: data/J0_to_J8.json, data/J3_to_J5.json, etc.
"""

import json
import os
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Cache global des données: {(start, end): data}
_CACHE = {}
_LOADED = False

# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================

def charger_donnees_combinaison(start, end):
    """
    Charge les données pré-calculées pour une combinaison (start → end).
    Retourne None si le fichier n'existe pas.
    """
    filepath = DATA_DIR / f"J{start}_to_J{end}.json"
    
    if not filepath.exists():
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def charger_toutes_les_donnees():
    """
    Charge toutes les données disponibles en mémoire au démarrage.
    Cherche tous les fichiers J*_to_J*.json dans le dossier data/.
    """
    global _CACHE, _LOADED
    
    if _LOADED:
        return
    
    print("📂 Chargement des données offline V2...")
    
    if not DATA_DIR.exists():
        print(f"   ⚠️ Dossier {DATA_DIR} non trouvé")
        _LOADED = True
        return
    
    # Chercher tous les fichiers correspondant au pattern
    count = 0
    for filepath in DATA_DIR.glob("J*_to_J*.json"):
        filename = filepath.stem  # "J0_to_J8"
        try:
            parts = filename.split("_to_")
            start = int(parts[0][1:])  # "J0" → 0
            end = int(parts[1][1:])    # "J8" → 8
            
            data = charger_donnees_combinaison(start, end)
            if data:
                _CACHE[(start, end)] = data
                n_sims = data.get('n_simulations', '?')
                if isinstance(n_sims, int):
                    n_sims = f"{n_sims:,}"
                print(f"   ✓ J{start}→J{end} ({n_sims} sims)")
                count += 1
        except (ValueError, IndexError) as e:
            print(f"   ⚠️ Fichier ignoré: {filepath.name} ({e})")
    
    # Rétrocompatibilité: charger aussi les anciens fichiers J0.json, J1.json...
    for j in range(8):
        old_filepath = DATA_DIR / f"J{j}.json"
        if old_filepath.exists() and (j, 8) not in _CACHE:
            try:
                with open(old_filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                _CACHE[(j, 8)] = data
                n_sims = data.get('n_simulations', '?')
                if isinstance(n_sims, int):
                    n_sims = f"{n_sims:,}"
                print(f"   ✓ J{j}→J8 [ancien format] ({n_sims} sims)")
                count += 1
            except Exception as e:
                print(f"   ⚠️ Erreur lecture {old_filepath.name}: {e}")
    
    _LOADED = True
    print(f"📂 {count} combinaisons chargées en mémoire.\n")


def donnees_disponibles():
    """
    Vérifie si des données offline sont disponibles.
    """
    if not _LOADED:
        charger_toutes_les_donnees()
    return len(_CACHE) > 0


def combinaison_disponible(start, end):
    """
    Vérifie si une combinaison spécifique est disponible.
    """
    if not _LOADED:
        charger_toutes_les_donnees()
    return (start, end) in _CACHE


def get_donnees(start, end):
    """
    Récupère les données pour une combinaison (start → end).
    Retourne None si non disponibles.
    """
    if not _LOADED:
        charger_toutes_les_donnees()
    
    return _CACHE.get((start, end))


def lister_combinaisons_disponibles():
    """
    Retourne la liste des combinaisons (start, end) disponibles.
    """
    if not _LOADED:
        charger_toutes_les_donnees()
    
    return sorted(_CACHE.keys())


# =============================================================================
# FONCTIONS D'ACCÈS AUX DONNÉES
# =============================================================================

def get_distribution_positions(start, end):
    """
    Retourne la distribution des positions pour chaque club.
    {club: {position: proba}}
    """
    data = get_donnees(start, end)
    if data and "base" in data:
        return data["base"].get("positions")
    return None


def get_distribution_points(start, end):
    """
    Retourne la distribution des points pour chaque club.
    {club: {points: proba}}
    """
    data = get_donnees(start, end)
    if data and "base" in data:
        return data["base"].get("points")
    return None


def get_distribution_par_position(start, end):
    """
    Retourne la distribution des points par position (pour les seuils).
    {position: {points: proba}}
    """
    data = get_donnees(start, end)
    if data and "base" in data:
        return data["base"].get("par_position")
    return None


def get_moyennes(start, end):
    """
    Retourne les moyennes statistiques pour chaque club.
    {club: {points, diff, buts, buts_ext, victoires, victoires_ext}}
    """
    data = get_donnees(start, end)
    if data and "base" in data:
        return data["base"].get("moyennes")
    return None


def get_scenario_distribution(start, end, journee_cible, club, resultat):
    """
    Retourne la distribution des positions pour un scénario spécifique.
    {club: {position: proba}}
    
    Note: Les scénarios ne sont générés que pour end=8.
    """
    data = get_donnees(start, end)
    if not data or "scenarios" not in data:
        return None
    
    scenarios = data["scenarios"]
    journee_key = str(journee_cible)
    
    if journee_key not in scenarios:
        return None
    if club not in scenarios[journee_key]:
        return None
    if resultat not in scenarios[journee_key][club]:
        return None
    
    return scenarios[journee_key][club][resultat]


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def calculer_proba_top8(distribution_positions, club):
    """
    Calcule la probabilité d'être dans le Top 8.
    """
    if not distribution_positions or club not in distribution_positions:
        return 0.0
    
    distrib = distribution_positions[club]
    return sum(distrib.get(str(r), distrib.get(r, 0)) for r in range(1, 9))


def calculer_proba_qualification(distribution_positions, club):
    """
    Calcule la probabilité d'être qualifié (Top 24).
    """
    if not distribution_positions or club not in distribution_positions:
        return 0.0
    
    distrib = distribution_positions[club]
    return sum(distrib.get(str(r), distrib.get(r, 0)) for r in range(1, 25))


def calculer_points_moyens(distribution_points, club):
    """
    Calcule les points moyens à partir de la distribution.
    """
    if not distribution_points or club not in distribution_points:
        return 0.0
    
    distrib = distribution_points[club]
    total = 0
    for pts, proba in distrib.items():
        total += int(pts) * proba
    return total


# =============================================================================
# INITIALISATION
# =============================================================================

# Le chargement se fait à la demande ou au premier appel
