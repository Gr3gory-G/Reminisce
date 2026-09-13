# Name: Gregory Gardner
# Date: Sept 13, 2026 
# App Description: This app is a study guide 
#   that turns your notes into quiz questions
#   using AI

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel

class OpenEndedQuestion(BaseModel):
    question: str
    ideal_answer: str
    key_concepts: list[str]

class StudySet(BaseModel):
    questions: list[OpenEndedQuestion]

class StudyNotesRequest(BaseModel):
    notes: str


# Reads the .env file and gets the GEMINI_API_KEY 
# needed to communicate with generative ai
load_dotenv()

app = FastAPI()

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"]
    allow_methods = ["*"]
    allow_headers = ["*"]
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
        model ="gemini-3.6-flash", # The specific generative engine model that the code is communicating with
        contents = (f"Generate 2 open-ended active recall questions based on these notes:\n\n{sample_notes}"), # The actual prompt that the AI will receive
        config = types.GenerateContentConfig(
            response_mime_type = "application/json", # Makes the engine restrict the output to JSON
            response_schema = StudySet, # guides the engine to align the formatting to match the structure of the StudySet class
        ),
    )
    return response.parsed


@app.post('/api/generate')
async def generate_quiz(data: StudyNotesRequest):
    study_set = generate_quiz_from_notes(data.notes)
    return study_set