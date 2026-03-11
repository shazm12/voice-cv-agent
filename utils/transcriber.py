from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def transcribe_audio(audio_bytes: bytes) -> str:
    client = Groq()
    transcription = client.audio.transcriptions.create(
        file=("audio.mp3", audio_bytes, "audio/mpeg"),
        model="whisper-large-v3-turbo",
        language="en",
        response_format="text",
        temperature=0.0
    )
    return transcription
