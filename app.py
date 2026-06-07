from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pypdf import PdfReader
import google.generativeai as genai
import os

# Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model
model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        return file.read()


@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:

        os.makedirs("uploads", exist_ok=True)

        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        reader = PdfReader(file_path)

        resume_text = ""

        for page in reader.pages:
            text = page.extract_text()

            if text:
                resume_text += text

        prompt = f"""
        Analyze the following resume and provide:

        1. Strengths
        2. Weaknesses
        3. Missing Skills
        4. Career Suggestions
        5. Overall Score out of 10

        Resume:

        {resume_text}
        """

        response = model.generate_content(prompt)

        return {
            "message": "Resume Analysis Completed",
            "filename": file.filename,
            "ai_feedback": response.text
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }


@app.get("/interview")
def start_interview():

    try:

        prompt = """
        Generate 10 interview questions for a Fresher Python Developer.

        Cover:
        - Python
        - OOP
        - SQL
        - Flask/FastAPI
        - Projects
        - HR Questions

        Return numbered questions.
        """

        response = model.generate_content(prompt)

        return {
            "message": "Interview Questions Generated",
            "questions": response.text
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }
    
for m in genai.list_models():
    print(m.name, m.supported_generation_methods)