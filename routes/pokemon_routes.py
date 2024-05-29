from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from services.pokemon_service import get_pokemon_info, get_random_pokemon, get_pokemon_long_name, get_random_better_pokemon

pokemon_bp = Blueprint('pokemon', __name__)

@pokemon_bp.route('/pokemon/<string:nombre>', methods=['GET'])
@jwt_required()
def get_pokemon(nombre):
    return get_pokemon_info(nombre)

@pokemon_bp.route('/random_pokemon/<string:tipo>', methods=['GET'])
@jwt_required()
def get_random_pokemon_route(tipo):
    return get_random_pokemon(tipo)

@pokemon_bp.route('/pokemon_long_name/<string:tipo>', methods=['GET'])
@jwt_required()
def get_pokemon_long_name_route(tipo):
    return get_pokemon_long_name(tipo)

@pokemon_bp.route('/random_better_pokemon/<string:ubicacion>', methods=['GET'])
@jwt_required()
def get_random_better_pokemon_route(ubicacion):
    return get_random_better_pokemon(ubicacion)