from flask_mail import Message, Mail
from flask import url_for, current_app

mail = Mail(__name__)
mail.init_app(current_app)

# Funcion para enviar url para verificar correo
def send_verification_email(correo, usuario, codigo_verificacion):
    # Crear url para la validacion
    verification_link = url_for('verify_email', usuario=usuario, codigo=codigo_verificacion, _external=True)
    
    # Enviar correo con el codigo de verificacion
    msg = Message(
    'Verifica tu correo electrónico',
    recipients=[correo],
    body=''
    )
    msg.html = f'''
    <p>Hola {usuario}, haz clic en el siguiente enlace para verificar tu correo electrónico:</p>
    <p><a href="{verification_link}">Verificar correo electrónico</a></p>
    '''
    mail.send(msg)

# Funcion para OTP a correo
def send_otp_email(correo, otp):
    msg = Message(
    'Your OTP Code',
    recipients=[correo],
    body=f'Tu código OTP es {otp}. Expira en 10 minutos.'
    )
    mail.send(msg)
