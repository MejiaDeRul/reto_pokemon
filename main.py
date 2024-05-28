from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from random import randint
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, template_folder='templates')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['MONGO_URI'] = 'mongodb://pokeadmin:testpassword@monguito:27017/?authSource=admin'
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')

jwt = JWTManager(app)

client = MongoClient(app.config['MONGO_URI'])
db = client.get_database('pokemons')
collection = db.usuarios

# Ruta de inicio de la API
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    nombre = request.json.get('nombre', None)
    usuario = request.json.get('usuario', None)
    contrasena = request.json.get('contrasena', None)
    correo = request.json.get('correo', None)

    if not all([nombre, usuario, contrasena, correo]):
        return jsonify({"msg": "Todos los campos son requeridos"}), 400

    if collection.find_one({"usuario": usuario}):
        return jsonify({"msg": "El usuario ya existe"}), 400

    hashed_password = generate_password_hash(contrasena)
    codigo_verificacion = str(randint(100000, 999999))

    user = {
        "nombre": nombre,
        "usuario": usuario,
        "contrasena": hashed_password,
        "correo": correo,
        "correo_verificado": False,
        "codigo_verificacion": codigo_verificacion
    }

    collection.insert_one(user)
    send_verification_email(correo, usuario, codigo_verificacion)

    return jsonify({"msg": "Registro exitoso"}), 201

def send_verification_email(correo, usuario, codigo_verificacion):
    verification_link = url_for('verify_email', usuario=usuario, codigo=codigo_verificacion, _external=True)
    
    msg = MIMEMultipart()
    msg.attach(MIMEText(f'Hola {usuario}, haz clic en este enlace para verificar tu correo electrónico: {verification_link}', 'plain'))
    msg['Subject'] = 'Verifica tu correo electrónico'
    msg['From'] = app.config['MAIL_USERNAME']
    msg['To'] = correo

    try:
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(app.config['MAIL_USERNAME'], [correo], msg.as_string())
            server.quit()
    except Exception as e:
        print(f"Error: {str(e)}")

@app.route('/verify_email/<string:usuario>/<string:codigo>', methods=['GET'])
def verify_email(usuario, codigo):
    user = collection.find_one({"usuario": usuario})
    if user and user.get('codigo_verificacion') == codigo:
        collection.update_one({'_id': user['_id']}, {'$set': {'correo_verificado': True}, '$unset': {'codigo_verificacion': ""}})
        return jsonify({"msg": "Correo electrónico verificado exitosamente"}), 200
    else:
        return jsonify({"msg": "Error de verificación de correo electrónico"}), 400

# Ruta para autenticación
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    usuario = data.get('usuario', None)
    contrasena = data.get('contrasena', None)

    if not usuario or not contrasena:
        return jsonify({"msg": "Todos los campos son requeridos"}), 400

    user = collection.find_one({"usuario": usuario})
    if not user or not check_password_hash(user['contrasena'], contrasena):
        return jsonify({"msg": "Usuario o contraseña incorrectos"}), 401

    if not user['correo_verificado']:
        return jsonify({"msg": "Por favor, verifica tu correo electrónico"}), 403

    otp = randint(100000, 999999)
    user['otp'] = otp
    collection.update_one({'_id': user['_id']}, {'$set': {'otp': otp}})
    try:
        send_otp_email(user['correo'], otp)
    except Exception as e:
        return jsonify({"msg": f"Error enviando el correo: {str(e)}"}), 500

    return jsonify({"msg": "OTP enviado a tu correo"}), 200

def send_otp_email(correo, otp):
    msg = MIMEMultipart()
    msg.attach(MIMEText(f'Tu código OTP es {otp}. Expira en 10 minutos.', 'plain'))
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = app.config['MAIL_USERNAME']
    msg['To'] = correo

    try:
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(app.config['MAIL_USERNAME'], [correo], msg.as_string())
            server.quit()
    except Exception as e:
        print(f"Error: {str(e)}")

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    usuario = request.json.get('usuario', None)
    otp = request.json.get('otp', None)

    if not usuario or not otp:
        return jsonify({"msg": "Todos los campos son requeridos"}), 400

    user = collection.find_one({"usuario": usuario})
    if not user or 'otp' not in user or user['otp'] != int(otp):
        return jsonify({"msg": "OTP incorrecto"}), 401

    access_token = create_access_token(identity=usuario, expires_delta=timedelta(hours=1))
    collection.update_one({'_id': user['_id']}, {'$unset': {'otp': ""}})
    return jsonify(access_token=access_token), 200


# Obtener el tipo de un pokemon
@app.route('/pokemon/<string:nombre>', methods=['GET'])
@jwt_required()
def get_pokemon(nombre):
    pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{nombre}'

    try:
        response = requests.get(pokemon_url)
        tipos = response.json()['types']
        return {'pokemon': nombre, 'tipos': [tipo['type']['name'] for tipo in tipos]}, response.status_code
    
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f"Error occurred: {req_err}"}), response.status_code
    
    except Exception as err:
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code


# Obtener un pokemon al azar de un tipo especifico 
@app.route('/random_pokemon/<string:tipo>', methods=['GET'])
@jwt_required()
def get_random_pokemon(tipo):
    pokemon_url = f'https://pokeapi.co/api/v2/type/{tipo}'

    try:
        response = requests.get(pokemon_url)
        pokemons = response.json()['pokemon']
        rn = randint(0, len(list(pokemons))-1) 
        
        return {'tipo': tipo, 'pokemon': pokemons[rn]['pokemon']['name']}, response.status_code
    
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f"Error occurred: {req_err}"}), response.status_code
    
    except Exception as err:
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code


# Pokemon con el nombre mas largo de cierto tipo
@app.route('/pokemon_long_name/<string:tipo>', methods=['GET'])
@jwt_required()
def get_random_long_name(tipo):
    pokemon_url = f'https://pokeapi.co/api/v2/type/{tipo}'

    try:
        response = requests.get(pokemon_url)
        pokemons = response.json()['pokemon']

        long_name_pokemon = ''
        for pokemon in list(pokemons):
            if len(long_name_pokemon) < len(pokemon['pokemon']['name']):
                long_name_pokemon = pokemon['pokemon']['name']  
        return {'tipo': tipo, 'pokemon': long_name_pokemon}, response.status_code
    
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f"Error occurred: {req_err}"}), response.status_code
    
    except Exception as err:
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code


# Obtener un pokemon al azar del tipo mas fuerte en mi zona, y que tenga las letras 'i', 'a' o 'm'   
@app.route('/random_better_pokemon', methods=['GET'])
@jwt_required()
def get_random_better_pokemon():
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    fecha_actual = datetime.now()

    fecha_rango_inicial = fecha_actual - timedelta(days=7)
    fecha_rango_final = fecha_actual - timedelta(days=2)

    fecha_rango_inicial = fecha_rango_inicial.strftime('%Y-%m-%d')
    fecha_rango_final = fecha_rango_final.strftime('%Y-%m-%d')

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 6.2442,
        "longitude": 75.5812,
        "start_date": fecha_rango_inicial,
        "end_date": fecha_rango_final,
        "hourly": "temperature_2m",
        "timezone": "auto"
    }

    try:
        responses = openmeteo.weather_api(url, params=params)

        response = responses[0]

        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        prom_temp = round(sum(hourly_temperature_2m)/len(hourly_temperature_2m), 2)

        if prom_temp < 0: 
            tipo = 'ice'
        elif prom_temp >= 0 and prom_temp <= 10:
            tipo = 'water'
        elif prom_temp >= 10 and prom_temp <= 20:
            tipo = 'normal'
        elif prom_temp >= 20 and prom_temp <= 30:
            tipo = 'ground'
        elif prom_temp >= 30:
            tipo = 'fire'

        pokemon_url = f'https://pokeapi.co/api/v2/type/{tipo}'

    except Exception as err:
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code
        

    try:
        response = requests.get(pokemon_url)
        pokemons = response.json()['pokemon']
        rn = randint(0, len(list(pokemons))-1) 

        pokemon = pokemons[rn]['pokemon']['name']

        while True:
            if 'i' in pokemon or 'a' in pokemon or 'm' in pokemon:
                break
            else:
                rn = randint(0, len(list(pokemons))-1) 
                pokemon = pokemons[rn]['pokemon']['name']

        return {'tipo': tipo, 'pokemon': pokemon, 'temperatura': prom_temp}, response.status_code
    
    except Exception as err:
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
