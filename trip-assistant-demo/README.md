# Trip Assistant: pokaz praktyczny (bezpieczeństwo)

Backend: **FastAPI + SQLAlchemy 2** (moduły `auth`, `trips`, `entries`). Frontend: **Vite (JS)**.
Wszystko poniżej działa na prawdziwym API, nie jest symulacją.

## Uruchomienie

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # Windows: copy .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # wklej wynik jako JWT_SECRET w .env
uvicorn app.main:app --reload --port 8000              # Swagger UI: http://localhost:8000/docs

# frontend (drugi terminal)
cd frontend && npm install && npm run dev              # http://localhost:5173

# testy
cd backend && pytest
```

## Struktura
```
backend/app/core/        settings.py (konfiguracja z .env), db.py (SQLAlchemy)
backend/app/modules/     auth/ trips/ entries/   (router, service, models, schemas)
backend/tests/           pytest (CORS, auth, IDOR, XSS-API)
backend/scripts/demo.py  scenariusz na żywo
frontend/src/main.js     demo XSS na prawdziwym DOM
```
