from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import current_app, render_template, url_for
from app import mail

def get_reset_token(user_id, expires_sec=1800):
    """Genera un token seguro que expira en 30 minutos (1800 seg)"""
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps({'user_id': user_id}, salt='password-reset-salt')

def verify_reset_token(token, expires_sec=1800):
    """Verifica el token y devuelve el ID del usuario si es válido"""
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
        return data['user_id']
    except Exception:
        return None

def send_password_reset_email(user):
    """Envía el correo de recuperación al usuario"""
    token = get_reset_token(user.id)
    reset_url = url_for('auth.reset_password_with_token', token=token, _external=True)
    
    # Si no hay credenciales SMTP configuradas, mostramos el enlace en la terminal para desarrollo
    if not current_app.config.get('MAIL_USERNAME'):
        print("\n" + "="*50)
        print("! ATENCION: SMTP no configurado !")
        print(f"Correo de recuperación para: {user.email}")
        print(f"Enlace de recuperación: {reset_url}")
        print("="*50 + "\n")
        return True # Simulamos envío exitoso
        
    try:
        msg = Message('Recuperación de Contraseña - Multimarcas Brazo',
                      recipients=[user.email])
        
        # Cuerpo del correo en HTML
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: #e8000d; text-align: center; text-transform: uppercase; font-style: italic;">Multimarcas Brazo</h2>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p>Hola <strong>{user.nombre_completo}</strong>,</p>
            <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta.</p>
            <p>Para crear una nueva contraseña, haz clic en el siguiente botón:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background-color: #e8000d; color: white; padding: 12px 25px; text-decoration: none; border-radius: 3px; font-weight: bold; letter-spacing: 1px; display: inline-block;">RESTABLECER CONTRASEÑA</a>
            </div>
            <p style="font-size: 12px; color: #777;">Si no solicitaste este cambio, simplemente ignora este correo y tu contraseña seguirá siendo la misma.</p>
            <p style="font-size: 12px; color: #777;">Este enlace expirará en 30 minutos.</p>
        </div>
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False
