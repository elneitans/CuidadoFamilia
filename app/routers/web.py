# app/routers/web.py

import os
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from twilio.rest import Client
from sqlalchemy.orm import Session
from datetime import datetime
from dotenv import load_dotenv

# Importamos la base de datos y los modelos
from app.database import SessionLocal
from app.models import User, Medication

load_dotenv()

router = APIRouter(
    prefix="",
    tags=["web"]
)

# --- Configuración de Twilio para notificaciones
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # Ej: "whatsapp:+14155238886"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------
# Página principal
# ------------------------
@router.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
      <title>CuidadoFamilia - Home</title>
    </head>
    <body>
      <h1>Bienvenido a CuidadoFamilia</h1>
      <p>
        <a href="/signup">Registrarse</a> | 
        <a href="/medication">Agregar Medicación</a>
      </p>
    </body>
    </html>
    """

# ------------------------
# Sign Up (Registro de Usuario)
# ------------------------
@router.get("/signup", response_class=HTMLResponse)
def show_signup_form():
    return """
    <html>
    <head>
      <title>Sign Up</title>
    </head>
    <body>
      <h1>Registro de Usuario</h1>
      <form action="/signup" method="post">
        <label>Nombre:</label><br>
        <input type="text" name="name" required><br><br>
        <label>Teléfono (Formato E.164, e.g. +56912345678):</label><br>
        <input type="text" name="phone_number" required><br><br>
        <input type="submit" value="Registrarme">
      </form>
    </body>
    </html>
    """

@router.post("/signup", response_class=HTMLResponse)
def process_signup_form(
    name: str = Form(...),
    phone_number: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.phone_number == phone_number).first()
    if existing_user:
        return f"""
        <html>
        <body>
          <h2>El número {phone_number} ya está registrado.</h2>
          <a href="/signup">Volver</a>
        </body>
        </html>
        """
    # Crear usuario
    new_user = User(name=name, phone_number=phone_number)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Enviar mensaje de bienvenida vía Twilio
    try:
        message = client.messages.create(
            body=f"Hola {name}, ¡bienvenido a CuidadoFamilia!",
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{phone_number}"
        )
    except Exception as e:
        return f"""
        <html>
        <body>
          <h2>Usuario creado, pero no se pudo enviar mensaje a {phone_number}. Error: {e}</h2>
          <a href="/">Volver al inicio</a>
        </body>
        </html>
        """
    return f"""
    <html>
    <body>
      <h2>¡Usuario creado exitosamente!</h2>
      <p>ID: {new_user.id}</p>
      <p>Nombre: {new_user.name}</p>
      <p>Teléfono: {new_user.phone_number}</p>
      <p>Twilio SID: {message.sid}</p>
      <br>
      <a href="/">Volver al inicio</a>
    </body>
    </html>
    """

# ------------------------
# Formulario para la rutina de medicación
# ------------------------
@router.get("/medication", response_class=HTMLResponse)
def show_medication_form():
    return """
    <html>
    <head>
      <title>Agregar Medicación</title>
    </head>
    <body>
      <h1>Agregar Medicación</h1>
      <form action="/medication" method="post">
        <label>Nombre del Medicamento:</label><br>
        <input type="text" name="name" required><br><br>
        <label>Horarios (ejemplo: 08:00,12:00,20:00):</label><br>
        <input type="text" name="schedule" required><br><br>
        <label>Fecha de Inicio (YYYY-MM-DD HH:MM):</label><br>
        <input type="text" name="start_date" required><br><br>
        <label>Fecha de Fin (opcional, YYYY-MM-DD HH:MM):</label><br>
        <input type="text" name="end_date"><br><br>
        <label>Dosis (ejemplo: 500 mg):</label><br>
        <input type="text" name="dosage"><br><br>
        <label>Frecuencia (ejemplo: diaria, cada 8 horas):</label><br>
        <input type="text" name="frequency"><br><br>
        <input type="submit" value="Guardar Medicación">
      </form>
    </body>
    </html>
    """

@router.post("/medication", response_class=HTMLResponse)
def process_medication_form(
    name: str = Form(...),
    schedule: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(None),
    dosage: str = Form(None),
    frequency: str = Form(None),
    db: Session = Depends(get_db)
):
    # Para simplificar, asumimos que el usuario ya está identificado; usamos un usuario fijo (por ejemplo, id 1)
    user_id = 1
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Formato de fecha de inicio inválido")
    end_dt = None
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Formato de fecha de fin inválido")
    # Se puede calcular next_dose_time en el scheduler; aquí lo dejamos en None
    next_dose_time = None

    new_medication = Medication(
        name=name,
        schedule=schedule,
        start_date=start_dt,
        end_date=end_dt,
        dosage=dosage,
        frequency=frequency,
        next_dose_time=next_dose_time,
        user_id=user_id
    )
    db.add(new_medication)
    db.commit()
    db.refresh(new_medication)
    return f"""
    <html>
    <body>
      <h2>Medicación agregada exitosamente!</h2>
      <p>ID: {new_medication.id}</p>
      <p>Nombre: {new_medication.name}</p>
      <p>Horarios: {new_medication.schedule}</p>
      <p>Fecha de Inicio: {new_medication.start_date}</p>
      <p>Fecha de Fin: {new_medication.end_date if new_medication.end_date else 'No especificado'}</p>
      <p>Dosis: {new_medication.dosage if new_medication.dosage else 'No especificado'}</p>
      <p>Frecuencia: {new_medication.frequency if new_medication.frequency else 'No especificado'}</p>
      <br>
      <a href="/">Volver al inicio</a>
    </body>
    </html>
    """
