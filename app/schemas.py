# app/schemas.py

from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    phone_number: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class MedicationBase(BaseModel):
    name: str
    schedule: str
    user_id: int

class MedicationCreate(MedicationBase):
    pass

class MedicationResponse(MedicationBase):
    id: int

    class Config:
        orm_mode = True
