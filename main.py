### Importar Librerias
# FLASK
from flask import Flask, render_template
from src.routes import auth_routes, pokemon_routes
from config import Config
import os

app = Flask(__name__, template_folder='src/templates') # Instanciar Flask e indicar el folder de plantillas

app.config.from_object(Config)

app.register_blueprint(auth_routes.auth_bp)
app.register_blueprint(pokemon_routes.pokemon_bp)

@app.route('/')
def home():
    return render_template('index.html') # Renderizar plantilla

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) ### Ejecutar la API