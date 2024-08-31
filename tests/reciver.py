import numpy as np
from scipy.io.wavfile import write, read
from scipy.io import wavfile
import io
from pydub import AudioSegment
from pydub.playback import play
import sounddevice as sd
import time

letras = "abcdefghijklmnopqrstuvwxyz"
numcode = ['22', '222', '2222', '33', '333', '3333', '44', '444', '4444', '55', '555', '5555', '66', '666', '6666', '77', '777', '7777', '77777', '88', '888', '8888', '99', '999', '9999', '99999']

def decpalabranum(palbraenc, sep="#", space="*"):
    palabra = ""
    caracter = ""
    for i in palbraenc:
        if i == sep:
            if caracter == space:
                palabra += " "
            else:
                try:
                    palabra += letras[numcode.index(caracter)]
                except:
                    palabra += str(caracter)
            caracter = ""
        else:
            caracter += i
    return palabra

FS = 24000

def dtmf_split(x, win=240, th=200):
    edges = []

    w = np.reshape(x[:int(len(x) / win) * win], (-1, win))
    we = np.sum(w * w, axis=1)
    L = len(we)

    ix = 0
    while ix < L:
        while ix < L and we[ix] < th:
            ix = ix + 1
        if ix >= L:
            break    # ending on silence
        iy = ix
        while iy < L and we[iy] > th:
            iy = iy + 1
        edges.append((ix * win, iy * win))
        ix = iy

    return edges

def dtmf_decode(x, edges=None):
    LO_FREQS = np.array([697.0, 770.0, 852.0, 941.0])
    HI_FREQS = np.array([1209.0, 1336.0, 1477.0])

    KEYS = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['*', '0', '#']]

    LO_RANGE = (680.0, 960.0)
    HI_RANGE = (1180.0, 1500.0)

    number = []

    if edges is None:
        edges = dtmf_split(x)
    for g in edges:
        X = abs(np.fft.fft(x[g[0]:g[1]]))
        N = len(X)
        res = float(FS) / N

        a = int(LO_RANGE[0] / res)
        b = int(LO_RANGE[1] / res)
        lo = a + np.argmax(X[a:b])
        a = int(HI_RANGE[0] / res)
        b = int(HI_RANGE[1] / res)
        hi = a + np.argmax(X[a:b])

        row = np.argmin(abs(LO_FREQS - lo * res))
        col = np.argmin(abs(HI_FREQS - hi * res))

        number.append(KEYS[row][col])
    return number


def save_audio(x, name='recorded.wav'):
    write(name, FS, x)
    print(f"Audio saved as {name}")

device_info = sd.query_devices(sd.default.device['input'], 'input')
supported_sample_rates = device_info['default_samplerate']

print(f"Default Sample Rate: {supported_sample_rates} Hz")

# Set a compatible sample rate
fs = int(supported_sample_rates)  # Adjust this if needed
#fs = 24000

duration = 5  # Duration of the recording in seconds

def record_audio():
    print("Recording...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    print("Recording complete.")
    return audio_data

# Record and decode the audio
audio_data = record_audio()
save_audio(audio_data)
decoded_number = dtmf_decode(audio_data)
decoded_text = decpalabranum(decoded_number)
print("Decoded DTMF tones:", decoded_number)
print("Decoded text:", decoded_text)
