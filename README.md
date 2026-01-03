# Ironclad Degree Auditor MVP

A deterministic degree audit tool for UCLA BS Computer Science program built with Next.js, TypeScript, Tailwind CSS, FastAPI, and PostgreSQL.

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Auth**: JWT-based authentication

## Features

- **Student Audit View**: Real-time degree progress tracking with visual progress bars
- **Admin Panel**: CRUD interface for managing course substitutions
- **PDF Export**: Generate comprehensive audit reports
- **Deterministic Logic**: Pure rule-based engine without AI/LLM
- **Mock Data**: Pre-seeded with 1 program, 30 courses, and 20 students

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

### Database Setup

1. Create PostgreSQL database:
```bash
createdb degree_audit
```

2. Update database connection in `backend/.env`:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/degree_audit
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py  # Seed database with mock data
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

### Demo Credentials

- **Email**: alice@ucla.edu
- **Password**: password123

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login

### Students
- `GET /api/students` - List all students
- `GET /api/students/{id}` - Get student details

### Audit
- `GET /api/audit/{student_id}` - Get audit report
- `GET /api/audit/{student_id}/pdf` - Download PDF report

### Substitutions (Admin)
- `GET /api/substitutions` - List substitutions
- `POST /api/substitutions` - Create substitution
- `PUT /api/substitutions/{id}` - Update substitution
- `DELETE /api/substitutions/{id}` - Delete substitution

## Project Structure

```
/workspace
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── database.py       # Database connection
│   │   ├── auth.py           # Authentication logic
│   │   ├── audit_engine.py   # Degree audit engine
│   │   ├── pdf_generator.py  # PDF export
│   │   └── config.py         # Configuration
│   ├── seed.py               # Database seeding script
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx          # Login page
    │   │   ├── dashboard/        # Student audit view
    │   │   └── admin/            # Admin panel
    │   ├── lib/
    │   │   └── api.ts            # API client
    │   └── types/
    │       └── index.ts          # TypeScript interfaces
    ├── package.json
    └── .env.local

## Architecture

### Audit Engine Logic

The audit engine follows deterministic rules:

1. **Load Student Data**: Fetch all enrollments and approved substitutions
2. **Apply Filters**: Match completed courses against requirements
3. **Calculate Credits**: Sum credits for each requirement category
4. **Determine Status**:
   - `completed`: 100% of requirements met
   - `on_track`: ≥75% progress
   - `at_risk`: <75% progress

### Data Model

- **Student**: User accounts and program enrollment
- **Program**: Degree programs (BS-CS)
- **Course**: Course catalog with credits
- **Requirement**: Program requirements with credit thresholds
- **Enrollment**: Student course completions
- **Substitution**: Approved course substitutions

## Development

### Adding New Requirements

Edit `backend/seed.py` to add new requirements:

```python
{
    "name": "New Requirement",
    "type": RequirementType.ELECTIVE,
    "credits": 16.0,
    "courses": ["CS100", "CS200"]
}
```

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Production Deployment

1. Update `SECRET_KEY` in backend `.env`
2. Configure production database
3. Set `NEXT_PUBLIC_API_URL` to production API URL
4. Deploy backend with Gunicorn/Uvicorn
5. Deploy frontend with Vercel/Netlify

## License

MIT
