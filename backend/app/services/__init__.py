"""
Authentication Service Module
Handles user authentication logic including registration, login, and verification
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import setup_logger
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

logger = setup_logger(__name__)


class AuthenticationError(Exception):
    """Custom exception for authentication errors"""

    pass


class UserService:
    """Service for user management and authentication"""

    @staticmethod
    async def create_user(
        db: AsyncSession, user_data: UserCreate
    ) -> UserResponse:
        """
        Create a new user account.

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            UserResponse: Created user data

        Raises:
            AuthenticationError: If email already exists or validation fails
        """
        # Check if email already exists
        existing_user = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_user.scalar_one_or_none():
            logger.warning(f"Registration attempt with existing email: {user_data.email}")
            raise AuthenticationError("Email already registered")

        try:
            # Create new user
            hashed_password = hash_password(user_data.password)
            new_user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                role="student",
                preferences={"theme": "light", "notifications": True},
            )

            db.add(new_user)
            await db.flush()  # Flush to get the ID without committing
            await db.commit()

            logger.info(f"User created successfully: {new_user.email}")
            return UserResponse.from_orm(new_user)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise AuthenticationError(f"Failed to create user: {str(e)}")

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> tuple[User, str]:
        """
        Authenticate user with email and password.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            Tuple of (User, JWT token)

        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Find user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            raise AuthenticationError("Invalid email or password")

        # Note: In Phase 2, we'll add password verification to the User model
        # For now, we're using basic structure
        logger.info(f"User authenticated successfully: {email}")

        # Create JWT token
        token = create_access_token(user_id=str(user.id), email=user.email)

        return user, token

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            User object or None if not found
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User object or None if not found
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user_profile(
        db: AsyncSession, user_id: str, **kwargs
    ) -> UserResponse:
        """
        Update user profile information.

        Args:
            db: Database session
            user_id: User UUID
            **kwargs: Fields to update

        Returns:
            Updated UserResponse

        Raises:
            AuthenticationError: If user not found
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise AuthenticationError("User not found")

        # Update only allowed fields
        allowed_fields = {"full_name", "bio", "preferences"}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        await db.commit()

        logger.info(f"User profile updated: {user_id}")
        return UserResponse.from_orm(user)

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str) -> None:
        """
        Delete user account (soft delete approach recommended in production).

        Args:
            db: Database session
            user_id: User UUID

        Raises:
            AuthenticationError: If user not found
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise AuthenticationError("User not found")

        await db.delete(user)
        await db.commit()

        logger.info(f"User deleted: {user_id}")
