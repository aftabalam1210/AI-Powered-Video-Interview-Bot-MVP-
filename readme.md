
# AI-Powered Video Interview Bot  

A complete **browser-based AI bot** that conducts screening interviews.  
Built with **FastAPI**, **LangChain**, **Google Gemini**, and a lightweight **HTML/CSS/JavaScript** frontend.  

---

## 🚀 Features

- **Dynamic Introduction** – AI greets candidates with a **role-specific** introduction.  
- **AI-Generated Questions** – 5–7 tailored interview questions based on the job description.  
- **In-Browser Video Recording** – Uses the browser's **MediaRecorder API** to capture responses.  
- **AI Video Transcription** – Powered by **Gemini 1.5 Flash’s multimodal capabilities**.  
- **AI Performance Summary** – Structured evaluation: _Overall Summary, Strengths, Areas for Improvement_.  

---

## 🛠 Tech Stack

- **Backend:** FastAPI  
- **AI Framework:** LangChain  
- **LLM:** Google Gemini 1.5 Flash  
- **Frontend:** HTML, CSS, JavaScript  
- **Python Libraries:** `uvicorn`, `python-multipart`, `google-generativeai`, `langchain-google-genai`  

---

## 🧠 Prompt Design Approach  

The bot’s AI features are driven by **specialized prompts** sent to Google Gemini models:  

1. **Introduction Prompt** – Friendly, professional greeting using `role_title` & `role_description`.  
2. **Question Generation Prompt** – Exactly **5 technical/behavioral questions** in numbered list format.  
3. **Transcription Prompt** – Multimodal instruction to **transcribe spoken words from video** only.  
4. **Evaluation Prompt** – AI acts as an **expert technical recruiter**, providing a strict output format:  
   - Overall Summary  
   - Strengths  
   - Areas for Improvement  

---

## 📂 Project Structure

```plaintext
ai-interview-bot/
│-- services/             # Modular AI logic
│   │-- __init__.py
│   └-- ai_services.py
│-- static/               # CSS and JS
│   │-- style.css
│   └-- main.js
│-- templates/            # HTML templates
│   │-- candidate_view.html
│   └-- recruiter_view.html
│-- main.py               # FastAPI app entry point
│-- requirements.txt      # Dependencies
└-- README.md              # Project documentation
````

---

## ⚙️ Setup & Installation

### 1️⃣ Create Folder Structure

Ensure your folders & files match the structure above.

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Set Google API Key

Get an API key from **Google AI Studio** and set it as an environment variable.

**Linux / macOS:**

```bash
export GOOGLE_API_KEY='your-google-api-key'
```

**Windows (Command Prompt):**

```cmd
set GOOGLE_API_KEY="your-google-api-key"
```

> 💡 Add it to your shell startup file (`.bashrc`, `.zshrc`, etc.) to avoid setting it every time.

### 4️⃣ Run the Application

```bash
uvicorn main:app --reload
```

### 5️⃣ Use the Application

* **Candidate View:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Recruiter View:** [http://127.0.0.1:8000/recruiter\_report](http://127.0.0.1:8000/recruiter_report)

---




---


Do you want me to add that next?
```
