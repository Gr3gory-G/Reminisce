# Name: Gregory Gardner
# Date: Sept 13, 2026 
# App Description: This app is a study guide 
#   that turns your notes into quiz questions
#   using AI

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

class OpenEndedQuestion(BaseModel):
    question: str
    ideal_answer: str
    key_concepts: list[str]

class StudySet(BaseModel):
    questions: list[OpenEndedQuestion]

# Reads the .env file and gets the GEMINI_API_KEY 
# needed to communicate with generative ai
load_dotenv()

# Initialize the Gemini client; creates an 
# instance that represents the conversation 
# between the app and AI
client = genai.Client()

# Mock study notes to test the app
sample_notes = """Photosynthesis is the process used by plants to convert light energy into chemical energy. 
It primarily occurs in the chloroplasts, utilizing sunlight, water, and carbon dioxide to produce oxygen and glucose."""

# Sends a prompt to the AI through the established client
response = client.models.generate_content(
    model ="gemini-3.6-flash", # The specific generative engine model that the code is communicating with
    contents = (f"Generate 2 open-ended active recall questions based on these notes:\n\n{sample_notes}"), # The actual prompt that the AI will receive
    config = types.GenerateContentConfig(
        response_mime_type = "application/json", # Makes the engine restrict the output to JSON
        response_schema = StudySet, # guides the engine to align the formatting to match the structure of the StudySet class
    ),
)


quiz_data = response.parsed

for i, item in enumerate(quiz_data.questions, 1):
    print(f'---Prompt {i} ---')
    print(f'Q: {item.question}')
    print(f'Ideal Answer: {item.ideal_answer}')
    print(f'Grading Rubric (Must Mention): {item.key_concepts}\n')