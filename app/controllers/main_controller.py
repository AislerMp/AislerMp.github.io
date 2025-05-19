from app.models import Factura, Listas, Usuario, Resultados, Limite
from app import db
from datetime import datetime
from app.utils import consultar_facturas, agregar_credenciales_fact
from collections import defaultdict
import json

def indexRoute():
    facturas = Factura.allFacturas()
    facturas = [f.to_dict() for f in facturas]
    limiteMax = Limite.getMonto_Limite()
    limite_Reventado = Limite.getMonto_Limite_Reventado()
    sorteos = Listas.allSorteos()

    objs = (facturas, limiteMax, limite_Reventado, sorteos)
    return objs

def registroRoute(usuario, fecha, sorteo_id, sorteo_hora_Cierre, numero, montos, reventados):
    limiteMax = Limite.getMonto_Limite()
    limiteReventado = Limite.getMonto_Limite_Reventado()

    sorteo_hora_Cierre = datetime.strptime(sorteo_hora_Cierre.strip(), "%H:%M:%S").time()
    ahora = datetime.now()

    numeros = [{"numero": int(num), "monto": int(monto), "reventado": int(reventado)} for num, monto, reventado in zip(numero, montos, reventados)]
    total = round(sum(float(m) for m in montos), 2)
    total += round(sum(float(m) for m in reventados), 2)

    if datetime.combine(fecha, sorteo_hora_Cierre) <= ahora:
        msj = ("La hora de cierre ya pasó.")
        return (-1, msj)
    
    montos_existentes, reventados_existentes = consultar_facturas(sorteo_id, fecha)
    
    # Paso 2: Sumar montos del input (pueden repetirse)
    montos_nuevos = {}
    reventados_nuevos = {}
    for item in numeros:
        num = item["numero"]
        monto = item["monto"]
        rev = item["reventado"]
        montos_nuevos[num] = montos_nuevos.get(num, 0) + monto
        reventados_nuevos[num] = reventados_nuevos.get(num, 0) + rev

    # Paso 3: Validar por cada número si supera el límite
    for num in montos_nuevos.keys():
        monto_total = montos_existentes.get(num, 0) + montos_nuevos[num]
        rev_total = reventados_existentes.get(num, 0) + reventados_nuevos[num]

        if monto_total > limiteMax:
            return (-1, f"El número {num} excede el límite normal. Límite: ₡{limiteMax}, actual: ₡{monto_total}")
        if rev_total > limiteReventado:
            return (-1, f"El número {num} excede el límite reventado. Límite: ₡{limiteReventado}, actual: ₡{rev_total}")

    try:
        factura = Factura(
            Usuario=usuario,
            idLista=sorteo_id,
            Fecha_Vendida=fecha,
            Numeros=json.dumps(numeros),
            Monto=total
        )
        db.session.add(factura)
        db.session.commit()
        msj = ("Compra registrada correctamente.")
    except Exception as e:
        db.session.rollback()
        msj = (f"Error: {e}")
        return (-1, msj)
    finally:
        idFactura = factura.getID()
        db.session.close()
        return(1, msj, idFactura)

def ver_factura_Route(factura_id):
    try:
        factura_obj = db.get_or_404(Factura, factura_id)
        factura_dicc = factura_obj.to_dict()
    except Exception as e:
        db.session.rollback()
        msj = (f"Error: {e}")
        return (-1, msj)
    
    factura = agregar_credenciales_fact(factura_dicc)
    return (1, factura)

def facturaGanadora_Route(idFactura, usuario):
    try:
        factura_obj = Factura.query.filter_by(idFactura=idFactura, Usuario=usuario).first()
        pagoxNumero, pagoxReventado = Limite.getPagoxNumero(), Limite.getPagoxReventado()
    except Exception as e:
        db.session.rollback()
        msj = (f"Error: {e}")
        return (-1, msj)
    
    if not factura_obj:
        msj = "Lo siento no se ha encontrado ninguna factura"
        return (-1, msj)
    
    factura_dicc = factura_obj.to_dict()

    ganador = Resultados.query.filter_by(idLista=factura_dicc['idLista'], Fecha=factura_dicc['Fecha_Vendida']).first()
    if not ganador:
        ganador = ''

    factura = agregar_credenciales_fact(factura_dicc)
    return (1, factura, ganador, pagoxNumero, pagoxReventado)

def pagarFactura_Route(idFactura):
    try:
        factura_obj = Factura.query.filter_by(idFactura=idFactura).first()
        factura_obj.is_paid = True
        db.session.commit()
        msj = "Factura pagada correctamente."
    except Exception as e:
        db.session.rollback()
        msj = f"Error al pagar la factura: {e}"
        return (-1, msj)
    finally:
        db.session.close()
        return (1, msj)
    
def registrarNumeroGanador_Route(fecha, sorteo_id, numero_ganador, is_reventado):
    resultado = Resultados.query.filter_by(idLista=sorteo_id, Fecha=fecha).first()
    if resultado:
        msj = "Ya existe un número ganador registrado para esta fecha y sorteo."
        return (-1, msj)
    try:
        sorteo_id = int(sorteo_id)
        numero_ganador = int(numero_ganador)
        is_reventado = bool(is_reventado)
    except ValueError as e:
        return (-1, f"Error al convertir los datos: {e}")

    try:
        resultado = Resultados(
            idLista=sorteo_id,
            Fecha=fecha,
            Numero_Ganador=numero_ganador,
            Reventado=is_reventado
        )
        db.session.add(resultado)
        db.session.commit()
        msj = "Número ganador registrado correctamente."
    except Exception as e:
        db.session.rollback()
        msj = f"Error al registrar el número ganador: {e}"
        return (-1, msj)
    finally:
        db.session.close()
        return (1, msj)
    
def ActualizarValidaciones_Route(limiteMax, limiteReventadoMax, pagoxNumero, pagoxReventado):
    try:
        limite = Limite.query.first()
        if not limite:
            msj = "No se encontró el límite en la base de datos."
            return (-1, msj)
        
        limite.Monto_Limite = limiteMax
        limite.Monto_Limite_Reventado = limiteReventadoMax
        limite.PagoxNumero = pagoxNumero
        limite.PagoxReventado = pagoxReventado

        db.session.commit()
        msj = "Validaciones actualizadas correctamente."
    except Exception as e:
        db.session.rollback()
        msj = f"Error al actualizar las validaciones: {e}"
        return (-1, msj)
    finally:
        db.session.close()
        return (1, msj)