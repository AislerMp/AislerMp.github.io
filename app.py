from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY_FLASK")

db_url = os.getenv("DATABASE_URL")

if db_url is None:
    raise ValueError("ERROR: La variable de entorno DATABASE_URL no está definida")

app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace("mysql://", "mysql+pymysql://")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Definir una tabla de ejemplo
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)

# Crear la base de datos en Railway (si no existe)
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/usuarios")
def obtener_usuarios():
    usuarios = User.query.all()  # Obtiene todos los usuarios
    lista_usuarios = [{"id": u.id, "nombre": u.nombre} for u in usuarios]  # Convierte los objetos en diccionarios
    return jsonify(lista_usuarios)  # Devuelve los usuarios en formato JSON

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)