from flask import request, jsonify, url_for
from pymongo import MongoClient # Cliente para usar bases de MongoDB
import logging # Libreria para hacer logs
from werkzeug.security import generate_password_hash, check_password_hash # Generador de hash para las contraseñas
from random import randint # Generador de numeros random enteros
import smtplib # Libreria para enviar correos
from email.mime.text import MIMEText # Instancia para crear del cuerpo del correo
from email.mime.multipart import MIMEMultipart # Instancia para crear objetos de tipo correo
from src.utils.Security import generate_token # Funcion para generar token JWT 
import os

# Crear un logger 
logging.basicConfig(filename='/app/logs/logs.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s') # Configurar logging
logger = logging.getLogger(__name__)

#┬─┐┌─┐┌─┐┬┌─┐┌┬┐┌─┐┬─┐
#├┬┘├┤ │ ┬│└─┐ │ ├┤ ├┬┘
#┴└─└─┘└─┘┴└─┘ ┴ └─┘┴└─
# Servicio para registrar usuarios
def register_service():
    client = MongoClient(os.environ.get('MONGO_URI')) # Crear cliente para conectar con cluster de mongo
    db = client.get_database('pokemons') # Usar la base llamada 'pokemons'
    collection = db.usuarios  # Usar la coleccion 'usuarios' 

    logger.info('Inicio de registro de usuario')

    # Extraer datos solicitados para registrar un usuario 
    nombre = request.json.get('nombre', None)
    usuario = request.json.get('usuario', None)
    contrasena = request.json.get('contrasena', None)
    conf_contrasena = request.json.get('conf_contrasena', None)
    correo = request.json.get('correo', None)

    # Verificar que no falte ninguno de los datos
    if not all([nombre, usuario, contrasena, conf_contrasena, correo]):
        logger.info('No se han llenado todos los campos, fin de registro')
        return jsonify({'msg': "Todos los campos son requeridos"}), 400
    
    # Confirmar que ha ingresado bien la contraseña
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
    

# Funcion para enviar url para verificar correo
def send_verification_email(correo, usuario, codigo_verificacion):
    # Crear url para la validacion, este direcciona al endpoint que añadamos
    link_verificacion = url_for('auth.verify_email', usuario=usuario, codigo=codigo_verificacion, _external=True)

    # Configuración del servidor SMTP
    servidor_smtp = os.environ.get('EMAIL_SERVER')
    puerto_smtp = os.environ.get('EMAIL_PORT')

    # Configuración del remitente
    remitente = os.environ.get('EMAIL_USER')
    contraseña = os.environ.get('EMAIL_PASSWORD')

    # Crear un objeto de mensaje MIME
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = correo
    mensaje['Subject'] = 'Verifica tu correo electrónico'

    # Agregar el cuerpo del mensaje
    mensaje.attach(MIMEText(f'''
                            <p>Hola {usuario}, haz clic en el siguiente enlace para verificar tu correo electrónico:</p>
                            <p><a href="{link_verificacion}">Verificar correo electrónico</a></p>
                            ''', 'html'))

    # Iniciar una conexión SMTP segura con el servidor
    with smtplib.SMTP(host=servidor_smtp, port=puerto_smtp) as servidor_smtp:
        servidor_smtp.starttls()  # Iniciar cifrado TLS
        servidor_smtp.login(remitente, contraseña)  # Autenticarse en el servidor SMTP
        texto_del_mensaje = mensaje.as_string()
        servidor_smtp.sendmail(remitente, correo, texto_del_mensaje)  # Enviar correo electrónico

#┬  ┬┌─┐┬─┐┬┌─┐┬┌─┐┌─┐┬─┐  ┌─┐┌┬┐┌─┐┬┬  
#└┐┌┘├┤ ├┬┘│├┤ ││  ├─┤├┬┘  ├┤ │││├─┤││  
# └┘ └─┘┴└─┴└  ┴└─┘┴ ┴┴└─  └─┘┴ ┴┴ ┴┴┴─┘
# Servicio para verificar correo de usuario recien creado
def verify_email_service(usuario, codigo):
    client = MongoClient(os.environ.get('MONGO_URI')) # Crear cliente para conectar con cluster de mongo
    db = client.get_database('pokemons') # Usar la base llamada 'pokemons'
    collection = db.usuarios  # Usar la coleccion 'usuarios' 

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

#┬  ┌─┐┌─┐┬┌┐┌
#│  │ ││ ┬││││
#┴─┘└─┘└─┘┴┘└┘
# Servicio para autenticación de usuario
def login_service():
    client = MongoClient(os.environ.get('MONGO_URI')) # Crear cliente para conectar con cluster de mongo
    db = client.get_database('pokemons') # Usar la base llamada 'pokemons'
    collection = db.usuarios  # Usar la coleccion 'usuarios' 

    # Extraer datos para iniciar sesion
    data = request.json
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

# Funcion para enviar OTP a correo
def send_otp_email(correo, otp):
    # Configuración del servidor SMTP
    servidor_smtp = os.environ.get('EMAIL_SERVER')
    puerto_smtp = os.environ.get('EMAIL_PORT')

    # Configuración del remitente
    remitente = os.environ.get('EMAIL_USER')
    contraseña = os.environ.get('EMAIL_PASSWORD')

    # Crear un objeto de mensaje MIME
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = correo
    mensaje['Subject'] = 'Tu codigo OTP'

    # Agregar el cuerpo del mensaje
    mensaje.attach(MIMEText(f'Tu código OTP es {otp}.', 'plain'))

    # Iniciar una conexión SMTP segura con el servidor
    with smtplib.SMTP(host=servidor_smtp, port=puerto_smtp) as servidor:
        servidor.starttls()  # Iniciar cifrado TLS
        servidor.login(remitente, contraseña)  # Autenticarse en el servidor SMTP
        texto_del_mensaje = mensaje.as_string()
        servidor.sendmail(remitente, correo, texto_del_mensaje)  # Enviar correo electrónico

#┬  ┬┌─┐┬─┐┬┌─┐┬┌─┐┌─┐┬─┐  ┌─┐┌┬┐┌─┐
#└┐┌┘├┤ ├┬┘│├┤ ││  ├─┤├┬┘  │ │ │ ├─┘
# └┘ └─┘┴└─┴└  ┴└─┘┴ ┴┴└─  └─┘ ┴ ┴    
# Servicio para verificar si es correcto el codigo OTP
def verify_otp_service():
    client = MongoClient(os.environ.get('MONGO_URI')) # Crear cliente para conectar con cluster de mongo
    db = client.get_database('pokemons') # Usar la base llamada 'pokemons'
    collection = db.usuarios  # Usar la coleccion 'usuarios' 

    # Extraer datos
    usuario = request.json.get('usuario', None)
    otp = request.json.get('otp', None)
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
            return jsonify({"msg": "OTP incorrecto o no existe"}), 401
        logger.info('Verificaicon exitosa')
    except Exception as err:
        logger.error(f'Fin de verificacion por error: {err}')
        return jsonify({"msg": f"Error enviando el correo: {err}"}), 500

    try:
        # Crear el token JWT para acceder a la API
        access_token = generate_token(usuario) # la session dura 1 hora
        collection.update_one({'_id': user['_id']}, {'$unset': {'otp': ""}}) # eliminar el codigo OTP del usuario
        logger.info('Token de acceso creado')
        logger.info('Fin de inicio de sesion y verificacion')
        return jsonify(access_token=access_token), 200
    except Exception as err:
        logger.error(f'Fin de verificacion por error: {err}')
        return jsonify({"msg": f"Error enviando el correo: {err}"}), 500