import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import numpy as np
import io
from scipy.io.wavfile import write
from pydub import AudioSegment

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        super().__init__()
        self.audio_data = None

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convert audio frame to numpy array
        self.audio_data = frame.to_ndarray()
        return frame

    def get_audio_bytes(self):
        if self.audio_data is not None:
            return self.audio_data.tobytes()
        else:
            return None

st.title("Audio Recorder")

def save_audio(audio_data):
    # Convert numpy array to WAV format and save
    audio = np.array(audio_data, dtype=np.int16)
    buffer = io.BytesIO()
    write(buffer, 16000, audio)  # Sample rate should match your WebRTC settings
    buffer.seek(0)
    return buffer.getvalue()

def process_audio(audio_bytes):
    # Convert byte data to AudioSegment
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
    output = io.BytesIO()
    audio.export(output, format="wav")
    return output.getvalue()

webrtc_ctx = webrtc_streamer(
    key="audio-stream",
    mode=WebRtcMode.RECVONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False}
)

if webrtc_ctx.audio_processor:
    audio_bytes = webrtc_ctx.audio_processor.get_audio_bytes()
    if audio_bytes:
        st.write("Audio data received")
        audio_data = process_audio(audio_bytes)
        st.audio(audio_data, format="audio/wav")
    else:
        st.write("No audio data available")
else:
    st.write("Audio Processor is not available")
