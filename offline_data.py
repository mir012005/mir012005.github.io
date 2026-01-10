#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE DE DONNÉES OFFLINE
=========================
Ce module charge les données pré-calculées et fournit des fonctions
pour y accéder rapidement sans recalculer.

Les données sont chargées une fois au démarrage et restent en mémoire.
"""

import json
import os
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Cache global des données (chargées une seule fois)
_CACHE = {}
_LOADED = False

# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================

def charger_donnees_journee(journee):
    """
    Charge les données pré-calculées pour une journée donnée.
    Retourne None si le fichier n'existe pas.
    """
    filepath = DATA_DIR / f"J{journee}.json"
    
    if not filepath.exists():
        print(f"⚠️ Fichier {filepath} non trouvé. Fallback sur simulation live.")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def charger_toutes_les_donnees():
    """
    Charge toutes les données en mémoire au démarrage.
    """
    global _CACHE, _LOADED
    
    if _LOADED:
        return
    
    print("📂 Chargement des données offline...")
    
    for j in range(8):
        data = charger_donnees_journee(j)
        if data:
            _CACHE[j] = data
            print(f"   ✓ J{j} chargée ({data.get('n_simulations', '?'):,} simulations)")
        else:
            print(f"   ✗ J{j} non disponible")
    
    _LOADED = True
    print(f"📂 {len(_CACHE)} fichiers chargés en mémoire.\n")


def donnees_disponibles():
    """
    Vérifie si les données offline sont disponibles.
    """
    return len(_CACHE) > 0


def get_donnees(journee_depart):
    """
    Récupère les données pour une journée de départ.
    Retourne None si non disponibles.
    """
    if not _LOADED:
        charger_toutes_les_donnees()
    
    return _CACHE.get(journee_depart)


# =============================================================================
# FONCTIONS D'ACCÈS AUX DONNÉES
# =============================================================================

def get_distribution_positions(journee_depart):
    """
    Retourne la distribution des positions pour chaque club.
    {club: {position: proba}}
    """
    data = get_donnees(journee_depart)
    if data and "base" in data:
        return data["base"].get("positions")
    return None


def get_distribution_points(journee_depart):
    """
    Retourne la distribution des points pour chaque club.
    {club: {points: proba}}
    """
    data = get_donnees(journee_depart)
    if data and "base" in data:
        return data["base"].get("points")
    return None


def get_distribution_par_position(journee_depart):
    """
    Retourne la distribution des points par position (pour les seuils).
    {position: {points: proba}}
    """
    data = get_donnees(journee_depart)
    if data and "base" in data:
        return data["base"].get("par_position")
    return None


def get_moyennes(journee_depart):
    """
    Retourne les moyennes statistiques pour chaque club.
    {club: {points, diff, buts, buts_ext, victoires, victoires_ext}}
    """
    data = get_donnees(journee_depart)
    if data and "base" in data:
        return data["base"].get("moyennes")
    return None


def get_scenario_distribution(journee_depart, journee_cible, club, resultat):
    """
    Retourne la distribution des positions pour un scénario spécifique.
    {club: {position: proba}}
    """
    data = get_donnees(journee_depart)
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
# FONCTIONS UTILITAIRES (Calculs à partir des distributions)
# =============================================================================

def calculer_proba_top8(distribution_positions, club):
    """
    Calcule la probabilité d'être dans le Top 8 à partir de la distribution.
    """
    if not distribution_positions or club not in distribution_positions:
        return 0.0
    
    distrib = distribution_positions[club]
    # Somme des probabilités des positions 1 à 8
    return sum(distrib.get(str(r), distrib.get(r, 0)) for r in range(1, 9))


def calculer_proba_qualification(distribution_positions, club):
    """
    Calcule la probabilité d'être qualifié (Top 24) à partir de la distribution.
    """
    if not distribution_positions or club not in distribution_positions:
        return 0.0
    
    distrib = distribution_positions[club]
    # Somme des probabilités des positions 1 à 24
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
# INITIALISATION AUTOMATIQUE
# =============================================================================

# Charger les données au premier import (optionnel, peut être fait explicitement)
# charger_toutes_les_donnees()
