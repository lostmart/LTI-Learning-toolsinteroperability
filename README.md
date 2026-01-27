## Setup


### 2. Create and activate Python virtual environment

**Linux/Mac:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell:**

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

**Git Bash (Windows):**

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn[standard] pydantic-settings sqlalchemy psycopg2-binary python-jose[cryptography] cryptography PyJWT requests httpx
```

### 4. Start FastAPI server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Important Notes

- Always use `.venv` (with the dot) for consistency
- Add both `venv/` and `.venv/` to `.gitignore`

## WINDOWS USERS

**Windows PowerShell:**

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

**Git Bash (Windows):**

```bash
python -m venv .venv
source .venv/Scripts/activate
```

## fOLDER

```text
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   ├── security.py         # JWT validation, key management
│   │   └── dependencies.py     # FastAPI dependencies (auth, db)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # SQLAlchemy models
│   │   ├── platform.py         # LMS platform registration
│   │   ├── exercise.py         # Coding exercises
│   │   └── submission.py       # Student submissions
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── lti.py              # Pydantic schemas for LTI
│   │   ├── exercise.py         # Request/response models
│   │   └── submission.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── lti/
│   │   │   ├── __init__.py
│   │   │   ├── launch.py       # LTI launch endpoints
│   │   │   └── grades.py       # Grade passback
│   │   ├── exercises.py        # Exercise CRUD
│   │   └── submissions.py      # Code submission endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── lti_service.py      # LTI protocol logic
│   │   ├── jwks_service.py     # Key management
│   │   ├── grading_service.py  # Auto-grading logic
│   │   └── execution_service.py # Code execution (Docker)
│   └── db/
│       ├── __init__.py
│       ├── session.py          # Database session management
│       └── base.py             # Base models
├── alembic/                    # Database migrations
├── tests/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```
