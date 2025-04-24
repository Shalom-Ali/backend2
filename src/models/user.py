from pydantic import BaseModel
from typing import List, Dict

class User(BaseModel):
    id: str
    email: str
    progress: Dict[str, float]  # e.g., {"module1": 0.75, "module2": 0.20}
    preferences: List[str]      # e.g., ["math", "science"]
