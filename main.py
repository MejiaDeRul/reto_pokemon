# FLASK
from flask import Flask, render_template
from config import Config
from routes import auth_routes, pokemon_routes

app = Flask(__name__, template_folder='templates') # Instanciar Flask e indicar el folder de plantillas
app.config.from_object(Config)
app.register_blueprint(auth_routes.auth_bp)
app.register_blueprint(pokemon_routes.pokemon_bp)

#┬┌┐┌┬┌─┐┬┌─┐
#││││││  ││ │
#┴┘└┘┴└─┘┴└─┘
# Ruta de inicio de la API y la cual renderiza una plantilla html
@app.route('/')
def home():
    return render_template('index.html') # Renderizar plantilla

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) ### Ejecutar la API
