# app/routes/main.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from datetime import datetime
from app import db
from app.models import Factura, Limite, Listas, Resultados
from app.utils import consultar_facturas, agregar_credenciales_fact
from app.controllers.main_controller import indexRoute, registroRoute, facturaGanadora_Route, registrarNumeroGanador_Route

main_bp = Blueprint('main', __name__)

@main_bp.route("/index")
def index():
    result = indexRoute()
    facturas, limiteMax, limite_Reventado, sorteos = result
    
    return render_template("index.html", sorteos=sorteos, limiteMax=limiteMax, limite_Reventado=limite_Reventado, facturas=facturas)

@main_bp.route("/registrar_tiempo", methods=["POST"])
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
def ver_factura(factura_id):
    factura_obj = db.get_or_404(Factura, factura_id)
    factura_dicc = factura_obj.to_dict()

    factura = agregar_credenciales_fact(factura_dicc)

    return render_template("factura.html", factura=factura)

@main_bp.route("/FacturaGanadora", methods=["POST", "GET"])
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
def pagarFactura(idFactura):
    try:
        factura_obj = Factura.query.filter_by(idFactura=idFactura).first()
        factura_obj.is_paid = True
        db.session.commit()
        flash("Factura pagada correctamente.")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al pagar la factura: {e}")
    finally:
        db.session.close()
        return render_template('pagarNumero.html')
    
@main_bp.route("/registrarNumeroGanador", methods=["POST", "GET"])
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