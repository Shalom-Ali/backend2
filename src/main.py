from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import auth, learning, ai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ZUniques-Hackathon-STG-UAEN-02.azurewebsites.net",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth, prefix="/auth")
app.include_router(learning, prefix="/learning")
app.include_router(ai, prefix="/ai")

@app.get("/")
async def root():
    return {"message": "Personalized Learning Backend"}
