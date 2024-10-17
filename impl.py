import pymongo
from pymongo import MongoClient
import bcrypt
import csv
from faker import Faker

# Este script genera un csv con usuarios y contraseñas aleatorias, y los almacena en una base de datos MongoDB.

# Configuración de la conexión a MongoDB
client = MongoClient('mongodb+srv://scasasbuenas:EaFOacx8sknELd1Y@cluster0.3wjlju4.mongodb.net/')
db = client['ofipensiones']
users = db.users

# Función para registrar usuarios
def register_user(email, password):
    if users.find_one({"email": email}):
        return False
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users.insert_one({"email": email, "password": hashed_password})
    return True

# Función para autenticar usuarios
def authenticate_user(email, password):
    user = users.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return True
    else:
        return False

# Generar datos de usuario y guardar en CSV
def generate_users(num_users):
    fake = Faker()
    with open('users.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['email', 'password', 'registered_in_db'])
        
        for _ in range(num_users):
            email = fake.email()
            password = fake.password()
            # Aleatoriamente decidir si el usuario está registrado en DB
            registered_in_db = fake.boolean(chance_of_getting_true=80)  # 80% de chance de estar registrado
            
            if registered_in_db:
                register_user(email, password)
            writer.writerow([email, password, registered_in_db])

# Ejemplo de uso
if __name__ == "__main__":
    generate_users(2000)  # Genera 2000 usuarios y los añade al archivo CSV
    print("Usuarios generados y almacenados.")

    # Registro y autenticación de ejemplo
    if register_user("user@example.com", "securepassword123"):
        print("Usuario registrado con éxito.")
    else:
        print("El usuario ya está registrado.")
    
    if authenticate_user("user@example.com", "securepassword123"):
        print("Autenticación exitosa.")
    else:
        print("Error de autenticación.")
