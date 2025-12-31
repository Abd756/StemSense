import torchaudio
import torch

print("Torchaudio version:", torchaudio.__version__)
print("Available backends:", torchaudio.list_audio_backends())

# Try to save a dummy wav
dummy_wav = torch.randn(1, 16000)
try:
    torchaudio.save("test_dummy.wav", dummy_wav, 16000)
    print("Saving successful!")
except Exception as e:
    print("Saving failed!")
    print(e)
