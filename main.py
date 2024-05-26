from flask import Flask, jsonify
import requests
from random import randint
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy
from datetime import datetime, timedelta

app = Flask(__name__)

# Ruta de inicio de la API
@app.route('/')
def home():
    return 'Welcome Home'

# Obtener el tipo de un pokemon
@app.route('/get_pokemon/<string:nombre>', methods=['GET'])
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
@app.route('/get_random_pokemon/<string:tipo>', methods=['GET'])
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
@app.route('/get_pokemon_long_name/<string:tipo>', methods=['GET'])
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
@app.route('/get_random_better_pokemon', methods=['GET'])
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
    app.run(debug=True, port=5000)