# AI Job Intelligence Platform - Version 1

## Backend

1. Open a terminal in the project root.
2. Activate the virtual environment.
3. Install dependencies:

   pip install -r backend/requirements.txt

4. Start the API:

   uvicorn backend.app.main:app --reload

5. Open:

   http://127.0.0.1:8000/docs

## Main features in Version 1

- User registration and login
- Session-based authentication
- Resume storage
- Resume skill extraction
- Resume/role skill-gap analysis
- Career recommendations
- Job listing and search
- Job applications
- Interview question generation
- Dashboard statistics

This version intentionally uses local deterministic AI logic so the application can run without an external AI API key. LLM/RAG/vector integrations can be added after the core platform is working.
