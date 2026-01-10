# 🚀 SYSTÈME DE DONNÉES OFFLINE - Guide d'utilisation

## Vue d'ensemble

Ce système permet de pré-calculer toutes les simulations Monte Carlo (1 million de fois) et de les stocker dans des fichiers JSON. Le site web devient alors **instantané** car il lit simplement les données pré-calculées au lieu de simuler en temps réel.

---

## 📁 Fichiers créés

| Fichier | Description |
|---------|-------------|
| `generate_offline_data.py` | Script pour générer les données (à exécuter une fois) |
| `offline_data.py` | Module Python qui charge et fournit les données |
| `MODIFICATIONS_SIMULATOR.py` | Nouvelles versions des fonctions à copier dans `simulator.py` |
| `data/J0.json` ... `data/J7.json` | Fichiers de données générés (après exécution) |

---

## 🔧 Installation (3 étapes)

### Étape 1 : Modifier `simulator.py`

**1.1** Ajouter cet import **en haut du fichier** (après les autres imports) :

```python
# Import du module de données offline
try:
    import offline_data
    offline_data.charger_toutes_les_donnees()
    OFFLINE_DISPONIBLE = offline_data.donnees_disponibles()
    print(f"✅ Mode OFFLINE activé" if OFFLINE_DISPONIBLE else "⚠️ Mode LIVE (pas de données offline)")
except ImportError:
    OFFLINE_DISPONIBLE = False
    print("⚠️ Module offline_data non trouvé - Mode LIVE")
```

**1.2** Remplacer les 7 fonctions suivantes par celles du fichier `MODIFICATIONS_SIMULATOR.py` :

- `get_web_simulation` (vers ligne 1123)
- `get_web_seuils` (vers ligne 1037)
- `get_simulation_flexible` (vers ligne 1306)
- `get_probas_top8_qualif` (vers ligne 1396)
- `get_scenario_analysis` (vers ligne 1495)
- `get_web_hypometre` (vers ligne 1579)
- `get_web_evolution` (vers ligne 1659)

---

### Étape 2 : Générer les données offline

Ouvre un terminal dans le dossier du projet et exécute :

```bash
# Génération complète (ATTENTION : ~2-4 heures avec 1 million de simulations)
python generate_offline_data.py

# OU pour tester d'abord avec moins de simulations (plus rapide) :
python generate_offline_data.py --simulations 10000

# OU pour générer une seule journée :
python generate_offline_data.py --journee 6 --simulations 100000
```

**Options disponibles :**
- `--journee J` : Générer uniquement pour la journée J (0 à 7)
- `--simulations N` : Nombre de simulations (défaut: 1000000)
- `--no-scenarios` : Ne pas générer les scénarios (plus rapide mais fonctionnalités réduites)

---

### Étape 3 : Lancer le serveur

```bash
python app.py
```

Au démarrage, tu devrais voir :
```
📂 Chargement des données offline...
   ✓ J0 chargée (1,000,000 simulations)
   ✓ J1 chargée (1,000,000 simulations)
   ...
📂 8 fichiers chargés en mémoire.
✅ Mode OFFLINE activé
Serveur lancé sur http://127.0.0.1:5000
```

---

## ⏱️ Temps de génération estimés

| Simulations | Temps par journée | Temps total (8 journées) |
|-------------|-------------------|--------------------------|
| 10,000 | ~2 min | ~15 min |
| 100,000 | ~15 min | ~2 heures |
| 1,000,000 | ~2 heures | ~16 heures |

**💡 Conseil** : Lance la génération pendant la nuit ou sur un serveur puissant.

---

## 📊 Structure des données générées

Chaque fichier `JX.json` contient :

```json
{
  "journee_depart": 0,
  "n_simulations": 1000000,
  "generated_at": "2024-01-10T15:30:00",
  
  "base": {
    "positions": {
      "Arsenal": {"1": 0.052, "2": 0.078, ...},
      "Bayern": {...},
      ...
    },
    "points": {
      "Arsenal": {"10": 0.02, "11": 0.05, ...},
      ...
    },
    "par_position": {
      "8": {"15": 0.12, "16": 0.25, ...},
      "24": {...}
    },
    "moyennes": {
      "Arsenal": {"points": 14.2, "diff": 5.3, "buts": 12.1, ...},
      ...
    }
  },
  
  "scenarios": {
    "1": {
      "Arsenal": {
        "V": {"Arsenal": {"1": 0.08, ...}, "Bayern": {...}, ...},
        "N": {...},
        "D": {...}
      },
      ...
    },
    ...
  }
}
```

---

## 🔄 Quand régénérer les données ?

Tu dois régénérer les données :

1. **Après chaque vraie journée de LDC** : Les données `données_J1`, `données_J2`, etc. changent
2. **Si tu modifies le modèle de simulation** : Changement des coefficients Elo, Poisson, etc.
3. **Si tu ajoutes/retires des équipes**

---

## 🐛 Dépannage

### "Module offline_data non trouvé"
→ Vérifie que `offline_data.py` est dans le même dossier que `simulator.py`

### "Fichier J0.json non trouvé"
→ Exécute d'abord `python generate_offline_data.py`

### Les données sont en mode LIVE malgré les fichiers
→ Vérifie que l'import en haut de `simulator.py` est correct

### Erreur de mémoire pendant la génération
→ Réduis le nombre de simulations : `--simulations 500000`

---

## 📈 Avantages du mode OFFLINE

| Aspect | Mode LIVE | Mode OFFLINE |
|--------|-----------|--------------|
| Temps de réponse | 5-30 secondes | < 100 ms |
| Précision | ~1000 simulations | 1,000,000 simulations |
| Charge serveur | Élevée | Nulle |
| Consommation CPU | Continue | Aucune |

---

## 💾 Taille des fichiers générés

Avec 1 million de simulations :
- Chaque `JX.json` : ~5-15 MB
- Total `data/` : ~80-120 MB

Les fichiers sont compressibles si besoin (gzip réduit de ~70%).
