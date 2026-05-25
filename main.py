from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "https://crud-app-18-frontend-react.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    name: str
    age: int

@app.get("/")
def home():
    return {"message": "Backend Working!"}

@app.post("/create")
def create_student(student: Student):
    doc = db.collection("students").document()
    doc.set(student.dict())
    return {"id": doc.id, "message": "Student Added"}

@app.get("/read")
def read_students():
    docs = db.collection("students").stream()
    return [{**d.to_dict(), "id": d.id} for d in docs]

@app.put("/update/{stu_id}")
def update_student(stu_id: str, student: Student):
    db.collection("students").document(stu_id).update(student.dict())
    return {"message": "Student Updated"}

@app.delete("/delete/{stu_id}")
def delete_student(stu_id: str):
    db.collection("students").document(stu_id).delete()
    return {"message": "Student Deleted"}