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

#============ 17: 37 19/12/2025===============================
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
#===========================================================

if __name__ == '__main__':
    print("Serveur lancé sur http://127.0.0.1:5000")
    app.run(debug=True)
