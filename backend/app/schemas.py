from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum


class RequirementTypeEnum(str, Enum):
    CORE = "CORE"
    ELECTIVE = "ELECTIVE"
    GENERAL_ED = "GENERAL_ED"
    MAJOR = "MAJOR"


class CourseBase(BaseModel):
    course_code: str
    name: str
    credits: float
    description: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: int

    class Config:
        from_attributes = True


class StudentBase(BaseModel):
    student_id: str
    name: str
    email: EmailStr


class StudentCreate(StudentBase):
    password: str
    program_id: int


class Student(StudentBase):
    id: int
    program_id: int

    class Config:
        from_attributes = True


class ProgramBase(BaseModel):
    name: str
    code: str
    total_credits_required: float


class ProgramCreate(ProgramBase):
    pass


class Program(ProgramBase):
    id: int

    class Config:
        from_attributes = True


class RequirementBase(BaseModel):
    name: str
    requirement_type: RequirementTypeEnum
    credits_required: float
    description: Optional[str] = None


class RequirementCreate(RequirementBase):
    program_id: int
    course_ids: List[int] = []


class Requirement(RequirementBase):
    id: int
    program_id: int

    class Config:
        from_attributes = True


class EnrollmentBase(BaseModel):
    course_id: int
    grade: Optional[str] = None
    semester: str
    year: int
    completed: bool = False


class EnrollmentCreate(EnrollmentBase):
    student_id: int


class Enrollment(EnrollmentBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True


class SubstitutionBase(BaseModel):
    original_course_id: int
    substitute_course_id: int
    reason: Optional[str] = None
    approved: bool = False


class SubstitutionCreate(SubstitutionBase):
    student_id: int


class SubstitutionUpdate(BaseModel):
    reason: Optional[str] = None
    approved: Optional[bool] = None


class Substitution(SubstitutionBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    student_db_id: int
    student_number: str
    student_name: str
    is_admin: bool


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    # Accept either email or student_id ("username") to reduce login confusion.
    identifier: str
    password: str


class RequirementProgress(BaseModel):
    requirement_id: int
    requirement_name: str
    requirement_type: str
    credits_required: float
    credits_completed: float
    percentage: float
    is_met: bool
    completed_courses: List[Course]
    missing_courses: List[Course]


class AuditReport(BaseModel):
    student: Student
    program: Program
    total_credits_required: float
    total_credits_completed: float
    overall_percentage: float
    status: str  # "on_track", "at_risk", "completed"
    requirements: List[RequirementProgress]
    graduation_eligible: bool
