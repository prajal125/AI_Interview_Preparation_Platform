from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pypdf import PdfReader
import google.generativeai as genai
import os

# Gemini API Key
genai.configure(api_key="YOUR_NEW_API_KEY")

# Gemini Model
model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()

latest_resume_text = ""


# Home Page
@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        return file.read()


# Login Page
@app.get("/login", response_class=HTMLResponse)
def login_page():
    with open("templates/login.html", "r", encoding="utf-8") as file:
        return file.read()


# Register Page
@app.get("/register", response_class=HTMLResponse)
def register_page():
    with open("templates/register.html", "r", encoding="utf-8") as file:
        return file.read()


# Resume Upload + Analysis
@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    global latest_resume_text

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

        latest_resume_text = resume_text

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


# Interview Questions
@app.get("/interview")
def generate_questions():

    global latest_resume_text

    try:

        if not latest_resume_text:
            return {
                "message": "Please upload resume first"
            }

        prompt = f"""
        Based on this resume generate 10 interview questions.

        Resume:

        {latest_resume_text}

        Cover:
        - Python
        - Java
        - SQL
        - Projects
        - MCA Background
        - HR Questions
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