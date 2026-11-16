from fastapi import FastAPI, File, UploadFile
import uvicorn

app = FastAPI(title="Audio Language Model API", version="1.0")

@app.get("/")
def read_root():
    return {"status": "ALM Backend is running"}

@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    # Placeholder for future audio event detection and diarization logic
    return {
        "filename": file.filename,
        "message": "Audio received successfully. Processing pipeline to be integrated."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)