# backend/app/routers/categories.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.models import (
    Category, User,
    CategoryCreate, CategoryRead, CategoryUpdate,
)
from app.auth.dependencies import get_current_user, require_admin
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryRead])
async def get_categories(
    session: Session = Depends(get_session)
):
    """Get all categories (public endpoint)"""

    categories = session.exec(select(Category)).all()

    return [
        CategoryRead(
            id=category.id,
            name=category.name
        )
        for category in categories
    ]


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: str,
    session: Session = Depends(get_session)
):
    """Get category by ID"""

    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return CategoryRead(
        id=category.id,
        name=category.name
    )


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Create a new category (admin only)"""

    # Check if category name already exists
    existing_category = session.exec(
        select(Category).where(Category.name == category_data.name)
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )

    # Create category
    new_category = Category(
        name=category_data.name
    )

    session.add(new_category)
    session.commit()
    session.refresh(new_category)

    logger.info(
        f"Category created: {new_category.name} by {current_user.email}")

    return CategoryRead(
        id=new_category.id,
        name=new_category.name
    )


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Update category (admin only)"""

    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if new name already exists (if name is being changed)
    if category_data.name and category_data.name != category.name:
        existing_category = session.exec(
            select(Category).where(Category.name == category_data.name)
        ).first()

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )

    # Update category
    category_dict = category_data.model_dump(exclude_unset=True)
    for field, value in category_dict.items():
        setattr(category, field, value)

    session.commit()
    session.refresh(category)

    logger.info(f"Category updated: {category.name} by {current_user.email}")

    return CategoryRead(
        id=category.id,
        name=category.name
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Delete category (admin only)"""

    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if category is being used by any courses
    from app.models.models import Course
    courses_using_category = session.exec(
        select(Course).where(Course.category_id == category_id)
    ).first()

    if courses_using_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category that is being used by courses"
        )

    session.delete(category)
    session.commit()

    logger.info(f"Category deleted: {category.name} by {current_user.email}")
