from typing import AsyncGenerator
from fastapi import HTTPException,Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import async_session_maker
from app.models.user import User
from app.core.security import oauth2_scheme,verify_token

async def get_db()->AsyncGenerator[AsyncSession,None]:
  async with async_session_maker() as session:
    yield session

async def get_current_user(token:str =Depends(oauth2_scheme),db:AsyncSession = Depends(get_db))->User:
 email= verify_token(token)
 result = select(User).where(
   User.email==email,
   User.is_active==True)
 
 user = result.scalar_one_or_none()
 if user is None:
   raise HTTPException(
     status_code=status.HTTP_401_UNAUTHORIZED,
                      detail="User not found or inactive")