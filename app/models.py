# models.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True)
#    gender = Column(String)

    medications = relationship("Medication", back_populates="user")

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    schedule = Column(String, nullable=True)
    # Fecha en la que inicia la rutina de medicación
    start_date = Column(DateTime, nullable=False, default=func.now())
    # Fecha opcional en la que finaliza la rutina (si aplica)
    end_date = Column(DateTime, nullable=True)
    # Información sobre la dosis, por ejemplo "500 mg" o "1 tableta"
    dosage = Column(String, nullable=True)
    # Frecuencia de administración (por ejemplo, "diaria", "cada 8 horas", etc.)
    frequency = Column(String, nullable=True)
    # Fecha y hora de la próxima dosis (útil para el sistema de notificaciones)
    next_dose_time = Column(DateTime, nullable=True)
    # Relación con el usuario que tiene asignado este medicamento
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="medications")

#class MedicalConditions(Base):
#    '''
#    Relación con Usuario, sus condiciones médicas. 
#    También ligado a la medicación que toma por tal enfermedad.
#    Cuidado con que no tome nada por esa condición. (cardinalidad)
#    '''
#    __tablename__ = "medical_conditions"    
#
#
#    user_id = Column(Integer, ForeignKey("users.id"))
#    name = Column(String, nullable=False)
#    severity = Column(String, nullable=False) #aquí valores predeterminados. 4 niveles
#
#