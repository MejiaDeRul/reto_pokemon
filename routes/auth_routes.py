from flask import Blueprint, request
from services.auth_service import register_user, login_user, verify_email, verify_otp

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    return register_user(request.json)

@auth_bp.route('/login', methods=['POST'])
def login():
    return login_user(request.json)

@auth_bp.route('/verify_email/<string:usuario>/<string:codigo>', methods=['GET'])
def verify_email_route(usuario, codigo):
    return verify_email(usuario, codigo)

@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp_route():
    return verify_otp(request.json)