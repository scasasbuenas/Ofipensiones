from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

# Crear la aplicación FastAPI
app = FastAPI()

# Logger para el sistema
logging.basicConfig(level=logging.DEBUG)

# Modelos de datos
class FacturacionResponse(BaseModel):
    reporte: dict
    timestamp: datetime

@app.post("/reporte_facturacion", response_model=FacturacionResponse)
async def generar_reporte_facturacion(email: EmailStr = Form(...), password: str = Form(...)):
    """
    Genera un reporte del proceso de facturación anual.
    """
    # Simulación de lógica
    logging.info("Generando reporte de facturación anual...")
    reporte = {"ingresos": 10000, "gastos": 5000, "balance": 5000}  # Simula datos
    return {"reporte": reporte, "timestamp": datetime.utcnow()}

@app.get("/facturas", response_model=list[FacturacionResponse])
async def obtener_facturas():
    """
    Recupera todas las facturas generadas.
    """
    # Recuperar todas las facturas desde MongoDB
    facturas = facturacion.find()  # Suponiendo que usas MongoDB
    lista_facturas = [
        {
            "reporte": {
                "ingresos": factura.get("ingresos"),
                "gastos": factura.get("gastos"),
                "balance": factura.get("balance"),
            },
            "timestamp": factura.get("timestamp"),
        }
        for factura in facturas
    ]
    return lista_facturas

from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, EmailStr
from datetime import datetime
import random
import logging


# Logger para el sistema
logging.basicConfig(level=logging.DEBUG)

# Modelos de datos
class FacturaInfo(BaseModel):
    cuanto_pague: float
    cuando_pague: str
    a_tiempo: bool

class UsuarioFacturas(BaseModel):
    usuario: str
    facturas: list[FacturaInfo]

class InstitucionFacturas(BaseModel):
    institucion: str
    usuarios: list[UsuarioFacturas]

class FacturacionResponse(BaseModel):
    instituciones: list[InstitucionFacturas]

# MongoDB
from pymongo import MongoClient

# Configuración de MongoDB
client = MongoClient("mongodb+srv://scasasbuenas:EaFOacx8sknELd1Y@cluster0.3wjlju4.mongodb.net/?retryWrites=true&w=majority")
db = client["ofipensiones"]  # Base de datos

# Crear colecciones y datos iniciales
def inicializar_base_de_datos():
    # Instituciones
    instituciones = ["Instituto Nacional", "Colegio Moderno", "Escuela Técnica"]
    usuarios_base = [
        {"email": f"usuario{i}@example.com", "password": f"password{i}23", "rol": "usuario"}
        for i in range(1, 6)
    ]

    # Inicializar usuarios
    usuarios = db["usuarios"]
    usuarios.insert_many(usuarios_base)

    # Crear facturación organizada
    facturacion = db["facturacion"]
    facturacion.delete_many({})  # Limpiar la colección antes de insertar datos nuevos
    facturas_por_institucion = []

    for institucion in instituciones:
        usuarios_facturacion = []
        for usuario in usuarios_base:
            facturas_usuario = [
                {
                    "cuanto_pague": round(random.uniform(100, 1000), 2),
                    "cuando_pague": datetime(2024, random.randint(1, 12), random.randint(1, 28)).isoformat(),
                    "a_tiempo": random.choice([True, False]),
                }
                for _ in range(5)  # Cada usuario tiene 5 facturas
            ]
            usuarios_facturacion.append({
                "usuario": usuario["email"],
                "facturas": facturas_usuario
            })
        facturas_por_institucion.append({
            "institucion": institucion,
            "usuarios": usuarios_facturacion
        })

    # Insertar facturas en la base de datos
    facturacion.insert_many(facturas_por_institucion)
    print("Base de datos inicializada correctamente con facturas organizadas por institución.")


# Endpoint para inicializar la base de datos
@app.get("/inicializar_db")
async def inicializar_db():
    """
    Inicializa la base de datos con datos iniciales.
    """
    inicializar_base_de_datos()
    return {"message": "Base de datos inicializada correctamente."}


# Endpoint para verificar facturas
@app.get("/verificar_facturas", response_model=list[InstitucionFacturas])
async def verificar_facturas():
    """
    Verifica las facturas organizadas por institución.
    """
    facturas = db["facturacion"].find({}, {"_id": 0})  # Excluir el campo "_id"
    return list(facturas)


@app.get("/porcentaje_facturas_pendientes")
async def porcentaje_facturas_pendientes():
    """
    Calcula el porcentaje de facturas pendientes (a_tiempo=False) por institución.
    """
    # Recuperar todas las instituciones y sus facturas
    instituciones = db["facturacion"].find({}, {"_id": 0, "institucion": 1, "usuarios": 1})

    resultados = []
    for institucion in instituciones:
        total_facturas = 0
        facturas_pendientes = 0

        # Iterar sobre los usuarios y sus facturas
        for usuario in institucion["usuarios"]:
            for factura in usuario["facturas"]:
                total_facturas += 1
                if not factura["a_tiempo"]:  # Si la factura no está a tiempo
                    facturas_pendientes += 1

        # Calcular el porcentaje de facturas pendientes
        porcentaje_pendientes = (facturas_pendientes / total_facturas * 100) if total_facturas > 0 else 0

        # Agregar el resultado de esta institución
        resultados.append({
            "institucion": institucion["institucion"],
            "total_facturas": total_facturas,
            "facturas_pendientes": facturas_pendientes,
            "porcentaje_pendientes": round(porcentaje_pendientes, 2)
        })

    return {"resultados": resultados}

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from reportlab.pdfgen import canvas



# Configuración de SMTP para enviar correos
SMTP_SERVER = "smtp.gmail.com"  # Servidor SMTP de Gmail
SMTP_PORT = 587
SMTP_EMAIL = "santiago.xasasbuenas@gmail.com"  # Reemplaza con tu correo
SMTP_PASSWORD = "yvwe dtts anid cpml"  # Reemplaza con la contraseña de tu correo

def generar_pdf(reporte, nombre_archivo):
    """
    Genera un archivo PDF con el contenido del reporte.
    """
    c = canvas.Canvas(nombre_archivo)
    c.drawString(100, 800, "Reporte de Facturación")
    c.drawString(100, 780, f"Fecha: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

    y = 750
    for item in reporte:
        c.drawString(100, y, f"Institución: {item['institucion']}")
        c.drawString(120, y - 20, f"Total Facturas: {item['total_facturas']}")
        c.drawString(120, y - 40, f"Facturas Pendientes: {item['facturas_pendientes']}")
        c.drawString(120, y - 60, f"Porcentaje Pendientes: {item['porcentaje_pendientes']}%")
        y -= 100

    c.save()
    #descargarlo
    print("PDF generado exitosamentsadklfbarsbfgwieoabfe.")
    return nombre_archivo



def enviar_correo(destinatario, asunto, mensaje, archivo):
    """
    Envía un correo con un archivo adjunto.
    """
    try:
        # Crear el correo
        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = destinatario
        msg["Subject"] = asunto

        # Adjuntar el mensaje
        msg.attach(MIMEBase("text", "plain"))
        msg.attach(MIMEBase("application", "octet-stream"))

        # Adjuntar el archivo PDF
        with open(archivo, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(archivo)}")
            msg.attach(part)

        # Enviar el correo
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


@app.post("/enviar_reporte")
async def enviar_reporte(email: EmailStr):
    """
    Genera un reporte en PDF y lo envía por correo.
    """
    # Obtener datos de facturación desde la base de datos
    instituciones = db["facturacion"].find({}, {"_id": 0})

    reporte = []
    for institucion in instituciones:
        total_facturas = sum(len(usuario["facturas"]) for usuario in institucion["usuarios"])
        facturas_pendientes = sum(
            sum(1 for factura in usuario["facturas"] if not factura["a_tiempo"])
            for usuario in institucion["usuarios"]
        )
        porcentaje_pendientes = (facturas_pendientes / total_facturas * 100) if total_facturas > 0 else 0

        reporte.append({
            "institucion": institucion["institucion"],
            "total_facturas": total_facturas,
            "facturas_pendientes": facturas_pendientes,
            "porcentaje_pendientes": round(porcentaje_pendientes, 2),
        })

    # Generar el archivo PDF
    nombre_archivo = "reporte_facturacion.pdf"
    generar_pdf(reporte, nombre_archivo)

    # Enviar el PDF por correo
    enviar_correo(email, "Reporte de Facturación", "Adjunto el reporte de facturación.", nombre_archivo)

    # Eliminar el archivo PDF después de enviarlo
    os.remove(nombre_archivo)

    return {"message": "Reporte enviado exitosamente al correo."}
from fastapi.responses import FileResponse
import os
@app.get("/descargar_pdf", response_class=FileResponse)
async def descargar_pdf():
    """
    Endpoint para descargar un archivo PDF generado dinámicamente.
    """
    nombre_archivo = "reporte_facturacion.pdf"
    generar_pdf(nombre_archivo)

    # Devolver el archivo PDF como respuesta
    return FileResponse(
        path=nombre_archivo,
        media_type="application/pdf",
        filename=nombre_archivo
    )
    
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI
import asyncio


@app.post("/send-email")
async def send_email():
    sender_email = "santiago.xasasbuenas@gmail.com"
    sender_password = "yvwe dtts anid cpml"
    receiver_email = "juanlozanog9@gmail.com"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Correo de prueba desde FastAPI"
    body = "Este es un correo de prueba enviado desde una aplicación FastAPI."
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return {"message": "Correo enviado exitosamente"}
    except Exception as e:
        return {"message": str(e)}