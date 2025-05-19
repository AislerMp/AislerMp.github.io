# app/routes/auth.py
from flask import Blueprint, render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_user, logout_user
from app import db
from app.controllers.auth_controller import login_route, registro_route

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        usuario_obj = login_route(usuario, contrasena)

        if usuario_obj[0] == -1:
            flash(usuario_obj[1])
            return redirect(request.referrer)
        
        if usuario_obj[0] == -2:
            return jsonify(error={"Lo siento" : f"Ha habido un error: {usuario_obj[1]}"})
        
        if usuario_obj[0] == 1:
            login_user(usuario_obj[1])
            
        return redirect(url_for('main.index'))
    return render_template("login.html")

@auth_bp.route("/cerrar_sesion")
def cerrar_sesion():
    logout_user()
    return redirect(url_for("auth.login"))

@auth_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        
        result = registro_route(usuario, contrasena)
        if result[0] == -1:
            flash(result[1])
            return redirect(url_for('auth.registrar'))

        if result[0] == 1:
            login_user(result[1])
        
        if result[0] == -2:
            flash(f"Error: {result[1]}")
            return redirect(request.referrer)
        
        return redirect(url_for('main.index'))

    return render_template("registrar.html")
