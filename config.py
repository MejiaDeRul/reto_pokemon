import os

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') # Llave secreta de la API
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') # Llave secreta para JWT
    MONGO_URI = os.environ.get('MONGO_URI') # Direccion para conectar a mongodb dentro de otro contenedor
    MAIL_SERVER = 'smtp.office365.com' # Servidor del correo usado para enviar correos (outlook)
    MAIL_PORT = 587 # Puerto para enviar los correos
    MAIL_USE_TLS = True # Agregar cifrado punto a punto con protocolo TLS
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('EMAIL_USER') # Direccion de correo usado 
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD') # Contraseña de ese correo
    MAIL_DEFAULT_SENDER = os.environ.get('EMAIL_USER') # Configurarlo para que envie con este correo por defecto
