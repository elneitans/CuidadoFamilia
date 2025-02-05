# app/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import os
from twilio.rest import Client
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models import Medication

# Cargar variables de entorno
load_dotenv()

# Configuración de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # Ejemplo: "whatsapp:+14155238886"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Mapeo de frecuencias a intervalos de tiempo (ajusta según tus requerimientos)
FREQUENCY_MAP = {
    "diaria": timedelta(days=1),
    "cada 8 horas": timedelta(hours=8)
}

def check_medication_notifications():
    """Revisa la tabla 'medications' para detectar dosis pendientes y envía notificaciones vía WhatsApp."""
    print(f"[Scheduler] Revisando notificaciones de medicación a las: {datetime.now()}")
    db: Session = SessionLocal()
    try:
        now = datetime.now()
        # Consultar medicamentos que tienen next_dose_time definido y que ya vencieron (<= now)
        due_medications = db.query(Medication).filter(
            Medication.next_dose_time != None,
            Medication.next_dose_time <= now
        ).all()

        for med in due_medications:
            # Si el medicamento no tiene un usuario asociado, saltamos
            if not med.user:
                continue

            # Obtenemos el teléfono del usuario
            phone = med.user.phone_number
            # Creamos un mensaje preaprobado
            message_body = f"Hola {med.user.name}, es hora de tomar tu medicamento: {med.name}."
            
            try:
                message = client.messages.create(
                    body=message_body,
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=f"whatsapp:{phone}"
                )
                print(f"[Scheduler] Notificación enviada para med ID {med.id} a {phone} (SID: {message.sid})")
            except Exception as e:
                print(f"[Scheduler] Error enviando notificación para med ID {med.id}: {e}")

            # Actualizar el campo next_dose_time según la frecuencia configurada
            if med.frequency in FREQUENCY_MAP:
                delta = FREQUENCY_MAP[med.frequency]
                next_time = med.next_dose_time
                # Si la hora de la próxima dosis ya pasó, sumamos repetidamente el intervalo hasta que sea mayor que ahora
                while next_time <= now:
                    next_time += delta
                med.next_dose_time = next_time
            else:
                # Si no se define una frecuencia, se puede dejar como None o implementar lógica adicional
                med.next_dose_time = None

            db.add(med)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Scheduler] Error en el scheduler: {e}")
    finally:
        db.close()

def start_scheduler():
    """Inicia el scheduler que ejecuta la función de notificaciones cada minuto."""
    scheduler = BackgroundScheduler()
    # Se programa la ejecución cada 1 minuto (ajusta según lo necesites)
    scheduler.add_job(check_medication_notifications, 'interval', minutes=1)
    scheduler.start()
    print("[Scheduler] Scheduler iniciado.")
