"""
Dashboard API Routes
Provides summary statistics for the student dashboard
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logger import setup_logger
from app.models import Note, QuizSession

from .auth import get_current_user

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    responses={
        401: {"description": "Unauthorized"},
    },
)
async def get_dashboard_summary(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get dashboard summary statistics for current user.

    **Headers:**
    - `Authorization`: Bearer {token}

    **Response:**
    ```json
    {
      "total_notes": 5,
      "total_topics": 12,
      "total_quizzes": 8,
      "average_quiz_score": 78.5,
      "learning_streak": 3,
      "last_activity": "2024-01-20T15:30:00Z"
    }
    ```

    **Metrics:**
    - `total_notes`: Number of uploaded notes
    - `total_topics`: Number of extracted topics
    - `total_quizzes`: Number of completed quizzes
    - `average_quiz_score`: Average score across quizzes
    - `learning_streak`: Consecutive days of activity
    - `last_activity`: Last interaction timestamp

    **Security:** Requires valid JWT token
    """
    try:
        user_id = current_user["id"]

        # Count total notes
        notes_result = await db.execute(
            select(func.count(Note.id)).where(Note.user_id == user_id)
        )
        total_notes = notes_result.scalar() or 0

        # Count total quizzes
        quizzes_result = await db.execute(
            select(func.count(QuizSession.id)).where(
                QuizSession.user_id == user_id,
                QuizSession.status == "completed",
            )
        )
        total_quizzes = quizzes_result.scalar() or 0

        # Get average quiz score
        avg_score_result = await db.execute(
            select(func.avg(QuizSession.score_percentage)).where(
                QuizSession.user_id == user_id,
                QuizSession.status == "completed",
            )
        )
        average_score = avg_score_result.scalar() or 0

        # TODO: Calculate learning streak
        # TODO: Get last activity timestamp

        return {
            "total_notes": total_notes,
            "total_topics": 0,  # TODO: Calculate from topics table
            "total_quizzes": total_quizzes,
            "average_quiz_score": round(average_score, 2),
            "learning_streak": 0,  # TODO: Implement streak calculation
            "last_activity": None,  # TODO: Get from AI interactions
        }

    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard summary",
        )
