from fastapi import APIRouter, HTTPException
from src.models.user import User
from src.services.db import CosmosDB

router = APIRouter()
db = CosmosDB()

@router.post("/login")
async def login(email: str):
    user = db.get_user(email)  # Simplified; use Entra ID in production
    if not user:
        user = {"id": email, "email": email, "progress": {}, "preferences": []}
        db.upsert_user(user)
    return {"user_id": user["id"]}
