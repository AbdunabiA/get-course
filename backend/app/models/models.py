# backend/app/models/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

# Enums


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    INSTRUCTOR = "INSTRUCTOR"
    ADMIN = "ADMIN"

# Base model with common fields


class TimestampModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# User Model


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    role: UserRole = Field(default=UserRole.STUDENT)


class User(UserBase, TimestampModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    password_hash: str

    # Relationships
    profile: Optional["Profile"] = Relationship(back_populates="user")
    courses: List["Course"] = Relationship(back_populates="instructor")
    enrollments: List["Enrollment"] = Relationship(back_populates="student")
    reviews: List["Review"] = Relationship(back_populates="student")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str
    name: str


class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None

# Profile Model


class ProfileBase(SQLModel):
    name: str
    bio: Optional[str] = None
    avatar: Optional[str] = None


class Profile(ProfileBase, TimestampModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", unique=True)

    # Relationships
    user: Optional[User] = Relationship(back_populates="profile")


class ProfileCreate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime


class ProfileUpdate(SQLModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

# Category Model


class CategoryBase(SQLModel):
    name: str = Field(unique=True, index=True)


class Category(CategoryBase, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Relationships
    courses: List["Course"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: str


class CategoryUpdate(SQLModel):
    name: Optional[str] = None

# Course Model


class CourseBase(SQLModel):
    title: str = Field(index=True)
    description: str
    image: Optional[str] = None
    price: Optional[float] = Field(default=0.0, ge=0)
    is_published: bool = Field(default=False)


class Course(CourseBase, TimestampModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    instructor_id: str = Field(foreign_key="user.id")
    category_id: Optional[str] = Field(default=None, foreign_key="category.id")

    # Relationships
    instructor: Optional[User] = Relationship(back_populates="courses")
    category: Optional[Category] = Relationship(back_populates="courses")
    lessons: List["Lesson"] = Relationship(
        back_populates="course", cascade_delete=True)
    enrollments: List["Enrollment"] = Relationship(back_populates="course")
    reviews: List["Review"] = Relationship(back_populates="course")


class CourseCreate(CourseBase):
    category_id: Optional[str] = None


class CourseRead(CourseBase):
    id: str
    instructor_id: str
    category_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Include related data
    instructor: Optional[UserRead] = None
    category: Optional[CategoryRead] = None
    lessons_count: Optional[int] = None
    enrollments_count: Optional[int] = None


class CourseUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    price: Optional[float] = None
    is_published: Optional[bool] = None
    category_id: Optional[str] = None

# Lesson Model


class LessonBase(SQLModel):
    title: str
    content: str
    video_url: Optional[str] = None
    order: int = Field(ge=1)


class Lesson(LessonBase, TimestampModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    course_id: str = Field(foreign_key="course.id")

    # Relationships
    course: Optional[Course] = Relationship(back_populates="lessons")


class LessonCreate(LessonBase):
    pass


class LessonRead(LessonBase):
    id: str
    course_id: str
    created_at: datetime
    updated_at: datetime


class LessonUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    order: Optional[int] = None

# Enrollment Model


class EnrollmentBase(SQLModel):
    progress: float = Field(default=0.0, ge=0.0, le=100.0)


class Enrollment(EnrollmentBase, TimestampModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="user.id")
    course_id: str = Field(foreign_key="course.id")

    # Relationships
    student: Optional[User] = Relationship(back_populates="enrollments")
    course: Optional[Course] = Relationship(back_populates="enrollments")

    # Unique constraint: one enrollment per student per course
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class EnrollmentCreate(EnrollmentBase):
    course_id: str


class EnrollmentRead(EnrollmentBase):
    id: str
    student_id: str
    course_id: str
    created_at: datetime
    updated_at: datetime

    # Include related data
    course: Optional[CourseRead] = None


class EnrollmentUpdate(SQLModel):
    progress: Optional[float] = None

# Review Model


class ReviewBase(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: str


class Review(ReviewBase, TimestampModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="user.id")
    course_id: str = Field(foreign_key="course.id")

    # Relationships
    student: Optional[User] = Relationship(back_populates="reviews")
    course: Optional[Course] = Relationship(back_populates="reviews")

    # Unique constraint: one review per student per course
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class ReviewCreate(ReviewBase):
    course_id: str


class ReviewRead(ReviewBase):
    id: str
    student_id: str
    course_id: str
    created_at: datetime

    # Include related data
    student: Optional[UserRead] = None


class ReviewUpdate(SQLModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

# RefreshToken Model (for JWT rotation)


class RefreshTokenBase(SQLModel):
    hashed_token: str = Field(unique=True, index=True)
    is_revoked: bool = Field(default=False)
    expires_at: datetime


class RefreshToken(RefreshTokenBase, TimestampModel, table=True):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    replaced_by_id: Optional[str] = Field(
        default=None, foreign_key="refreshtoken.id")

    # Relationships
    user: Optional[User] = Relationship(back_populates="refresh_tokens")


class RefreshTokenCreate(RefreshTokenBase):
    user_id: str


class RefreshTokenRead(RefreshTokenBase):
    id: str
    user_id: str
    created_at: datetime
