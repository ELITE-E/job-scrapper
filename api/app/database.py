from sqlalchemy.ext.asyncio import async_sessionmaker,create_async_engine
from config import settings

DATABASE_URL=settings.get_db_url()

engine=create_async_engine(url=DATABASE_URL,
                           pool_size=10,
                           max_overflow=20,
                           pool_timeout=30,
                           echo=True)

async_session_maker=async_sessionmaker(engine,
                                       expire_on_commit=False)

