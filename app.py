from flask import Flask, render_template, jsonify, request, redirect, flash, url_for
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Float
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
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

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.Integer, nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    usuario = db.Column(db.String(80), nullable=False, unique=True)
    contrasena = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()



@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        cedula = request.form.get('cedula')

        cedula_user = db.session.execute(db.select(User).where(User.cedula == cedula)).scalar()
        usuario = db.session.execute(db.select(User).where(User.usuario == usuario)).scalar()

        if not cedula_user:
            flash("Cedula no existente, por favor intentar de nuevo")
            return redirect(url_for('login'))  
        elif not usuario:
            flash("Nombre de Usuario no existe, por favor intentar de nuevo")
        elif not check_password_hash(usuario.contrasena, contrasena):
            flash("Contrasenaña no es correcta, por favor intentar de nuevo")
        else:
            login_user(usuario)
            return redirect(url_for('index'))
        
    return render_template("login.html")

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        usuario_ = request.form.get('usuario')
        cedula_ = request.form.get('cedula')
        email_ = request.form.get('email')
        contrasena = request.form.get('contrasena')

        usuario = db.session.execute(db.select(User).where(User.usuario == usuario)).scalar()

        if usuario:
            flash("Usuario ya existente")
            redirect(url_for('login'))
        
        hashed_password = generate_password_hash(contrasena, method="pbkdf2:sha256", salt_length=8)


        nuevo_usuario = User(
            usuario = usuario_,
            cedula = cedula_,
            email = email_,
            contrasena = hashed_password,
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        login_user(nuevo_usuario)
        return redirect(url_for('login'))
    return render_template("registrar.html")


@app.route("/index")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)