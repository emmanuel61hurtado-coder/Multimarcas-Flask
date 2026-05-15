from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.repuesto import Repuesto

repuestos_bp = Blueprint('repuestos', __name__)

def empleado_required_check():
    if not (current_user.is_empleado() or current_user.is_admin()):
        flash('Acceso denegado.', 'danger')
        return False
    return True


@repuestos_bp.route('/')
@login_required
def index():
    busqueda = request.args.get('q', '').strip()
    categoria = request.args.get('categoria', '').strip()

    query = Repuesto.query

    if busqueda:
        query = query.filter(Repuesto.nombre.ilike(f'%{busqueda}%'))

    if categoria:
        query = query.filter_by(categoria=categoria)

    repuestos = query.all()

    categorias = db.session.query(Repuesto.categoria).distinct().all()

    return render_template(
        'repuestos/index.html',
        repuestos=repuestos,
        categorias=[c[0] for c in categorias if c[0]],
        busqueda=busqueda,
        categoria_sel=categoria
    )


@repuestos_bp.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():
    if not empleado_required_check():
        return redirect(url_for('repuestos.index'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        categoria = request.form.get('categoria', '')
        marca = request.form.get('marca', '')
        precio = request.form.get('precio', '0')
        stock = request.form.get('stock', '0')
        descripcion = request.form.get('descripcion', '')

        if not nombre:
            flash('El nombre es obligatorio.', 'danger')
            return render_template('repuestos/agregar.html')

        try:
            precio_val = float(precio)
            stock_val = int(stock)

            if precio_val < 0 or stock_val < 0:
                raise ValueError

        except:
            flash('Precio o stock inválido.', 'danger')
            return render_template('repuestos/agregar.html')

        rep = Repuesto(
            nombre=nombre,
            categoria=categoria,
            marca=marca,
            precio=precio_val,
            stock=stock_val,
            descripcion=descripcion
        )

        db.session.add(rep)
        db.session.commit()

        flash('Repuesto agregado.', 'success')
        return redirect(url_for('repuestos.index'))

    return render_template('repuestos/agregar.html')


@repuestos_bp.route('/<int:rid>/editar', methods=['GET', 'POST'])
@login_required
def editar(rid):
    if not empleado_required_check():
        return redirect(url_for('repuestos.index'))

    rep = Repuesto.query.get_or_404(rid)

    if request.method == 'POST':
        rep.nombre = request.form.get('nombre', rep.nombre)
        rep.categoria = request.form.get('categoria', rep.categoria)
        rep.marca = request.form.get('marca', rep.marca)
        rep.descripcion = request.form.get('descripcion', rep.descripcion)

        try:
            precio = float(request.form.get('precio', rep.precio))
            stock = int(request.form.get('stock', rep.stock))

            if precio < 0 or stock < 0:
                raise ValueError

            rep.precio = precio
            rep.stock = stock

        except:
            flash('Precio o stock inválido.', 'danger')
            return render_template('repuestos/editar.html', rep=rep)

        db.session.commit()
        flash('Repuesto actualizado.', 'success')
        return redirect(url_for('repuestos.index'))

    return render_template('repuestos/editar.html', rep=rep)


@repuestos_bp.route('/<int:rid>/eliminar', methods=['POST'])
@login_required
def eliminar(rid):
    if not empleado_required_check():
        return redirect(url_for('repuestos.index'))

    rep = Repuesto.query.get_or_404(rid)

    db.session.delete(rep)
    db.session.commit()

    flash('Repuesto eliminado.', 'info')
    return redirect(url_for('repuestos.index'))