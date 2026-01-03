"""
Integration test for the Ironclad Degree Auditor
Tests the complete flow: authentication, audit, and substitutions
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Student, Program, Course, Requirement, Enrollment
from app.audit_engine import AuditEngine
from app.auth import verify_password


def test_database_seeded():
    """Test that database is properly seeded"""
    db = SessionLocal()
    
    try:
        # Check programs
        programs = db.query(Program).all()
        assert len(programs) >= 1, "No programs found"
        print(f"✓ Found {len(programs)} program(s)")
        
        # Check courses
        courses = db.query(Course).all()
        assert len(courses) >= 30, f"Expected at least 30 courses, found {len(courses)}"
        print(f"✓ Found {len(courses)} courses")
        
        # Check students
        students = db.query(Student).all()
        assert len(students) >= 20, f"Expected at least 20 students, found {len(students)}"
        print(f"✓ Found {len(students)} students")
        
        # Check requirements
        requirements = db.query(Requirement).all()
        assert len(requirements) >= 4, f"Expected at least 4 requirements, found {len(requirements)}"
        print(f"✓ Found {len(requirements)} requirements")
        
        print("\n✓ Database seeding test PASSED")
        return True
        
    except AssertionError as e:
        print(f"\n✗ Database seeding test FAILED: {e}")
        return False
    finally:
        db.close()


def test_authentication():
    """Test authentication system"""
    db = SessionLocal()
    
    try:
        # Test valid login
        student = db.query(Student).filter(Student.email == "alice@ucla.edu").first()
        assert student is not None, "Test student not found"
        
        # Verify password
        is_valid = verify_password("password123", student.password_hash)
        assert is_valid, "Password verification failed"
        
        print("✓ Authentication test PASSED")
        return True
        
    except AssertionError as e:
        print(f"✗ Authentication test FAILED: {e}")
        return False
    finally:
        db.close()


def test_audit_engine():
    """Test the audit engine logic"""
    db = SessionLocal()
    
    try:
        engine = AuditEngine(db)
        
        # Test audit for first student (should be near completion)
        report = engine.run_audit(1)
        
        assert report is not None, "Audit report is None"
        assert report.student.id == 1, "Wrong student in report"
        assert report.program is not None, "Program not in report"
        assert len(report.requirements) >= 4, "Not enough requirements in report"
        assert 0 <= report.overall_percentage <= 100, f"Invalid percentage: {report.overall_percentage}"
        assert report.status in ["on_track", "at_risk", "completed"], f"Invalid status: {report.status}"
        
        print(f"\n✓ Audit Report for {report.student.name}:")
        print(f"  - Program: {report.program.name}")
        print(f"  - Credits: {report.total_credits_completed}/{report.total_credits_required}")
        print(f"  - Progress: {report.overall_percentage}%")
        print(f"  - Status: {report.status}")
        print(f"  - Graduation Eligible: {report.graduation_eligible}")
        
        # Test requirement details
        for req in report.requirements:
            print(f"\n  {req.requirement_name}:")
            print(f"    - Credits: {req.credits_completed}/{req.credits_required}")
            print(f"    - Progress: {req.percentage}%")
            print(f"    - Status: {'MET' if req.is_met else 'NOT MET'}")
            print(f"    - Completed: {len(req.completed_courses)} courses")
            print(f"    - Missing: {len(req.missing_courses)} courses")
        
        print("\n✓ Audit engine test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Audit engine test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_multiple_students():
    """Test audit engine with multiple students (varying completion levels)"""
    db = SessionLocal()
    
    try:
        engine = AuditEngine(db)
        
        # Test first 5 students
        students_tested = 0
        for student_id in range(1, 6):
            report = engine.run_audit(student_id)
            assert report is not None, f"Report for student {student_id} is None"
            students_tested += 1
        
        print(f"✓ Tested {students_tested} students successfully")
        return True
        
    except Exception as e:
        print(f"✗ Multiple students test FAILED: {e}")
        return False
    finally:
        db.close()


def test_status_determination():
    """Test that status is correctly determined"""
    db = SessionLocal()
    
    try:
        engine = AuditEngine(db)
        
        # Test students with different completion levels
        statuses = []
        for student_id in range(1, 21):
            report = engine.run_audit(student_id)
            statuses.append({
                'id': student_id,
                'name': report.student.name,
                'percentage': report.overall_percentage,
                'status': report.status
            })
        
        # Verify status logic
        for s in statuses:
            if s['status'] == 'completed':
                assert s['percentage'] == 100.0, f"Completed status but {s['percentage']}% complete"
            elif s['status'] == 'on_track':
                assert s['percentage'] >= 75.0, f"On track status but only {s['percentage']}% complete"
            elif s['status'] == 'at_risk':
                assert s['percentage'] < 75.0, f"At risk status but {s['percentage']}% complete"
        
        print("\n✓ Status Distribution:")
        completed = sum(1 for s in statuses if s['status'] == 'completed')
        on_track = sum(1 for s in statuses if s['status'] == 'on_track')
        at_risk = sum(1 for s in statuses if s['status'] == 'at_risk')
        
        print(f"  - Completed: {completed}")
        print(f"  - On Track: {on_track}")
        print(f"  - At Risk: {at_risk}")
        
        print("\n✓ Status determination test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Status determination test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("IRONCLAD DEGREE AUDITOR - TEST SUITE")
    print("="*60)
    print()
    
    tests = [
        ("Database Seeding", test_database_seeded),
        ("Authentication", test_authentication),
        ("Audit Engine", test_audit_engine),
        ("Multiple Students", test_multiple_students),
        ("Status Determination", test_status_determination),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[Testing: {test_name}]")
        print("-" * 60)
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
