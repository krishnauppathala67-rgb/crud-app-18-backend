from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import firebase_admin
from firebase_admin import credentials, firestore, auth

from pydantic import BaseModel

import os
import json
import random
import smtplib
from email.message import EmailMessage


# -----------------------------
# Firebase Setup
# -----------------------------
firebase_key_json = os.getenv("FIREBASE_KEY_JSON")

if firebase_key_json:
    firebase_key_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(firebase_key_dict)
else:
    cred = credentials.Certificate("firebase_key.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()
otp_store = {}

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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
# Models
# -----------------------------
class Student(BaseModel):
    name: str
    age: int


class EmailRequest(BaseModel):
    email: str


class OTPVerifyRequest(BaseModel):
    email: str
    otp: str


# -----------------------------
# Send OTP Email
# -----------------------------
def send_otp_email(to_email: str, otp: str):
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_user or not email_password:
        raise HTTPException(
            status_code=500,
            detail="EMAIL_USER or EMAIL_PASSWORD not found"
        )

    msg = EmailMessage()
    msg["Subject"] = "Your CRUD App Login Code"
    msg["From"] = email_user
    msg["To"] = to_email
    msg.set_content(f"Your 4-digit login code is: {otp}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_user, email_password)
        smtp.send_message(msg)


# -----------------------------
# Firebase Token Verification
# -----------------------------
def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    try:
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        return decoded_token

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def home():
    return {"message": "Backend Working!"}


@app.post("/send-otp")
def send_otp(data: EmailRequest):
    otp = str(random.randint(1000, 9999))

    otp_store[data.email] = otp

    send_otp_email(data.email, otp)

    return {"message": "OTP sent successfully"}


@app.post("/verify-otp")
def verify_otp(data: OTPVerifyRequest):
    saved_otp = otp_store.get(data.email)

    if saved_otp == data.otp:
        del otp_store[data.email]
        return {"message": "OTP verified successfully"}   
    
        raise HTTPException(status_code=400, detail="Invalid OTP")   )

    if saved_otp != request.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    del otp_store[request.email]

    return {"message": "OTP verified successfully"}


@app.post("/create")
def create_student(
    student: Student,
    authorization: str = Header(None)
):
    user = verify_token(authorization)

    doc = db.collection("students").document()
    doc.set({
        "name": student.name,
        "age": student.age,
        "created_by": user.get("email")
    })

    return {
        "id": doc.id,
        "message": "Student Added",
        "user": user.get("email")
    }


@app.get("/read")
def read_students(authorization: str = Header(None)):
    user = verify_token(authorization)

    docs = db.collection("students").stream()

    students = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        students.append(data)

    return students


@app.put("/update/{stu_id}")
def update_student(
    stu_id: str,
    student: Student,
    authorization: str = Header(None)
):
    user = verify_token(authorization)

    db.collection("students").document(stu_id).update({
        "name": student.name,
        "age": student.age,
        "updated_by": user.get("email")
    })

    return {
        "message": "Student Updated",
        "user": user.get("email")
    }


@app.delete("/delete/{stu_id}")
def delete_student(
    stu_id: str,
    authorization: str = Header(None)
):
    user = verify_token(authorization)

    db.collection("students").document(stu_id).delete()

    return {
        "message": "Student Deleted",
        "user": user.get("email")
    }