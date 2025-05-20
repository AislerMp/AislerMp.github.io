# app/routes/main.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app import db
from app.models import Factura, Limite, Listas, Resultados, login_required, current_user, admin_only
from app.controllers.main_controller import indexRoute, registroRoute, facturaGanadora_Route, registrarNumeroGanador_Route, ver_factura_Route, pagarFactura_Route, ActualizarValidaciones_Route
main_bp = Blueprint('main', __name__)


@main_bp.route("/index")
@login_required
def index():
    result = indexRoute()
    facturas, limiteMax, limite_Reventado, sorteos = result
    print(current_user.Usuario)
    return render_template("index.html", sorteos=sorteos, limiteMax=limiteMax, limite_Reventado=limite_Reventado, facturas=facturas)

@main_bp.route("/registrar_tiempo", methods=["POST"])
@login_required
def registrar_tiempo():
    usuario = current_user.Usuario
    fecha = datetime.strptime(request.form.get('fecha'), "%Y-%m-%d").date()
    sorteo_id, sorteo_hora_Cierre = request.form.get('sorteo').split(",")

    numero = request.form.getlist('numero[]')
    montos = request.form.getlist('monto[]')
    reventados = request.form.getlist('reventado_monto[]')

    result = registroRoute(usuario, fecha, sorteo_id, sorteo_hora_Cierre, numero, montos, reventados)
    
    if result[0] == -1:
        flash(result[1])
        return redirect(url_for('main.index'))

    if result[0] == 1:
        flash(result[1])
        return redirect(url_for('main.ver_factura', factura_id=result[2]))

@main_bp.route("/factura/<int:factura_id>")
@login_required
def ver_factura(factura_id):
    result = ver_factura_Route(factura_id)
    if result[0] == -1:
        flash(result[1])
        return redirect(url_for('main.index'))

    return render_template("factura.html", factura=result[1])

@main_bp.route("/FacturaGanadora", methods=["POST", "GET"])
@login_required
def facturaGanadora():
    if request.method == "POST":
        idFactura = request.form.get('idFactura')
        result = facturaGanadora_Route(idFactura, current_user.Usuario)
        
        if result[0] == -1:
            flash(result[1])
            return redirect(url_for('main.facturaGanadora'))

        return render_template('pagarNumero.html', factura=result[1], ganador=result[2], pagoxNumero=result[3], pagoxReventado=result[4])
    return render_template('pagarNumero.html')

@main_bp.route("/pagarFactura/<int:idFactura>", methods=["POST", "GET"])
@login_required
def pagarFactura(idFactura):
    result = pagarFactura_Route(idFactura)
    if result[0] == -1:
        flash(result[1])
        return redirect(url_for('main.index'))
    flash(result[1])
    return redirect(url_for('main.facturaGanadora'))
    
@main_bp.route("/registrarNumeroGanador", methods=["POST", "GET"])
@login_required
@admin_only
def registrarNumeroGanador():
    sorteos = Listas.allSorteos()
    if request.method == "POST":
        fecha = datetime.strptime(request.form.get('fecha'), "%Y-%m-%d").date()
        sorteo_id, sorteo_hora_Cierre = request.form.get('sorteo').split(",")
        numero_ganador = request.form.get('numeroGanador')
        is_reventado = True if request.form.get('hiddenBoolean') == "True" else False
        
        result = registrarNumeroGanador_Route(fecha, sorteo_id, numero_ganador, is_reventado)
        if result[0] == -1:
            flash(result[1])
            return redirect(url_for('main.registrarNumeroGanador'))
        
        if result[0] == 1:
            flash(result[1])
            return redirect(url_for('main.index'))
        
        return redirect(url_for('main.index'))
    return render_template('agregarNumeroGanador.html', sorteos=sorteos)

@main_bp.route("/ActualizarValidaciones", methods=["POST", "GET"])
@login_required
@admin_only
def ActualizarValidaciones():
    try:
        sorteos = Listas.allSorteos()
        limiteMax, limiteReventadoMax, pagoxNumero, pagoxReventado = Limite.getMonto_Limite(), Limite.getMonto_Limite_Reventado(), Limite.getPagoxNumero(), Limite.getPagoxReventado()
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}")
        return redirect(url_for('main.index'))
    
    if request.method == "POST":
        limiteMax = request.form.get('limiteMax')
        limiteReventadoMax = request.form.get('limiteReventadoMax')
        pagoxNumero = request.form.get('pagoxNumero')
        pagoxReventado = request.form.get('pagoxReventado')

        result = ActualizarValidaciones_Route(limiteMax, limiteReventadoMax, pagoxNumero, pagoxReventado)
        if result[0] == -1:
            flash(result[1])
            return redirect(url_for('main.index'))
        
        if result[0] == 1:
            flash(result[1])
            return redirect(url_for('main.index'))
        
        return redirect(url_for('main.ActualizarValidaciones'))
    return render_template("updateValidations.html", sorteos=sorteos, limiteMax=limiteMax, limiteReventadoMax=limiteReventadoMax, pagoxNumero=pagoxNumero, pagoxReventado=pagoxReventado)