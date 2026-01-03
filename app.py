from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import simulator  # Ton fichier simulator.py

app = Flask(__name__, static_folder='.')
CORS(app)

# ==============================================================================
# 1. ROUTES STATIQUES (POUR AFFICHER LE SITE)
# ==============================================================================

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# ==============================================================================
# 2. ROUTES GÉNÉRALES (SIMULATEUR, CLASSEMENT, DUEL)
# ==============================================================================

@app.route('/api/clubs', methods=['GET'])
def get_clubs():
    try:
        return jsonify(simulator.get_clubs_list())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    try:
        data = request.json or {}
        club = data.get('club')
        day = int(data.get('day', 6))
        
        if not club: return jsonify({"error": "Club manquant"}), 400
        
        # Simulation individuelle d'un club
        res = simulator.get_web_simulation(club, journee_depart=day)
        if "error" in res: return jsonify(res), 404
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/seuils', methods=['POST']) # Changé de GET à POST
def get_seuils():
    try:
        data = request.json or {}
        # On récupère la journée demandée, par défaut 0
        day = int(data.get('day', 0))
        
        print(f"--> Calcul des seuils globaux (Base J{day})...")
        
        # Appel de la fonction mise à jour
        result = simulator.get_web_seuils(nb_simulations=1000, journee_depart=day)
        
        return jsonify(result)
    except Exception as e:
        print(f"ERREUR SEUILS : {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict-match', methods=['POST'])
def predict_match():
    # Duel entre deux équipes (Page Duel)
    data = request.json or {}
    return jsonify(simulator.get_match_prediction(data.get('home'), data.get('away')))

@app.route('/api/rankings', methods=['POST'])
def get_rankings():
    # Classement projeté (Page Classement)
    data = request.json or {}
    return jsonify(simulator.get_simulation_flexible(
        n_simulations=1000, 
        start_day=int(data.get('start', 0)), 
        end_day=int(data.get('end', 8))
    ))

@app.route('/api/probas', methods=['POST'])
def get_probas():
    # Page Probabilités (Tableaux Top 8 / Qualif)
    data = request.json or {}
    return jsonify(simulator.get_probas_top8_qualif(
        nb_simulations=1000, 
        journee_depart=int(data.get('day', 6))
    ))

# ==============================================================================
# 3. ROUTES ONGLET 1 : IMPACT MATCHS (DÉTAILLÉ)
# ==============================================================================

@app.route('/api/match-impact', methods=['POST'])
def get_match_impact():
    try:
        data = request.json or {}
        res = simulator.get_web_match_impact(
            club=data.get('club'), 
            journee=int(data.get('journee', 7)), 
            nb_simulations=1000, 
            journee_donnees=int(data.get('journee_donnees', 6))
        )
        if "error" in res: return jsonify(res), 404
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/all-matches-impact', methods=['POST'])
def get_all_matches_impact():
    try:
        data = request.json or {}
        return jsonify(simulator.get_web_all_matches_impact(
            journee=int(data.get('journee', 7)), 
            nb_simulations=500, 
            journee_donnees=int(data.get('journee_donnees', 6))
        ))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/next-match-scenarios', methods=['POST'])
def get_next_match_scenarios():
    try:
        data = request.json or {}
        return jsonify(simulator.get_web_club_next_match_scenarios(
            club=data.get('club'), 
            nb_simulations=1000, 
            journee_donnees=int(data.get('journee_donnees', 6))
        ))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================================================
# 4. ROUTES ONGLET 2 : SCÉNARIO & HYPE (RAPIDE)
# ==============================================================================

@app.route('/api/scenario', methods=['POST'])
def run_scenario():
    try:
        data = request.json or {}
        res = simulator.get_scenario_analysis(
            club_cible=data.get('club'), 
            journee_cible=int(data.get('day', 7)), 
            resultat_fixe=data.get('result'), 
            journee_depart=int(data.get('start_day', 6)), 
            n_simulations=500
        )
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/importance', methods=['POST'])
def get_importance_route():
    try:
        data = request.json or {}
        res = simulator.get_web_importance(
            journee_cible=int(data.get('target', 7)), 
            journee_depart=int(data.get('start', 6)), 
            n_simulations=300
        )
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================================================
# LANCEMENT DU SERVEUR
# ==============================================================================

if __name__ == '__main__':
    print("Serveur lancé sur http://127.0.0.1:5000")
    app.run(debug=True)