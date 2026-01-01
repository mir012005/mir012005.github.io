from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

# --- MODIFICATION ICI ---
# On importe "simulator" car c'est le nom de votre fichier (simulator.py)
import simulator 

app = Flask(__name__, static_folder='.')
CORS(app) 

# ------------------------------------------------------------------
# 1. ROUTES POUR LE SITE WEB
# ------------------------------------------------------------------

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# ------------------------------------------------------------------
# 2. ROUTES API
# ------------------------------------------------------------------

#============ 16: 42 19/12/2025===============================
@app.route('/api/clubs', methods=['GET'])
def get_clubs():
    try:
        clubs = simulator.get_clubs_list()
        return jsonify(clubs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#======================================================
"""
@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    try:
        data = request.json
        club = data.get('club')
        
        print(f"--> Simulation demandée pour : {club}")
        
        if not club:
            return jsonify({"error": "Nom de club manquant"}), 400

        # Appel avec "simulator."
        resultats = simulator.get_web_simulation(club)
        
        if "error" in resultats:
            return jsonify(resultats), 404
            
        return jsonify(resultats)
        
    except Exception as e:
        print(f"ERREUR : {e}")
        return jsonify({"error": str(e)}), 500

"""
"""
<section id="ranking" class="page" style="display:none;">
            <h2>🏆 Classement Projeté (Moyenne)</h2>
            
            <div class="controls-bar">
                <div class="control-group">
                    <label>De :</label>
                    <select id="startDay">
                        <option value="1" selected>J0</option><option value="1">J1</option><option value="2">J2</option>
                        <option value="3">J3</option><option value="4">J4</option>
                        <option value="5">J5</option><option value="6">J6</option>
                        <option value="7">J7</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>À :</label>
                    <select id="endDay">
                        <option value="1">J1</option><option value="2">J2</option>
                        <option value="3">J3</option><option value="4">J4</option>
                        <option value="5">J5</option><option value="6">J6</option>
                        <option value="7">J7</option><option value="8" selected>J8</option>
                    </select>
                </div>
                <button class="action-btn" onclick="chargerClassement()">🔄 Calculer</button>
            </div>

            <div class="table-container">
                <table class="ranking-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th style="text-align:left;">Club</th>
                            <th>Points</th>
                            <th>Diff. Buts</th>
                            <th>Buts</th>
                            <th class="secondary-stat">Buts Ext.</th>
                            <th>Victoires</th>
                            <th class="secondary-stat">Vict. Ext.</th>
                        </tr>
                    </thead>
                    <tbody id="rankingBody">
                        <tr><td colspan="8">Cliquez sur Calculer...</td></tr>
                    </tbody>
                </table>
            </div>
            
            <div class="legend">
                <span class="dot green"></span> Qualif Directe (1-8)
                <span class="dot orange"></span> Barrages (9-24)
                <span class="dot red"></span> Éliminé (25-36)
            </div>
        </section>
"""
    
@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    try:
        data = request.json or {}
        club = data.get('club')
        day = int(data.get('day', 6)) # On récupère le jour
        
        if not club:
            return jsonify({"error": "Club manquant"}), 400

        # Appel de la fonction web simulation
        resultats = simulator.get_web_simulation(club, journee_depart=day)
        
        if "error" in resultats:
            return jsonify(resultats), 404
            
        return jsonify(resultats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/seuils', methods=['GET'])
def get_seuils():
    try:
        print("--> Calcul des seuils globaux...")
        # Appel avec "simulator."
        data = simulator.get_web_seuils(nb_simulations=1000)
        return jsonify(data)
    except Exception as e:
        print(f"ERREUR : {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/importance', methods=['GET'])
def get_importance():
    try:
        print("--> Analyse de l'importance des matchs...")
        # Appel avec "simulator."
        data = simulator.get_web_importance_matchs(nb_simulations=500)
        return jsonify(data)
    except Exception as e:
        print(f"ERREUR : {e}")
        return jsonify({"error": str(e)}), 500

#============ 19/12/2025===============================
@app.route('/api/predict-match', methods=['POST'])
def predict_match():
    try:
        data = request.json
        home = data.get('home')
        away = data.get('away')
        
        # Appel de la fonction du simulateur
        result = simulator.get_match_prediction(home, away)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#============ 20/12/2025===============================
"""
@app.route('/api/ranking', methods=['POST'])
def get_ranking():
    try:
        # Récupération des données JSON envoyées par le site
        data = request.json
        
        # Par défaut : Simulation complète (J1 à J8) si rien n'est précisé
        start = int(data.get('start', 1))
        end = int(data.get('end', 8))

        # Appel de la nouvelle fonction wrapper
        result = simulator.get_simulation_flexible(n_simulations=1000, start_day=start, end_day=end)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
"""
@app.route('/api/rankings', methods=['POST'])
def get_rankings():
    try:
        data = request.json or {}
        
        # On récupère le début et la fin demandés
        # Par défaut : du début (0) à la fin (8)
        start = int(data.get('start', 0))
        end = int(data.get('end', 8))
        
        print(f"--> Simulation de J{start} jusqu'à J{end}...")
        
        # Appel de la fonction flexible avec les deux bornes
        results = simulator.get_simulation_flexible(n_simulations=1000, start_day=start, end_day=end)
        
        return jsonify(results)
        
    except Exception as e:
        print(f"ERREUR RANKING: {e}")
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------
# 2. Route pour les PROBABILITÉS (Top 8 / Qualif)
# -----------------------------------------------------
@app.route('/api/rankings_top8_qualif', methods=['POST']) # Changé en POST
def get_probas_api():
    try:
        data = request.json or {}
        day = int(data.get('day', 6))
        
        print(f"--> Calcul Probas (Base J{day})...")
        
        # Appel de la fonction probas
        results = simulator.get_probas_top8_qualif(nb_simulations=1000, journee_depart=day)
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ------------------------------------------------------------------
# ROUTES POUR L'ANALYSE D'IMPACT DES MATCHS
# ------------------------------------------------------------------

@app.route('/api/match-impact', methods=['POST'])
def get_match_impact():
    try:
        data = request.json or {}
        club = data.get('club')
        journee = int(data.get('journee', 7))
        journee_donnees = int(data.get('journee_donnees', 6))
        
        if not club:
            return jsonify({"error": "Club manquant"}), 400
        
        result = simulator.get_web_match_impact(club, journee, nb_simulations=1000, journee_donnees=journee_donnees)
        
        if "error" in result:
            return jsonify(result), 404
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/all-matches-impact', methods=['POST'])
def get_all_matches_impact():
    try:
        data = request.json or {}
        journee = int(data.get('journee', 7))
        journee_donnees = int(data.get('journee_donnees', 6))
        
        result = simulator.get_web_all_matches_impact(journee, nb_simulations=500, journee_donnees=journee_donnees)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/next-match-scenarios', methods=['POST'])
def get_next_match_scenarios():
    try:
        data = request.json or {}
        club = data.get('club')
        journee_donnees = int(data.get('journee_donnees', 6))
        
        if not club:
            return jsonify({"error": "Club manquant"}), 400
        
        result = simulator.get_web_club_next_match_scenarios(club, nb_simulations=1000, journee_donnees=journee_donnees)
        
        if "error" in result:
            return jsonify(result), 404
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#===============================================================================================

if __name__ == '__main__':
    print("Serveur lancé sur http://127.0.0.1:5000")
    app.run(debug=True)


