from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel
import os
import json

# -----------------------------
# Firebase Setup
# -----------------------------
firebase_key_json = os.getenv("FIREBASE_KEY_JSON")

if not firebase_key_json:
    raise Exception("FIREBASE_KEY_JSON not found in Railway variables")

firebase_key_dict = json.loads(firebase_key_json)

cred = credentials.Certificate(firebase_key_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://crud-app-18-frontend-react.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Model
# -----------------------------
class Student(BaseModel):
    name: str
    age: int

# -----------------------------
# Routes
# -----------------------------
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