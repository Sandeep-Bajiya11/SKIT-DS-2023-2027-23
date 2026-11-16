from fastapi import FastAPI, File, UploadFile
import uvicorn
import shutil
import os
import speech_recognition as sr
from textblob import TextBlob

app = FastAPI(title="Audio Language Model API", version="1.1")

@app.get("/")
def read_root():
    return {"status": "ALM Backend is running"}

@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    # 1. Save the uploaded file temporarily
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    transcribed_text = "Could not understand audio"
    emotion_result = "Neutral"
    
    # 2. Process Audio using SpeechRecognition
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(temp_file_path) as source:
            audio_data = recognizer.record(source)
            # Using Google's free web speech API for immediate results
            transcribed_text = recognizer.recognize_google(audio_data)
            
            # 3. Basic Emotion/Sentiment Reasoning on the text
            analysis = TextBlob(transcribed_text)
            if analysis.sentiment.polarity > 0.1:
                emotion_result = f"Positive (Confidence score: {round(analysis.sentiment.polarity, 2)})"
            elif analysis.sentiment.polarity < -0.1:
                emotion_result = f"Negative (Confidence score: {round(analysis.sentiment.polarity, 2)})"
            else:
                emotion_result = "Neutral / Professional"
                
    except Exception as e:
        transcribed_text = f"Error processing audio: {str(e)}"
        
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return {
        "filename": file.filename,
        "transcription": transcribed_text,
        "emotion": emotion_result,
        "events": "Background noise analysis pending model integration",
        "diarization": "Single speaker assumed (multi-speaker model pending)"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)