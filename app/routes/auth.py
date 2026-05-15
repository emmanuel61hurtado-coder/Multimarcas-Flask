from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import urlparse
from app import db
from app.models.user import User
from app.utils.email import send_password_reset_email, verify_reset_token

auth_bp = Blueprint('auth', __name__)

# =========================
# 🔐 LOGIN
# =========================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    # 🚫 si ya está logueado, redirige según rol (sin loops)
    if current_user.is_authenticated:
        if current_user.rol == 'admin':
            return redirect(url_for('admin.dashboard'))
        if current_user.rol == 'empleado':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('cliente.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password) and user.activo:

            login_user(user, remember=remember)
            flash(f'Bienvenido, {user.nombre_completo}!', 'success')

            # 🔥 redirección por rol (CONTROL TOTAL)
            if user.rol == 'admin':
                return redirect(url_for('admin.dashboard'))

            if user.rol == 'empleado':
                return redirect(url_for('admin.dashboard'))

            return redirect(url_for('cliente.dashboard'))

        flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html')


# =========================
# 📝 REGISTRO
# =========================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    if request.method == 'POST':
        nombre = request.form.get('nombre_completo', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not all([nombre, username, email, password]):
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('El correo ya está registrado.', 'danger')
            return render_template('auth/register.html')

        user = User(
            nombre_completo=nombre,
            username=username,
            email=email,
            telefono=telefono,
            rol='cliente',
            password=generate_password_hash(password),
            activo=True
        )

        db.session.add(user)
        db.session.commit()

        flash('Cuenta creada exitosamente. Inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# =========================
# 🚪 LOGOUT
# =========================
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))


# =========================
# 👤 PERFIL
# =========================
@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():

    if request.method == 'POST':

        nombre = request.form.get('nombre_completo', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()

        if nombre:
            current_user.nombre_completo = nombre

        if email:
            existe = User.query.filter(
                User.email == email,
                User.id != current_user.id
            ).first()

            if existe:
                flash('El correo ya está en uso.', 'danger')
                return render_template('auth/perfil.html')

            current_user.email = email

        if telefono:
            current_user.telefono = telefono

        new_pass = request.form.get('new_password', '')

        if new_pass:
            if len(new_pass) < 6:
                flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
                return render_template('auth/perfil.html')

            current_user.password = generate_password_hash(new_pass)

        db.session.commit()
        flash('Perfil actualizado exitosamente.', 'success')

    return render_template('auth/perfil.html')


# =========================
# 🗑️ ELIMINAR CUENTA
# =========================
@auth_bp.route('/eliminar_cuenta', methods=['POST'])
@login_required
def eliminar_cuenta():
    user = current_user
    # En lugar de db.session.delete(user), lo desactivamos lógicamente
    # Esto preserva las facturas y referencias de contabilidad
    user.activo = False
    db.session.commit()

    logout_user()
    flash('Tu cuenta ha sido eliminada permanentemente. Esperamos verte pronto.', 'info')
    return redirect(url_for('auth.login'))

# =========================
# 🔑 RECUPERAR CONTRASEÑA
# =========================
@auth_bp.route('/recuperar_password', methods=['GET', 'POST'])
def recuperar_password():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        
        # Siempre mostramos el mismo mensaje para no revelar qué emails están registrados
        flash('Si el correo existe en nuestro sistema, recibirás instrucciones para restablecer tu contraseña.', 'info')
        
        if user and user.activo:
            send_password_reset_email(user)
            
        return redirect(url_for('auth.login'))

    return render_template('auth/recuperar.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    user_id = verify_reset_token(token)
    if not user_id:
        flash('El enlace de recuperación es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.recuperar_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('auth/reset.html', token=token)

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            return render_template('auth/reset.html', token=token)

        user = User.query.get(user_id)
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/reset.html', token=token)