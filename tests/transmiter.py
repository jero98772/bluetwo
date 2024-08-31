import numpy as np
from scipy.io.wavfile import write, read
import sounddevice as sd
import io

letras = "abcdefghijklmnopqrstuvwxyz"
numcode = ['22', '222', '2222', '33', '333', '3333', '44', '444', '4444', '55', '555', '5555', '66', '666', '6666', '77', '777', '7777', '77777', '88', '888', '8888', '99', '999', '9999', '99999']

def encpalabranum(palabra, sep="#", space="*"):
    palabraenc = ""
    for i in palabra:
        try:
            palabraenc += str(int(i))
            palabraenc += sep
        except:
            pass
        for ii in range(len(numcode)):
            if i == letras[ii]:
                palabraenc += numcode[ii]
                palabraenc += sep
        if i == " ":
            palabraenc += space
            palabraenc += sep
    return sep + palabraenc

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
        s = np.sin(2 * np.pi * DTMF[d][0] / FS * n) + np.sin(2 * np.pi * DTMF[d][1] / FS * n)
        x = np.concatenate((x, s, np.zeros(int(SPACE * FS))))
    return x

def save_audio(x, name='sine_wave.wav'):
    x = np.asarray(x)
    x = (x).astype(np.int16)
    write(name, FS, x)
    print(f"Audio saved as {name}")

def play_audio(audio_data, fs):
    sd.play(audio_data, samplerate=fs)
    sd.wait()  #

name='sine_wave.wav'
# Encode and transmit the text
text_input = input("Enter text to encode: ")
encoded_text = encpalabranum(text_input)
audio_data = dtmf_dial(encoded_text)
print("Encoded DTMF tones:", encoded_text)
save_audio(audio_data)

fs, audio_data = read(name)  # Load the WAV file
play_audio(audio_data, fs)
