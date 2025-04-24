from fastapi import APIRouter
from src.services.db import CosmosDB

router = APIRouter()
db = CosmosDB()

@router.get("/content/{user_id}")
async def get_content(user_id: str):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Simplified personalization: recommend based on preferences
    content = {"module": "math", "content": "Algebra basics"} if "math" in user.get("preferences", []) else {"module": "general", "content": "Intro to learning"}
    return content

@router.post("/progress/{user_id}")
async def update_progress(user_id: str, module: str, progress: float):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.update_progress(user_id, module, progress)
    return {"status": "success"}
