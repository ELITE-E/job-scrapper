from sqlalchemy.ext.asyncio import async_sessionmaker,create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Use the computed field for database URL
# The computed field will be a PostgresDsn object, convert to string
DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI)

engine=create_async_engine(url=DATABASE_URL,
                           pool_size=10,
                           max_overflow=20,
                           pool_timeout=30,
                           echo=True)

async_session_maker=async_sessionmaker(engine,
                                       expire_on_commit=False)
AsyncSessionLocation = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)