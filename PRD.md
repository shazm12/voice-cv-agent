# PRD.md — Voice CV Agent (POC)

## Context
Build a minimal voice AI agent that knows the contents of a PDF resume and answers questions about it over a real phone call. The goal is a working POC using only free-tier services, callable from any phone.

---

## Tech Stack (All Free Tier)

| Layer | Service | Free Tier |
|---|---|---|
| Telephony | **Twilio** | $15 trial credit, real phone number |
| STT | **Groq Whisper** (`whisper-large-v3-turbo`) | Free tier (no credit card) |
| LLM | **LangChain + ChatGroq** (`llama-3.3-70b-versatile`) | Free tier |
| TTS | **Twilio `<Say>`** | Free (built-in, no extra service) |
| Resume Parsing | **PyMuPDFLoader** (`langchain-community`) | Free, local |
| Backend | **Python + FastAPI** | Free, local |
| Tunneling | **ngrok** | Free tier (1 tunnel) |

> **TTS upgrade path**: Replace Twilio `<Say>` with ElevenLabs (10K chars/month free) for a more natural voice later.

---

## Architecture

```
[Caller] ──calls──► [Twilio phone number]
                          │
                    POST /voice (greeting)
                          │
                    ◄── TwiML: <Say> greeting + <Record>
                          │
               [Caller speaks their question]
                          │
                    POST /transcribe (with RecordingUrl)
                          │
                    Download audio from Twilio
                          │
                    Groq Whisper STT
                          │
                    Groq Llama LLM
                    (resume as system prompt context)
                          │
                    ◄── TwiML: <Say> answer + <Record> (loop)
```

### Why `<Record>` over `<Gather input="speech">`
- `<Gather>` uses Twilio's own STT (costs from credit balance)
- `<Record>` gives us the raw audio file → we run Groq Whisper for free
- Better STT quality with Groq Whisper v3

---

## Project Structure

```
voice-cv-agent/
├── main.py              # FastAPI app — all webhook routes
├── resume_parser.py     # PDF → plain text via PyMuPDF
├── llm_client.py        # Groq client (STT + LLM)
├── resume/
│   └── resume.pdf       # User's resume file
├── requirements.txt
└── .env                 # TWILIO_*, GROQ_API_KEY
```

---

## Implementation Plan

### Step 0 — Project Scaffolding Files
- Create `CLAUDE.md` at project root with project context, stack overview, key conventions, and file map for AI assistant reference
- Create `PRD.md` at project root with this POC plan as a product requirements document for ongoing reference

### Step 1 — Project Setup
- `requirements.txt`: `fastapi`, `uvicorn`, `groq`, `pymupdf`, `python-dotenv`, `httpx`, `langchain-groq`, `langchain-core`, `langchain-community`
- `.env` template with `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `GROQ_API_KEY`

### Step 2 — Resume Parser (`resume_parser.py`)
- Use `PyMuPDFLoader("resume/resume.pdf", mode="single")` from `langchain_community`
- Load once at app startup and store the text globally

### Step 3 — LangChain Client (`llm_client.py`)
- **`transcribe(audio_bytes)`**: Direct Groq SDK call (Whisper is not in LangChain) → return transcript string
- **`answer(question, resume_text)`**: LCEL chain:
  ```python
  prompt = ChatPromptTemplate.from_messages([
      ("system", "Answer questions about this resume in 2-3 sentences.\n\n{resume}"),
      ("human", "{question}")
  ])
  chain = prompt | ChatGroq(model="llama-3.3-70b-versatile") | StrOutputParser()
  ```
  Call `chain.invoke({"resume": resume_text, "question": question})`

### Step 4 — FastAPI App (`main.py`)

#### `POST /voice` — Entry point (Twilio calls this on incoming call)
```xml
<Response>
  <Say>Hi! I'm [Name]'s AI assistant. Ask me anything about their resume after the beep.</Say>
  <Record maxLength="15" action="/transcribe" transcribe="false" playBeep="true"/>
</Response>
```

#### `POST /transcribe` — Called by Twilio after recording
1. Get `RecordingUrl` from Twilio POST body
2. Download the `.mp3` audio using `httpx` (with Twilio auth)
3. Send audio to Groq Whisper → get transcript
4. Send transcript + resume text to Groq Llama → get answer
5. Return TwiML:
```xml
<Response>
  <Say>{answer}</Say>
  <Record maxLength="15" action="/transcribe" transcribe="false" playBeep="true"/>
</Response>
```
This loops — caller can keep asking questions.

#### `POST /hangup` — Optional graceful exit
- Detect phrases like "goodbye", "thanks" in transcript → return `<Hangup/>`

### Step 5 — Local Run + ngrok Tunnel
```bash
uvicorn main:app --reload --port 8000
ngrok http 8000
```
Set ngrok URL as Twilio webhook for the phone number.

### Step 6 — Twilio Configuration
- Buy a phone number in Twilio Console (uses trial credit, ~$1/month)
- Set webhook: `POST https://<ngrok-url>/voice` for "A call comes in"

---

## Key Implementation Details

- **Resume loaded at startup**: parsed once, injected as system prompt on every LLM call
- **Audio download**: Twilio recordings require HTTP Basic Auth (`account_sid:auth_token`)
- **Response conciseness**: LLM system prompt instructs 2-3 sentence answers (voice-friendly)
- **Loop**: Every `/transcribe` response includes another `<Record>` to keep conversation going
- **Timeout handling**: `<Record timeout="5">` — hangs up if no speech detected for 5s

---

## Environment Variables

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```
---

## Verification / Testing

1. Add `resume/resume.pdf` to the project
2. `pip install -r requirements.txt`
3. Start server: `uvicorn main:app --reload`
4. Start tunnel: `ngrok http 8000`
5. Set ngrok HTTPS URL as Twilio webhook
6. Call the Twilio number and ask questions like:
   - "What programming languages does this person know?"
   - "Where did they go to university?"
   - "What was their most recent job?"
7. Verify answers are accurate to the resume content

---

## Phase 2 — GitHub Tool Calling (Agent Upgrade)

The LLM is being upgraded from a simple prompt-response chain to a **tool-calling agent**. This allows callers to ask questions about GitHub activity (repos, projects, profile) in addition to the resume.

### What Changes

- `llm_client.py`: Replace the static LCEL chain with a `bind_tools` agentic loop. The LLM can now decide at runtime whether to call a GitHub tool or answer directly.
- `github_tools.py` (new): PyGithub client + 3 read-only LangChain tools exposed to the LLM.
- `pyproject.toml`: Add `PyGithub>=2.6.1`.
- `.env`: Add `GITHUB_TOKEN` (classic PAT, `public_repo` read scope).
- `main.py`: No changes — `answer()` signature is preserved.

### GitHub Tools Available to the Agent

| Tool | Trigger |
|---|---|
| `list_public_repos` | "What are your GitHub projects?" |
| `get_repo_details` | "Tell me about your [repo] project" |
| `get_github_profile_summary` | "What does your GitHub look like?" |

### Agentic Loop Design

```
HumanMessage (question)
        │
   LLM (bind_tools)
        │
   tool_calls?  ──yes──► execute tool(s) ──► ToolMessage(result)
        │                                           │
       no                                     back to LLM
        │
   Final answer (2–3 sentences, voice-friendly)
```

Max 4 iterations to prevent runaway tool calls. Every tool catches exceptions and returns a graceful fallback string — a GitHub API failure never breaks the voice call.

---

## Future Upgrades (post-POC)

- Replace `<Say>` with ElevenLabs TTS for a natural voice
- Add conversation history for multi-turn context
- Deploy to Railway/Render free tier to eliminate ngrok
