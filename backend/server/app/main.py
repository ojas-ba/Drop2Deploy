from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from firebase_middleware import FireBaseAuthenticationMiddleware
from db import init_db
from fastapi.middleware.cors import CORSMiddleware

def lifespan(app: FastAPI):
    init_db()
    yield
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(CORSMiddleware,allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(FireBaseAuthenticationMiddleware)

@app.get("/auth")
def read_root():
    return {"message": "Welcome to the Drop2Deploy API!"}

@app.get("/protected")
def protected_route():
    return {"message": "This is a protected route, accessible only to authenticated users."}
