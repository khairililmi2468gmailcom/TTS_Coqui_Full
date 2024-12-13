import torch
from TTS.api import TTS

# Tentukan perangkat (GPU atau CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Inisialisasi TTS dengan model bark
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print("Is Multilingual: ", tts.is_multi_lingual)
print("Is Multi Speaker: ", tts.is_multi_speaker)

tts2 = TTS("tts_models/multilingual/multi-dataset/bark").to(device)
print("Is Multilingual: ", tts2.is_multi_lingual)
print("Is Multi Speaker: ", tts2.is_multi_speaker)

# Tentukan speaker_id yang ingin digunakan
#speaker_id = "v2/en_speaker_0"  # Tentukan speaker ID yang ingin digunakan

# Jalankan TTS untuk mengonversi teks ke suara dan simpan ke file
#tts.tts_to_file(
   # text="こちらは句読点のない日本語の文です", 
  #  speaker_id=speaker_id, 
 #   file_path="output.wav"
#)
