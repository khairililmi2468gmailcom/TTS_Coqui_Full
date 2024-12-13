import os
import io
import shutil
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException, Form, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from TTS.api import TTS
import soundfile as sf
import json
import numpy as np
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
# Declare global variable for TTS model
tts = None
# Tentukan perangkat yang digunakan (CUDA jika tersedia, selain itu CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Membuat aplikasi FastAPI
app = FastAPI()

# CORS middleware
origins = [
    "http://localhost:3002",  # URL frontend lokal
    "http://192.168.0.26:3002",  # IP frontend React lokal
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        tts = TTS("tts_models/multilingual/multi-dataset/bark").to(device)
        return {"message": "Model TTS Bark started successfully."}
    return {"message": "Model TTS Bark is already running."}

# Fungsi untuk menghentikan model TTS
@app.post("/stop-model")
async def stop_model():
    global tts
    if tts is not None:
        tts = None
        torch.cuda.empty_cache()  # Kosongkan cache GPU
        return {"message": "Model TTS Bark stopped successfully."}
    return {"message": "Model TTS Bark is not running."}
# Inisialisasi model TTS dengan Bark

@app.get("/status")
async def get_status():
    """
    Returns the status of the Bark TTS model.
    """
    global tts
    return {"active": tts is not None}

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
@app.websocket("/ws/bark")
async def tts_websocket(websocket: WebSocket, _: None = Depends(check_model_active)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"Received data: {data}")
            
            try:
                request = json.loads(data)
                text = request["text"]
            except json.JSONDecodeError:
                await websocket.send_text("Error: Invalid JSON format.")
                continue

 
            text_chunks = split_text(text)  # Memecah teks panjang
            logging.info(f"Text split into {len(text_chunks)} chunks.")

            final_audio = []

            for chunk in text_chunks:
                try:
                    # Generate speech from text using Bark
                    wav = await asyncio.to_thread(tts.tts, text=chunk)
                    logging.info(f"Generated audio chunk, length: {len(wav)} bytes.")
                    final_audio.append(wav)
                except AssertionError as e:
                    await websocket.send_text(f"Error during synthesis: {str(e)}")
                    continue

            combined_audio = np.concatenate(final_audio)

            wav_int16 = np.int16(combined_audio / np.max(np.abs(combined_audio)) * 32767)

            with io.BytesIO() as byte_io:
                sf.write(byte_io, wav_int16, 22050, format='WAV')
                byte_io.seek(0)
                await websocket.send_bytes(byte_io.read())
            logging.info("Audio sent to client.")
    except WebSocketDisconnect:
        logging.info("Client disconnected")


