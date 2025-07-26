import numpy as np
from scipy.io.wavfile import write, read
from scipy.io import wavfile
import io
import os
import tempfile
import telebot
from telebot import types
import subprocess

# Your bot token here
BOT_TOKEN = "-"
bot = telebot.TeleBot(BOT_TOKEN)

letras = "abcdefghijklmnopqrstuvwxyz"
FS = 22050
numcode = ['22', '222', '2222', '33', '333', '3333', '44', '444', '4444', '55', '555', '5555', '66', '666', '6666', '77', '777', '7777', '77777', '88', '888', '8888', '99', '999', '9999', '99999']

def encpalabranum(palabra, sep="#", space="*"):
    palabraenc = ""
    for i in palabra:
        if i.isdigit():
            palabraenc += str(int(i))
            palabraenc += sep
        else:
            for ii in range(len(numcode)):
                if i == letras[ii]:
                    palabraenc += numcode[ii]
                    palabraenc += sep
                    break
            if i == " ":
                palabraenc += space
                palabraenc += sep
    return sep + palabraenc

def decpalabranum(palbraenc, sep="#", space="*"):
    palabra = ""
    caracter = ""
    for i in palbraenc:
        if i == sep:
            if caracter == space:
                palabra += " "
            else:
                if caracter in numcode:
                    palabra += letras[numcode.index(caracter)]
                else:
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

def convert_audio_to_wav(input_file, output_file):
    """Convert audio file to WAV using ffmpeg"""
    cmd = [
        'ffmpeg', '-i', input_file, 
        '-ar', str(FS),  # Set sample rate
        '-ac', '1',      # Convert to mono
        '-y',            # Overwrite output file
        output_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def text_to_audio(text):
    encoded_text = encpalabranum(text.lower())
    print(f"Encoded: {encoded_text}")  # Debug
    audio_data = dtmf_dial(encoded_text)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    print(f"\nSample rate: {FS}, Data type: {audio_data.dtype}, Shape: {audio_data.shape}")  # Debug
    print(f"Audio stats: min={np.min(audio_data)}, max={np.max(audio_data)}, mean={np.mean(audio_data)}")  # Debug
    write(temp_file.name, FS, audio_data)
    print(f"Audio saved to: {temp_file.name}")  
    temp_file.close()

    return temp_file.name

def audio_to_text(audio_file_path):
    # Read audio file
    rate, audio_data = wavfile.read(audio_file_path)
    print(f"\nSample rate: {rate}, Data type: {audio_data.dtype}, Shape: {audio_data.shape}")  # Debug
    print(f"Audio stats: min={np.min(audio_data)}, max={np.max(audio_data)}, mean={np.mean(audio_data)}")  # Debug
    
    # Decode DTMF
    decoded_number = dtmf_decode(audio_data)
    print(f"Decoded numbers: {decoded_number}")  # Debug
    
    decoded_text = decpalabranum(''.join(decoded_number))
    print(f"Decoded text: {decoded_text}")  # Debug
    return decoded_text
    
    
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🎵 Welcome to DTMF Audio Bot! 🎵

This bot can:
📝 Convert your text messages to DTMF audio
🎧 Convert DTMF audio back to text

How to use:
• Send me any text message and I'll convert it to audio
• Send me an audio file and I'll decode it back to text

Just type something or send an audio file to get started!
"""
    bot.reply_to(message, welcome_text)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text
    
    # Skip commands
    if text.startswith('/'):
        return
    
    bot.reply_to(message, f"🔄 Converting text to audio: '{text}'")
    
    # Generate audio from text
    audio_file_path = text_to_audio(text)
    
    # Send audio file
    with open(audio_file_path, 'rb') as audio_file:
        bot.send_audio(
            message.chat.id, 
            audio_file,
            caption=f"🎵 Audio generated from: '{text}'",
            title="DTMF Audio"
        )
    
    # Clean up temporary file
    os.unlink(audio_file_path)

@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    bot.reply_to(message, "🎧 Processing your audio...")
    
    # Get file info
    if message.content_type == 'voice':
        file_info = bot.get_file(message.voice.file_id)
    else:
        file_info = bot.get_file(message.audio.file_id)
    
    # Download the file
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Save to temporary file with original extension
    file_extension = os.path.splitext(file_info.file_path)[1] or '.ogg'
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
    temp_input.write(downloaded_file)
    temp_input.close()
    
    # Convert to WAV using ffmpeg
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_wav.close()
    
    if convert_audio_to_wav(temp_input.name, temp_wav.name):
        print(f"Processing audio file: {temp_wav.name}")  # Debug
        
        # Decode audio to text
        decoded_text = audio_to_text(temp_wav.name)
        
        if decoded_text.strip():
            bot.reply_to(message, f"📝 Decoded text: '{decoded_text}'")
        else:
            bot.reply_to(message, "❌ Could not decode the audio. Make sure it contains DTMF tones.")
    else:
        bot.reply_to(message, "❌ Could not process audio file. Make sure ffmpeg is installed.")
    
    # Clean up temporary files
    os.unlink(temp_input.name)
    if os.path.exists(temp_wav.name):
        os.unlink(temp_wav.name)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    # Check if it's an audio file
    if message.document.mime_type and message.document.mime_type.startswith('audio/'):
        bot.reply_to(message, "🎧 Processing your audio file...")
        
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_extension = os.path.splitext(message.document.file_name)[1] or '.wav'
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_input.write(downloaded_file)
        temp_input.close()
        
        # Convert to proper WAV format
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_wav.close()
        
        if convert_audio_to_wav(temp_input.name, temp_wav.name):
            decoded_text = audio_to_text(temp_wav.name)
            
            if decoded_text.strip():
                bot.reply_to(message, f"📝 Decoded text: '{decoded_text}'")
            else:
                bot.reply_to(message, "❌ Could not decode the audio. Make sure it contains DTMF tones.")
        else:
            bot.reply_to(message, "❌ Could not process audio file. Make sure ffmpeg is installed.")
        
        os.unlink(temp_input.name)
        if os.path.exists(temp_wav.name):
            os.unlink(temp_wav.name)
    else:
        bot.reply_to(message, "Please send an audio file or text message.")

if __name__ == '__main__':
    print("🤖 DTMF Bot is starting...")
    print("Make sure to set your BOT_TOKEN!")
    print("Install required packages: pip install pyTelegramBotAPI numpy scipy")
    print("Make sure ffmpeg is installed on your system")
    bot.infinity_polling()