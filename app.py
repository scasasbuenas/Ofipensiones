from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from pymongo import MongoClient
import bcrypt
import requests

# Configuración inicial google RECAPTCHA
SITE_KEY = '6Ld002cqAAAAAMTiK-Bt_DW8cXW5SP5pYbCyLmzS'
SECRET_KEY = '6Ld002cqAAAAAKafoKBCiLmtSXfIqUxqllXeIgLD'
VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

# Configuración inicial de Flask y MongoDB
app = Flask(__name__)
app.secret_key = 'holabuenosdias'  # Necesaria para manejar sesiones en Flask
client = MongoClient('mongodb+srv://scasasbuenas:EaFOacx8sknELd1Y@cluster0.3wjlju4.mongodb.net/')
db = client['ofipensiones']
users = db.users

# Bloquea el acceso a las rutas que requieran login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_json):
        self.id = str(user_json['_id'])
        self.email = user_json['email']

# Cargar usuario por ID
@login_manager.user_loader
def load_user(user_id):
    user = users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return None
    return User(user)


# Pagina principal
@app.route('/')
def home():
    return render_template('home.html')


# Registro de usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email',False)
        password = request.form.get('password', False)
        
        # Verificar si el correo ya existe
        if users.find_one({'email': email}):
            flash('El correo ya está registrado.')
            return redirect(url_for('register'))
        
        # Hash de la contraseña antes de almacenarla
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users.insert_one({'email': email, 'password': hashed_password})
        
        flash('Usuario registrado exitosamente!')
        return redirect(url_for('login'))
    return render_template('register.html')

from bson.objectid import ObjectId


# Autenticación de usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.find_one({'email': email})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            user_obj = User(user)
            login_user(user_obj)  # Flask-Login gestiona la sesión
            
            secret_response = request.form['g-recaptcha-response']
            verify_response = requests.post(url=f'{VERIFY_URL}?secret={SECRET_KEY}&response={secret_response}').json()
            
            if verify_response.get('success'):
                return redirect(url_for('dashboard'))
            else:
                flash('Error de reCAPTCHA. Por favor, inténtelo de nuevo.')
        
        flash('Credenciales inválidas. Intente nuevamente.', 'error')
    
    return render_template('login.html', site_key=SITE_KEY)


# Dashboard después del login
@app.route('/dashboard')
@login_required
def dashboard():
    user = load_user(current_user.get_id())  # Carga la información del usuario actual
    return render_template('dashboard.html', email=user.email)


# Cerrar sesión
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

