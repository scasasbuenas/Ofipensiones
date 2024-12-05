from fastapi_app.app import app

# Listar rutas registradas
@app.get("/routes")
async def list_routes():
    return [{"path": route.path, "methods": route.methods} for route in app.routes]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
