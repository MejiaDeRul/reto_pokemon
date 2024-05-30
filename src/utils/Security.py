from datetime import datetime, timedelta
import jwt
import os

def generate_token(user):
    payload = {
        'iat': datetime.now(),
        'exp': datetime.now() + timedelta(hours=1),
        'username': user
    }
    return jwt.encode(payload, os.environ.get('JWT_SECRET_KEY'), algorithm='HS256')

def verify_token(headers):
    if 'Authorization' in headers.keys():
        authorization = headers['Authorization']
        encoded_code = authorization.split(' ')[1]

        try:
            payload = jwt.decode(encoded_code, os.environ.get('JWT_SECRET_KEY'), algorithms=['HS256'])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidSignatureError:
            return False