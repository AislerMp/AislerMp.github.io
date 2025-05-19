# app/models.py
from app import db, login_manager
from flask_login import UserMixin, login_required, current_user
from datetime import datetime
from functools import wraps
import json
from flask import abort

def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    return wrapper

class Usuario(UserMixin, db.Model):
    __tablename__ = 'Usuario'
    idUsuario = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    Usuario = db.Column(db.String(100), unique=True, nullable=False)
    Contrasena = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    facturas = db.relationship('Factura', backref='usuario', lazy=True)

    @property
    def id(self):
        return self.idUsuario

class Listas(db.Model):
    __tablename__ = 'Listas'
    idLista = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Hora_Cierre = db.Column(db.Time, nullable=False)

    facturas = db.relationship('Factura', backref='lista', lazy=True)
    resultados = db.relationship('Resultados', backref='lista', lazy=True)

    def allSorteos():
        sorteos = db.session.execute(db.select(Listas)).scalars().all()
        return sorteos

class Factura(db.Model):
    __tablename__ = 'Factura'
    idFactura = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    Usuario = db.Column(db.String(100), db.ForeignKey('Usuario.Usuario'), nullable=False)
    idLista = db.Column(db.Integer, db.ForeignKey('Listas.idLista'), nullable=False)
    Fecha_Actual = db.Column(db.DateTime, nullable=False, default=datetime.now())
    Fecha_Vendida = db.Column(db.Date, nullable=False)
    Numeros = db.Column(db.JSON, nullable=False)
    Monto = db.Column(db.Numeric(10,2), nullable=False)
    is_paid = db.Column(db.Boolean, nullable=False, default=False)

    def allFacturas():
        facturas = db.session.execute(db.select(Factura)).scalars().all()
        return facturas

    def getID(self):
        return self.idFactura
    
    def to_dict(self):
        return {
            "idFactura": self.idFactura,
            "Usuario": self.Usuario,
            "idLista": self.idLista,
            "Fecha_Actual": self.Fecha_Actual.strftime("%Y-%m-%d %H:%M:%S"),
            "Fecha_Vendida": self.Fecha_Vendida.strftime("%Y-%m-%d"),
            "Numeros": json.loads(self.Numeros),
            "Monto": self.Monto,
            "is_paid" : self.is_paid
        }

class Resultados(db.Model):
    __tablename__ = 'Resultados'
    idResultados = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    idLista = db.Column(db.Integer, db.ForeignKey('Listas.idLista'), nullable=False)
    Fecha = db.Column(db.Date, nullable=False)
    Numero_Ganador = db.Column(db.Integer, nullable=False)
    Reventado = db.Column(db.Boolean, nullable=False, default=False)

    @staticmethod
    def getAllResultados():
        resultados = db.session.execute(db.select(Resultados)).scalars().all()
        return resultados
    

class Limite(db.Model):
    __tablename__ = 'Limite'
    idLimite = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    Monto_Limite = db.Column(db.Integer, nullable=False)
    Monto_Limite_Reventado = db.Column(db.Integer, nullable=False)
    PagoxNumero = db.Column(db.Integer, nullable=False)
    PagoxReventado = db.Column(db.Integer, nullable=False)

    @staticmethod
    def getMonto_Limite():
        limite = db.session.execute(db.select(Limite)).scalar()
        return limite.Monto_Limite if limite else 0
    
    @staticmethod
    def getMonto_Limite_Reventado():
        limite = db.session.execute(db.select(Limite)).scalar()
        return limite.Monto_Limite_Reventado if limite else 0
    
    @staticmethod
    def getPagoxNumero():
        limite = db.session.execute(db.select(Limite)).scalar()
        return limite.PagoxNumero if limite else 0
    
    @staticmethod
    def getPagoxReventado():
        limite = db.session.execute(db.select(Limite)).scalar()
        return limite.PagoxReventado if limite else 0

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))
