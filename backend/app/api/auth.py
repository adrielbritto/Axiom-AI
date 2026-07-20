"""
Authentication API Routes
Handles user registration, login, logout, and session management
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.schemas import (
    ErrorResponse,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.services import AuthenticationError, UserService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# ============================================================================
# DEPENDENCIES
# ============================================================================


async def get_current_user(
    authorization: str = None,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Dependency to extract and validate current user from JWT token.

    Args:
        authorization: Authorization header (Bearer token)
        db: Database session

    Returns:
        UserResponse: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = authorization.replace("Bearer ", "")
    token_data = decode_access_token(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = await UserService.get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return UserResponse.from_orm(user)


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or email exists"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Register a new user account.

    **Request Body:**
    - `email`: User email address (must be unique)
    - `password`: Password (minimum 8 characters)
    - `full_name`: User's full name
    - `confirm_password`: Password confirmation (must match)

    **Response:**
    - `id`: User UUID
    - `email`: User email
    - `full_name`: User full name
    - `role`: User role (default: "student")
    - `created_at`: Account creation timestamp

    **Errors:**
    - `400`: Email already registered or validation failed
    - `500`: Server error during registration

    **Example:**
    ```json
    {
      "email": "student@example.com",
      "password": "SecurePass123!",
      "full_name": "John Doe"
    }
    ```
    """
    try:
        return await UserService.create_user(db, user_data)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again.",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Login user with email and password.

    **Request Body:**
    - `email`: User email address
    - `password`: User password

    **Response:**
    - `access_token`: JWT token for authenticated requests
    - `token_type`: "bearer"
    - `user`: User information (email, name, role, etc.)

    **Errors:**
    - `400`: Invalid email or password
    - `500`: Server error during login

    **Usage:**
    Include the token in subsequent requests:
    ```
    Authorization: Bearer <access_token>
    ```

    **Example:**
    ```json
    {
      "email": "student@example.com",
      "password": "SecurePass123!"
    }
    ```
    """
    try:
        user, token = await UserService.authenticate_user(
            db, credentials.email, credentials.password
        )
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.from_orm(user),
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again.",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def get_current_user_info(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    """
    Get current authenticated user information.

    **Headers:**
    - `Authorization`: Bearer {token}

    **Response:**
    - User profile information

    **Errors:**
    - `401`: Invalid or missing token

    **Security:** Requires valid JWT token
    """
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def logout(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> None:
    """
    Logout current user.

    **Headers:**
    - `Authorization`: Bearer {token}

    **Response:**
    - Status 204 No Content on success

    **Note:**
    - Token should be removed from client storage after logout
    - Token remains valid until expiration (stateless JWT)
    - For production, implement token blacklist

    **Security:** Requires valid JWT token
    """
    # In production, add token to blacklist
    # For now, frontend handles token deletion
    pass


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def refresh_token(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> TokenResponse:
    """
    Refresh JWT access token.

    **Headers:**
    - `Authorization`: Bearer {current_token}

    **Response:**
    - New JWT token with refreshed expiration

    **Errors:**
    - `401`: Invalid or expired token

    **Security:** Requires valid JWT token
    """
    # In production, implement proper refresh token flow
    # For now, just return the same user data
    return TokenResponse(
        access_token="",  # Would generate new token
        token_type="bearer",
        user=current_user,
    )
