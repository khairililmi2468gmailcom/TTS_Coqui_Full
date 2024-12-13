import torch  # Tambahkan ini untuk menggunakan torch.cuda
from TTS.api import TTS

# Tentukan device yang akan digunakan
device = "cuda" if torch.cuda.is_available() else "cpu"

# Inisialisasi model TTS multi-speaker
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

wav = tts.tts(
    text="Hello, how are you today, are you fine?",
    speaker_wav="/home/alim/alim_workspace/TTS_Test_Tool/CoquiTTS/dataset/LJSpeech-1.1/wavs/LJ004-0223.wav",  # File suara referensi pembicara
    language="in"  # Kode bahasa ISO
)

# Simpan hasil ke file
tts.tts_to_file(
    text="Hello, how are you today, are you fine?",
    speaker_wav="/home/alim/alim_workspace/TTS_Test_Tool/CoquiTTS/dataset/LJSpeech-1.1/wavs/LJ004-0223.wav",
    language="in",
    file_path="output/output_multispeaker.wav"
)

