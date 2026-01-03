from sqlalchemy.orm import Session
from typing import List, Dict, Set
from app.models import Student, Course, Requirement, Enrollment, Substitution, RequirementCourse
from app.schemas import AuditReport, RequirementProgress, Course as CourseSchema


class AuditEngine:
    """
    Deterministic degree audit engine - pure rule-based logic, no LLM.
    """

    def __init__(self, db: Session):
        self.db = db

    def run_audit(self, student_id: int) -> AuditReport:
        """
        Main audit function that processes student data and generates complete audit report.
        """
        # Load student data
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student with id {student_id} not found")

        program = student.program
        
        # Get all student enrollments
        enrollments = self.db.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.completed == True
        ).all()

        # Get approved substitutions
        substitutions = self.db.query(Substitution).filter(
            Substitution.student_id == student_id,
            Substitution.approved == True
        ).all()

        # Build substitution map: original_course_id -> substitute_course_id
        substitution_map = {sub.original_course_id: sub.substitute_course_id for sub in substitutions}

        # Get all program requirements
        requirements = self.db.query(Requirement).filter(
            Requirement.program_id == program.id
        ).all()

        # Calculate requirement progress
        requirement_progress_list = []
        total_credits_completed = 0.0

        for requirement in requirements:
            progress = self._calculate_requirement_progress(
                requirement, enrollments, substitution_map
            )
            requirement_progress_list.append(progress)
            total_credits_completed += progress.credits_completed

        # Determine status
        overall_percentage = (total_credits_completed / program.total_credits_required * 100) if program.total_credits_required > 0 else 0
        status = self._determine_status(overall_percentage, requirement_progress_list)
        
        # Check graduation eligibility
        graduation_eligible = all(req.is_met for req in requirement_progress_list)

        return AuditReport(
            student=student,
            program=program,
            total_credits_required=program.total_credits_required,
            total_credits_completed=total_credits_completed,
            overall_percentage=round(overall_percentage, 2),
            status=status,
            requirements=requirement_progress_list,
            graduation_eligible=graduation_eligible
        )

    def _calculate_requirement_progress(
        self,
        requirement: Requirement,
        enrollments: List[Enrollment],
        substitution_map: Dict[int, int]
    ) -> RequirementProgress:
        """
        Calculate progress for a single requirement.
        """
        # Get all courses that satisfy this requirement
        requirement_courses = self.db.query(RequirementCourse).filter(
            RequirementCourse.requirement_id == requirement.id
        ).all()
        
        required_course_ids = {rc.course_id for rc in requirement_courses}

        # Track completed courses for this requirement
        completed_course_ids: Set[int] = set()
        completed_courses: List[Course] = []
        credits_completed = 0.0

        for enrollment in enrollments:
            course_id = enrollment.course_id
            
            # Check if this course (or its substitute) satisfies the requirement
            if course_id in required_course_ids:
                completed_course_ids.add(course_id)
                completed_courses.append(enrollment.course)
                credits_completed += enrollment.course.credits
            elif course_id in substitution_map.values():
                # Check if this is a substitute for a required course
                original_id = next((k for k, v in substitution_map.items() if v == course_id), None)
                if original_id and original_id in required_course_ids:
                    completed_course_ids.add(original_id)
                    completed_courses.append(enrollment.course)
                    credits_completed += enrollment.course.credits

        # Get missing courses
        missing_course_ids = required_course_ids - completed_course_ids
        missing_courses = self.db.query(Course).filter(Course.id.in_(missing_course_ids)).all() if missing_course_ids else []

        # Calculate percentage
        percentage = (credits_completed / requirement.credits_required * 100) if requirement.credits_required > 0 else 0
        is_met = credits_completed >= requirement.credits_required

        return RequirementProgress(
            requirement_id=requirement.id,
            requirement_name=requirement.name,
            requirement_type=requirement.requirement_type.value,
            credits_required=requirement.credits_required,
            credits_completed=round(credits_completed, 2),
            percentage=round(percentage, 2),
            is_met=is_met,
            completed_courses=[CourseSchema.from_orm(c) for c in completed_courses],
            missing_courses=[CourseSchema.from_orm(c) for c in missing_courses]
        )

    def _determine_status(self, overall_percentage: float, requirements: List[RequirementProgress]) -> str:
        """
        Determine student status based on progress.
        - completed: 100% of all requirements met
        - on_track: >= 75% progress or within normal range
        - at_risk: < 75% progress
        """
        if all(req.is_met for req in requirements):
            return "completed"
        elif overall_percentage >= 75.0:
            return "on_track"
        else:
            return "at_risk"
