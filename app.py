import os
import io
import shutil
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException, Form, Request
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

# Tentukan perangkat yang digunakan (CUDA jika tersedia, selain itu CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# List alias bahasa yang didukung
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

# Inisialisasi model TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Path untuk menyimpan speaker
SPEAKERS_DIR = "/home/alim/alim_workspace/TTS_Test_Tool/CoquiTTS/datavoice/"

# Membuat aplikasi FastAPI
app = FastAPI()

# CORS middleware
origins = [
    "http://localhost:3002",  # URL frontend lokal
    "http://0.0.0.0:3002",  # IP frontend React lokal
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fungsi untuk memuat daftar speaker
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

# Memuat daftar speaker
speakers = load_speakers()

# Fungsi untuk meresample audio menggunakan librosa
def resample_audio(file_path, target_sample_rate):
    audio, original_sample_rate = librosa.load(file_path, sr=None)
    if original_sample_rate != target_sample_rate:
        audio = librosa.resample(audio, orig_sr=original_sample_rate, target_sr=target_sample_rate)
    return audio, target_sample_rate

# Fungsi untuk memecah teks panjang menjadi potongan yang lebih pendek
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

# WebSocket endpoint untuk TTS
@app.websocket("/ws/tts")
async def tts_websocket(websocket: WebSocket):
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

            text_chunks = split_text(sanitized_text)  # Memecah teks panjang
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

# Endpoint untuk mendapatkan daftar speaker
@app.get("/speakers")
async def get_speakers():
    global speakers
    return {key: value["alias"] for key, value in speakers.items()}

# Endpoint untuk mendapatkan daftar bahasa yang didukung
@app.get("/languages")
async def get_languages():
    return language_aliases

# Endpoint untuk mendapatkan daftar file speaker
@app.get("/list-files")
async def list_files():
    """
    Returns a list of available speaker files.
    """
    files = [f for f in os.listdir(SPEAKERS_DIR) if f.endswith(".wav")]
    return files


# Endpoint untuk upload sample
@app.post("/upload-sample/")
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

# Endpoint untuk menghapus file speaker
@app.delete("/delete-file")
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
