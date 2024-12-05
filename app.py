from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from pymongo import MongoClient
import bcrypt
import requests
import smtplib
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

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
            
            if verify_response.get('success') == False:
                send_confirmation_code(email)
                return redirect(url_for('confirm_code'))
            else:
                flash('Error de reCAPTCHA. Por favor, inténtelo de nuevo.')
        
        flash('Credenciales inválidas. Intente nuevamente.', 'error')
    
    return render_template('login.html', site_key=SITE_KEY)


# Confirmación de código de autenticación
@app.route('/confirm_code', methods=['GET', 'POST'])
def confirm_code():
    if request.method == 'POST':
        code = request.form['confirmation_code']
        if code == session.get('confirmation_code'):
            session['confirmation_code_validated'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('No logramos autenticar tu identidad. Intenta nuevamente.', 'error')
            return redirect(url_for('login'))
    else:
        if 'confirmation_code_validated' in session and session['confirmation_code_validated']:
            return redirect(url_for('dashboard'))
        flash('Debe confirmar su código antes de acceder al dashboard.', 'error')
    return render_template('confirm_code.html')


# Generar y enviar código de confirmación
def send_confirmation_code(email):
    code = str(random.randint(100000, 999999))
    session['confirmation_code'] = code
    logging.debug(f'Generated confirmation code: {code} for email: {email}')
    try:
        # Configurar el servidor SMTP y enviar el correo
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('santiago.xasasbuenas@gmail.com', 'yvwe dtts anid cpml')  # Replace 'yvwe dtts anid cpml' with the generated App Password
        
        # Construir el mensaje de correo electrónico
        msg = MIMEMultipart('alternative')
        msg['From'] = 'santiago.xasasbuenas@gmail.com'
        msg['To'] = email
        msg['Subject'] = 'Código de Confirmación'
        
        text = f'Su código de confirmación es: {code}'
        html = f'<p>Su código de confirmación es: <strong>{code}</strong></p>'
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        server.sendmail('santiago.xasasbuenas@gmail.com', email, msg.as_string())
        server.quit()
        logging.debug('Email sent successfully')
    except Exception as e:
        logging.error(f'Failed to send email: {e}')


# Dashboard después del login
@app.route('/dashboard')
@login_required
def dashboard():
    if 'confirmation_code_validated' not in session or not session['confirmation_code_validated']:
        flash('Debe confirmar su código antes de acceder al dashboard.', 'error')
        return redirect(url_for('confirm_code'))
    
    user = load_user(current_user.get_id())  # Carga la información del usuario actual
    return render_template('dashboard.html', email=user.email)


# Cerrar sesión
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

