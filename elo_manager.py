import pandas as pd
import requests
import io
import time
import json
import os
from datetime import datetime

# ==========================================
# 1. CONSTANTES & MAPPING
# ==========================================
# Si possible, importez CLUBS_SIMULATOR depuis scraper.py pour éviter les doublons
from scraper import CLUBS_SIMULATOR, MAPPING_WIKI, calendrier_ldc, get_live_elo, generer_historique_elo


CACHE_FILE = "elo_cache.json"

# ==========================================
# 4. FONCTION POUR LE SITE (CACHE)
# ==========================================
def get_current_elos():
    """
    À utiliser dans votre site web/duel.
    Vérifie le cache JSON avant d'appeler l'API.
    """
    today_str = datetime.today().strftime('%Y-%m-%d')

    # 1. Lecture Cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
            if data.get("date") == today_str:
                return data["elos"]
        except: pass

    # 2. Mise à jour Cache (si absent ou expiré)
    elos, _ = get_live_elo()
    
    if elos:
        with open(CACHE_FILE, 'w') as f:
            json.dump({"date": today_str, "elos": elos}, f, indent=4)
            
    return elos

# ==========================================
# 5. EXÉCUTION
# ==========================================
if __name__ == "__main__":
    # Test 1 : Historique complet
    print("\n--- TEST GÉNÉRATION HISTORIQUE ---")
    history = generer_historique_elo()
    
    print("\n✅ CODE À COPIER DANS SIMULATOR.PY :")
    print("historique_elo = {")
    for j, data in history.items():
        print(f"    {j}: {data},")
    print("}")

    # Test 2 : Cache Live pour le site
    print("\n--- TEST CACHE LIVE ---")
    current = get_current_elos()
    print(f"Elo actuel Real Madrid : {current.get('Real Madrid')}")