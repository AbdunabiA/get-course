# backend/app/routers/instructor.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func, and_
from app.core.database import get_session
from app.models.models import (
    Course, Lesson, Enrollment, Review, User,
    UserRole
)
from app.auth.dependencies import get_current_user, require_instructor
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/instructor", tags=["Instructor Dashboard"])


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_instructor_dashboard(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_instructor)
):
    """Get instructor dashboard statistics"""

    # Get total courses
    total_courses = session.exec(
        select(func.count(Course.id)).where(
            Course.instructor_id == current_user.id)
    ).first()

    # Get published courses
    published_courses = session.exec(
        select(func.count(Course.id)).where(
            and_(
                Course.instructor_id == current_user.id,
                Course.is_published == True
            )
        )
    ).first()

    # Get total enrollments across all courses
    total_enrollments = session.exec(
        select(func.count(Enrollment.id))
        .select_from(Enrollment)
        .join(Course)
        .where(Course.instructor_id == current_user.id)
    ).first()

    # Get total lessons
    total_lessons = session.exec(
        select(func.count(Lesson.id))
        .select_from(Lesson)
        .join(Course)
        .where(Course.instructor_id == current_user.id)
    ).first()

    # Get average rating across all courses
    avg_rating = session.exec(
        select(func.avg(Review.rating))
        .select_from(Review)
        .join(Course)
        .where(Course.instructor_id == current_user.id)
    ).first()

    # Get recent enrollments (last 5)
    recent_enrollments = session.exec(
        select(Enrollment, Course, User)
        .select_from(Enrollment)
        .join(Course)
        .join(User, Enrollment.student_id == User.id)
        .where(Course.instructor_id == current_user.id)
        .order_by(Enrollment.created_at.desc())
        .limit(5)
    ).all()

    recent_enrollments_data = [
        {
            "student_email": user.email,
            "course_title": course.title,
            "enrolled_at": enrollment.created_at,
            "progress": enrollment.progress
        }
        for enrollment, course, user in recent_enrollments
    ]

    return {
        "overview": {
            "total_courses": total_courses or 0,
            "published_courses": published_courses or 0,
            "total_students": total_enrollments or 0,
            "total_lessons": total_lessons or 0,
            "average_rating": round(float(avg_rating), 2) if avg_rating else 0.0
        },
        "recent_enrollments": recent_enrollments_data
    }


@router.get("/courses", response_model=List[Dict[str, Any]])
async def get_instructor_courses(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_instructor)
):
    """Get all courses created by the current instructor"""

    courses = session.exec(
        select(Course).where(Course.instructor_id == current_user.id)
    ).all()

    courses_data = []
    for course in courses:
        # Get course statistics
        lessons_count = session.exec(
            select(func.count(Lesson.id)).where(Lesson.course_id == course.id)
        ).first()

        enrollments_count = session.exec(
            select(func.count(Enrollment.id)).where(
                Enrollment.course_id == course.id)
        ).first()

        # Get average rating for this course
        avg_rating = session.exec(
            select(func.avg(Review.rating)).where(
                Review.course_id == course.id)
        ).first()

        # Get total revenue (if course has price)
        total_revenue = (course.price or 0) * (enrollments_count or 0)

        courses_data.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "image": course.image,
            "price": course.price,
            "is_published": course.is_published,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "statistics": {
                "lessons_count": lessons_count or 0,
                "enrollments_count": enrollments_count or 0,
                "average_rating": round(float(avg_rating), 2) if avg_rating else 0.0,
                "total_revenue": total_revenue
            }
        })

    return courses_data


@router.get("/courses/{course_id}/analytics", response_model=Dict[str, Any])
async def get_course_analytics(
    course_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_instructor)
):
    """Get detailed analytics for a specific course"""

    # Verify course ownership
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view analytics for this course"
        )

    # Get enrollments with progress data
    enrollments = session.exec(
        select(Enrollment).where(Enrollment.course_id == course_id)
    ).all()

    # Calculate progress statistics
    total_enrollments = len(enrollments)
    if total_enrollments > 0:
        total_progress = sum(e.progress for e in enrollments)
        avg_progress = total_progress / total_enrollments

        # Count completion rates
        completed_count = sum(1 for e in enrollments if e.progress >= 100.0)
        completion_rate = (completed_count / total_enrollments) * 100
    else:
        avg_progress = 0.0
        completion_rate = 0.0
        completed_count = 0

    # Get reviews
    reviews = session.exec(
        select(Review).where(Review.course_id == course_id)
    ).all()

    review_stats = {
        "total_reviews": len(reviews),
        "average_rating": round(sum(r.rating for r in reviews) / len(reviews), 2) if reviews else 0.0,
        "rating_distribution": {
            "5_star": sum(1 for r in reviews if r.rating == 5),
            "4_star": sum(1 for r in reviews if r.rating == 4),
            "3_star": sum(1 for r in reviews if r.rating == 3),
            "2_star": sum(1 for r in reviews if r.rating == 2),
            "1_star": sum(1 for r in reviews if r.rating == 1),
        }
    }

    # Get lesson count
    lessons_count = session.exec(
        select(func.count(Lesson.id)).where(Lesson.course_id == course_id)
    ).first()

    # Calculate revenue
    total_revenue = (course.price or 0) * total_enrollments

    return {
        "course_info": {
            "id": course.id,
            "title": course.title,
            "price": course.price,
            "is_published": course.is_published,
            "lessons_count": lessons_count or 0
        },
        "enrollment_stats": {
            "total_enrollments": total_enrollments,
            "completed_enrollments": completed_count,
            "average_progress": round(avg_progress, 2),
            "completion_rate": round(completion_rate, 2)
        },
        "review_stats": review_stats,
        "revenue_stats": {
            "total_revenue": total_revenue,
            "revenue_per_enrollment": course.price or 0
        }
    }


@router.post("/upgrade-request")
async def request_instructor_upgrade(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Request upgrade to instructor role (students only)"""

    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only students can request instructor upgrade"
        )

    # In a real implementation, you might:
    # 1. Create a pending request record
    # 2. Send notification to admins
    # 3. Require additional information/verification

    # For MVP, we'll just return a success message
    logger.info(f"Instructor upgrade requested by {current_user.email}")

    return {
        "message": "Instructor upgrade request submitted. You will be notified when approved.",
        "status": "pending"
    }
