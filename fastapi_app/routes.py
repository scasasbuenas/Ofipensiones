from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from datetime import datetime
import bcrypt

app = FastAPI()
client = MongoClient('mongodb://localhost:27017/')
db = client['ofipensiones']
facturacion = db.facturacion
users = db.users

class FacturacionResponse(BaseModel):
    reporte: dict
    timestamp: datetime

@app.post("/reporte_facturacion", response_model=FacturacionResponse)
async def generar_reporte_facturacion(email: EmailStr = Form(...), password: str = Form(...)):
    user = users.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    reporte = facturacion.find_one({"tipo": "anual"})
    if not reporte:
        raise HTTPException(status_code=404, detail="No se encontraron datos de facturación anual")

    return {
        "reporte": reporte,
        "timestamp": datetime.utcnow()
    }
