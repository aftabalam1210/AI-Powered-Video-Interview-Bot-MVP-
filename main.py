# main.py
import os
from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# --- ADD THESE TWO LINES ---
from dotenv import load_dotenv
load_dotenv() # This loads the variables from .env into the environment
# ---------------------------

# Import the modular AI functions from the services directory.
from services.ai_services import (
    generate_interview_content,
    transcribe_video_file,
    evaluate_transcription
)



# --- FASTAPI APP SETUP ---
app = FastAPI(title="AI Interview Bot")

# This setup requires 'static' and 'templates' folders to exist.
# A user-friendly error is provided if they are missing.
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
except RuntimeError:
    print("\n--- FATAL ERROR ---")
    print("Could not find 'static' or 'templates' directories.")
    print("Please create them in the root of your project and restart.")
    print("-------------------\n")
    exit()

# In-memory data store for the MVP.
# This dictionary holds the data for a single interview session.
# In a production app, this would be replaced by a database.
interview_data = {}


# --- API ENDPOINTS ---
# These define the URLs and logic for the web application.

@app.get("/", response_class=HTMLResponse)
async def get_candidate_view(request: Request):
    """Serves the main candidate-facing HTML page."""
    return templates.TemplateResponse("candidate_view.html", {"request": request})

@app.post("/start_interview")
async def start_interview(role_title: str = Form(...), role_description: str = Form(...)):
    """
    Handles the initial form submission. It calls the AI service to generate
    the interview content and stores it in our session data.
    """
    try:
        content = await generate_interview_content(role_title, role_description)
        
        # Store the generated content for this session.
        interview_data['role_title'] = role_title
        interview_data['questions'] = content.get("questions", [])
        interview_data['responses'] = []  # Clear any previous responses.
        
        return JSONResponse(content=content)
    except Exception as e:
        print(f"ERROR in /start_interview: {e}")
        return JSONResponse(status_code=500, content={"error": "Could not generate interview content due to an API error."})

@app.post("/submit_response")
async def submit_response(video: UploadFile = File(...)):
    """
    Handles the submission of a single video answer. It saves the video
    temporarily, sends it for transcription, and stores the result.
    """
    # Create a temporary path to save the uploaded video file.
    video_path = f"temp_{video.filename}"
    try:
        with open(video_path, "wb") as buffer:
            buffer.write(await video.read())
        
        # Call the AI service to transcribe the video.
        transcribed_text = await transcribe_video_file(video_path)
        
        # Add the transcription to our session data.
        interview_data.get('responses', []).append(transcribed_text)
        
        return JSONResponse(content={"status": "success", "transcription": transcribed_text})
    except Exception as e:
        print(f"ERROR in /submit_response: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to process the video response."})
    finally:
        # Clean up the temporary local file after processing.
        if os.path.exists(video_path):
            os.remove(video_path)

@app.get("/recruiter_report", response_class=HTMLResponse)
async def get_recruiter_report(request: Request):
    """Generates and serves the final evaluation report for the recruiter."""
    full_transcription = "\n\n".join(interview_data.get('responses', []))
    role_title = interview_data.get('role_title', 'N/A')
    
    try:
        # Call the AI service to get the final evaluation.
        evaluation = await evaluate_transcription(role_title, full_transcription)
        
        return templates.TemplateResponse("recruiter_view.html", {
            "request": request, 
            "role_title": role_title,
            "evaluation": evaluation
        })
    except Exception as e:
        print(f"ERROR in /recruiter_report: {e}")
        # Display a user-friendly error on the report page itself.
        error_message = "Could not generate the evaluation due to a server error. Please check the logs."
        return templates.TemplateResponse("recruiter_view.html", {
            "request": request, 
            "role_title": role_title,
            "evaluation": error_message
        })
