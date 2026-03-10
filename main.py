from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse
import httpx
import os
from dotenv import load_dotenv
from resume_parser import load_resume
from transcriber import transcribe_audio
from llm_client import answer


load_dotenv()
app = FastAPI()

print("Loading resume data...")
resume_text = load_resume("resume/resume.pdf")
print("Resume data loaded successfully!")


@app.post("/voice")
async def voice():
    response = VoiceResponse()
    response.say("Hello caller, ask me anything about Shamik's profile.")
    response.record(
        max_length=10,
        action="/transcribe",
        transcribe=False,
        play_beep=True
    )

    return PlainTextResponse(str(response), media_type="text/xml")


@app.post("/transcribe")
async def transcribe(request: Request):
    form_data = await request.form()
    recording_url = form_data.get("RecordingUrl") + ".mp3"

    async with httpx.AsyncClient() as client:
        client_response = await client.get(
            recording_url,
            auth=(os.getenv("TWILIO_ACCOUNT_SID"),
                  os.getenv("TWILIO_AUTH_TOKEN"))
        )
    audio_bytes = client_response.content

    transcript = transcribe_audio(audio_bytes)
    llm_response = answer(transcript, resume_text)

    response = VoiceResponse()
    response.say(llm_response)
    response.record(max_length=15, action="/transcribe",
                    transcribe=False, play_beep=True)
    return PlainTextResponse(str(response), media_type="text/xml")
