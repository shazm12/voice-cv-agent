# Voice CV Agent

A phone-based AI assistant that answers questions about a resume over a real call. Callers speak their questions, the agent transcribes and understands them, then speaks the answer back — all in real time.

## Tech Stack

| Layer | Tool |
|---|---|
| Telephony | Twilio |
| Speech-to-Text | Groq Whisper (`whisper-large-v3-turbo`) |
| Language Model | Groq Llama (`llama-3.3-70b-versatile`) |
| Resume Parsing | PyMuPDF |
| Backend | FastAPI |
| Tunneling (local dev) | ngrok |

## Endpoints

| Endpoint | What it does |
|---|---|
| `POST /voice` | Entry point for an incoming call — greets the caller and starts listening |
| `POST /transcribe` | Receives the caller's recorded audio, transcribes it, generates an answer, and speaks it back |
