import os
import io
import shutil
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException, Form, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from TTS.api import TTS
import librosa
import soundfile as sf
import string
import json
import numpy as np
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
# Declare global variable for TTS model
tts = None
# Determine the device to use (CUDA if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# List of supported language aliases
language_aliases = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "pl": "Polish",
    "tr": "Turkish",
    "ru": "Russian",
    "nl": "Dutch",
    "cs": "Czech",
    "ar": "Arabic",
    "zh-cn": "Chinese",
    "hu": "Hungarian",
    "ko": "Korean",
    "ja": "Japanese",
    "hi": "Hindi"
}


# Path to store speaker files
SPEAKERS_DIR = "/home/alim/alim_workspace/TTS_Test_Tool/CoquiTTS/datavoice/"

# Create the FastAPI application
app = FastAPI()

# CORS middleware
origins = [
    "http://localhost:3002",  # Local frontend URL
    "http://192.168.0.26:3002",  # Local React frontend IP
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fungsi untuk memeriksa apakah model aktif
def check_model_active():
    if tts is None:
        raise HTTPException(status_code=400, detail="Model TTS is not active. Please start the model first.")


# Fungsi untuk memulai model TTS
@app.post("/start-model")
async def start_model():
    global tts
    if tts is None:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        return {"message": "Model TTS xtts_v2 started successfully."}
    return {"message": "Model TTS xtts_v2 is already running."}

# Fungsi untuk menghentikan model TTS
@app.post("/stop-model")
async def stop_model():
    global tts
    if tts is not None:
        tts = None
        torch.cuda.empty_cache()  # Kosongkan cache GPU
        return {"message": "Model TTS xtts_v2 stopped successfully."}
    return {"message": "Model TTS xtts_v2 is not running."}
@app.get("/status")
async def get_status():
    """
    Returns the status of the XTTS model.
    """
    global tts
    return {"active": tts is not None}


# Function to load the list of speakers
def load_speakers():
    speakers = {}
    for speaker_file in os.listdir(SPEAKERS_DIR):
        if speaker_file.endswith(".wav"):
            speaker_name = os.path.splitext(speaker_file)[0]
            speakers[speaker_name] = {
                "alias": speaker_name,
                "path": os.path.join(SPEAKERS_DIR, speaker_file),
                "sample_rate": 22050,
            }
    return speakers

# Load the list of speakers
speakers = load_speakers()

# Function to resample audio using librosa
def resample_audio(file_path, target_sample_rate):
    audio, original_sample_rate = librosa.load(file_path, sr=None)
    if original_sample_rate != target_sample_rate:
        audio = librosa.resample(audio, orig_sr=original_sample_rate, target_sr=target_sample_rate)
    return audio, target_sample_rate

# Function to split long text into shorter chunks
def split_text(text, max_length=400):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(word)
        current_length += len(word) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# WebSocket endpoint for TTS
@app.websocket("/ws/tts")
async def tts_websocket(websocket: WebSocket, _: None = Depends(check_model_active)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"Received data: {data}")
            
            try:
                request = json.loads(data)
                text = request["text"]
                language = request["language"]
                speaker = request["speaker"]
            except json.JSONDecodeError:
                await websocket.send_text("Error: Invalid JSON format.")
                continue

            sanitized_text = text.translate(str.maketrans('', '', string.punctuation))

            if language not in language_aliases:
                await websocket.send_text(f"Unsupported language: {language}")
                continue

            global speakers
            if speaker not in speakers:
                speakers = load_speakers()
                if speaker not in speakers:
                    await websocket.send_text(f"Unsupported speaker: {speaker}")
                    continue

            speaker_config = speakers[speaker]
            speaker_wav = speaker_config["path"]
            sample_rate = speaker_config["sample_rate"]

            resampled_audio, resampled_rate = await asyncio.to_thread(resample_audio, speaker_wav, sample_rate)
            logging.info("Audio resampled successfully.")

            resampled_path = "/tmp/resampled_audio.wav"
            sf.write(resampled_path, resampled_audio, resampled_rate)

            text_chunks = split_text(sanitized_text)  # Split long text
            logging.info(f"Text split into {len(text_chunks)} chunks.")

            final_audio = []

            for chunk in text_chunks:
                try:
                    wav = await asyncio.to_thread(tts.tts, text=chunk, speaker_wav=resampled_path, language=language)
                    logging.info(f"Generated audio chunk, length: {len(wav)} bytes.")
                    final_audio.append(wav)
                except AssertionError as e:
                    await websocket.send_text(f"Error during synthesis: {str(e)}")
                    continue

            combined_audio = np.concatenate(final_audio)

            wav_int16 = np.int16(combined_audio / np.max(np.abs(combined_audio)) * 32767)

            with io.BytesIO() as byte_io:
                sf.write(byte_io, wav_int16, sample_rate, format='WAV')
                byte_io.seek(0)
                await websocket.send_bytes(byte_io.read())
            logging.info("Audio sent to client.")
    except WebSocketDisconnect:
        logging.info("Client disconnected")

# Endpoint to get the list of speakers
@app.get("/speakers", dependencies=[Depends(check_model_active)])
async def get_speakers():
    global speakers
    return {key: value["alias"] for key, value in speakers.items()}

# Endpoint to get the list of supported languages
@app.get("/languages", dependencies=[Depends(check_model_active)])
async def get_languages():
    return language_aliases

# Endpoint to get the list of speaker files
@app.get("/list-files", dependencies=[Depends(check_model_active)])
async def list_files():
    """
    Returns a list of available speaker files.
    """
    files = [f for f in os.listdir(SPEAKERS_DIR) if f.endswith(".wav")]
    return files

# Endpoint to upload a speaker sample
@app.post("/upload-sample/", dependencies=[Depends(check_model_active)])
async def upload_sample(
    file: UploadFile = File(...),
    speaker_name: str = Form(...)
):
    if not speaker_name:
        raise HTTPException(status_code=400, detail="Speaker name is required.")

    formatted_speaker_name = "_".join(word.capitalize() for word in speaker_name.strip().split())

    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are allowed.")

    file_path = os.path.join(SPEAKERS_DIR, f"{formatted_speaker_name}.wav")

    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File with this speaker name already exists.")

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        global speakers
        speakers = load_speakers()

        return {"message": f"Sample uploaded successfully for speaker: {formatted_speaker_name}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save file. Please try again later.")

# Endpoint to delete a speaker file
@app.delete("/delete-file", dependencies=[Depends(check_model_active)])
async def delete_file(request: Request):
    data = await request.json()
    file_name = data.get("file_name")

    if not file_name:
        raise HTTPException(status_code=400, detail="file_name is required")

    file_path = os.path.join(SPEAKERS_DIR, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.remove(file_path)
        
        global speakers
        speakers = load_speakers()

        return {"message": f"File {file_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
