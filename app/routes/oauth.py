from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from google.oauth2 import id_token
import httpx

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User as UserModel
from app.db.session import get_db

router = APIRouter(tags=["oauth"])


@router.get("/login/google")
async def login_google():
    """
    Generate Google OAuth login URL
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )

    authorization_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        "response_type=code&"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        "scope=openid%20email%20profile&"
        "access_type=offline"
    )

    return {"authorization_url": authorization_url}


@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """
    Handle Google OAuth callback
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)

        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Failed to fetch Google token")

        tokens = response.json()
        id_token_str = tokens.get("id_token")

        if not id_token_str:
            raise HTTPException(
                status_code=400, detail="Invalid token response from Google")

    # Verify the ID token
    try:
        id_info = id_token.verify_oauth2_token(
            id_token_str, httpx.Client(), settings.GOOGLE_CLIENT_ID)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid ID token: {str(e)}")

    user_email = id_info.get("email")
    user_name = id_info.get("name", "")
    google_id = id_info.get("sub")

    if not user_email or not google_id:
        raise HTTPException(
            status_code=400, detail="Google authentication failed")

    # Check if user exists
    result = await db.execute(
        select(UserModel).where(
            (UserModel.email == user_email) | (
                UserModel.google_id == google_id)
        )
    )
    user = result.scalars().first()

    # Create or update user
    if not user:
        user = UserModel(
            email=user_email,
            full_name=user_name,
            google_id=google_id,
            is_active=True,
        )
        db.add(user)
    elif not user.google_id:
        user.google_id = google_id

    await db.commit()
    await db.refresh(user)

    # Create JWT token
    access_token = create_access_token(subject=user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "name": user.full_name
        }
    }
