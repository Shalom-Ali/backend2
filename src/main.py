from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import auth, learning

app = FastAPI()

# Allow frontend CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(learning.router, prefix="/learning")

@app.get("/")
async def root():
    return {"message": "Personalized Learning Backend"}
