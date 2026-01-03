from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RequirementType(str, enum.Enum):
    CORE = "CORE"
    ELECTIVE = "ELECTIVE"
    GENERAL_ED = "GENERAL_ED"
    MAJOR = "MAJOR"


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    
    program = relationship("Program", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    total_credits_required = Column(Float, nullable=False)
    
    students = relationship("Student", back_populates="program")
    requirements = relationship("Requirement", back_populates="program", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    credits = Column(Float, nullable=False)
    description = Column(Text)
    
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    requirements = relationship("RequirementCourse", back_populates="course", cascade="all, delete-orphan")


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    name = Column(String, nullable=False)
    requirement_type = Column(Enum(RequirementType), nullable=False)
    credits_required = Column(Float, nullable=False)
    description = Column(Text)
    
    program = relationship("Program", back_populates="requirements")
    courses = relationship("RequirementCourse", back_populates="requirement", cascade="all, delete-orphan")


class RequirementCourse(Base):
    __tablename__ = "requirement_courses"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    requirement = relationship("Requirement", back_populates="courses")
    course = relationship("Course", back_populates="requirements")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    grade = Column(String)
    semester = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False)
    
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Substitution(Base):
    __tablename__ = "substitutions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    original_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    substitute_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    reason = Column(Text)
    approved = Column(Boolean, default=False)
    
    student = relationship("Student", foreign_keys=[student_id])
    original_course = relationship("Course", foreign_keys=[original_course_id])
    substitute_course = relationship("Course", foreign_keys=[substitute_course_id])
