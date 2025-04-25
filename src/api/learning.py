from fastapi import APIRouter
from pydantic import BaseModel
from src.services.db import CosmosDB

router = APIRouter()
db = CosmosDB()

class ProgressUpdate(BaseModel):
    module: str
    progress: int

@router.get("/content/{user_id}")
async def get_content(user_id: str):
    # Dummy content; integrate with Cosmos DB later
    return {"module": "Intro to Python", "details": "Learn basics of Python programming"}

@router.post("/progress/{user_id}")
async def update_progress(user_id: str, update: ProgressUpdate):
    user = db.update_progress(user_id, update.module, update.progress)
    if user:
        return {"status": "Progress updated"}
    return {"error": "User not found"}
