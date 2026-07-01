# CodeMentor-AI
# CodeMentor AI — Personalized GenAI Coding Tutor

IEEE TechForGood 2026 | Group 031

## Project Structure

```
codementor-ai/
├── frontend/          # React + Vite + Monaco Editor
│   └── src/
│       ├── components/    # Reusable UI components
│       ├── pages/         # Route-level pages
│       ├── hooks/         # Custom React hooks
│       ├── utils/         # Helpers (prompt builder, skill engine)
│       └── context/       # Global state (skill profile)
├── backend/           # FastAPI + LangChain + Claude API
│   └── app/
│       ├── routers/       # API route handlers
│       ├── services/      # Business logic (AI, judge, skill)
│       ├── models/        # SQLAlchemy DB models
│       └── schemas/       # Pydantic request/response schemas
└── docker-compose.yml
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker (optional, for Judge0)
- Anthropic API key

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env            # Set VITE_API_URL=http://localhost:8000
npm run dev
```

### 3. Judge0 (Code Execution) via Docker
```bash
docker-compose up -d judge0
```
Judge0 will run on http://localhost:2358

### 4. Full Stack via Docker Compose
```bash
docker-compose up --build
```
- Frontend: http://localhost:5173
- Backend:  http://localhost:8000
- API Docs: http://localhost:8000/docs

## Features
- AI-powered code analysis using Claude API + LangChain
- Adaptive skill profiling with concept gap detection
- Socratic hint engine (progressive disclosure)
- Code execution via Judge0 (20+ languages)
- Persistent learning history with SQLite
- Real-time feedback with error pattern tracking
