"""
Seed script to populate database with mock data.
Creates 1 BS Computer Science program, 30 courses, and 20 students.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import (
    Program, Course, Requirement, RequirementCourse,
    Student, Enrollment, Substitution, RequirementType
)
from app.auth import get_password_hash


def seed_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(Substitution).delete()
        db.query(Enrollment).delete()
        db.query(RequirementCourse).delete()
        db.query(Requirement).delete()
        db.query(Student).delete()
        db.query(Course).delete()
        db.query(Program).delete()
        db.commit()
        
        # Create BS Computer Science Program
        program = Program(
            name="Bachelor of Science in Computer Science",
            code="BS-CS",
            total_credits_required=180.0
        )
        db.add(program)
        db.commit()
        db.refresh(program)
        print(f"✓ Created program: {program.name}")
        
        # Create 30 courses
        courses_data = [
            # Core CS courses (12 courses)
            ("CS31", "Introduction to Computer Science I", 4.0, "Fundamentals of programming"),
            ("CS32", "Introduction to Computer Science II", 4.0, "Data structures and algorithms"),
            ("CS33", "Introduction to Computer Organization", 4.0, "Computer architecture basics"),
            ("CS35L", "Software Construction", 4.0, "Software development tools and practices"),
            ("CS111", "Operating Systems Principles", 4.0, "OS concepts and design"),
            ("CS118", "Computer Network Fundamentals", 4.0, "Networking protocols and systems"),
            ("CS131", "Programming Languages", 4.0, "Language design and implementation"),
            ("CS180", "Introduction to Algorithms and Complexity", 4.0, "Algorithm analysis"),
            ("CS181", "Introduction to Formal Languages and Automata Theory", 4.0, "Theory of computation"),
            ("CS143", "Database Systems", 4.0, "Database design and SQL"),
            ("CS161", "Artificial Intelligence", 4.0, "AI fundamentals"),
            ("CS174A", "Computer Graphics", 4.0, "3D graphics and rendering"),
            
            # Math requirements (6 courses)
            ("MATH31A", "Differential and Integral Calculus", 4.0, "Calculus I"),
            ("MATH31B", "Integration and Infinite Series", 4.0, "Calculus II"),
            ("MATH32A", "Calculus of Several Variables", 4.0, "Multivariable calculus"),
            ("MATH33A", "Linear Algebra and Applications", 4.0, "Linear algebra"),
            ("MATH61", "Introduction to Discrete Structures", 4.0, "Discrete math"),
            ("STATS100A", "Introduction to Probability", 4.0, "Probability theory"),
            
            # CS Electives (8 courses)
            ("CS152", "Computer Vision", 4.0, "Image processing and computer vision"),
            ("CS174C", "Computer Animation", 4.0, "Animation techniques"),
            ("CS188", "Computer Networks", 4.0, "Advanced networking"),
            ("CS136", "Computer Security", 4.0, "Security principles"),
            ("CS144", "Web Applications", 4.0, "Full-stack web development"),
            ("CS145", "Data Mining", 4.0, "Machine learning and data analysis"),
            ("CS168", "Mobile Development", 4.0, "iOS and Android development"),
            ("CS172", "Compiler Construction", 4.0, "Compiler design"),
            
            # General Education (4 courses)
            ("ENGCOMP3", "English Composition", 4.0, "Writing fundamentals"),
            ("PHILOS31", "Logic and Critical Thinking", 4.0, "Logical reasoning"),
            ("PHYSICS1A", "Physics for Scientists and Engineers", 4.0, "Mechanics"),
            ("CHEM20A", "General Chemistry", 4.0, "Chemistry fundamentals"),
        ]
        
        courses = []
        for code, name, credits, desc in courses_data:
            course = Course(
                course_code=code,
                name=name,
                credits=credits,
                description=desc
            )
            db.add(course)
            courses.append(course)
        
        db.commit()
        for course in courses:
            db.refresh(course)
        print(f"✓ Created {len(courses)} courses")
        
        # Create requirements
        requirements_data = [
            {
                "name": "Core Computer Science",
                "type": RequirementType.CORE,
                "credits": 48.0,
                "courses": ["CS31", "CS32", "CS33", "CS35L", "CS111", "CS118", "CS131", "CS180", "CS181", "CS143", "CS161", "CS174A"]
            },
            {
                "name": "Mathematics Foundation",
                "type": RequirementType.MAJOR,
                "credits": 24.0,
                "courses": ["MATH31A", "MATH31B", "MATH32A", "MATH33A", "MATH61", "STATS100A"]
            },
            {
                "name": "Computer Science Electives",
                "type": RequirementType.ELECTIVE,
                "credits": 32.0,
                "courses": ["CS152", "CS174C", "CS188", "CS136", "CS144", "CS145", "CS168", "CS172"]
            },
            {
                "name": "General Education",
                "type": RequirementType.GENERAL_ED,
                "credits": 16.0,
                "courses": ["ENGCOMP3", "PHILOS31", "PHYSICS1A", "CHEM20A"]
            }
        ]
        
        requirements = []
        for req_data in requirements_data:
            requirement = Requirement(
                program_id=program.id,
                name=req_data["name"],
                requirement_type=req_data["type"],
                credits_required=req_data["credits"],
                description=f"Required credits for {req_data['name']}"
            )
            db.add(requirement)
            db.commit()
            db.refresh(requirement)
            
            # Link courses to requirement
            for course_code in req_data["courses"]:
                course = next((c for c in courses if c.course_code == course_code), None)
                if course:
                    req_course = RequirementCourse(
                        requirement_id=requirement.id,
                        course_id=course.id
                    )
                    db.add(req_course)
            
            requirements.append(requirement)
            db.commit()
        
        print(f"✓ Created {len(requirements)} requirements")
        
        # Create 20 students with varying progress
        students_data = [
            {"id": "12345001", "name": "Alice Johnson", "email": "alice@ucla.edu"},
            {"id": "12345002", "name": "Bob Smith", "email": "bob@ucla.edu"},
            {"id": "12345003", "name": "Charlie Brown", "email": "charlie@ucla.edu"},
            {"id": "12345004", "name": "Diana Prince", "email": "diana@ucla.edu"},
            {"id": "12345005", "name": "Ethan Hunt", "email": "ethan@ucla.edu"},
            {"id": "12345006", "name": "Fiona Apple", "email": "fiona@ucla.edu"},
            {"id": "12345007", "name": "George Wilson", "email": "george@ucla.edu"},
            {"id": "12345008", "name": "Hannah Montana", "email": "hannah@ucla.edu"},
            {"id": "12345009", "name": "Ivan Rodriguez", "email": "ivan@ucla.edu"},
            {"id": "12345010", "name": "Julia Roberts", "email": "julia@ucla.edu"},
            {"id": "12345011", "name": "Kevin Hart", "email": "kevin@ucla.edu"},
            {"id": "12345012", "name": "Laura Palmer", "email": "laura@ucla.edu"},
            {"id": "12345013", "name": "Michael Jordan", "email": "michael@ucla.edu"},
            {"id": "12345014", "name": "Nina Simone", "email": "nina@ucla.edu"},
            {"id": "12345015", "name": "Oscar Wilde", "email": "oscar@ucla.edu"},
            {"id": "12345016", "name": "Patricia Lee", "email": "patricia@ucla.edu"},
            {"id": "12345017", "name": "Quincy Jones", "email": "quincy@ucla.edu"},
            {"id": "12345018", "name": "Rachel Green", "email": "rachel@ucla.edu"},
            {"id": "12345019", "name": "Steve Rogers", "email": "steve@ucla.edu"},
            {"id": "12345020", "name": "Tina Turner", "email": "tina@ucla.edu"},
        ]
        
        students = []
        for student_data in students_data:
            student = Student(
                student_id=student_data["id"],
                name=student_data["name"],
                email=student_data["email"],
                password_hash=get_password_hash("password123"),  # Default password for all
                program_id=program.id
            )
            db.add(student)
            students.append(student)
        
        db.commit()
        for student in students:
            db.refresh(student)
        print(f"✓ Created {len(students)} students (password: password123)")
        
        # Create enrollments with varying completion levels
        # Create diverse enrollment patterns
        core_courses = [c for c in courses if c.course_code.startswith("CS")][:12]
        math_courses = [c for c in courses if c.course_code.startswith(("MATH", "STATS"))]
        elective_courses = [c for c in courses if c.course_code in ["CS152", "CS174C", "CS188", "CS136", "CS144", "CS145", "CS168", "CS172"]]
        gen_ed_courses = [c for c in courses if c.course_code in ["ENGCOMP3", "PHILOS31", "PHYSICS1A", "CHEM20A"]]
        
        for i, student in enumerate(students):
            # Vary completion based on student index
            if i < 5:  # Students 0-4: Near completion (90-100%)
                courses_to_enroll = core_courses + math_courses + elective_courses + gen_ed_courses
                completed = True
            elif i < 10:  # Students 5-9: On track (75-89%)
                courses_to_enroll = core_courses + math_courses + elective_courses[:6] + gen_ed_courses
                completed = True
            elif i < 15:  # Students 10-14: Mid-progress (50-74%)
                courses_to_enroll = core_courses[:8] + math_courses[:4] + elective_courses[:4] + gen_ed_courses[:2]
                completed = True
            else:  # Students 15-19: At risk (<50%)
                courses_to_enroll = core_courses[:4] + math_courses[:2] + gen_ed_courses[:1]
                completed = True
            
            for j, course in enumerate(courses_to_enroll):
                year = 2023 + (j // 4)  # Spread across years
                semester = ["Fall", "Winter", "Spring"][j % 3]
                
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    grade="A" if i < 10 else "B",
                    semester=semester,
                    year=year,
                    completed=completed
                )
                db.add(enrollment)
        
        db.commit()
        print("✓ Created enrollments for all students")
        
        # Create sample substitutions
        # Student 1: Substitute CS174C with CS152
        substitution1 = Substitution(
            student_id=students[0].id,
            original_course_id=next(c.id for c in courses if c.course_code == "CS174C"),
            substitute_course_id=next(c.id for c in courses if c.course_code == "CS152"),
            reason="Student demonstrated proficiency through prior coursework",
            approved=True
        )
        db.add(substitution1)
        
        # Student 3: Pending substitution
        substitution2 = Substitution(
            student_id=students[2].id,
            original_course_id=next(c.id for c in courses if c.course_code == "CS168"),
            substitute_course_id=next(c.id for c in courses if c.course_code == "CS144"),
            reason="Transfer credit evaluation pending",
            approved=False
        )
        db.add(substitution2)
        
        db.commit()
        print("✓ Created sample substitutions")
        
        print("\n" + "="*50)
        print("Database seeded successfully!")
        print("="*50)
        print(f"Program: {program.name}")
        print(f"Total courses: {len(courses)}")
        print(f"Total students: {len(students)}")
        print(f"Total requirements: {len(requirements)}")
        print("\nSample login credentials:")
        print("Email: alice@ucla.edu")
        print("Password: password123")
        print("="*50)
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
