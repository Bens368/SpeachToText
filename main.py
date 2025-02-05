import openai
import streamlit as st
import os
from moviepy import *

# Configuration de l'API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("🎥 Video to Text & Summary Transcriber")
st.write(
    "Welcome! This tool converts video files into text using OpenAI's Whisper model, "
    "and then generates a structured summary. Upload a video to get started!"
)

# Initialisation des états
if "transcription" not in st.session_state:
    st.session_state.transcription = None
if "summary" not in st.session_state:
    st.session_state.summary = None


# Fonction pour extraire l'audio d'une vidéo
def extract_audio_from_video(video_path, output_audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)


# Téléchargement du fichier vidéo
uploaded_file = st.file_uploader("📤 Upload your video file", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file:
    # Sauvegarder le fichier téléchargé localement
    video_path = f"./uploaded_videos/{uploaded_file.name}"
    os.makedirs("uploaded_videos", exist_ok=True)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded {uploaded_file.name} successfully!")

    # Extraire l'audio du fichier vidéo
    audio_path = video_path.rsplit(".", 1)[0] + ".mp3"
    st.write("🔊 Extracting audio from the video...")
    extract_audio_from_video(video_path, audio_path)
    st.success("✅ Audio extracted successfully!")

    # Transcrire l'audio à l'aide du modèle Whisper
    st.write("📝 Transcribing the audio...")
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = openai.Audio.transcribe(model="whisper-1", file=audio_file)
        st.session_state.transcription = transcription["text"]
        st.success("✅ Transcription completed successfully!")
    except Exception as e:
        st.error(f"❌ An error occurred during transcription: {e}")

# Afficher le bouton "Générer le résumé" si la transcription est disponible
if st.session_state.transcription and "summary" not in st.session_state:
    if st.button("📝 Generate Structured Summary"):
        st.write("⏳ Generating summary... Please wait.")

        # Demander à OpenAI de générer un résumé structuré
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing transcriptions into structured formats."},
                    {"role": "user", "content": f"Summarize the following transcription into a structured format:\n\n{st.session_state.transcription}"}
                ],
                temperature=0.7
            )
            st.session_state.summary = response["choices"][0]["message"]["content"]
            st.success("✅ Summary generated successfully!")
        except Exception as e:
            st.error(f"❌ An error occurred during summarization: {e}")

# Afficher le résumé si disponible
if st.session_state.summary:
    st.write("📌 **Structured Summary:**")
    st.text_area("Summary", st.session_state.summary, height=300)

# Bouton pour réinitialiser l'application
if st.button("🔄 Reset"):
    st.session_state.transcription = None
    st.session_state.summary = None
    st.experimental_rerun()
