import os
import io
import shutil
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from TTS.api import TTS
import soundfile as sf
import json
import numpy as np
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Determine the device to be used (CUDA if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Create FastAPI application
app = FastAPI()

# CORS middleware
origins = [
    "http://localhost:3002",  # Local frontend URL
    "http://192.168.0.26:3002",  # Local frontend React IP
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the TTS model with Bark
tts = TTS("tts_models/multilingual/multi-dataset/bark").to(device)


# Function to split long text into smaller chunks
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
@app.websocket("/ws/bark")
async def tts_websocket(websocket: WebSocket):
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

            # Split long text into smaller chunks
            text_chunks = split_text(text)
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

            # Combine all generated audio chunks
            combined_audio = np.concatenate(final_audio)

            # Normalize and convert the audio to 16-bit format
            wav_int16 = np.int16(combined_audio / np.max(np.abs(combined_audio)) * 32767)

            # Send the combined audio back to the client
            with io.BytesIO() as byte_io:
                sf.write(byte_io, wav_int16, 22050, format='WAV')
                byte_io.seek(0)
                await websocket.send_bytes(byte_io.read())
            logging.info("Audio sent to client.")
    except WebSocketDisconnect:
        logging.info("Client disconnected")
