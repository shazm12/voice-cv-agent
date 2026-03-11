# Voice CV Agent

A phone-based AI agent that answers questions about a resume and GitHub profile over a real call. Callers speak their questions, the agent transcribes and understands them, then speaks the answer back — all in real time.

The LLM runs as a tool-calling agent and can fetch live GitHub data (repos, project details, profile summary) on demand using the GitHub API.

## Tech Stack

| Layer | Tool |
|---|---|
| Telephony | Twilio |
| Speech-to-Text | Groq Whisper (`whisper-large-v3-turbo`) |
| Language Model | Groq Llama (`llama-3.3-70b-versatile`) with tool calling |
| GitHub API | PyGithub |
| Resume Parsing | PyMuPDF |
| Backend | FastAPI |
| Tunneling (local dev) | ngrok |

## Endpoints

| Endpoint | What it does |
|---|---|
| `POST /voice` | Entry point for an incoming call — greets the caller and starts listening |
| `POST /transcribe` | Receives the caller's recorded audio, transcribes it, generates an answer, and speaks it back |
