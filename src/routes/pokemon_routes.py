from flask import Blueprint, jsonify, request
from src.utils.Security import verify_token
from src.services.pokemon_services import get_pokemon_service, get_random_pokemon_service, get_random_long_name_service, get_random_better_pokemon_service

pokemon_bp = Blueprint('pokemon', __name__)

#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┬ ┬┌┐┌┌─┐
#├─┘│ ││││ │ │ │  │ │││││ │
#┴  └─┘┘└┘ ┴ └─┘  └─┘┘└┘└─┘
# Obtener el tipo de un pokemon
@pokemon_bp.route('/pokemon/<string:nombre>', methods=['GET'])
def get_pokemon(nombre):
    tiene_acceso = verify_token(request.headers)

    if tiene_acceso:
        return get_pokemon_service(nombre)
    else:
        return jsonify({'error': 'No cuenta con acceso'}), 401


#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌┬┐┌─┐┌─┐
#├─┘│ ││││ │ │ │   │││ │└─┐
#┴  └─┘┘└┘ ┴ └─┘  ─┴┘└─┘└─┘
# Obtener un pokemon al azar de un tipo especifico 
@pokemon_bp.route('/random_pokemon/<string:tipo>', methods=['GET'])
def get_random_pokemon(tipo):
    tiene_acceso = verify_token(request.headers)

    if tiene_acceso:
       return get_random_pokemon_service(tipo)
    else:
        return jsonify({'error': 'No cuenta con acceso'}), 401

#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌┬┐┬─┐┌─┐┌─┐
#├─┘│ ││││ │ │ │   │ ├┬┘├┤ └─┐
#┴  └─┘┘└┘ ┴ └─┘   ┴ ┴└─└─┘└─┘
# Pokemon con el nombre mas largo de cierto tipo
@pokemon_bp.route('/pokemon_long_name/<string:tipo>', methods=['GET'])
def get_random_long_name(tipo):
    tiene_acceso = verify_token(request.headers)

    if tiene_acceso:
        return get_random_long_name_service(tipo)
    else:
        return jsonify({'error': 'No cuenta con acceso'}), 401

#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌─┐┬ ┬┌─┐┌┬┐┬─┐┌─┐
#├─┘│ ││││ │ │ │  │  │ │├─┤ │ ├┬┘│ │
#┴  └─┘┘└┘ ┴ └─┘  └─┘└─┘┴ ┴ ┴ ┴└─└─┘
# Obtener un pokemon al azar del tipo mas fuerte en mi zona, y que tenga las letras 'i', 'a' o 'm' en su nombre
@pokemon_bp.route('/random_better_pokemon/<string:ubicacion>', methods=['GET'])
def get_random_better_pokemon(ubicacion):
    tiene_acceso = verify_token(request.headers)

    if tiene_acceso:
        return get_random_better_pokemon_service(ubicacion)
    else:
        return jsonify({'error': 'No cuenta con acceso'}), 401