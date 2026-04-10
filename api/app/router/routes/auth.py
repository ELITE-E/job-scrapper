from fastapi import APIRouter, Depends,HTTPException,status,Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select

from app.schemas.auth import Token
from app.schemas.user import UserCreate
from app.dependencies import get_db,get_current_user

from app.services.auth_service import create_user,authenticate_user
from app.core.security import create_access_token,create_refresh_token,verify_token
from app.models.user import User

from app.schemas.error import HTTPError
from app.schemas.user import UserResponse
from app.core.limiter import limiter



router = APIRouter(prefix="/auth",tags=["auth"])

@router.post(
        "/register",
        response_model=Token,
         responses={
        400: {"model": HTTPError, "description": "Email already registered"},
        422: {"model": HTTPError, "description": "Validation error"},
    },
    )
@limiter.limit("3/minute")
async def  register(
    request:Request,
    user_in:UserCreate,
    db:AsyncSession = Depends(get_db)
):
    try:
        user = await create_user(
            db,
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Email already registered")
    access_token = create_access_token(data={"sub":user.email})

    return {"access_token":access_token}


@router.post(
        "/login",
        response_model=Token,
          responses={
        401: {"model": HTTPError, "description": "Invalid credentials"},
        422: {"model": HTTPError, "description": "Validation error"},
    },
    )
@limiter.limit("5/minute")      
async def login(
    request:Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token({"sub":user.email})

    user.refresh_token = refresh_token
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token":refresh_token,
        "token_type":  "bearer"}


@router.get(
        "/me",
        response_model=UserResponse,
        responses={
        401: {"model": HTTPError, "description": "Unauthorized"},
        },
        )
async def get_me(current_user:User = Depends(get_current_user)):
    return current_user


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    email = verify_token(refresh_token, token_type="refresh")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or user.refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": user.email})

    return {"access_token": new_access_token}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    current_user.refresh_token = None
    await db.commit()

    return {"message": "Logged out successfully"}