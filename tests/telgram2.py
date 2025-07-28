import numpy as np
from scipy.io.wavfile import write, read
from scipy.io import wavfile
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from telegram.constants import ChatAction
import io

letras = "abcdefghijklmnopqrstuvwxyz"
FS = 22050
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

# Function to handle the recorded audio
def process_audio(audio_bytes):
    # Convert the byte data to an AudioSegment
    audio = AudioSegment.from_file(BytesIO(audio_bytes), format="webm")
    # Export as WAV
    output = BytesIO()
    audio.export(output, format="wav")
    return output.getvalue()

"""
def save_audio(x):
    x = np.asarray(x)
    x = (x).astype(np.int16)
    buffer = io.BytesIO()
    write(buffer, FS, x)
    buffer.seek(0)

    return x
"""
def save_audio(x,name):
# Convert to 16-bit PCM format

    write('sine_wave.wav', FS, x)


"""
noise = np.random.normal(0, 0.5, audio_data.shape)
noisy_array = audio_data# + noise
print(noisy_array)
save_audio(noisy_array,name)

_, audio_data = wavfile.read(name)

print(f"\nSample rate: {FS}, Data type: {audio_data.dtype}, Shape: {audio_data.shape}")  # Debug

print(f"Audio stats: min={np.min(audio_data)}, max={np.max(audio_data)}, mean={np.mean(audio_data)}")  # Debug

decoded_number = dtmf_decode(audio_data)
decoded_text = decpalabranum(decoded_number)
print(decoded_number)
print(decoded_text)

"""


from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from scipy.io import wavfile

TOKEN = ""
SAMPLE_AUDIO = 'sine_wave.wav'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action=ChatAction.TYPING
    )
    await update.message.reply_text("Hola")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("audio")
    user = update.message.from_user
    message = update.message
    
    # Get audio file object
    if message.audio:
        audio_file = message.audio
    elif message.voice:
        audio_file = message.voice
    else:
        await message.reply_text("No se pudo obtener el archivo de audio")
        return
    
    # Download the file with original extension
    file = await context.bot.get_file(audio_file.file_id)
    
    # Download to temporary file first (Telegram files are usually OGG/MP4)
    temp_file = f"temp_audio_{audio_file.file_id}"
    await file.download_to_drive(temp_file)
    
    # Convert to WAV if needed (you may need to add conversion logic here)
    # For now, try to read directly but handle the conversion
    try:
        sample_rate, audio_data = wavfile.read(temp_file)
    except:
        # If direct read fails, you need to convert the file to WAV first
        # This requires ffmpeg or similar tool
        await message.reply_text("Error: No se pudo procesar el archivo de audio. Necesita conversión a WAV.")
        return
    
    decoded_number = dtmf_decode(audio_data)
    decoded_text = decpalabranum(decoded_number)
    print(decoded_number)
    print(decoded_text)    
    await message.reply_text(f"numero {decoded_number} texto {decoded_text}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(user_text)
    encoded_text = encpalabranum(user_text)
    audio_data = dtmf_dial(encoded_text)
    print(encoded_text)
    print(audio_data)
    
    # Make sure save_audio creates a proper WAV file
    save_audio(audio_data, SAMPLE_AUDIO)
    
    # Send audio file and close it properly
    with open(SAMPLE_AUDIO, 'rb') as audio_file:
        await update.message.reply_audio(
            audio=audio_file,
            caption=f"Aquí tienes un audio de {user_text} significa {encoded_text}"
        )

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("Bot en funcionamiento...")
    app.run_polling()