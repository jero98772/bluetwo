import pyaudio
import wave
from scipy.io import wavfile
import numpy as np
# Configuration
FS = 22050
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1              # Number of audio channels (1 for mono, 2 for stereo)
RATE = 44100              # Sample rate (samples per second)
CHUNK = 1024              # Number of audio frames per buffer
RECORD_SECONDS = 5        # Number of seconds to record
WAVE_OUTPUT_FILENAME = "output.wav"  # Output file name

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open stream
try:
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
except OSError as e:
    print(f"Error opening stream: {e}")
    audio.terminate()
    exit(1)

print("Recording...")

frames = []

# Record data
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    except IOError as e:
        print(f"Error: {e}")

print("Finished recording.")

# Stop and close the stream
stream.stop_stream()
stream.close()
audio.terminate()

# Save the recorded data as a WAV file
with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print(f"File saved as {WAVE_OUTPUT_FILENAME}")


def decpalabranum(palbraenc,sep="#",space="*"):
    palabra = ""
    caracter = ""
    for i in palbraenc:
        if i ==  sep:
            if caracter == space:
                palabra += " "
            else:
                try:
                    palabra += letras[numcode.index(caracter)]
                except:
                    palabra += str(caracter)
            caracter = ""
        else:
            caracter+=i
    return palabra
def dtmf_split(x, win=240, th=200):
    edges = []
    
    w = np.reshape(x[:int(len(x)/win)*win], (-1, win))
    we = np.sum(w * w, axis=1)
    L = len(we)
    
    ix = 0
    while ix < L:
        while ix < L and we[ix] < th:
            ix = ix+1
        if ix >= L:
            break    # ending on silence
        iy = ix
        while iy < L and we[iy] > th:
            iy = iy+1
        edges.append((ix * win, iy * win))
        ix = iy
    
    return edges

def dtmf_decode(x, edges = None):
    # the DTMF frequencies
    LO_FREQS = np.array([697.0, 770.0, 852.0, 941.0])
    HI_FREQS = np.array([1209.0, 1336.0, 1477.0])

    KEYS = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['*', '0', '#']]
    
    # frequency ranges to search for low and high DTMF tones
    LO_RANGE = (680.0, 960.0)
    HI_RANGE = (1180.0, 1500.0)

    number = []
    
    # now examine each tone in turn. the freqency mapping on the DFT
    #  axis will be dependent on the length of the data vector
    if edges is None:
        edges = dtmf_split(x)
    for g in edges:
        # compute the DFT of the tone segment
        X = abs(np.fft.fft(x[g[0]:g[1]]))
        N = len(X)
        # compute the resolution in Hz of a DFT bin
        res = float(FS) / N
        
        # find the peak location within the low freq range
        a = int(LO_RANGE[0] / res)
        b = int(LO_RANGE[1] / res)
        lo = a + np.argmax(X[a:b])
        # find the peak location within the high freq range
        a = int(HI_RANGE[0] / res)
        b = int(HI_RANGE[1] / res)
        hi = a + np.argmax(X[a:b])
      
        # now match the results to the DTMF frequencies
        row = np.argmin(abs(LO_FREQS - lo * res))
        col = np.argmin(abs(HI_FREQS - hi * res))

        # and finally convert that to the pressed key
        number.append(KEYS[row][col])
    return number


_, audio_data = wavfile.read(WAVE_OUTPUT_FILENAME)
decoded_number = dtmf_decode(audio_data)
decoded_text = decpalabranum(decoded_number)
print("Decoded number",decoded_number)
print("Decoded text",decoded_text)