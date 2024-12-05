from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from flask_app.app import app as flask_app  # Asegúrate de que Flask está correctamente importado
from fastapi_app.app import app as fastapi_app  # Asegúrate de que FastAPI está correctamente importado

# Crear la instancia principal de FastAPI
app = FastAPI()

# Montar Flask en /flask
app.mount("/flask", WSGIMiddleware(flask_app))

# Montar FastAPI en /fastapi
app.mount("/fastapi", fastapi_app)

# Endpoint raíz para pruebas
@app.get("/")
async def root():
    return {"message": "Hello, Flask + FastAPI Integration"}

# Endpoint para listar rutas
@app.get("/routes")
async def list_routes():
    return [{"path": route.path, "name": route.name} for route in app.routes]
