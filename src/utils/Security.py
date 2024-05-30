from datetime import datetime, timedelta
import jwt # Libreria para manejar tokens JWT
import os

# Funcion para generar tokens
def generate_token(user):
    # Parametros para generar el token
    payload = {
        'iat': datetime.now(),
        'exp': datetime.now() + timedelta(hours=1), # condicion para el vencimiento
        'username': user
    }
    # Generar el codigo usando clave secreta para JWT
    return jwt.encode(payload, os.environ.get('JWT_SECRET_KEY'), algorithm='HS256')

# Funcion para verificar tokens
def verify_token(headers):
    # Verificar si el token esta en los encabezados del request
    if 'Authorization' in headers.keys():
        # Extraer el codigo
        authorization = headers['Authorization']
        encoded_code = authorization.split(' ')[1]

        try:
            # Decodificar el codigo y verificar si es correcto
            payload = jwt.decode(encoded_code, os.environ.get('JWT_SECRET_KEY'), algorithms=['HS256'])
            return True
        except jwt.ExpiredSignatureError: # Si el token expira
            return False
        except jwt.InvalidSignatureError: # Si el token es invalido
            return False