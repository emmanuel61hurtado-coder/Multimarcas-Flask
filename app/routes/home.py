from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models.moto import Moto

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    # Siempre mostramos la bienvenida informativa al inicio
    return render_template('home/welcome.html')


@home_bp.route('/servicios')
def servicios():
    return render_template('home/servicios.html')


@home_bp.route('/marcas')
def marcas():
    return render_template('home/marcas.html')


@home_bp.route('/citas-info')
def citas_info():
    return render_template('home/citas_info.html')


@home_bp.route('/repuestos-info')
def repuestos_info():
    return render_template('home/repuestos_info.html')


@home_bp.route('/nosotros')
def nosotros():
    return render_template('home/nosotros.html')