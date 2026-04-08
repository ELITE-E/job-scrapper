from datetime import datetime,timedelta,timezone
from jose import JWTError,jwt
from passlib.context import CryptContext
from fastapi import HTTPException,status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def create_access_token(data:dict,expires_delta:timedelta |None= None)->str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,
                      settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)

def decode_token(token:str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        return None
    
def get_password_hash(password:str)->str:
  return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    return pwd_context.verify(plain_password,hashed_password)

def verify_token(token:str):
     try:
         payload = jwt.decode(
             token,
             settings.SECRET_KEY,
             algorithms=[settings.ALGORITHM]
         )

         sub :str | None = payload.get("sub")

         if sub is None :
             raise HTTPException(
                 status_code=status.HTTP_401_UNAUTHORIZED,
                 detail="Could not validate credentials"
             )
         return sub
     
     except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) 