from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel
import os
import json

# -----------------------------
#   FIREBASE SETUP (RAILWAY FIX)
# -----------------------------
firebase_key_json = os.getenv("FIREBASE_KEY_JSON")

if not firebase_key_json:
    raise Exception("❌ FIREBASE_KEY_JSON is missing in Railway Variables")

# Convert JSON string → Python dict
firebase_dict = json.loads(firebase_key_json)

# Create credential from dictionary
cred = credentials.Certificate(firebase_dict)

# Initialize Firebase app only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# -----------------------------
#   FASTAPI APP
# -----------------------------
app = FastAPI()

# CORS SETUP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Model
class Item(BaseModel):
    name: str
    age: int

# Routes
@app.get("/")
def home():
    return {"message": "Backend is running with Firebase via Railway ENV!"}

@app.post("/create")
def create(item: Item):
    doc_ref = db.collection("students").document()
    doc_ref.set(item.dict())
    return {"id": doc_ref.id, "message": "Created successfully"}

@app.get("/read")
def read():
    docs = db.collection("students").stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]

@app.put("/update/{id}")
def update(id: str, item: Item):
    db.collection("students").document(id).update(item.dict())
    return {"message": "Updated successfully"}

@app.delete("/delete/{id}")
def delete(id: str):
    db.collection("students").document(id).delete()
    return {"message": "Deleted successfully"}