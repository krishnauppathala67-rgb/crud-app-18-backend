from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel
import os
import json

# ---------------------
#   Firebase Setup (ENV Variable Version)
# ---------------------

# Load Firebase key from Railway environment variable
firebase_key_json = os.getenv("FIREBASE_KEY_JSON")

if not firebase_key_json:
    raise Exception("❌ FIREBASE_KEY_JSON not found in Railway environment variables!")

# Convert the long JSON string → Python dict
firebase_key_dict = json.loads(firebase_key_json)

# Initialize Firebase Admin using dict
firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------------
#      FastAPI App
# ---------------------
app = FastAPI()

# ---------------------
#       CORS
# ---------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------
#   Pydantic Model
# ---------------------
class Item(BaseModel):
    name: str
    age: int

# ---------------------
#       CRUD API
# ---------------------

@app.get("/")
def home():
    return {"message": "Backend is running with ENV Firebase!"}

@app.post("/create")
def create(item: Item):
    doc_ref = db.collection("students").document()
    doc_ref.set(item.dict())
    return {"id": doc_ref.id, "message": "Created successfully"}

@app.get("/read")
def read():
    docs = db.collection("students").stream()
    students = [{**doc.to_dict(), "id": doc.id} for doc in docs]
    return students

@app.put("/update/{id}")
def update(id: str, item: Item):
    db.collection("students").document(id).update(item.dict())
    return {"message": "Updated successfully"}

@app.delete("/delete/{id}")
def delete(id: str):
    db.collection("students").document(id).delete()
    return {"message": "Deleted successfully"}