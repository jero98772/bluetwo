import streamlit as st
import numpy as np
from scipy.io.wavfile import write, read
from scipy.io import wavfile
#https://github.com/stefanrmmr/streamlit-audio-recorder
#streamlit run main.py 
import io

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

FS = 24000

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



def save_audio(x):
    x = np.asarray(x)
    x = (x).astype(np.int16)
    buffer = io.BytesIO()
    write(buffer, FS, x)
    buffer.seek(0)

    return x
def save_audio(x,name):
# Convert to 16-bit PCM format

    write('sine_wave.wav', FS, x)
# Streamlit UI
st.title("DTMF Encoding and Decoding")

text_input = st.text_input("Enter text to encode:")

if st.button("Encode and Generate Audio"):
    encoded_text = encpalabranum(text_input)
    st.write(f"Encoded text: {encoded_text}")

    audio_data = dtmf_dial(encoded_text)
    #audio_file = save_audio(audio_data)
    name='sine_wave.wav'
    save_audio(audio_data,name)

    _, audio_data = wavfile.read(name)

    st.audio(audio_data, format='audio/wav',sample_rate=FS)

    # Decode and display
    #audio_array, _ = read(io.BytesIO(audio_file.getvalue()))
    #_, audio_data = read(audio_file)
    decoded_number = dtmf_decode(audio_data)
    decoded_text = decpalabranum(decoded_number)
    st.write(f"Decoded text: {decoded_text}")

