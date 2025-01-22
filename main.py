import openai
import streamlit as st
import os
from moviepy import *

# Configuration de l'API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("Video to Text Transcriber")
st.write(
    "Welcome to the Video to Text Transcriber! This tool uses OpenAI's Whisper model "
    "to convert video files into text. Upload a video file to get started!")

# Initialisation de l'état si nécessaire
if "transcription" not in st.session_state:
    st.session_state.transcription = None


# Fonction pour extraire l'audio d'une vidéo
def extract_audio_from_video(video_path, output_audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)


# Téléchargement du fichier vidéo
uploaded_file = st.file_uploader("Upload your video file",
                                 type=["mp4", "mkv", "avi", "mov"])

if uploaded_file:
    # Sauvegarder le fichier téléchargé localement
    video_path = f"./uploaded_videos/{uploaded_file.name}"
    os.makedirs("uploaded_videos", exist_ok=True)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Uploaded {uploaded_file.name} successfully!")

    # Extraire l'audio du fichier vidéo
    audio_path = video_path.replace(".mp4", ".mp3").replace(
        ".mkv", ".mp3").replace(".avi", ".mp3").replace(".mov", ".mp3")
    st.write("Extracting audio from the video...")
    extract_audio_from_video(video_path, audio_path)
    st.success("Audio extracted successfully!")

    # Transcrire l'audio à l'aide du modèle Whisper
    st.write("Transcribing the audio...")
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = openai.Audio.transcribe(model="whisper-1",
                                                    file=audio_file)
        st.session_state.transcription = transcription["text"]
        st.success("Transcription completed successfully!")
    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")

# Afficher la transcription si disponible
if st.session_state.transcription:
    st.write("Here is the transcription:")
    st.text_area("Transcription", st.session_state.transcription, height=300)

# Bouton pour réinitialiser l'application
if st.button("Reset"):
    st.session_state.transcription = None
    st.experimental_rerun()
