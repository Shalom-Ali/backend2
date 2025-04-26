from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from src.services.db import CosmosDB
import json
from datetime import datetime

load_dotenv()

router = APIRouter()

# Pydantic models for request/response
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

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-09-01-preview"
)

# Initialize Cosmos DB
cosmos_db = CosmosDB()

@router.post("/generate", response_model=DescriptionOutput | QuizOutput)
async def generate_content(input: ContentInput):
    try:
        # Get user ID from auth (assuming user is authenticated)
        user_id = "anonymous"  # Replace with actual user ID from auth context

        # Define system message
        system_message = (
            "You are an expert educational assistant. Based on the provided topic or paragraph, "
            "generate either a detailed description or a set of multiple-choice quiz questions. "
            "For descriptions, provide a concise summary or elaboration (100-150 words). "
            "For quizzes, generate 3 multiple-choice questions, each with 4 options and one correct answer. "
            "Return quiz responses in JSON format with fields: 'question', 'options' (list), 'correct_answer'."
        )

        # Customize prompt
        if input.output_type == "description":
            user_prompt = f"Generate a detailed description for the following topic or paragraph:\n\n{input.content}"
        elif input.output_type == "quiz":
            user_prompt = (
                f"Generate 3 multiple-choice quiz questions based on the following topic or paragraph. "
                f"Each question must have 4 options and one correct answer. Return the response as JSON.\n\n{input.content}"
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid output_type. Use 'description' or 'quiz'.")

        # Call Azure OpenAI
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        content = response.choices[0].message.content

        # Store in Cosmos DB
        content_doc = {
            "id": f"{user_id}_{datetime.utcnow().isoformat()}",
            "user_id": user_id,
            "content_type": input.output_type,
            "input_content": input.content,
            "output_content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        cosmos_db.store_content(content_doc)

        # Process response
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
                raise HTTPException(status_code=500, detail="Failed to parse quiz response from AI model.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")
