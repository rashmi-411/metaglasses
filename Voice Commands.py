import shutil
import torchaudio
from torchaudio.datasets import SPEECHCOMMANDS

# Remove existing data
shutil.rmtree('./data', ignore_errors=True)

# Download fresh
dataset = SPEECHCOMMANDS(root='./data', download=True)
waveform, sample_rate, label, *_ = dataset[0]
print(f"Label: {label}")
torchaudio.save("sample.wav", waveform, sample_rate)
