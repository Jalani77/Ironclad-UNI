from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.database import get_db, engine, Base
from app.models import Student, Course, Requirement, Enrollment, Substitution, Program
from app.schemas import (
    StudentCreate, Student as StudentSchema,
    CourseCreate, Course as CourseSchema,
    RequirementCreate, Requirement as RequirementSchema,
    EnrollmentCreate, Enrollment as EnrollmentSchema,
    SubstitutionCreate, SubstitutionUpdate, Substitution as SubstitutionSchema,
    ProgramCreate, Program as ProgramSchema,
    LoginRequest, Token, AuditReport
)
from app.auth import verify_password, get_password_hash, create_access_token
from app.audit_engine import AuditEngine
from app.pdf_generator import generate_audit_pdf
from app.config import get_settings

settings = get_settings()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ironclad Degree Auditor API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Authentication
@app.post("/api/auth/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.email == login_data.email).first()
    if not student or not verify_password(login_data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": student.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Student endpoints
@app.post("/api/students", response_model=StudentSchema)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(
        student_id=student.student_id,
        name=student.name,
        email=student.email,
        password_hash=get_password_hash(student.password),
        program_id=student.program_id
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/api/students/{student_id}", response_model=StudentSchema)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.get("/api/students", response_model=List[StudentSchema])
def list_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


# Program endpoints
@app.post("/api/programs", response_model=ProgramSchema)
def create_program(program: ProgramCreate, db: Session = Depends(get_db)):
    db_program = Program(**program.dict())
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program


@app.get("/api/programs", response_model=List[ProgramSchema])
def list_programs(db: Session = Depends(get_db)):
    return db.query(Program).all()


# Course endpoints
@app.post("/api/courses", response_model=CourseSchema)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@app.get("/api/courses", response_model=List[CourseSchema])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()


# Requirement endpoints
@app.post("/api/requirements", response_model=RequirementSchema)
def create_requirement(requirement: RequirementCreate, db: Session = Depends(get_db)):
    from app.models import RequirementCourse
    
    db_requirement = Requirement(
        program_id=requirement.program_id,
        name=requirement.name,
        requirement_type=requirement.requirement_type,
        credits_required=requirement.credits_required,
        description=requirement.description
    )
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    
    # Add course associations
    for course_id in requirement.course_ids:
        req_course = RequirementCourse(
            requirement_id=db_requirement.id,
            course_id=course_id
        )
        db.add(req_course)
    
    db.commit()
    return db_requirement


@app.get("/api/requirements", response_model=List[RequirementSchema])
def list_requirements(program_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Requirement)
    if program_id:
        query = query.filter(Requirement.program_id == program_id)
    return query.all()


# Enrollment endpoints
@app.post("/api/enrollments", response_model=EnrollmentSchema)
def create_enrollment(enrollment: EnrollmentCreate, db: Session = Depends(get_db)):
    db_enrollment = Enrollment(**enrollment.dict())
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment


@app.get("/api/enrollments", response_model=List[EnrollmentSchema])
def list_enrollments(student_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Enrollment)
    if student_id:
        query = query.filter(Enrollment.student_id == student_id)
    return query.all()


# Substitution endpoints (CRUD for admin)
@app.post("/api/substitutions", response_model=SubstitutionSchema)
def create_substitution(substitution: SubstitutionCreate, db: Session = Depends(get_db)):
    db_substitution = Substitution(**substitution.dict())
    db.add(db_substitution)
    db.commit()
    db.refresh(db_substitution)
    return db_substitution


@app.get("/api/substitutions", response_model=List[SubstitutionSchema])
def list_substitutions(student_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Substitution)
    if student_id:
        query = query.filter(Substitution.student_id == student_id)
    return query.all()


@app.get("/api/substitutions/{substitution_id}", response_model=SubstitutionSchema)
def get_substitution(substitution_id: int, db: Session = Depends(get_db)):
    substitution = db.query(Substitution).filter(Substitution.id == substitution_id).first()
    if not substitution:
        raise HTTPException(status_code=404, detail="Substitution not found")
    return substitution


@app.put("/api/substitutions/{substitution_id}", response_model=SubstitutionSchema)
def update_substitution(
    substitution_id: int,
    substitution_update: SubstitutionUpdate,
    db: Session = Depends(get_db)
):
    db_substitution = db.query(Substitution).filter(Substitution.id == substitution_id).first()
    if not db_substitution:
        raise HTTPException(status_code=404, detail="Substitution not found")
    
    update_data = substitution_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_substitution, key, value)
    
    db.commit()
    db.refresh(db_substitution)
    return db_substitution


@app.delete("/api/substitutions/{substitution_id}")
def delete_substitution(substitution_id: int, db: Session = Depends(get_db)):
    db_substitution = db.query(Substitution).filter(Substitution.id == substitution_id).first()
    if not db_substitution:
        raise HTTPException(status_code=404, detail="Substitution not found")
    
    db.delete(db_substitution)
    db.commit()
    return {"message": "Substitution deleted successfully"}


# Audit endpoint
@app.get("/api/audit/{student_id}", response_model=AuditReport)
def get_audit_report(student_id: int, db: Session = Depends(get_db)):
    engine = AuditEngine(db)
    try:
        report = engine.run_audit(student_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/audit/{student_id}/pdf")
def get_audit_pdf(student_id: int, db: Session = Depends(get_db)):
    engine = AuditEngine(db)
    try:
        report = engine.run_audit(student_id)
        pdf_bytes = generate_audit_pdf(report)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=audit_report_{report.student.student_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
