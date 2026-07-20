"""
Authentication Tests
Unit tests for authentication endpoints
"""

import pytest
from httpx import AsyncClient

from app.main import app
from app.services import UserService


@pytest.mark.asyncio
async def test_register_user(test_db, mock_user_data):
    """Test user registration."""
    user = await UserService.create_user(test_db, mock_user_data)

    assert user.email == mock_user_data["email"]
    assert user.full_name == mock_user_data["full_name"]
    assert user.role == "student"
    assert user.id is not None


@pytest.mark.asyncio
async def test_register_duplicate_email(test_db, mock_user_data):
    """Test registration fails with duplicate email."""
    # First registration
    await UserService.create_user(test_db, mock_user_data)

    # Second registration with same email
    from app.services import AuthenticationError

    with pytest.raises(AuthenticationError, match="Email already registered"):
        await UserService.create_user(test_db, mock_user_data)


@pytest.mark.asyncio
async def test_get_user_by_email(test_db, mock_user_data):
    """Test fetching user by email."""
    created_user = await UserService.create_user(test_db, mock_user_data)

    retrieved_user = await UserService.get_user_by_email(
        test_db, mock_user_data["email"]
    )

    assert retrieved_user is not None
    assert retrieved_user.email == created_user.email
    assert retrieved_user.id == created_user.id


@pytest.mark.asyncio
async def test_update_user_profile(test_db, mock_user_data):
    """Test updating user profile."""
    user = await UserService.create_user(test_db, mock_user_data)

    updated_user = await UserService.update_user_profile(
        test_db, str(user.id), full_name="Updated Name", bio="New bio"
    )

    assert updated_user.full_name == "Updated Name"
    assert updated_user.bio == "New bio"


@pytest.mark.asyncio
async def test_delete_user(test_db, mock_user_data):
    """Test user deletion."""
    user = await UserService.create_user(test_db, mock_user_data)

    await UserService.delete_user(test_db, str(user.id))

    # Verify user is deleted
    deleted_user = await UserService.get_user_by_id(test_db, str(user.id))
    assert deleted_user is None
