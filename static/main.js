document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENT SELECTORS ---
    const roleForm = document.getElementById('role-form');
    const startBtn = document.getElementById('start-btn');
    const welcomeSection = document.getElementById('welcome-section');
    const interviewSection = document.getElementById('interview-section');
    const introductionTextEl = document.getElementById('introduction-text');
    const questionTextEl = document.getElementById('question-text');
    const recordBtn = document.getElementById('record-btn');
    const nextBtn = document.getElementById('next-btn');
    const videoPreview = document.getElementById('video-preview');
    const statusText = document.getElementById('status-text');

    // --- STATE VARIABLES ---
    let mediaRecorder;
    let recordedChunks = [];
    let questions = [];
    let currentQuestionIndex = 0;
    let stream;

    // --- EVENT LISTENERS ---

    // Handle the initial form submission to start the interview.
    roleForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        setButtonLoading(startBtn, 'Initializing...');

        const formData = new FormData(roleForm);

        try {
            const response = await fetch('/start_interview', { method: 'POST', body: formData });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.statusText}`);
            }
            const data = await response.json();

            if (!data.questions || data.questions.length === 0) {
                 throw new Error("The AI did not return any questions. Please check the role description and try again.");
            }

            questions = data.questions;
            introductionTextEl.textContent = data.introduction;
            
            // Switch from the welcome view to the interview view.
            welcomeSection.classList.add('hidden');
            interviewSection.classList.remove('hidden');

            displayCurrentQuestion();
        } catch (error) {
            console.error('Failed to start interview:', error);
            alert(`Could not start the interview: ${error.message}`);
            setButtonEnabled(startBtn, 'Start Interview');
        }
    });

    // Handle the record button click to start/stop recording.
    recordBtn.addEventListener('click', async () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            stopRecording();
        } else {
            await startRecording();
        }
    });

    // Handle the "Next Question" button click.
    nextBtn.addEventListener('click', () => {
        currentQuestionIndex++;
        displayCurrentQuestion();
    });


    // --- CORE FUNCTIONS ---

    /**
     * Displays the current question or ends the interview if all questions are answered.
     */
    function displayCurrentQuestion() {
        if (currentQuestionIndex < questions.length) {
            questionTextEl.textContent = `Question ${currentQuestionIndex + 1}/${questions.length}: ${questions[currentQuestionIndex]}`;
            recordBtn.classList.remove('hidden');
            nextBtn.classList.add('hidden');
            setButtonEnabled(recordBtn, 'Start Recording');
            statusText.textContent = "Click 'Start Recording' when you are ready to answer.";
        } else {
            endInterview();
        }
    }

    /**
     * Requests camera/mic access and starts recording the user's response.
     */
    async function startRecording() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            videoPreview.srcObject = stream;
            recordedChunks = [];

            mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) recordedChunks.push(event.data);
            };
            mediaRecorder.onstop = handleRecordingStop;

            mediaRecorder.start();
            setButtonEnabled(recordBtn, 'Stop Recording');
            statusText.textContent = 'Recording...';
        } catch (error) {
            console.error('Error accessing media devices:', error);
            alert('Could not access your camera and microphone. Please check your browser permissions and refresh the page.');
        }
    }

    /**
     * Stops the current recording.
     */
    function stopRecording() {
        mediaRecorder.stop();
        setButtonLoading(recordBtn, 'Processing...');
        statusText.textContent = 'Processing your response... Please wait.';
    }

    /**
     * Handles the logic after a recording has stopped, including uploading the video.
     */
    async function handleRecordingStop() {
        const videoBlob = new Blob(recordedChunks, { type: 'video/webm' });
        const formData = new FormData();
        formData.append('video', videoBlob, `response_${currentQuestionIndex}.webm`);
        
        try {
            const response = await fetch('/submit_response', { method: 'POST', body: formData });
            if (!response.ok) {
                 const errorData = await response.json();
                 throw new Error(errorData.error || `Server error: ${response.statusText}`);
            }
            const result = await response.json();
            console.log('Transcription successful:', result.transcription);
            
            statusText.textContent = 'Response submitted successfully!';
            recordBtn.classList.add('hidden');
            nextBtn.classList.remove('hidden');
        } catch (error) {
            console.error('Failed to submit response:', error);
            alert(`Could not submit your response: ${error.message}. Please try recording again.`);
            setButtonEnabled(recordBtn, 'Start Recording');
        }
    }

    /**
     * Cleans up and ends the interview session.
     */
    function endInterview() {
        questionTextEl.textContent = "Thank you for completing the interview!";
        videoPreview.style.display = 'none';
        recordBtn.classList.add('hidden');
        nextBtn.classList.add('hidden');
        statusText.textContent = "You will be redirected to the recruiter's report shortly.";
        
        // Stop all media tracks to turn off the camera light.
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        
        // Redirect to the report page after a short delay.
        setTimeout(() => window.location.href = '/recruiter_report', 3000);
    }


    // --- UTILITY FUNCTIONS ---
    function setButtonLoading(button, text) {
        button.disabled = true;
        button.textContent = text;
    }

    function setButtonEnabled(button, text) {
        button.disabled = false;
        button.textContent = text;
    }
});
