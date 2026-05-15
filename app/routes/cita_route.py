from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.cita import Cita
from app.models.moto import Moto

citas_bp = Blueprint('citas', __name__)

@citas_bp.route('/')
@login_required
def index():
    if current_user.is_admin() or current_user.is_empleado():
        mis_citas = Cita.query.order_by(Cita.fecha.desc()).all()
    else:
        mis_citas = Cita.query.filter_by(user_id=current_user.id).order_by(Cita.fecha.desc()).all()
    return render_template('citas/index.html', citas=mis_citas)


@citas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    # Obtener las motos del usuario actual
    motos = Moto.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        moto_id = request.form.get('moto_id')
        fecha_str = request.form.get('fecha')
        hora_str = request.form.get('hora')
        tipo = request.form.get('tipo_servicio')
        desc = request.form.get('descripcion', '')

        # Validar que se haya seleccionado una moto
        if not moto_id:
            flash('Debes seleccionar una moto registrada. Si no tienes una, por favor regístrala primero en la sección de Motos.', 'danger')
            return redirect(url_for('citas.nueva'))

        # Buscar la moto y validar pertenencia
        moto = Moto.query.filter_by(id=moto_id, user_id=current_user.id).first()
        if not moto:
            flash('La moto seleccionada no está registrada o no te pertenece.', 'danger')
            return redirect(url_for('citas.nueva'))

        if not all([fecha_str, hora_str, tipo]):
            flash('Completa todos los campos obligatorios de la cita.', 'danger')
            return render_template('citas/nueva.html', motos=motos)

        try:
            fecha_hora_str = f"{fecha_str} {hora_str}"
            fecha_dt = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')
            
            # Validación de horario comercial
            dia_semana = fecha_dt.weekday() # 0=Lunes, 6=Domingo
            hora = fecha_dt.hour
            minuto = fecha_dt.minute
            
            if dia_semana == 6: # Domingo
                flash('No abrimos los domingos. Por favor selecciona un día de Lunes a Sábado.', 'warning')
                return render_template('citas/nueva.html', motos=motos)
                
            if hora < 8:
                flash('El horario de atención comienza a las 8:00 AM.', 'warning')
                return render_template('citas/nueva.html', motos=motos)
                
            if dia_semana <= 4: # Lunes a Viernes
                # Hasta las 17:00 (5 PM)
                if hora > 17 or (hora == 17 and minuto > 0):
                    flash('De Lunes a Viernes atendemos hasta las 5:00 PM.', 'warning')
                    return render_template('citas/nueva.html', motos=motos)
            elif dia_semana == 5: # Sábado
                # Hasta las 12:00 PM
                if hora > 12 or (hora == 12 and minuto > 0):
                    flash('Los Sábados solo atendemos hasta las 12:00 PM.', 'warning')
                    return render_template('citas/nueva.html', motos=motos)
                    
        except ValueError:
            flash('Fecha u hora inválida.', 'danger')
            return render_template('citas/nueva.html', motos=motos)

        cita = Cita(
            fecha=fecha_dt,
            tipo_servicio=tipo,
            descripcion=desc,
            user_id=current_user.id,
            moto_id=moto.id
        )

        db.session.add(cita)
        db.session.commit()

        flash('Cita agendada exitosamente.', 'success')
        return redirect(url_for('citas.index'))

    return render_template('citas/nueva.html', motos=motos)


@citas_bp.route('/<int:cid>')
@login_required
def detalle(cid):
    cita = Cita.query.get_or_404(cid)

    if not (current_user.is_admin() or current_user.is_empleado() or cita.user_id == current_user.id):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('citas.index'))

    return render_template('citas/detalle.html', cita=cita)


@citas_bp.route('/<int:cid>/editar', methods=['GET', 'POST'])
@login_required
def editar(cid):
    cita = Cita.query.get_or_404(cid)

    if not (current_user.is_admin() or current_user.is_empleado() or cita.user_id == current_user.id):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('citas.index'))

    motos = Moto.query.filter_by(user_id=cita.user_id).all()

    if request.method == 'POST':
        fecha_str = request.form.get('fecha')
        hora_str = request.form.get('hora')

        if not fecha_str or not hora_str:
            flash('Fecha y hora son obligatorias.', 'danger')
            return render_template('citas/editar.html', cita=cita, motos=motos)

        cita.tipo_servicio = request.form.get('tipo_servicio', cita.tipo_servicio)
        cita.descripcion = request.form.get('descripcion', cita.descripcion)

        try:
            cita.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            cita.hora = datetime.strptime(hora_str, '%H:%M').time()
        except:
            flash('Fecha u hora inválida.', 'danger')
            return render_template('citas/editar.html', cita=cita, motos=motos)

        db.session.commit()
        flash('Cita actualizada.', 'success')
        return redirect(url_for('citas.detalle', cid=cid))

    return render_template('citas/editar.html', cita=cita, motos=motos)


@citas_bp.route('/<int:cid>/cancelar', methods=['POST'])
@login_required
def cancelar(cid):
    cita = Cita.query.get_or_404(cid)

    if not (current_user.is_admin() or current_user.is_empleado() or cita.user_id == current_user.id):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('citas.index'))

    cita.estado = 'cancelada'
    db.session.commit()

    flash('Cita cancelada.', 'info')
    return redirect(url_for('citas.index'))


@citas_bp.route('/<int:cid>/borrar', methods=['POST'])
@login_required
def borrar(cid):
    cita = Cita.query.get_or_404(cid)

    if not (current_user.is_admin() or current_user.is_empleado() or cita.user_id == current_user.id):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('citas.index'))

    # Solo permitir borrar si ya está cancelada
    if cita.estado != 'cancelada':
        flash('Solo puedes eliminar definitivamente las citas que ya han sido canceladas primero.', 'warning')
        return redirect(url_for('citas.index'))

    db.session.delete(cita)
    db.session.commit()

    flash('La cita ha sido eliminada permanentemente.', 'info')
    return redirect(url_for('citas.index'))