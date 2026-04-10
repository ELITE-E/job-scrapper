from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import get_password_hash,verify_password

async def create_user(
        db:AsyncSession,
        email:str,
        password:str,
        full_name:str | None
):
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValueError("Email already registered")
    
    user = User(
        email =email,
        hashed_password= get_password_hash(password=password),
        full_name=full_name
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user

async def authenticate_user(
        db:AsyncSession,
        email:str,
        password:str
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return None
    if not verify_password(password,user.hashed_password):
        return None
    return user