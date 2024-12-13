import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from TTS.api import TTS
import asyncio
import librosa
import soundfile as sf
import string
from typing import List

# Determine the device to use (CUDA if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# List of supported languages and their aliases
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

# List of speakers with their aliases, file paths, and sample rates
speakers = {
    "speaker_1": {
        "alias": "Ana",
        "path": "/home/alim/alim_workspace/TTS_Test_Tool/CoquiTTS/dataset/LJSpeech-1.1/wavs/LJ004-0223.wav",
        "sample_rate": 22050
    },
    "speaker_2": {
        "alias": "Prabowo",
        "path": "/home/alim/alim_workspace/TTS_Test_Tool/CoquiTTS/dataset/LJSpeech-1.1/wavs/prabowo.wav",
        "sample_rate": 22050
    },
    "speaker_3": {
        "alias": "Jokowi",
        "path": "/home/alim/alim_workspace/TTS_Test_Tool/CoquiTTS/dataset/LJSpeech-1.1/wavs/jokowi.wav",
        "sample_rate": 22050
    }
}

# Initialize the TTS model
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Create the FastAPI application
app = FastAPI()

# Define allowed origins for CORS
origins = [
    "http://localhost:3002",  # Frontend local URL
<<<<<<< HEAD
    "http://192.168.0.26:3002",  # Frontend React local IP
=======
    "http://0.0.0.0:3002",  # Frontend React local IP
>>>>>>> 2c3d9cf169fc27cd8c127ed2d6d5c28e0919d0c7
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

# Function to resample audio using librosa
def resample_audio(file_path, target_sample_rate):
    # Load the audio file with its original sampling rate
    audio, original_sample_rate = librosa.load(file_path, sr=None)
    # Resample if the original sample rate is different from the target
    if original_sample_rate != target_sample_rate:
        audio = librosa.resample(audio, orig_sr=original_sample_rate, target_sr=target_sample_rate)
    return audio, target_sample_rate

@app.websocket("/ws/tts")
async def tts_websocket(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    max_token_limit = 400  # Adjust this limit according to the model's configuration
    try:
        while True:
            # Receive the data from the client
            data = await websocket.receive_text()
            request = data.split(",")  # Data format: "text,language,speaker"
            text = request[0]
            language = request[1]
            speaker = request[2]

            # Sanitize text by removing punctuation
            sanitized_text = text.translate(str.maketrans('', '', string.punctuation))

            # Validate the language and speaker
            if language not in language_aliases:
                await websocket.send_text(f"Unsupported language: {language}")
                continue

            if speaker not in speakers:
                await websocket.send_text(f"Unsupported speaker: {speaker}")
                continue

            # Truncate text if it exceeds the token limit
            if len(sanitized_text) > max_token_limit:
                sanitized_text = sanitized_text[:max_token_limit]
                await websocket.send_text(f"Warning: Text was truncated to {max_token_limit} characters.")

            # Get the speaker configuration
            speaker_config = speakers[speaker]
            speaker_wav = speaker_config["path"]
            sample_rate = speaker_config["sample_rate"]

            # Resample the speaker's audio if necessary
            resampled_audio, resampled_rate = await asyncio.to_thread(resample_audio, speaker_wav, sample_rate)
            resampled_path = "output/resampled_speaker.wav"
            # Save the resampled audio to a file
            sf.write(resampled_path, resampled_audio, resampled_rate)

            # Process text-to-speech with the resampled audio
            try:
                wav = await asyncio.to_thread(tts.tts, text=sanitized_text, speaker_wav=resampled_path, language=language)
            except AssertionError as e:
                await websocket.send_text(f"Error during synthesis: {str(e)}")
                continue

            # Save the generated audio to a file
            output_path = "output/output_multispeaker.wav"
            sf.write(output_path, wav, sample_rate)

            # Send the audio file to the frontend
            with open(output_path, "rb") as audio_file:
                audio_data = audio_file.read()
                await websocket.send_bytes(audio_data)

    except WebSocketDisconnect:
        print("Client disconnected")

# Endpoint to fetch the list of speakers and their aliases
@app.get("/speakers")
async def get_speakers():
    return {key: value["alias"] for key, value in speakers.items()}

# Endpoint to fetch the list of supported languages and their aliases
@app.get("/languages")
async def get_languages():
    return language_aliases
