from flask import Blueprint, jsonify, request
from src.utils.Security import verify_token # Verficador de token de acceso
from src.services.pokemon_services import get_pokemon_service, get_random_pokemon_service, get_random_long_name_service, get_random_better_pokemon_service # Funciones para los retos

# Crear blueprint
pokemon_bp = Blueprint('pokemon', __name__)

# Estas rutas solo funcionan si ya se ha iniciado sesion y cuenta con el token JWT que se genera despues de confirmar en el correo el codigo OTP

#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┬ ┬┌┐┌┌─┐
#├─┘│ ││││ │ │ │  │ │││││ │
#┴  └─┘┘└┘ ┴ └─┘  └─┘┘└┘└─┘
# Ruta para Obtener el tipo de un pokemon
@pokemon_bp.route('/pokemon/<string:nombre>', methods=['GET'])
def get_pokemon(nombre):
    tiene_acceso = verify_token(request.headers) # Verificar si ya se tiene el token de acceso y es correcto

    # Ejecutar el servicio si es correcto el token
    if tiene_acceso:
        return get_pokemon_service(nombre)
    else:
        return jsonify({'error': 'No cuenta con acceso'}), 401


#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌┬┐┌─┐┌─┐
#├─┘│ ││││ │ │ │   │││ │└─┐
#┴  └─┘┘└┘ ┴ └─┘  ─┴┘└─┘└─┘
# Ruta para Obtener un pokemon al azar de un tipo especifico 
@pokemon_bp.route('/random_pokemon/<string:tipo>', methods=['GET'])
def get_random_pokemon(tipo):
    tiene_acceso = verify_token(request.headers) # Verificar si ya se tiene el token de acceso y es correcto

    if tiene_acceso:
       return get_random_pokemon_service(tipo)
    else:
        return jsonify({'error': 'No cuenta con acceso'}), 401

#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌┬┐┬─┐┌─┐┌─┐
#├─┘│ ││││ │ │ │   │ ├┬┘├┤ └─┐
#┴  └─┘┘└┘ ┴ └─┘   ┴ ┴└─└─┘└─┘
#Ruta para obtener el Pokemon con el nombre mas largo de cierto tipo
@pokemon_bp.route('/pokemon_long_name/<string:tipo>', methods=['GET'])
def get_random_long_name(tipo):
    tiene_acceso = verify_token(request.headers) # Verificar si ya se tiene el token de acceso y es correcto

    if tiene_acceso:
        return get_random_long_name_service(tipo)
    else:
        return jsonify({'error': 'No cuenta con acceso'}), 401

#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌─┐┬ ┬┌─┐┌┬┐┬─┐┌─┐
#├─┘│ ││││ │ │ │  │  │ │├─┤ │ ├┬┘│ │
#┴  └─┘┘└┘ ┴ └─┘  └─┘└─┘┴ ┴ ┴ ┴└─└─┘
#Ruta para Obtener un pokemon al azar del tipo mas fuerte en mi zona, y que tenga las letras 'i', 'a' o 'm' en su nombre
@pokemon_bp.route('/random_better_pokemon/<string:ubicacion>', methods=['GET'])
def get_random_better_pokemon(ubicacion):
    tiene_acceso = verify_token(request.headers) # Verificar si ya se tiene el token de acceso y es correcto

    if tiene_acceso:
        return get_random_better_pokemon_service(ubicacion)
    else:
        return jsonify({'error': 'No cuenta con acceso'}), 401