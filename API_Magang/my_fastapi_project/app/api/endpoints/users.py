"""
User endpoints — placeholder.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
def get_users():
    """Placeholder — implementasi nanti."""
    return {"message": "User endpoint — belum diimplementasi"}
