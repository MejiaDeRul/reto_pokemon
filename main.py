### Importar Librerias
# FLASK
from flask import Flask, render_template
from flasgger import Swagger
import yaml
from src.routes import auth_routes, pokemon_routes # Importar rutas
from config import Config # Importar configuraciones
import os

app = Flask(__name__, template_folder='templates') # Instanciar Flask e indicar el folder de plantillas

app.config.from_object(Config) # Configurar app

app.register_blueprint(auth_routes.auth_bp) # Añadir ruta de autenticacion
app.register_blueprint(pokemon_routes.pokemon_bp) # Añadir ruta de pokemon

# Cargar la especificación Swagger desde un archivo YAML
with open('./docs/swagger.yml', 'r') as file:
    swagger_template = yaml.safe_load(file)

# Configurar Swagger
swagger = Swagger(app, template=swagger_template)

# Cargar plantilla y mostrarla
@app.route('/')
def home():
    return render_template('index.html') # Renderizar plantilla

@app.route('/docs')
def docs():
    return render_template('docs/docs/index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) ### Ejecutar la API