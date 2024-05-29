from flask import jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token
from datetime import timedelta
from pymongo import MongoClient # Base de datos NoSQL Mongo
from random import randint
import logging
from .email_service import send_verification_email, send_otp_email

logging.basicConfig(filename='../logs/logs.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s') # Configurar logging
logger = logging.getLogger(__name__)
jwt = JWTManager(__name__)

client = MongoClient(current_app.config['MONGO_URI']) # Crear cliente para conectar con cluster de mongo
db = client.get_database('pokemons') # Usar la base llamada 'pokemons'
collection = db.usuarios  # Usar la coleccion 'usuarios' 

#┬─┐┌─┐┌─┐┬┌─┐┌┬┐┌─┐┬─┐
#├┬┘├┤ │ ┬│└─┐ │ ├┤ ├┬┘
#┴└─└─┘└─┘┴└─┘ ┴ └─┘┴└─
# Ruta para registrar usuarios
def register_user(data):
    logger.info('Inicio de registro de usuario')
    # Extraer datos solicitados para registrar un usuario 
    nombre = data.get('nombre', None)
    usuario = data.get('usuario', None)
    contrasena = data.get('contrasena', None)
    conf_contrasena = data.get('conf_contrasena', None)
    correo = data.get('correo', None)

    # Verificar que no falte ninguno de los datos
    if not all([nombre, usuario, contrasena, conf_contrasena, correo]):
        logger.info('No se han llenado todos los campos, fin de registro')
        return jsonify({'msg': "Todos los campos son requeridos"}), 400
    
    if contrasena != conf_contrasena:
        logger.info('Las contraseñas no coinciden, fin de registro')
        return jsonify({'msg': "Las contraseñas no coinciden"}), 400

    try:
        # Verificar que el usuario que se quiere crear no este en la base de datos
        if collection.find_one({'usuario': usuario}) or collection.find_one({'correo': correo}):
            logger.info('El usuario ya existe, fin de registro')
            return jsonify({'msg': 'El usuario ya existe'}), 400
    except Exception as err:
        logger.error(f'Fin de registro por error: {err}')
        return jsonify({'msg': f'Error: {err}'}), 400

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
    try:
        collection.insert_one(user)
        logger.info('Nuevo usuario creado')
        send_verification_email(correo, usuario, codigo_verificacion)
        logger.info('Correo de verificacion enviado')
        logger.info('Fin de registro de usuario')
        return jsonify({'msg': 'Registro exitoso'}), 201
    except Exception as err:
        logger.error(f'Fin de registro por error: {err}')
        return jsonify({'msg': f'Error: {err}'}), 400

#┬  ┌─┐┌─┐┬┌┐┌
#│  │ ││ ┬││││
#┴─┘└─┘└─┘┴┘└┘
# Ruta para autenticación de usuario
def login_user(data):
    # Extraer datos para iniciar sesion
    usuario = data.get('usuario', None)
    contrasena = data.get('contrasena', None)
    logger.info(f'Intento de inicio de sesion por parte de {usuario}')

    # Verificar que no falten datos
    if not usuario or not contrasena:
        logger.info('No se han llenado todos los campos, fin de registro')
        return jsonify({'msg': 'Todos los campos son requeridos'}), 400

    try:
        # Verificar si existe usuario y si su contrasena es correcta
        user = collection.find_one({'usuario': usuario})
        if not user or not check_password_hash(user['contrasena'], contrasena):
            logger.info('Fin de inicio de sesion por usuario o contrasena incorrectos')
            return jsonify({'msg': 'Usuario o contraseña incorrectos'}), 401
    except Exception as err:
        logger.error(f'Fin de inicio de sesion por error: {err}')
        return jsonify({'msg': f'Error: {err}'}), 400

    # Verificar que el usuario tiene verificado su correo
    if not user['correo_verificado']:
        logger.info('Fin de inicio de sesion por correo no verificado')
        return jsonify({'msg': 'Por favor, verifica tu correo electrónico'}), 403

    # Generar OTP y hacerle hash
    otp = str(randint(100000, 999999))
    hashed_otp = generate_password_hash(otp)
    try:
        # Guardar OTP
        collection.update_one({'_id': user['_id']}, {'$set': {'otp': hashed_otp}})
        logger.info('Codigo OTP generado')
        # Enviar OTP a correo
        send_otp_email(user['correo'], otp)
        logger.info('Correo con codigo enviado')
        logger.info('A espera de verificacion de codigo OTP')
    except Exception as err:
        logger.error(f'Fin de inicio de sesion por error: {err}')
        return jsonify({"msg": f"Error enviando el correo: {err}"}), 500

    return jsonify({"msg": "OTP enviado a tu correo"}), 200

#┬  ┬┌─┐┬─┐┬┌─┐┬┌─┐┌─┐┬─┐  ┌─┐┌┬┐┌─┐┬┬  
#└┐┌┘├┤ ├┬┘│├┤ ││  ├─┤├┬┘  ├┤ │││├─┤││  
# └┘ └─┘┴└─┴└  ┴└─┘┴ ┴┴└─  └─┘┴ ┴┴ ┴┴┴─┘
# Ruta para verificar correo de usuario recien creado
def verify_email(usuario, codigo):
    logger.info('Inicio de verificacion de correo de usuario nuevo')
    try:
        # Extraer el usuario de la db
        user = collection.find_one({'usuario': usuario})
        # Verificar si es el codigo de verificacion
        if user and check_password_hash(user.get('codigo_verificacion'), codigo):
            # Cambiar estado a verificado
            collection.update_one({'_id': user['_id']}, {'$set': {'correo_verificado': True}, '$unset': {'codigo_verificacion': ''}})
            logger.info('Correo verificado exitosamente')
            logger.info('Fin de verificacion de correo')
            return 'Correo verificado exitosamente', 200
        else:
            logger.error(f'Error verificando correo, posible codigo incorrecto')
            return 'Error al verificar el correo', 400
    except Exception as err:
        logger.error(f'Fin de registro por error: {err}')
        return jsonify({'msg': f'Error: {err}'}), 400

#┬  ┬┌─┐┬─┐┬┌─┐┬┌─┐┌─┐┬─┐  ┌─┐┌┬┐┌─┐
#└┐┌┘├┤ ├┬┘│├┤ ││  ├─┤├┬┘  │ │ │ ├─┘
# └┘ └─┘┴└─┴└  ┴└─┘┴ ┴┴└─  └─┘ ┴ ┴    
# Ruta para verificar si es correcto el codigo OTP
def verify_otp(data):
    # Extraer datos
    usuario = data.get('usuario', None)
    otp = data.get('otp', None)
    logger.info(f'Inicio de verificacion de codigo OTP por parte de usuario {usuario}')

    # Verificar que no falten datos
    if not usuario or not otp:
        logger.info('Campos no ingresados')
        return jsonify({"msg": "Todos los campos son requeridos"}), 400

    try:
        # Verificar si el codigo OTP es correcto
        user = collection.find_one({"usuario": usuario})
        if not user or 'otp' not in user or not check_password_hash(user['otp'], otp):
            logger.info('Codigo ingresado es incorrecto')
            return jsonify({"msg": "OTP incorrecto"}), 401
        logger.info('Verificaicon exitosa')
    except Exception as err:
        logger.error(f'Fin de verificacion por error: {err}')
        return jsonify({"msg": f"Error enviando el correo: {err}"}), 500

    try:
        # Crear el token JWT para acceder a la API
        access_token = create_access_token(identity=usuario, expires_delta=timedelta(hours=1)) # la session dura 1 hora
        collection.update_one({'_id': user['_id']}, {'$unset': {'otp': ""}}) # eliminar el codigo OTP del usuario
        logger.info('Token de acceso creado')
        logger.info('Fin de inicio de sesion y verificacion')
        return jsonify(access_token=access_token), 200
    except Exception as err:
        logger.error(f'Fin de verificacion por error: {err}')
        return jsonify({"msg": f"Error enviando el correo: {err}"}), 500
