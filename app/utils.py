# app/utils.py
import json
from app.models import Factura, Listas
from app import db
from collections import defaultdict
from sqlalchemy import text

def consultar_facturas(sorteo_id, fecha):
    #Sumar todos los montos y los reventados de todos los numeros y los repetidos 
    # Paso 1: Obtener datos existentes con bloqueo (evita race condition)
    facturas = db.session.query(Factura.Numeros).filter_by(
        idLista=sorteo_id,
        Fecha_Vendida=fecha
    ).with_for_update().all()

    montos_existentes = {}
    reventados_existentes = {}

    for row in facturas:
        try:
            lista = json.loads(row.Numeros)
        except Exception:
            continue
        for item in lista:
            num = item["numero"]
            monto = item.get("monto", 0)
            rev = item.get("reventado", 0)
            montos_existentes[num] = montos_existentes.get(num, 0) + monto
            reventados_existentes[num] = reventados_existentes.get(num, 0) + rev
                
    return montos_existentes, reventados_existentes

def agregar_credenciales_fact(factura):
    lista_obj = db.session.execute(db.select(Listas).where(Listas.idLista == factura["idLista"])).scalar()
    
    # Obtener el nombre del sorteo y la fecha de cierre en una sola variable
    sorteo_nombre = ' '.join([lista_obj.Nombre, lista_obj.Hora_Cierre.strftime("%H:%M"), "PM"])

    numeros_por_monto = defaultdict(list)
    for numero in factura["Numeros"]:
        monto = numero["monto"]
        num = numero["numero"]
        numeros_por_monto[monto].append(num)

    numeros_por_reventado = defaultdict(list)
    for numero in factura["Numeros"]:
        reventado = numero["reventado"]
        num = numero["numero"]
        if reventado != '0':
            numeros_por_reventado[reventado].append(num)
        

    print(dict(numeros_por_reventado))
    # Convertir a dict normal (por si lo necesitas en el template)
    factura["ResumenAgrupado"] = dict(numeros_por_monto)
    factura["ResumenReventado"] = dict(numeros_por_reventado)
    factura["sorteo_nombre"] = sorteo_nombre

    return factura