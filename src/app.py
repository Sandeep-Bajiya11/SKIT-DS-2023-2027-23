import streamlit as st
import requests

st.title("Audio Language Model (ALM)")
st.write("Listen, Think, and Understand")

uploaded_file = st.file_uploader("Upload Audio File (WAV/MP3)", type=['wav', 'mp3'])

if uploaded_file is not None:
    st.audio(uploaded_file)
    if st.button("Process Audio"):
        # This will eventually connect to your FastAPI backend
        st.info("Sending to ALM engine...")
        st.success("Audio processed successfully! (Mock result for demonstration)")