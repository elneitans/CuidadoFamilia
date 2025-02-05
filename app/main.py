# main.py

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal, init_db
from models import User, Medication

# Pydantic schema para crear un usuario
class UserCreate(BaseModel):
    name: str
    phone_number: str

# Pydantic schema para crear un medicamento
class MedicationCreate(BaseModel):
    name: str
    schedule: str
    user_id: int

app = FastAPI(title="CuidadoFamilia v0")

# Se ejecuta al levantar el servidor
@app.on_event("startup")
def on_startup():
    init_db()

# Dependencia para obtener sesión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"msg": "Bienvenido a CuidadoFamilia!"}

@app.post("/users/", response_model=dict)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en la base de datos.
    """
    db_user = User(name=user_data.name, phone_number=user_data.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {
        "msg": "Usuario creado exitosamente",
        "user_id": db_user.id,
        "name": db_user.name
    }

@app.post("/medications/", response_model=dict)
def create_medication(med_data: MedicationCreate, db: Session = Depends(get_db)):
    """
    Asigna un medicamento a un usuario existente.
    """
    db_med = Medication(
        name=med_data.name,
        schedule=med_data.schedule,
        user_id=med_data.user_id
    )
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return {
        "msg": "Medicamento creado y asignado correctamente",
        "medication_id": db_med.id
    }

@app.get("/users/{user_id}", response_model=dict)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retorna la información de un usuario por su ID.
    Incluye los medicamentos asociados.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return {"error": "Usuario no encontrado"}
    
    # Serializar la info de medicamentos
    meds = [
        {"id": med.id, "name": med.name, "schedule": med.schedule}
        for med in db_user.medications
    ]
    return {
        "id": db_user.id,
        "name": db_user.name,
        "phone_number": db_user.phone_number,
        "medications": meds
    }
