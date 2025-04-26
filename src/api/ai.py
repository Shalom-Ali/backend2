from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from src.services.db import CosmosDB
import json
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

router = APIRouter()

# Input and output formats
class ContentInput(BaseModel):
    content: str  # Topic or paragraph
    output_type: str  # "description" or "quiz"

class DescriptionOutput(BaseModel):
    description: str

class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_answer: str

class QuizOutput(BaseModel):
    questions: list[QuizQuestion]

# Connect to Azure OpenAI
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-09-01-preview"
)

# Connect to Cosmos DB
cosmos_db = CosmosDB()

# Retry logic for Azure OpenAI
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_openai(client, model, messages):
    return client.chat.completions.create(model=model, messages=messages, max_tokens=500)

@router.post("/generate", response_model=DescriptionOutput | QuizOutput)
async def generate_content(input: ContentInput):
    try:
        user_id = "anonymous"  # No login required for now

        # Instructions for the AI
        system_message = (
            "You are a helpful teacher. For a given topic or paragraph, "
            "create either a short description (100-150 words) or 3 multiple-choice quiz questions. "
            "Each quiz question needs 4 options and one correct answer. "
            "For quizzes, return the response as JSON with fields: 'question', 'options' (list), 'correct_answer'."
        )

        # Prepare the AI request
        if input.output_type == "description":
            user_prompt = f"Write a short description (100-150 words) for this topic or paragraph:\n\n{input.content}"
        elif input.output_type == "quiz":
            user_prompt = (
                f"Create 3 multiple-choice quiz questions based on this topic or paragraph. "
                f"Each question must have 4 options and one correct answer. Return the response as JSON.\n\n{input.content}"
            )
        else:
            raise HTTPException(status_code=400, detail="Please choose 'description' or 'quiz'.")

        # Call Azure OpenAI
        response = call_openai(
            client,
            os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ]
        )

        content = response.choices[0].message.content

        # Save to Cosmos DB
        content_doc = {
            "id": f"{user_id}_{datetime.utcnow().isoformat()}",
            "user_id": user_id,
            "content_type": input.output_type,
            "input_content": input.content,
            "output_content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        cosmos_db.store_content(content_doc)

        # Return the result
        if input.output_type == "description":
            return DescriptionOutput(description=content)
        else:
            try:
                quiz_data = json.loads(content)
                questions = [
                    QuizQuestion(
                        question=q["question"],
                        options=q["options"],
                        correct_answer=q["correct_answer"]
                    )
                    for q in quiz_data
                ]
                return QuizOutput(questions=questions)
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="AI quiz response was not valid JSON.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
