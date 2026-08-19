# Multimodal RAG Platform — Base (LLM Input Layer)

This is the first milestone from the architecture docs: a working chat
UI wired to an open-source LLM stack (**vLLM + LiteLLM**), with file
attachment and voice-recording affordances already in place so the
ingestion/transcription pipeline has somewhere to plug into next.

Nothing here is a toy stub pretending to be a chat box — the frontend
really streams tokens over SSE from a real FastAPI endpoint, which
really calls out to LiteLLM, which really proxies to vLLM.

```
multimodal-rag-platform/
├── backend/                     FastAPI app
│   ├── app/
│   │   ├── main.py              entrypoint, CORS, router mount
│   │   ├── core/
│   │   │   └── config.py        all env-driven settings (single source of truth)
│   │   ├── api/v1/
│   │   │   ├── router.py        aggregates every endpoint module
│   │   │   └── endpoints/
│   │   │       ├── chat.py      POST /api/v1/chat  (SSE streaming)
│   │   │       ├── upload.py    POST /api/v1/upload (file attachments)
│   │   │       └── health.py    GET  /api/v1/health
│   │   ├── services/llm/
│   │   │   ├── base.py          BaseLLMProvider — the interface everything else depends on
│   │   │   └── litellm_provider.py   the vLLM/LiteLLM adapter
│   │   └── schemas/chat.py      Pydantic request/response models
│   ├── litellm_config.yaml      routes LiteLLM -> your vLLM server
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                    React + Vite + TypeScript
    └── src/
        ├── main.tsx / App.tsx
        ├── components/
        │   ├── chat/            ChatInput, ChatWindow, MessageBubble, AttachmentChip, EmptyState
        │   └── layout/          Header, ThemeToggle
        ├── hooks/                useChat, useVoiceRecorder, useAutoResizeTextarea
        ├── lib/                  api.ts (SSE + upload calls), types.ts
        └── context/              ThemeContext (light/dark)
```

## Why this structure

Every folder maps to one of the "6 abstract interfaces" idea from your
architecture doc: `services/llm/base.py` defines a contract
(`BaseLLMProvider`), and `litellm_provider.py` is the only file that
knows LiteLLM/vLLM exist. When you later add transcription
(`services/transcription/`), doc parsing, or the vector store, you'll
follow the same pattern: interface + adapter, one new folder, one new
line in `router.py`. **You should never need to touch `main.py` or the
frontend to swap an underlying tool.**

On the frontend, `lib/api.ts` is the only file that knows the backend's
URL shape and the SSE wire format — components only ever call
`sendMessage`/`uploadFile` from hooks. If you later switch from SSE to
WebSockets for voice, you edit `api.ts` and `useChat.ts`; no component
changes.

---

## 1. Prerequisites

| Tool | Version | Why |
|---|---|---|
| Python | 3.10+ | backend |
| Node.js | 18+ | frontend (Vite) |
| A GPU host (or cloud GPU) | — | to run vLLM at usable speed. CPU works for testing with a tiny model but will be slow. |

## 2. Install everything

```bash
# --- Backend ---
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# vLLM is a separate heavy dependency (CUDA-linked) — install it only
# on the machine that will actually serve the model:
pip install vllm

# --- Frontend ---
cd ../frontend
npm install
```

## 3. Run the three processes (each in its own terminal)

**Terminal 1 — vLLM (the actual model server)**
```bash
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Meta-Llama-3.1-8B-Instruct \
  --port 8001
```
Swap the model for anything on Hugging Face that fits your GPU
(`Qwen/Qwen2.5-7B-Instruct` is a good lighter alternative). This is the
only place the actual model name is chosen at the inference layer.

**Terminal 2 — LiteLLM proxy**
```bash
cd backend
litellm --config litellm_config.yaml --port 4000
```
This exposes an OpenAI-compatible API on `:4000` and is what the
`model_name: local-llama3` in `litellm_config.yaml` maps to — that
`local-llama3` string is what `DEFAULT_MODEL` in `.env` references, and
it's the string the frontend never has to know about.

**Terminal 3 — FastAPI backend**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 4 — Frontend**
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** — the chat UI loads with a smooth
fade-in, an attach-file button, a mic button, a send button, and a
light/dark toggle in the header (persists across reloads via
`localStorage`, respects OS preference on first visit).

## 4. What's already wired vs. what's next

**Working now:**
- Streaming chat (token-by-token) from the browser all the way to vLLM
- File attach → uploaded to `/api/v1/upload`, shown as a chip on the
  composer and on the sent message
- Voice recording via `MediaRecorder` → uploaded as a `.webm` blob,
  shown as an attachment (transcription isn't wired yet — see below)
- Light/dark theme, responsive layout, keyboard send (Enter / Shift+Enter
  for newline)

**Deliberately stubbed, per your architecture doc's phasing:**
- `upload.py` returns metadata only — it doesn't persist to S3 or
  enqueue a Celery ingestion job yet
- No retrieval/RAG splice into `chat.py` yet — it's a direct LLM
  passthrough
- No auth (`BaseContextResolver` / JWT) yet
- Voice attachments aren't transcribed (Faster-Whisper adapter isn't
  built yet) — they're just uploaded as audio files today

Each of those is a new adapter behind an existing or new interface, not
a rewrite — that's the point of the structure above.

## 5. Opening this in Cursor

Open the **repo root** (`multimodal-rag-platform/`) as the workspace so
Cursor's indexing and search span both `backend/` and `frontend/`
together — most changes (e.g. adding an endpoint + wiring it into
`lib/api.ts`) touch both sides at once.


$env:DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/multimodal_rag"
echo $env:DATABASE_URL





"C:\Users\subha\Downloads\minio.exe" server "C:\minio\data" --console-address ":9001"