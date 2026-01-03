# Development Guide

## Architecture Overview

### Backend (FastAPI + SQLAlchemy)

```
backend/
├── app/
│   ├── main.py           # FastAPI app + all endpoints
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic validation schemas
│   ├── database.py       # DB connection & session management
│   ├── auth.py           # JWT authentication
│   ├── audit_engine.py   # Core audit logic (deterministic)
│   ├── pdf_generator.py  # ReportLab PDF generation
│   └── config.py         # Environment configuration
├── seed.py               # Database seeding script
├── test_system.py        # Integration tests
└── requirements.txt      # Python dependencies
```

### Frontend (Next.js 14 + TypeScript)

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx          # Login page (/)
│   │   ├── layout.tsx        # Root layout
│   │   ├── globals.css       # Global styles
│   │   ├── dashboard/
│   │   │   └── page.tsx      # Student audit view
│   │   └── admin/
│   │       └── page.tsx      # Admin CRUD interface
│   ├── lib/
│   │   └── api.ts            # Axios API client
│   └── types/
│       └── index.ts          # TypeScript interfaces
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Data Model

### Core Entities

1. **Program**: Degree programs (e.g., BS-CS)
   - Fields: name, code, total_credits_required

2. **Student**: User accounts
   - Fields: student_id, name, email, password_hash, program_id

3. **Course**: Course catalog
   - Fields: course_code, name, credits, description

4. **Requirement**: Program requirements
   - Fields: name, requirement_type, credits_required, program_id
   - Types: CORE, ELECTIVE, GENERAL_ED, MAJOR

5. **RequirementCourse**: Many-to-many link between Requirements and Courses
   - Fields: requirement_id, course_id

6. **Enrollment**: Student course completions
   - Fields: student_id, course_id, grade, semester, year, completed

7. **Substitution**: Course substitutions (admin managed)
   - Fields: student_id, original_course_id, substitute_course_id, reason, approved

### Entity Relationships

```
Program 1--* Student
Program 1--* Requirement
Student 1--* Enrollment
Course 1--* Enrollment
Requirement *--* Course (via RequirementCourse)
Student 1--* Substitution
Course 1--* Substitution (as original)
Course 1--* Substitution (as substitute)
```

## Audit Engine Logic

### Algorithm

The audit engine (`audit_engine.py`) follows these steps:

1. **Load Student Data**
   ```python
   - Fetch student record
   - Get program requirements
   - Load completed enrollments (completed=True)
   - Load approved substitutions (approved=True)
   ```

2. **Build Substitution Map**
   ```python
   substitution_map = {original_course_id: substitute_course_id}
   ```

3. **Process Each Requirement**
   ```python
   for requirement in program.requirements:
       - Get required course IDs
       - Match enrollments (including substitutes)
       - Sum credits completed
       - Calculate percentage
       - Determine if requirement is met
   ```

4. **Calculate Overall Status**
   ```python
   if all requirements met: "completed"
   elif progress >= 75%: "on_track"
   else: "at_risk"
   ```

5. **Check Graduation Eligibility**
   ```python
   graduation_eligible = all(requirement.is_met for requirement in requirements)
   ```

### Key Features

- **Deterministic**: No randomness, same input = same output
- **No LLM**: Pure rule-based logic
- **Efficient**: Single database query per requirement
- **Accurate**: Handles substitutions correctly

## API Endpoints

### Authentication
```
POST /api/auth/login
Body: { "email": "string", "password": "string" }
Response: { "access_token": "jwt_token", "token_type": "bearer" }
```

### Audit
```
GET /api/audit/{student_id}
Response: AuditReport (see schemas.py)

GET /api/audit/{student_id}/pdf
Response: Binary PDF file
```

### Students
```
GET /api/students
GET /api/students/{id}
POST /api/students
```

### Courses
```
GET /api/courses
POST /api/courses
```

### Requirements
```
GET /api/requirements?program_id={id}
POST /api/requirements
```

### Enrollments
```
GET /api/enrollments?student_id={id}
POST /api/enrollments
```

### Substitutions (Admin CRUD)
```
GET /api/substitutions?student_id={id}
POST /api/substitutions
PUT /api/substitutions/{id}
DELETE /api/substitutions/{id}
```

## Frontend Components

### Login Page (/)
- Email/password form
- JWT token storage
- Demo credentials display

### Dashboard (/dashboard)
- Overall progress card with status badge
- Progress bars (overall + per requirement)
- Requirement cards with:
  - Credits completed/required
  - Percentage progress
  - Completed courses (green badges)
  - Missing courses (red badges)
- PDF download button

### Admin Panel (/admin)
- Substitutions table with filtering
- Create form with dropdowns
- Approve/Delete actions
- Real-time updates

## Testing Strategy

### Manual Testing

1. **Database Seeding**
   ```bash
   cd backend
   python seed.py
   ```

2. **Backend API**
   ```bash
   uvicorn app.main:app --reload
   # Visit http://localhost:8000/docs for Swagger UI
   ```

3. **Frontend**
   ```bash
   cd frontend
   npm run dev
   # Visit http://localhost:3000
   ```

### Automated Testing

```bash
cd backend
python test_system.py
```

Tests include:
- Database seeding validation
- Authentication system
- Audit engine logic
- Multiple student scenarios
- Status determination rules

## Deployment

### Local Development

1. Start PostgreSQL:
   ```bash
   docker-compose up -d
   ```

2. Backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python seed.py
   uvicorn app.main:app --reload
   ```

3. Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Production Considerations

1. **Security**
   - Change SECRET_KEY in .env
   - Use HTTPS
   - Enable CORS restrictions
   - Add rate limiting

2. **Database**
   - Use managed PostgreSQL (AWS RDS, etc.)
   - Enable connection pooling
   - Set up backups

3. **Backend**
   - Deploy with Gunicorn + Uvicorn workers
   - Use environment variables
   - Enable logging
   - Monitor with Sentry

4. **Frontend**
   - Deploy to Vercel/Netlify
   - Configure API URL
   - Enable CDN
   - Set up analytics

## Future Enhancements

### Phase 2 Features
- Multi-program support
- Admin dashboard with analytics
- Email notifications
- Course scheduling recommendations
- Transfer credit import
- Degree plan generator

### Technical Improvements
- Redis caching for audit reports
- WebSocket for real-time updates
- Batch audit processing
- Export to Excel
- Mobile responsive design
- Progressive Web App (PWA)

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up -d
python seed.py
```

### Frontend Build Errors
```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run dev
```

### Backend Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Performance Metrics

### Expected Response Times
- Login: < 500ms
- Audit Report: < 1s
- PDF Generation: < 2s
- Substitution CRUD: < 300ms

### Database Queries
- Audit engine: 3-5 queries per report
- Dashboard load: 1 query (audit report)
- Admin panel: 2 queries (substitutions + courses)

## Code Quality

### Python (Backend)
- Type hints throughout
- Docstrings for complex functions
- SQLAlchemy best practices
- Pydantic validation

### TypeScript (Frontend)
- Strict mode enabled
- Interface definitions
- Async/await patterns
- Error handling

## License

MIT - See LICENSE file
