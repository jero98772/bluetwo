import streamlit as st
import numpy as np
from scipy.io.wavfile import write, read
from scipy.io import wavfile
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase, ClientSettings
import av
import io
from pydub import AudioSegment
from io import BytesIO
FS = 22050
letras = "abcdefghijklmnopqrstuvwxyz"
numcode = ['22', '222', '2222', '33', '333', '3333', '44', '444', '4444', '55', '555', '5555', '66', '666', '6666', '77', '777', '7777', '77777', '88', '888', '8888', '99', '999', '9999', '99999']

def encpalabranum(palabra,sep="#",space="*"):
    palabraenc = ""
    for i in palabra:
        try:
            palabraenc+=str(int(i))
            palabraenc+=sep
        except:
            pass
        for ii in range(len(numcode)):
            if i == letras[ii]:
                palabraenc += numcode[ii]
                palabraenc+=sep
        if i == " ":
            palabraenc +=space
            palabraenc+=sep
    return sep+palabraenc


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


def dtmf_dial(number):
    DTMF = {
        '1': (697, 1209), '2': (697, 1336), '3': (697, 1477),
        '4': (770, 1209), '5': (770, 1336), '6': (770, 1477),
        '7': (852, 1209), '8': (852, 1336), '9': (852, 1477),
        '*': (941, 1209), '0': (941, 1336), '#': (941, 1477),        
    }
    MARK = 0.1
    SPACE = 0.1
    n = np.arange(0, int(MARK * FS))
    x = np.array([])
    for d in number:
        s = np.sin(2*np.pi * DTMF[d][0] / FS * n) + np.sin(2*np.pi * DTMF[d][1] / FS * n) 
        x = np.concatenate((x, s, np.zeros(int(SPACE * FS))))
    return x

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
            break
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

class AudioRecorder(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.frames.append(frame)
        return frame

    def get_audio_bytes(self):
        if len(self.frames) > 0:
            return b''.join([frame.to_ndarray().tobytes() for frame in self.frames])
        return None

client_settings = ClientSettings(
    media_stream_constraints={"audio": True, "video": False}
)

st.title("DTMF Encoding and Decoding")

ctx = webrtc_streamer(
    key="audio-recorder",
    mode=WebRtcMode.SENDRECV,
    client_settings=client_settings,
    audio_processor_factory=AudioRecorder
)

text_input = st.text_input("Enter text to encode:")

if st.button("Encode and Generate Audio"):
    encoded_text = encpalabranum(text_input)
    st.write(f"Encoded text: {encoded_text}")

    audio_data = dtmf_dial(encoded_text)
    name = 'sine_wave.wav'
    write(name, FS, audio_data.astype(np.int16))

    # Read and play the generated WAV file
    _, audio_data = wavfile.read(name)
    st.audio(audio_data, format='audio/wav', sample_rate=FS)

    decoded_number = dtmf_decode(audio_data)
    decoded_text = decpalabranum(decoded_number)
    st.write(f"Decoded text: {decoded_text}")

if st.button("Save and Decode Recorded Audio"):
    print("processor",ctx.audio_processor)
    if ctx.audio_processor:
        audio_bytes = ctx.audio_processor.get_audio_bytes()
        print("audio",audio_bytes)
        if audio_bytes:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
            output = io.BytesIO()
            audio.export(output, format="wav")
            wav_audio = output.getvalue()

            # Display the audio in Streamlit
            st.audio(wav_audio, format='audio/wav')
            
            # Convert WAV bytes to numpy array
            audio_array = np.frombuffer(wav_audio, dtype=np.int16)

            decoded_number = dtmf_decode(audio_array)
            decoded_text = decpalabranum(decoded_number)
            st.write(f"Decoded text: {decoded_text}")
        else:
            st.warning("No audio recorded yet!")
    else:
        st.warning("Audio processor not available!")
