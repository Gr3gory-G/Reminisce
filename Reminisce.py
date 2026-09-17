# Name: Gregory Gardner
# Date: Sept 13, 2026 
# App Description: This app is a study guide 
#   that turns your notes into quiz questions
#   using AI to build you ability to recall them

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import traceback

class OpenEndedQuestion(BaseModel):
    question: str
    ideal_answer: str
    key_concepts: list[str]

class StudySet(BaseModel):
    questions: list[OpenEndedQuestion]

class StudyNotesRequest(BaseModel):
    notes: str

# Schemas for grading
class ConceptEvaluation(BaseModel):
    concept: str
    present: bool
    evidence: str

class GradingResult(BaseModel):
    score_percentage: int
    evaluations: list[ConceptEvaluation]
    constructive_feedback: str

class GradeRequest(BaseModel):
    question: str
    key_concepts: list[str]
    user_answer: str



# Reads the .env file and gets the GEMINI_API_KEY 
# needed to communicate with generative ai
load_dotenv()

app = FastAPI()

ai_model = 'gemini-3.5-flash' # The specific ai model being communicated with

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Initialize the Gemini client; creates an 
# instance that represents the conversation 
# between the app and AI
client = genai.Client()

# Mock study notes to test the app
sample_notes = """Photosynthesis is the process used by plants to convert light energy into chemical energy. 
It primarily occurs in the chloroplasts, utilizing sunlight, water, and carbon dioxide to produce oxygen and glucose."""

# Sends a prompt to the AI through the established client
def generate_quiz_from_notes(notes: str) -> StudySet:
    response = client.models.generate_content(
        model = ai_model, # The specific generative engine model that the code is communicating with
        contents = (f"Generate 2 open-ended active recall questions based on these notes (If the notes provided are not viable enough to produce well made questions, give output that would raise an error in JSON):\n\n{notes}"), # The actual prompt that the AI will receive
        config = types.GenerateContentConfig(
            response_mime_type = "application/json", # Makes the engine restrict the output to JSON
            response_schema = StudySet, # guides the engine to align the formatting to match the structure of the StudySet class
        ),
    )
    return response.parsed


@app.post('/api/generate')
async def generate_quiz(data: StudyNotesRequest):
    try:
        print("Received notes:", repr(data.notes[:200]))

        study_set = generate_quiz_from_notes(data.notes)

        if study_set is None:
            raise Exception("Gemini returned no parsed response")

        return study_set
    except Exception as error:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(error))

@app.post("/api/grade", response_model=GradingResult)
async def grade_user_answer(data: GradeRequest):
    prompt = f"""
    You are an objective academic evaluator grading an open_ended response.GradeRequest

    Question: {data.question}
    Required Rubric (Key Concepts): {data.key_concepts}
    User Answer: {data.user_answer}

    Evaluate whether the user's answer demonstrates understanding of each key concept.
    Grade on semantic meaning, not exact keyword matches.
    """

    response = client.models.generate_content(
        model = ai_model,
        contents = prompt,
        config = types.GenerateContentConfig(
            response_mime_type = 'application/json',
            response_schema = GradingResult,
        ),
    )
    return response.parsed
