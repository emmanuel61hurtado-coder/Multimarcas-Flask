from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.moto import Moto

motos_bp = Blueprint('motos', __name__)

@motos_bp.route('/')
@login_required
def index():
    if current_user.is_empleado() or current_user.is_admin():
        motos = Moto.query.all()
    else:
        motos = Moto.query.filter_by(user_id=current_user.id).all()
    return render_template('motos/index.html', motos=motos)


@motos_bp.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():
    if request.method == 'POST':
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        placa = request.form.get('placa', '').strip().upper()
        año = request.form.get('año')
        color = request.form.get('color', '')
        cilindraje = request.form.get('cilindraje', '')

        if not all([marca, modelo, placa]):
            flash('Marca, modelo y placa son obligatorios.', 'danger')
            return render_template('motos/agregar.html')

        if Moto.query.filter_by(placa=placa).first():
            flash('Ya existe una moto con esa placa.', 'danger')
            return render_template('motos/agregar.html')

        try:
            año_val = int(año) if año else None
        except:
            flash('El año debe ser un número válido.', 'danger')
            return render_template('motos/agregar.html')

        moto = Moto(
            marca=marca,
            modelo=modelo,
            placa=placa,
            año=año_val,
            color=color,
            cilindraje=cilindraje,
            user_id=current_user.id
        )

        db.session.add(moto)
        db.session.commit()

        flash('Moto agregada exitosamente.', 'success')
        return redirect(url_for('motos.index'))

    return render_template('motos/agregar.html')


@motos_bp.route('/<int:mid>/editar', methods=['GET', 'POST'])
@login_required
def editar(mid):
    moto = Moto.query.get_or_404(mid)

    if not (current_user.is_empleado() or current_user.is_admin() or moto.user_id == current_user.id):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('motos.index'))

    if request.method == 'POST':
        marca = request.form.get('marca', moto.marca).strip()
        modelo = request.form.get('modelo', moto.modelo).strip()
        color = request.form.get('color', moto.color)
        cilindraje = request.form.get('cilindraje', moto.cilindraje)
        año = request.form.get('año')

        moto.marca = marca
        moto.modelo = modelo
        moto.color = color
        moto.cilindraje = cilindraje

        if año:
            try:
                moto.año = int(año)
            except:
                flash('El año debe ser un número válido.', 'danger')
                return render_template('motos/editar.html', moto=moto)

        db.session.commit()
        flash('Moto actualizada.', 'success')
        return redirect(url_for('motos.index'))

    return render_template('motos/editar.html', moto=moto)


@motos_bp.route('/<int:mid>/eliminar', methods=['POST'])
@login_required
def eliminar(mid):
    moto = Moto.query.get_or_404(mid)

    if not (current_user.is_empleado() or current_user.is_admin() or moto.user_id == current_user.id):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('motos.index'))

    db.session.delete(moto)
    db.session.commit()

    flash('Moto eliminada.', 'info')
    return redirect(url_for('motos.index'))