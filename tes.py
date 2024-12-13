import torch
from TTS.api import TTS

# Tentukan perangkat (GPU atau CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"


# Inisialisasi TTS dengan model bark
tts = TTS("tts_models/multilingual/multi-dataset/bark").to(device)

# Jalankan TTS untuk mengonversi teks ke suara
# Pastikan Anda memberikan path yang benar untuk file speaker wav dan bahasa
wav = tts.tts(text="", speaker_wav="/home/alim/alim_workspace/TTS_Test_Tool/CoquiTTS/datavoice/Nita.wav")

# Teks ke suara dan simpan ke file
tts.tts_to_file(text="こちらは句読点のない日本語の文です", speaker_wav="/home/alim/alim_workspace/TTS_Test_Tool/CoquiTTS/datavoice/Nita.wav", file_path="output.wav")
