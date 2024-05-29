import requests
import logging
from flask import jsonify
from random import randint

# Librerias para usar la API Open-Meteo
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy

from geopy.geocoders import Nominatim # Libreria para localizacion geografica
from datetime import datetime, timedelta # Libreria para saber fecha actual

logging.basicConfig(filename='../logs/logs.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s') # Configurar logging
logger = logging.getLogger(__name__)

#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┬ ┬┌┐┌┌─┐
#├─┘│ ││││ │ │ │  │ │││││ │
#┴  └─┘┘└┘ ┴ └─┘  └─┘┘└┘└─┘
# Obtener el tipo de un pokemon
def get_pokemon_info(nombre):
    # URL de pokeapi
    pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{nombre}'
    logger.info('Inicio de obtener el tipo de un pokemon')

    try:
        # Obetener la info del pokemon
        response = requests.get(pokemon_url)
        logger.info(f'Informacion de pokemon {nombre} obtenida exitosamente')
        # Extraer sus tipos o tipo
        tipos = response.json()['types']
        logger.info('Tipo extraido')
        # devolver el nombre del pokemon y sus tipos
        logger.info('Fin del proceso')
        return {'pokemon': nombre, 'tipos': [tipo['type']['name'] for tipo in tipos]}, response.status_code
    
    # Notificar errores comunes como copiar mal el nombre o no recibir informacion
    except requests.exceptions.HTTPError as http_err:
        logger.error(f'Interrupcion por error HTTP: {http_err}')
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        logger.error(f'Interrupcion por error en JSON: {json_err}')
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        logger.error(f'Interrupcion por error en Request: {req_err}')
        return jsonify({'error': f'Error occurred: {req_err}'}), response.status_code
    
    # Notificar otros errores
    except Exception as err:
        logger.error(f'Interrupcion por error: {err}')
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code


#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌┬┐┌─┐┌─┐
#├─┘│ ││││ │ │ │   │││ │└─┐
#┴  └─┘┘└┘ ┴ └─┘  ─┴┘└─┘└─┘
# Obtener un pokemon al azar de un tipo especifico 
def get_random_pokemon(tipo):
    # URL de pokeapi
    pokemon_url = f'https://pokeapi.co/api/v2/type/{tipo}'
    logger.info('Inicio de obtener pokemon aleatorio')

    try:
        # Obetener la info del tipo
        response = requests.get(pokemon_url)
        logger.info('Informacion obtenida exitosamente')
        # extraer solo los pokemons 
        pokemons = response.json()['pokemon']
        logger.info('Pokemons extraidos')

        # Generar un numero aleatorio entre 0 y el total de pokemons por ese tipo, este sera el pokemon aleatorio
        rn = randint(0, len(list(pokemons))-1) 
        logger.info('Fin del proceso con pokemon aleatorio')

        # NOTA: en la seccion type de la api hay mucha mas informacion como las diferencias de un solo pokemon en cada version, 
        #       por eso se accede a tantos diccionarios solo para obtener el nombre 
        return {'tipo': tipo, 'pokemon': pokemons[rn]['pokemon']['name']}, response.status_code 
    
    # Notificar errores comunes como copiar mal el nombre o no recibir informacion
    except requests.exceptions.HTTPError as http_err:
        logger.error(f'Interrupcion por error HTTP: {http_err}')
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        logger.error(f'Interrupcion por error en JSON: {json_err}')
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        logger.error(f'Interrupcion por error en Request: {req_err}')
        return jsonify({'error': f'Error occurred: {req_err}'}), response.status_code
    
    # Notificar otros errores
    except Exception as err:
        logger.error(f'Interrupcion por error: {err}')
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code


#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌┬┐┬─┐┌─┐┌─┐
#├─┘│ ││││ │ │ │   │ ├┬┘├┤ └─┐
#┴  └─┘┘└┘ ┴ └─┘   ┴ ┴└─└─┘└─┘
# Pokemon con el nombre mas largo de cierto tipo
def get_pokemon_long_name(tipo):
    pokemon_url = f'https://pokeapi.co/api/v2/type/{tipo}'
    logger.info('Inicio de obtener pokemon con nombre mas largo')

    try:
        # Obetener la info del tipo
        response = requests.get(pokemon_url)
        logger.info('Informacion obtenida exitosamente')
        # extraer solo los pokemons 
        pokemons = response.json()['pokemon']
        logger.info(f'Pokemons de tipo {tipo} extraidos')

        # Buscar el pokemon con nombre mas largo
        long_name_pokemon = ''
        for pokemon in list(pokemons): # Compara el actual nombre mas largo con el siguiente pokemon
            if len(long_name_pokemon) < len(pokemon['pokemon']['name']): # si el nombre del pokemon evaluado es mas largo que el actual nombre mas largo
                long_name_pokemon = pokemon['pokemon']['name']           # el actual nombre mas largo se vuelve el pokemon evaluado
        logger.info('Pokemon con nombre mas largo encontrado')
        logger.info('Fin del proceso de obtener pokemon con nombre largo')
        return {'tipo': tipo, 'pokemon': long_name_pokemon}, response.status_code
    
    # Notificar errores comunes como copiar mal el nombre o no recibir informacion
    except requests.exceptions.HTTPError as http_err:
        logger.error(f'Interrupcion por error HTTP: {http_err}')
        return jsonify({'error': f'Error HTTP: {http_err}'}), response.status_code
    
    except requests.exceptions.JSONDecodeError as json_err:
        logger.error(f'Interrupcion por error en JSON: {json_err}')
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), response.status_code
    
    except requests.exceptions.RequestException as req_err:
        logger.error(f'Interrupcion por error en Request: {req_err}')
        return jsonify({'error': f'Error occurred: {req_err}'}), response.status_code
    
    # Notificar otros errores
    except Exception as err:
        logger.error(f'Interrupcion por error: {err}')
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), response.status_code


#┌─┐┬ ┬┌┐┌┌┬┐┌─┐  ┌─┐┬ ┬┌─┐┌┬┐┬─┐┌─┐
#├─┘│ ││││ │ │ │  │  │ │├─┤ │ ├┬┘│ │
#┴  └─┘┘└┘ ┴ └─┘  └─┘└─┘┴ ┴ ┴ ┴└─└─┘
# Obtener un pokemon al azar del tipo mas fuerte en mi zona, y que tenga las letras 'i', 'a' o 'm' en su nombre
def get_random_better_pokemon(ubicacion):
    logger.info('Inicio de obtener pokemon dependiendo la temperatura')

    # Crear un cliente de la api Open-Meteo y almacenar temporalmente sus datos
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    logger.info('Datos de cache y cliente de open-meteo creados')

    # Crear un localizador con la ciudad donde estoy 
    geolocator = Nominatim(user_agent='geo_locator')
    location = geolocator.geocode(ubicacion)
    logger.info(f'Localizador creado para {location.address}')

    # Obtener la fecha de hoy
    fecha_actual = datetime.now()

    # Hacer un rango entre los ultmos 7 y ultimos 2 dias (Para alternativa de promedio de temperatura)
    fecha_rango_inicial = fecha_actual - timedelta(days=7)
    fecha_rango_final = fecha_actual - timedelta(days=2)

    # Ajustarlos al formato que acepta Open-Meteo para fechas
    fecha_rango_inicial = fecha_rango_inicial.strftime('%Y-%m-%d')
    fecha_rango_final = fecha_rango_final.strftime('%Y-%m-%d')
    logger.info('Variables de tiempo creadas')

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
        logger.info('Obtener datos de la api Open-Meteo exitoso')
        # Obtener temperatura actual de mi zona
        current = response.Current()
        temp = round(current.Variables(0).Value(), 2)
        logger.info(f'Temperatura actual en {ubicacion}: {temp}')
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
        logger.info('Mejor tipo de la zona seleccionado')

    # Notificar errores comunes como copiar mal el nombre o no recibir informacion
    except requests.exceptions.HTTPError as http_err:
        logger.error(f'Interrupcion por error HTTP: {http_err}')
        return jsonify({'error': f'Error HTTP: {http_err}'}), 403
    
    except requests.exceptions.JSONDecodeError as json_err:
        logger.error(f'Interrupcion por error en JSON: {json_err}')
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), 403
    
    except requests.exceptions.RequestException as req_err:
        logger.error(f'Interrupcion por error en Request: {req_err}')
        return jsonify({'error': f'Error occurred: {req_err}'}), 403
    
    # Notificar otros errores
    except Exception as err:
        logger.error(f'Interrupcion por error: {err}')
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), 500
        

    try:
        # Obetener la info del tipo
        response = requests.get(pokemon_url)
        logger.info('Informacion obtenida exitosamente')
        # extraer solo los pokemons 
        pokemons = response.json()['pokemon']
        logger.info(f'Pokemons de tipo {tipo} extraidos')

        # Generar un numero aleatorio entre 0 y el total de pokemons por ese tipo
        rn = randint(0, len(list(pokemons))-1) 
        # Pokemon aleatorio
        pokemon = pokemons[rn]['pokemon']['name']
        logger.info('Inicio de verificacion de condiciones del nombre')
        # Verificar si tiene 'i', 'a' o 'm' en su nombre
        while True:
            if 'i' in pokemon or 'a' in pokemon or 'm' in pokemon:
                logger.info('El pokemon cumple con las condiciones')
                break
            else:
                # sino tiene esas letras se volvera a escoger otro pokemon aleatoriamente
                rn = randint(0, len(list(pokemons))-1) 
                pokemon = pokemons[rn]['pokemon']['name']
                logger.info('El pokemon no cumple las condiciones, se escoge otro aleatorio')

        logger.info('Fin del proceso del mejor pokemon')
        return {'tipo': tipo, 'pokemon': pokemon, 'temperatura': temp, 'ubicacion': location.address}, 200
    
    # Notificar errores comunes como copiar mal el nombre o no recibir informacion
    except requests.exceptions.HTTPError as http_err:
        logger.error(f'Interrupcion por error HTTP: {http_err}')
        return jsonify({'error': f'Error HTTP: {http_err}'}), 403
    
    except requests.exceptions.JSONDecodeError as json_err:
        logger.error(f'Interrupcion por error en JSON: {json_err}')
        return jsonify({'error': f'Error en JSON o escribiendo el nombre: {json_err}'}), 403
    
    except requests.exceptions.RequestException as req_err:
        logger.error(f'Interrupcion por error en Request: {req_err}')
        return jsonify({'error': f'Error occurred: {req_err}'}), 403
    
    # Notificar otros errores
    except Exception as err:
        logger.error(f'Interrupcion por error: {err}')
        return jsonify({'error': f'Ha ocurrido un error: {err}'}), 500

