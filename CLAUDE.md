# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Voice CV Agent — a FastAPI webhook server that powers a phone-based AI assistant. Callers ask questions about a resume; the agent transcribes their speech via Groq Whisper, answers via Groq Llama, and speaks the reply back using Twilio TTS.

## Tech Stack

- **Telephony**: Twilio (`<Record>` for audio capture, `<Say>` for TTS)
- **STT**: Groq Whisper (`whisper-large-v3-turbo`)
- **LLM**: Groq (`llama-3.3-70b-versatile`)
- **Resume Parsing**: PyMuPDF (`fitz`)
- **Backend**: FastAPI + uvicorn
- **Tunneling**: ngrok (local dev)

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn main:app --reload --port 8000

# Expose via ngrok (separate terminal)
ngrok http 8000
```

## Architecture

### Call Flow

```
Caller → Twilio → POST /voice  → TwiML: <Say> greeting + <Record>
                 → POST /transcribe (RecordingUrl in body)
                   1. Download .mp3 from Twilio (HTTP Basic Auth: SID:token)
                   2. Groq Whisper → transcript
                   3. Groq Llama + resume context → answer
                   → TwiML: <Say> answer + <Record>  (loops back)
```

### Why `<Record>` not `<Gather input="speech">`

`<Gather>` uses Twilio's own paid STT. `<Record>` gives raw audio → we use Groq Whisper for free at higher quality.

### Resume Loading

`resume_parser.py` parses `resume/resume.pdf` once at startup using PyMuPDF. The full text is stored as a module-level global and injected into every LLM system prompt.

## File Map

| File | Purpose |
|---|---|
| `main.py` | FastAPI app — `/voice`, `/transcribe`, `/hangup` routes |
| `resume_parser.py` | PDF → plain text (loaded once at startup) |
| `llm_client.py` | `transcribe(audio_bytes)` and `answer(question, resume_text)` using Groq |
| `resume/resume.pdf` | The actual resume file (user must supply) |
| `.env` | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `GROQ_API_KEY` |

## Environment Variables

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```

## Twilio Webhook Setup

After starting ngrok, set the webhook in Twilio Console:
- Phone Number → "A call comes in" → Webhook → `POST https://<ngrok-url>/voice`

## LLM Prompt Convention

System prompt instructs the LLM to answer in 2–3 sentences max (voice-friendly brevity). Resume text is injected as part of the system prompt, not as a user message.

# Github Related Instructions
- Please follow this github documentation whenever writing commits:https://www.conventionalcommits.org/en/v1.0.0/
