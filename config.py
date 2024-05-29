import os

#┌─┐┌─┐┌┐┌┌─┐┬┌─┐┬ ┬┬─┐┌─┐┌─┐┬┌─┐┌┐┌┌─┐┌─┐
#│  │ ││││├┤ ││ ┬│ │├┬┘├─┤│  ││ ││││├┤ └─┐
#└─┘└─┘┘└┘└  ┴└─┘└─┘┴└─┴ ┴└─┘┴└─┘┘└┘└─┘└─┘
### Creacion de app y configuraciones
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('EMAIL_USER')