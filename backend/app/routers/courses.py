# backend/app/routers/courses.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func, and_
from app.core.database import get_session
from app.models.models import (
    Course, Lesson, Enrollment, Category, User,
    CourseCreate, CourseRead, CourseUpdate,
    LessonCreate, LessonRead, LessonUpdate,
    EnrollmentCreate, EnrollmentRead,
    CategoryCreate, CategoryRead,
    UserRole
)
from app.auth.dependencies import (
    get_current_user, require_instructor, require_admin
)
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/courses", tags=["Courses"])

# Course CRUD Operations


@router.get("/", response_model=List[CourseRead])
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    instructor_id: Optional[str] = Query(None),
    published_only: bool = Query(True),
    session: Session = Depends(get_session)
):
    """Get all courses with filtering and pagination"""

    # Build query
    query = select(Course)

    # Filter by published status (public endpoint shows published only by default)
    if published_only:
        query = query.where(Course.is_published == True)

    # Apply filters
    if search:
        query = query.where(Course.title.contains(search))

    if category_id:
        query = query.where(Course.category_id == category_id)

    if instructor_id:
        query = query.where(Course.instructor_id == instructor_id)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    courses = session.exec(query).all()

    # Build response with additional data
    course_reads = []
    for course in courses:
        # Get instructor info
        instructor = session.get(User, course.instructor_id)

        # Get category info
        category = session.get(
            Category, course.category_id) if course.category_id else None

        # Count lessons and enrollments
        lessons_count = session.exec(
            select(func.count(Lesson.id)).where(Lesson.course_id == course.id)
        ).first()

        enrollments_count = session.exec(
            select(func.count(Enrollment.id)).where(
                Enrollment.course_id == course.id)
        ).first()

        course_read = CourseRead(
            id=course.id,
            title=course.title,
            description=course.description,
            image=course.image,
            price=course.price,
            is_published=course.is_published,
            instructor_id=course.instructor_id,
            category_id=course.category_id,
            created_at=course.created_at,
            updated_at=course.updated_at,
            lessons_count=lessons_count or 0,
            enrollments_count=enrollments_count or 0
        )

        course_reads.append(course_read)

    return course_reads


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: str,
    session: Session = Depends(get_session)
):
    """Get course by ID with detailed information"""

    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Get instructor info
    instructor = session.get(User, course.instructor_id)

    # Get category info
    category = session.get(
        Category, course.category_id) if course.category_id else None

    # Count lessons and enrollments
    lessons_count = session.exec(
        select(func.count(Lesson.id)).where(Lesson.course_id == course.id)
    ).first()

    enrollments_count = session.exec(
        select(func.count(Enrollment.id)).where(
            Enrollment.course_id == course.id)
    ).first()

    return CourseRead(
        id=course.id,
        title=course.title,
        description=course.description,
        image=course.image,
        price=course.price,
        is_published=course.is_published,
        instructor_id=course.instructor_id,
        category_id=course.category_id,
        created_at=course.created_at,
        updated_at=course.updated_at,
        lessons_count=lessons_count or 0,
        enrollments_count=enrollments_count or 0
    )


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_instructor)
):
    """Create a new course (instructors and admins only)"""

    # Verify category exists if provided
    if course_data.category_id:
        category = session.get(Category, course_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )

    # Create course
    new_course = Course(
        title=course_data.title,
        description=course_data.description,
        image=course_data.image,
        price=course_data.price,
        is_published=course_data.is_published,
        instructor_id=current_user.id,
        category_id=course_data.category_id
    )

    session.add(new_course)
    session.commit()
    session.refresh(new_course)

    logger.info(f"Course created: {new_course.title} by {current_user.email}")

    return CourseRead(
        id=new_course.id,
        title=new_course.title,
        description=new_course.description,
        image=new_course.image,
        price=new_course.price,
        is_published=new_course.is_published,
        instructor_id=new_course.instructor_id,
        category_id=new_course.category_id,
        created_at=new_course.created_at,
        updated_at=new_course.updated_at,
        lessons_count=0,
        enrollments_count=0
    )


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: str,
    course_data: CourseUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update course (only by course owner or admin)"""

    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check permission (owner or admin)
    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course"
        )

    # Verify category exists if provided
    if course_data.category_id:
        category = session.get(Category, course_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )

    # Update course fields
    course_dict = course_data.model_dump(exclude_unset=True)
    for field, value in course_dict.items():
        setattr(course, field, value)

    session.commit()
    session.refresh(course)

    logger.info(f"Course updated: {course.title} by {current_user.email}")

    return CourseRead(
        id=course.id,
        title=course.title,
        description=course.description,
        image=course.image,
        price=course.price,
        is_published=course.is_published,
        instructor_id=course.instructor_id,
        category_id=course.category_id,
        created_at=course.created_at,
        updated_at=course.updated_at,
        lessons_count=0,  # You could calculate this if needed
        enrollments_count=0  # You could calculate this if needed
    )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete course (only by course owner or admin)"""

    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check permission (owner or admin)
    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this course"
        )

    session.delete(course)
    session.commit()

    logger.info(f"Course deleted: {course.title} by {current_user.email}")

# Lesson Management


@router.get("/{course_id}/lessons", response_model=List[LessonRead])
async def get_course_lessons(
    course_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get lessons for a course (enrolled users, instructors, or admins only)"""

    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check if user has access to lessons
    has_access = False

    # Course owner or admin has access
    if course.instructor_id == current_user.id or current_user.role == UserRole.ADMIN:
        has_access = True
    else:
        # Check if user is enrolled
        enrollment = session.exec(
            select(Enrollment).where(
                and_(
                    Enrollment.student_id == current_user.id,
                    Enrollment.course_id == course_id
                )
            )
        ).first()

        if enrollment:
            has_access = True

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be enrolled in this course to view lessons"
        )

    # Get lessons ordered by order field
    lessons = session.exec(
        select(Lesson)
        .where(Lesson.course_id == course_id)
        .order_by(Lesson.order)
    ).all()

    return [
        LessonRead(
            id=lesson.id,
            title=lesson.title,
            content=lesson.content,
            video_url=lesson.video_url,
            order=lesson.order,
            course_id=lesson.course_id,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at
        )
        for lesson in lessons
    ]


@router.post("/{course_id}/lessons", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: str,
    lesson_data: LessonCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a lesson for a course (course owner or admin only)"""

    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check permission (owner or admin)
    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add lessons to this course"
        )

    # Create lesson
    new_lesson = Lesson(
        title=lesson_data.title,
        content=lesson_data.content,
        video_url=lesson_data.video_url,
        order=lesson_data.order,
        course_id=course_id
    )

    session.add(new_lesson)
    session.commit()
    session.refresh(new_lesson)

    logger.info(
        f"Lesson created: {new_lesson.title} for course {course.title}")

    return LessonRead(
        id=new_lesson.id,
        title=new_lesson.title,
        content=new_lesson.content,
        video_url=new_lesson.video_url,
        order=new_lesson.order,
        course_id=new_lesson.course_id,
        created_at=new_lesson.created_at,
        updated_at=new_lesson.updated_at
    )
