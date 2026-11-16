import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="ALM Interface")
st.title("🎙️ Audio Language Model (ALM)")
st.caption("Listen, Think, and Understand - Live Processing Demo")

# 1. Add a toggle for the input method
input_method = st.radio("Choose Input Method:", ["Record Live Microphone", "Upload Audio File"], horizontal=True)
st.markdown("---")

audio_data = None

# 2. Display the correct widget based on the selection
if input_method == "Upload Audio File":
    audio_data = st.file_uploader("Upload Audio Sample (WAV format only)", type=['wav'])
else:
    st.info("Click the microphone icon below to start recording.")
    audio_data = st.audio_input("Record Live Audio") # Streamlit's native mic widget

# 3. Process the audio (works identically for both methods)
if audio_data is not None:
    st.audio(audio_data)
    
    if st.button("Run ALM Engine"):
        with st.spinner("Processing audio through FastAPI backend..."):
            
            # Extract the filename (Streamlit assigns 'audio.wav' to live recordings)
            filename = getattr(audio_data, 'name', 'live_recording.wav')
            files = {"file": (filename, audio_data.getvalue(), "audio/wav")}
            
            try:
                response = requests.post("http://localhost:8000/process-audio/", files=files)
                data = response.json()
                
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📝 Speech Recognition", 
                    "🎭 Emotion & Sentiment",
                    "👥 Speaker Diarization", 
                    "🔍 Event Detection"
                ])
                
                with tab1:
                    st.success("Transcribed Text")
                    st.write(f"> {data.get('transcription', 'No transcription available')}")
                    
                with tab2:
                    st.warning("Detected Emotion & Sentiment")
                    st.write(f"**Result:** {data.get('emotion', 'N/A')}")
                    
                with tab3:
                    st.info("Speaker Timeline")
                    st.write(data.get('diarization', 'N/A'))
                    
                with tab4:
                    st.error("Audio Events")
                    st.write(data.get('events', 'N/A'))
                    
            except Exception as e:
                st.error("Failed to connect to backend. Make sure the FastAPI server is running on port 8000.")
                
# [Leave your Text-to-Speech code at the bottom exactly as it is]