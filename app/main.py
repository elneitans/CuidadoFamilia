# app/main.py

import os
from fastapi import FastAPI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="CuidadoFamilia - IA + SignUp y Notificaciones")

# Importar routers existentes (DeepSeek, Web, etc.)
from app.routers import deepseek, web

app.include_router(deepseek.router)
app.include_router(web.router)

# Importar el scheduler
from app.scheduler import start_scheduler
from app.database import init_db

@app.on_event("startup")
def on_startup():
    # Crear las tablas en la base de datos (si no existen)
    init_db()
    # Iniciar el scheduler para notificaciones de medicación
    start_scheduler()

@app.get("/", include_in_schema=False)
def root():
    return {"msg": "Bienvenido a CuidadoFamilia. Visita / para ver la página principal."}