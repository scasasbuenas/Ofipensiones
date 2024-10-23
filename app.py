from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
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

# Autenticación de usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.find_one({'email': email})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = str(user['_id'])
            secret_response = request.form['g-recaptcha-response']
            
            verify_respose = requests.post(url=f'{VERIFY_URL}?secret={SECRET_KEY}&response={secret_response}').json()
            
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales inválidas. Intente nuevamente.', 'error')  # Etiqueta el mensaje como 'error'
            
    return render_template('login.html', site_key = SITE_KEY)

# Dashboard después del login
@app.route('/dashboard')
def dashboard():
    return 'Bienvenido al Dashboard'

if __name__ == '__main__':
    app.run(debug=True)
