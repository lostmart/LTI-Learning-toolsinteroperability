## fOLDER

```
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
