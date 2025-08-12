import os
import time
import base64
import asyncio
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- INITIALIZATION ---
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except (TypeError, ValueError):
    print("\n--- FATAL ERROR ---")
    print("GOOGLE_API_KEY environment variable not found.")
    print("Please set the key and restart the application.")
    print("-------------------\n")
    exit()

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
direct_gemini_model = genai.GenerativeModel('gemini-1.5-flash')
tts_model = genai.GenerativeModel('models/tts-1')


# --- PROMPT TEMPLATES ---
intro_template = PromptTemplate(
    input_variables=['role_title', 'role_description'],
    template="You are an AI hiring assistant. Generate a warm and welcoming introduction for a candidate applying for the {role_title} position. Briefly mention that this is an AI-assisted first-round interview designed to be fair and objective. The role involves: {role_description}."
)

question_template = PromptTemplate(
    input_variables=['role_description'],
    template="Based on the following job description, generate exactly 5 concise interview questions that cover both technical and behavioral aspects. Return them as a simple numbered list with no other introductory or concluding text. Job Description: {role_description}"
)

evaluation_template = PromptTemplate(
    input_variables=['role_title', 'full_transcription'],
    template="""As an expert technical recruiter, analyze the following interview transcript for the role of {role_title}.
    Provide a structured and objective evaluation. The output must be in a clean, easy-to-read format with these exact sections:

    **1. Overall Summary:** A brief paragraph summarizing the candidate's performance and communication skills.
    **2. Strengths:** 3-4 bullet points highlighting the candidate's strong points, referencing their answers.
    **3. Areas for Improvement:** 3-4 bullet points on weaknesses or areas to probe further in a live interview.

    Transcript:
    {full_transcription}
    """
)


# --- UPGRADED LANGCHAIN RUNNABLES (CHAINS) ---
output_parser = StrOutputParser()
intro_chain = intro_template | llm | output_parser
question_chain = question_template | llm | output_parser
evaluation_chain = evaluation_template | llm | output_parser


# --- CORE AI FUNCTIONS ---

async def text_to_speech(text: str) -> str | None:
    """
    Converts text to speech audio. Returns Base64 string on success, None on failure.
    This function will NOT crash the application if the TTS service fails.
    """
    try:
        response = tts_model.generate_content(
            text,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="audio/mpeg"
            )
        )
        return base64.b64encode(response.audio_content).decode('utf-8')
    except Exception as e:
        # If TTS fails, log the error to the console for debugging but don't stop the program.
        print(f"\n--- TTS WARNING ---")
        print(f"Text-to-speech generation failed: {e}")
        print("The interview will continue without the voice greeting.")
        print("-------------------\n")
        return None

async def generate_interview_content(role_title: str, role_description: str) -> dict:
    """
    Generates introduction text, questions, and greeting audio concurrently and safely.
    """
    # Run text generation tasks concurrently for better performance.
    intro_task = intro_chain.ainvoke({'role_title': role_title, 'role_description': role_description})
    questions_task = question_chain.ainvoke({'role_description': role_description})

    # Wait for both the introduction and questions to be generated.
    intro_text, questions_raw = await asyncio.gather(intro_task, questions_task)

    # Now that we have the intro text, attempt to generate the audio for it.
    # This is now a safe call that will not crash the app.
    greeting_audio_b64 = await text_to_speech(intro_text)

    questions_list = [q.strip() for q in questions_raw.split('\n') if q.strip() and q.strip()[0].isdigit()]
    
    return {
        "introduction": intro_text,
        "questions": questions_list,
        "greetingAudio": greeting_audio_b64
    }


async def transcribe_video_file(video_path: str) -> str:
    """Uploads a video file to Gemini and returns the transcription."""
    gemini_file = None
    try:
        gemini_file = genai.upload_file(path=video_path)
        
        while gemini_file.state.name == "PROCESSING":
            time.sleep(2)
            gemini_file = genai.get_file(gemini_file.name)

        if gemini_file.state.name == "FAILED":
            raise Exception("Gemini file processing failed.")

        response = direct_gemini_model.generate_content(
            ["Please transcribe the spoken words from this video. Return only the text.", gemini_file]
        )
        return response.text
    finally:
        if gemini_file:
            genai.delete_file(gemini_file.name)


async def evaluate_transcription(role_title: str, full_transcription: str) -> str:
    """Generates a final evaluation report using the upgraded LangChain runnable."""
    if not full_transcription or not full_transcription.strip():
        return "No valid responses were submitted for this interview."
        
    evaluation = await evaluation_chain.ainvoke({
        'full_transcription': full_transcription,
        'role_title': role_title
    })
    return evaluation
