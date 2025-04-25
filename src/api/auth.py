from fastapi import APIRouter
from pydantic import BaseModel
from src.services.db import CosmosDB

router = APIRouter()
db = CosmosDB()

class LoginRequest(BaseModel):
    email: str

@router.post("/login")
async def login(request: LoginRequest):
    user = db.get_user(request.email)
    if not user:
        user = {"id": request.email, "email": request.email, "progress": {}, "preferences": []}
        db.upsert_user(user)
    return {"user_id": user["id"]}
