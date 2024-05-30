from flask import Blueprint
from src.services.auth_services import register_service, verify_email_service, login_service, verify_otp_service


auth_bp = Blueprint('auth', __name__)

#┬─┐┌─┐┌─┐┬┌─┐┌┬┐┌─┐┬─┐
#├┬┘├┤ │ ┬│└─┐ │ ├┤ ├┬┘
#┴└─└─┘└─┘┴└─┘ ┴ └─┘┴└─
# Ruta para registrar usuarios
@auth_bp.route('/register', methods=['POST'])
def register():
    return register_service()

#┬  ┬┌─┐┬─┐┬┌─┐┬┌─┐┌─┐┬─┐  ┌─┐┌┬┐┌─┐┬┬  
#└┐┌┘├┤ ├┬┘│├┤ ││  ├─┤├┬┘  ├┤ │││├─┤││  
# └┘ └─┘┴└─┴└  ┴└─┘┴ ┴┴└─  └─┘┴ ┴┴ ┴┴┴─┘
# Ruta para verificar correo de usuario recien creado
@auth_bp.route('/verify_email/<string:usuario>/<string:codigo>', methods=['GET'])
def verify_email(usuario, codigo):
    return verify_email_service(usuario, codigo)

#┬  ┌─┐┌─┐┬┌┐┌
#│  │ ││ ┬││││
#┴─┘└─┘└─┘┴┘└┘
# Ruta para autenticación de usuario
@auth_bp.route('/login', methods=['POST'])
def login():
    return login_service()


#┬  ┬┌─┐┬─┐┬┌─┐┬┌─┐┌─┐┬─┐  ┌─┐┌┬┐┌─┐
#└┐┌┘├┤ ├┬┘│├┤ ││  ├─┤├┬┘  │ │ │ ├─┘
# └┘ └─┘┴└─┴└  ┴└─┘┴ ┴┴└─  └─┘ ┴ ┴    
# Ruta para verificar si es correcto el codigo OTP
@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    return verify_otp_service()