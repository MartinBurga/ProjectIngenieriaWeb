from models.usuario import Usuario
from flask import Blueprint, request, render_template, redirect, session, url_for
from utils.db import db

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form.get('username')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(nombre=username, password=password).first()

        if usuario and usuario.password == password:
            session['user_id'] = (usuario.id)
            return redirect(url_for('index'))
        else:
            return 'Credenciales inválidas. Inténtalo de nuevo.', 401

    return render_template("login.html")