### Importar Librerias
# FLASK
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message

from pymongo import MongoClient # Base de datos NoSQL Mongo
from werkzeug.security import generate_password_hash, check_password_hash # Generador de hash para las contraseñas
import requests # Libreria para extraer info de las API 
from random import randint # Generador de numeros enteros aleatorios
from geopy.geocoders import Nominatim # Libreria para localizacion geografica
from datetime import datetime, timedelta # Libreria para saber fecha actual
import os # Libreria para manejo del sistema operativo

# Librerias para usar la API Open-Meteo
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy

#┌─┐┌─┐┌┐┌┌─┐┬┌─┐┬ ┬┬─┐┌─┐┌─┐┬┌─┐┌┐┌┌─┐┌─┐
#│  │ ││││├┤ ││ ┬│ │├┬┘├─┤│  ││ ││││├┤ └─┐
#└─┘└─┘┘└┘└  ┴└─┘└─┘┴└─┴ ┴└─┘┴└─┘┘└┘└─┘└─┘
### Creacion de app y configuraciones
app = Flask(__name__, template_folder='templates') # Instanciar Flask e indicar el folder de plantillas

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') # Llave secreta de la API
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') # Llave secreta para JWT
app.config['MONGO_URI'] = os.environ.get('MONGO_URI') # Direccion para conectar a mongodb dentro de otro contenedor
app.config['MAIL_SERVER'] = 'smtp.office365.com' # Servidor del correo usado para enviar correos (outlook)
app.config['MAIL_PORT'] = 587 # Puerto para enviar los correos
app.config['MAIL_USE_TLS'] = True # Agregar cifrado punto a punto con protocolo TLS
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') # Direccion de correo usado 
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD') # Contraseña de ese correo
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER') # Configurarlo para que envie con este correo por defecto

jwt = JWTManager(app) # Instanciar jwt, usado para generar los tokens
mail = Mail(app) # Instanciar mail para mandar correos con flask

client = MongoClient(app.config['MONGO_URI']) # Crear cliente para conectar con cluster de mongo
db = client.get_database('pokemons') # Usar la base llamada 'pokemons'
collection = db.usuarios  # Usar la coleccion 'usuarios' 

### Endpoints
#┬┌┐┌┬┌─┐┬┌─┐
#││││││  ││ │
#┴┘└┘┴└─┘┴└─┘
# Ruta de inicio de la API y la cual renderiza una plantilla html
@app.route('/')
def home():
    return render_template('index.html') # Renderizar plantilla

#┬─┐┌─┐┌─┐┬┌─┐┌┬┐┌─┐┬─┐
#├┬┘├┤ │ ┬│└─┐ │ ├┤ ├┬┘
#┴└─└─┘└─┘┴└─┘ ┴ └─┘┴└─
# Ruta para registrar usuarios
@app.route('/register', methods=['POST'])
def register():
    # Extraer datos solicitados para registrar un usuario 
    nombre = request.json.get('nombre', None)
    usuario = request.json.get('usuario', None)
    contrasena = request.json.get('contrasena', None)
    conf_contrasena = request.json.get('conf_contrasena', None)
    correo = request.json.get('correo', None)

    # Verificar que no falte ninguno de los datos
    if not all([nombre, usuario, contrasena, conf_contrasena, correo]):
        return jsonify({'msg': "Todos los campos son requeridos"}), 400
    
    if contrasena != conf_contrasena:
        return jsonify({'msg': "Las contraseñas no coinciden"}), 400

    # Verificar que el usuario que se quiere crear no este en la base de datos
    if collection.find_one({'usuario': usuario}) or collection.find_one({'correo': correo}):
        return jsonify({'msg': 'El usuario ya existe'}), 400

    # Hacer hash a contraseña ingresada 
    hashed_password = generate_password_hash(contrasena)
    # Generar codigo temporal para verificar el correo
    codigo_verificacion = str(randint(100000, 999999))
    hashed_cv = generate_password_hash(codigo_verificacion)

    # Diccionario para agregar nuevo usuario a la base de datos
    user = {
        'nombre': nombre,
        'usuario': usuario,
        'contrasena': hashed_password,
        'correo': correo,
        'correo_verificado': False,
        'codigo_verificacion': hashed_cv
    }
    # Agregar nuevo usuario y enviar codigo de verificacion al correo
    collection.insert_one(user)
    send_verification_email(correo, usuario, codigo_verificacion)

    return jsonify({'msg': 'Registro exitoso'}), 201

# Funcion para enviar url para verificar correo
def send_verification_email(correo, usuario, codigo_verificacion):
    # Crear url para la validacion
    verification_link = url_for('verify_email', usuario=usuario, codigo=codigo_verificacion, _external=True)
    
    # Enviar correo con el codigo de verificacion
    msg = Message(
    'Verifica tu correo electrónico',
    recipients=[correo],
    body=''
    )
    msg.html = f'''
    <p>Hola {usuario}, haz clic en el siguiente enlace para verificar tu correo electrónico:</p>
    <p><a href="{verification_link}">Verificar correo electrónico</a></p>
    '''
    mail.send(msg)

#┬  ┬┌─┐┬─┐┬┌─┐┬┌─┐┌─┐┬─┐  ┌─┐┌┬┐┌─┐┬┬  
#└┐┌┘├┤ ├┬┘│├┤ ││  ├─┤├┬┘  ├┤ │││├─┤││  
# └┘ └─┘┴└─┴└  ┴└─┘┴ ┴┴└─  └─┘┴ ┴┴ ┴┴┴─┘
# Ruta para verificar correo de usuario recien creado
@app.route('/verify_email/<string:usuario>/<string:codigo>', methods=['GET'])
def verify_email(usuario, codigo):
    # Extraer el usuario de la db
    user = collection.find_one({'usuario': usuario})
    # Verificar si es el codigo de verificacion
    if user and check_password_hash(user.get('codigo_verificacion'), codigo):
        # Cambiar estado a verificado
        collection.update_one({'_id': user['_id']}, {'$set': {'correo_verificado': True}, '$unset': {'codigo_verificacion': ''}})
        return 'Correo verificado exitosamente', 200
    else:
        return 'Error al verificar el correo', 400

#┬  ┌─┐┌─┐┬┌┐┌
#│  │ ││ ┬││││
#┴─┘└─┘└─┘┴┘└┘
# Ruta para autenticación de usuario
@app.route('/login', methods=['POST'])
def login():
    # Extraer datos para iniciar sesion
    data = request.json
    usuario = data.get('usuario', None)
    contrasena = data.get('contrasena', None)

    # Verificar que no falten datos
    if not usuario or not contrasena:
        return jsonify({'msg': 'Todos los campos son requeridos'}), 400

    # Verificar si existe usuario y si su contrasena es correcta
    user = collection.find_one({'usuario': usuario})
    if not user or not check_password_hash(user['contrasena'], contrasena):
        return jsonify({'msg': 'Usuario o contraseña incorrectos'}), 401

    # Verificar que el usuario tiene verificado su correo
    if not user['correo_verificado']:
        return jsonify({'msg': 'Por favor, verifica tu correo electrónico'}), 403

    # Generar OTP y hacerle hash
    otp = str(randint(100000, 999999))
    hashed_otp = generate_password_hash(otp)
    # Guardar OTP
    collection.update_one({'_id': user['_id']}, {'$set': {'otp': hashed_otp}})
    # Enviar OTP a correo
    try:
        send_otp_email(user['correo'], otp)
    except Exception as e:
        return jsonify({"msg": f"Error enviando el correo: {str(e)}"}), 500

    return jsonify({"msg": "OTP enviado a tu correo"}), 200

# Funcion para OTP a correo
def send_otp_email(correo, otp):
    msg = Message(
    'Your OTP Code',
    recipients=[correo],
    body=f'Tu código OTP es {otp}. Expira en 10 minutos.'
    )
    mail.send(msg)


#┬  ┬┌─┐┬─┐┬┌─┐┬┌─┐┌─┐┬─┐  ┌─┐┌┬┐┌─┐
#└┐┌┘├┤ ├┬┘│├┤ ││  ├─┤├┬┘  │ │ │ ├─┘
# └┘ └─┘┴└─┴└  ┴└─┘┴ ┴┴└─  └─┘ ┴ ┴    
# Ruta para verificar si es correcto el codigo OTP
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    # Extraer datos
    usuario = request.json.get('usuario', None)
    otp = request.json.get('otp', None)

    # Verificar que no falten datos
    if not usuario or not otp:
        return jsonify({"msg": "Todos los campos son requeridos"}), 400

    # Verificar si el codigo OTP es correcto
    user = collection.find_one({"usuario": usuario})
    if not user or 'otp' not in user or not check_password_hash(user['otp'], otp):
        return jsonify({"msg": "OTP incorrecto"}), 401

    # Crear el token JWT para acceder a la API
    access_token = create_access_token(identity=usuario, expires_delta=timedelta(hours=1)) # la session dura 1 hora
    collection.update_one({'_id': user['_id']}, {'$unset': {'otp': ""}}) # eliminar el codigo OTP del usuario
    return jsonify(access_token=access_token), 200


#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┬ ┬┌┐┌┌─┐
#├─┘│ ││││ │ │ │  │ │││││ │
#┴  └─┘┘└┘ ┴ └─┘  └─┘┘└┘└─┘
# Obtener el tipo de un pokemon
@app.route('/pokemon/<string:nombre>', methods=['GET'])
@jwt_required() # Con este decorador si la sesion no tiene token de acceso no permite funcionar la ruta
def get_pokemon(nombre):
    # URL de pokeapi
    pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{nombre}'

    try:
        # Obetener la info del pokemon
        response = requests.get(pokemon_url)
        # Extraer sus tipos o tipo
        tipos = response.json()['types']
        # devolver el nombre del pokemon y sus tipos
        return {'pokemon': nombre, 'tipos': [tipo['type']['name'] for tipo in tipos]}, response.status_code
    
    # Notificar errores comunes como copiar mal el nombre o no recibir informacion
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        return jsonify({'error': f'Error occurred: {req_err}'}), response.status_code
    
    # Notificar otros errores
    except Exception as err:
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code


#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌┬┐┌─┐┌─┐
#├─┘│ ││││ │ │ │   │││ │└─┐
#┴  └─┘┘└┘ ┴ └─┘  ─┴┘└─┘└─┘
# Obtener un pokemon al azar de un tipo especifico 
@app.route('/random_pokemon/<string:tipo>', methods=['GET'])
@jwt_required()
def get_random_pokemon(tipo):
    # URL de pokeapi
    pokemon_url = f'https://pokeapi.co/api/v2/type/{tipo}'

    try:
        # Obetener la info del tipo
        response = requests.get(pokemon_url)
        # extraer solo los pokemons 
        pokemons = response.json()['pokemon']
        # Generar un numero aleatorio entre 0 y el total de pokemons por ese tipo, este sera el pokemon aleatorio
        rn = randint(0, len(list(pokemons))-1) 
        
        # NOTA: en la seccion type de la api hay mucha mas informacion como las diferencias de un solo pokemon en cada version, 
        #       por eso se accede a tantos diccionarios solo para obtener el nombre 
        return {'tipo': tipo, 'pokemon': pokemons[rn]['pokemon']['name']}, response.status_code 
    
    # Notificar errores comunes como copiar mal el nombre o no recibir informacion
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        return jsonify({'error': f'Error occurred: {req_err}'}), response.status_code
    
    # Notificar otros errores
    except Exception as err:
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code

#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌┬┐┬─┐┌─┐┌─┐
#├─┘│ ││││ │ │ │   │ ├┬┘├┤ └─┐
#┴  └─┘┘└┘ ┴ └─┘   ┴ ┴└─└─┘└─┘
# Pokemon con el nombre mas largo de cierto tipo
@app.route('/pokemon_long_name/<string:tipo>', methods=['GET'])
@jwt_required()
def get_random_long_name(tipo):
    pokemon_url = f'https://pokeapi.co/api/v2/type/{tipo}'

    try:
        # Obetener la info del tipo
        response = requests.get(pokemon_url)
        # extraer solo los pokemons 
        pokemons = response.json()['pokemon']

        # Buscar el pokemon con nombre mas largo
        long_name_pokemon = ''
        for pokemon in list(pokemons): # Compara el actual nombre mas largo con el siguiente pokemon
            if len(long_name_pokemon) < len(pokemon['pokemon']['name']): # si el nombre del pokemon evaluado es mas largo que el actual nombre mas largo
                long_name_pokemon = pokemon['pokemon']['name']           # el actual nombre mas largo se vuelve el pokemon evaluado
        return {'tipo': tipo, 'pokemon': long_name_pokemon}, response.status_code
    
    # Notificar errores comunes como copiar mal el nombre o no recibir informacion
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        return jsonify({'error': f'Error occurred: {req_err}'}), response.status_code
    
    # Notificar otros errores
    except Exception as err:
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code

#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌─┐┬ ┬┌─┐┌┬┐┬─┐┌─┐
#├─┘│ ││││ │ │ │  │  │ │├─┤ │ ├┬┘│ │
#┴  └─┘┘└┘ ┴ └─┘  └─┘└─┘┴ ┴ ┴ ┴└─└─┘
# Obtener un pokemon al azar del tipo mas fuerte en mi zona, y que tenga las letras 'i', 'a' o 'm' en su nombre
@app.route('/random_better_pokemon', methods=['GET'])
@jwt_required()
def get_random_better_pokemon():
    # Crear un cliente de la api Open-Meteo y almacenar temporalmente sus datos
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Crear un localizador con la ciudad donde estoy
    geolocator = Nominatim(user_agent='geo_locator')
    location = geolocator.geocode('El penol, Antioquia')

    # Obtener la fecha de hoy
    fecha_actual = datetime.now()

    # Hacer un rango entre los ultmos 7 y ultimos 2 dias (revisando los datos, la api demora 2 dias en subir bien los datos del clima)
    fecha_rango_inicial = fecha_actual - timedelta(days=7)
    fecha_rango_final = fecha_actual - timedelta(days=2)

    # Ajustarlos al formato que acepta Open-Meteo para fechas
    fecha_rango_inicial = fecha_rango_inicial.strftime('%Y-%m-%d')
    fecha_rango_final = fecha_rango_final.strftime('%Y-%m-%d')

    # url de Open-Meteo 
    url = 'https://api.open-meteo.com/v1/forecast'
    # Parametros para solicitar la temperatura en la zona en la que estoy
    params = {
        'latitude': location.latitude,
        'longitude': location.longitude,
        'start_date': fecha_rango_inicial,
        'end_date': fecha_rango_final,
        'hourly': 'temperature_2m',
        'current': 'temperature_2m',
        'timezone': 'auto'
    }

    try:
        # Obetener los datos del clima que necesito
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        # Obtener temperatura actual de mi zona
        current = response.Current()
        temp = round(current.Variables(0).Value(), 2)

        # Alternativa con un promedio semanal
        #hourly = response.Hourly()
        #hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        #temp = round(sum(hourly_temperature_2m)/len(hourly_temperature_2m), 2)

        # Escoger el tipo mas fuerte dependiendo de la temperatura
        if temp < 0: 
            tipo = 'ice'
        elif temp >= 0 and temp <= 10:
            tipo = 'water'
        elif temp >= 10 and temp <= 20:
            tipo = 'normal'
        elif temp >= 20 and temp <= 30:
            tipo = 'ground'
        elif temp >= 30:
            tipo = 'fire'

        # Hacer la url de pokeapi con ese tipo
        pokemon_url = f'https://pokeapi.co/api/v2/type/{tipo}'

    # Notificar errores comunes como copiar mal el nombre o no recibir informacion
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        return jsonify({'error': f'Error occurred: {req_err}'}), response.status_code
    
    # Notificar otros errores
    except Exception as err:
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), 403
        

    try:
        # Obetener info del tipo
        response = requests.get(pokemon_url)
        # Extraer los pokemons
        pokemons = response.json()['pokemon']
        # Generar un numero aleatorio entre 0 y el total de pokemons por ese tipo
        rn = randint(0, len(list(pokemons))-1) 
        # Pokemon aleatorio
        pokemon = pokemons[rn]['pokemon']['name']

        # Verificar si tiene 'i', 'a' o 'm' en su nombre
        while True:
            if 'i' in pokemon or 'a' in pokemon or 'm' in pokemon:
                break
            else:
                # sino tiene esas letras se volvera a escoger otro pokemon aleatoriamente
                rn = randint(0, len(list(pokemons))-1) 
                pokemon = pokemons[rn]['pokemon']['name']

        return {'tipo': tipo, 'pokemon': pokemon, 'temperatura': temp}, 200
    
    # Notificar errores comunes como copiar mal el nombre o no recibir informacion
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        return jsonify({'error': f'Error occurred: {req_err}'}), response.status_code
    
    # Notificar otros errores
    except Exception as err:
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), 403


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) ### Ejecutar la API
