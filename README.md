# bluetwo

This project encodes and decodes text using Dual-tone Multi-frequency (DTMF) signals. The code converts input text into a sequence of DTMF tones, saves the tones as a WAV file, and then decodes the audio back into the original text.

## Features

- **Text Encoding**: Converts input text into a numeric code, which is then converted into DTMF tones.
- **Audio Processing**: Generates a sine wave for each DTMF tone and saves it as a WAV file.
- **Text Decoding**: Extracts DTMF tones from the WAV file and decodes them back into the original text.
- **Supports English Alphabet and Digits**: The encoding scheme includes the full English alphabet and numbers.

## Requirements

- Python 3.x
- Required Python packages:
  - `numpy`
  - `scipy`
  - `pydub`

Install the dependencies using the following command:

```bash
pip install numpy scipy 
```

## How to Run

1. Save the script as `main.py`.

2. Run the script with Streamlit:

    ```bash
    python main.py
    ```

3. Enter the text you want to encode. The script will:
    - Encode the text into a numeric code.
    - Convert the code into DTMF tones.
    - Save the tones as a WAV file.
    - Decode the DTMF tones back into the original text.

## Code Explanation

### Encoding and Decoding

- `encpalabranum(palabra, sep="#", space="*")`: Encodes a word into a numeric code using a predefined mapping.
- `decpalabranum(palbraenc, sep="#", space="*")`: Decodes a numeric code back into the original text.

### DTMF Dialing

- `dtmf_dial(number)`: Generates DTMF tones for a given numeric code.

### DTMF Decoding

- `dtmf_split(x, win=240, th=200)`: Splits the DTMF signal into individual tones.
- `dtmf_decode(x, edges=None)`: Decodes the DTMF tones back into the corresponding numeric code.

### Audio Processing

- `process_audio(audio_bytes)`: Converts the recorded audio from bytes to a WAV file.
- `save_audio(x, name)`: Saves the generated audio to a WAV file.

## Example

- Input Text: `hola`
- Encoded Text: `#444#6666#5555#22#`
<audio controls>
  <source src="https://github.com/jero98772/bluetwo/raw/main/tests/hello.wav" type="audio/wav">
  Your browser does not support the audio element.
</audio>

- Decoded Text: `hola`

## Notes

- The script supports basic alphanumeric encoding. Spaces are represented by the `*` symbol.
- The WAV file is saved as `sine_wave.wav` in the working directory.
