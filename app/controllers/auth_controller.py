from app.models import Factura, Listas, Usuario, Resultados, Limite
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from collections import defaultdict

def login_route(usuario, contrasena):
    try:
        usuario_obj = db.session.execute(db.select(Usuario).where(Usuario.Usuario == usuario)).scalar()
    except Exception as e:
        return (-2, e)
    else:
        if not usuario_obj or not check_password_hash(usuario_obj.Contrasena, contrasena):
            msj = "Usuario o contraseña incorrectos."
            return (-1, msj)
    return (1, usuario_obj)

def registro_route(usuario, contrasena):
    if db.session.execute(db.select(Usuario).where(Usuario.Usuario == usuario)).scalar():
        msj = "Usuario ya existente"
        return (-1, msj)
    
    hashed_password = generate_password_hash(contrasena, method="pbkdf2:sha256", salt_length=8)

    try:
        nuevo_usuario = Usuario(Usuario=usuario, Contrasena=hashed_password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return (1, nuevo_usuario)
    except Exception as e:
        db.session.rollback()
        return (-2, e)