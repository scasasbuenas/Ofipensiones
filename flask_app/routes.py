from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user
from pymongo import MongoClient
import bcrypt

# Configuración inicial
app = Flask(__name__)
app.secret_key = 'flask_secret'
client = MongoClient('mongodb://localhost:27017/')
db = client['ofipensiones']
users = db.users

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_json):
        self.id = str(user_json['_id'])
        self.email = user_json['email']

@login_manager.user_loader
def load_user(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    return User(user) if user else None

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = users.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            login_user(User(user))
            return redirect(url_for("dashboard"))
        flash("Credenciales inválidas")
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    return "Bienvenido al Dashboard"
