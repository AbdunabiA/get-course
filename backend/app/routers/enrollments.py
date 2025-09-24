# backend/app/routers/enrollments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, and_
from app.core.database import get_session
from app.models.models import (
    Course, Enrollment, User,
    EnrollmentCreate, EnrollmentRead, EnrollmentUpdate,
    CourseRead, UserRole
)
from app.auth.dependencies import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/enrollments", tags=["Enrollments"])


@router.post("/courses/{course_id}/enroll", response_model=dict, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Enroll current user in a course"""

    # Get course
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check if course is published
    if not course.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is not published"
        )

    # Check if user is already enrolled
    existing_enrollment = session.exec(
        select(Enrollment).where(
            and_(
                Enrollment.student_id == current_user.id,
                Enrollment.course_id == course_id
            )
        )
    ).first()

    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )

    # Create enrollment
    new_enrollment = Enrollment(
        student_id=current_user.id,
        course_id=course_id,
        progress=0.0
    )

    session.add(new_enrollment)
    session.commit()
    session.refresh(new_enrollment)

    logger.info(f"User {current_user.email} enrolled in course {course.title}")

    return {
        "message": "Successfully enrolled in course",
        "enrollment": {
            "id": new_enrollment.id,
            "course_id": course_id,
            "course_title": course.title,
            "progress": new_enrollment.progress,
            "enrolled_at": new_enrollment.created_at
        }
    }


@router.get("/me", response_model=List[dict])
async def get_my_enrollments(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all courses the current user is enrolled in"""

    # Get enrollments with course information
    statement = select(Enrollment, Course).join(Course).where(
        Enrollment.student_id == current_user.id
    )
    results = session.exec(statement).all()

    enrollments = []
    for enrollment, course in results:
        # Get instructor info
        instructor = session.get(User, course.instructor_id)

        enrollments.append({
            "enrollment_id": enrollment.id,
            "progress": enrollment.progress,
            "enrolled_at": enrollment.created_at,
            "course": {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "image": course.image,
                "instructor": {
                    "id": instructor.id if instructor else None,
                    "email": instructor.email if instructor else None
                }
            }
        })

    return enrollments


@router.put("/courses/{course_id}/progress", response_model=dict)
async def update_course_progress(
    course_id: str,
    progress_data: EnrollmentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update progress for a course enrollment"""

    # Find enrollment
    enrollment = session.exec(
        select(Enrollment).where(
            and_(
                Enrollment.student_id == current_user.id,
                Enrollment.course_id == course_id
            )
        )
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )

    # Update progress
    if progress_data.progress is not None:
        enrollment.progress = progress_data.progress
        session.commit()
        session.refresh(enrollment)

        logger.info(
            f"Progress updated for user {current_user.email} in course {course_id}: {progress_data.progress}%")

    return {
        "message": "Progress updated successfully",
        "progress": enrollment.progress
    }


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unenroll_from_course(
    course_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Unenroll from a course"""

    # Find enrollment
    enrollment = session.exec(
        select(Enrollment).where(
            and_(
                Enrollment.student_id == current_user.id,
                Enrollment.course_id == course_id
            )
        )
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )

    # Delete enrollment
    session.delete(enrollment)
    session.commit()

    logger.info(
        f"User {current_user.email} unenrolled from course {course_id}")

# Admin/Instructor endpoints


@router.get("/courses/{course_id}/students", response_model=List[dict])
async def get_course_students(
    course_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all students enrolled in a course (instructor/admin only)"""

    # Get course
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check permission (course owner or admin)
    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view course enrollments"
        )

    # Get enrollments with student information
    statement = select(Enrollment, User).join(User, Enrollment.student_id == User.id).where(
        Enrollment.course_id == course_id
    )
    results = session.exec(statement).all()

    students = []
    for enrollment, student in results:
        students.append({
            "enrollment_id": enrollment.id,
            "progress": enrollment.progress,
            "enrolled_at": enrollment.created_at,
            "student": {
                "id": student.id,
                "email": student.email
            }
        })

    return students
