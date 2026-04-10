import secrets
from typing import Annotated,Any,Literal
from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    computed_field
)
from pydantic_settings import BaseSettings,SettingsConfigDict

def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)

class Settings(BaseSettings):

    PROJECT_NAME :str  = "Job Scrapper API"
    DESCRIPTION :str = "RESTful API for aggregated job listings from multiple job boards."
    VERSION :str = "1.0.0"
    CONTACT:dict ={"name":"Ex","email":"Johndoe566@gmail.com"},
    LISENCE_INFO:dict ={"name":"MIT"},
    API_V1_STR : str = "/api/v1",
    ENVIRONMENT :str = "development"
    DOCS_URL:str = "/api/v1/docs",
    REDOC_URL:str = "/api/v1/docs",

    SENTRY_DSN: HttpUrl | None = None
    SECRET_KEY:str 
    ALGORITHM:str 
    ACCESS_TOKEN_EXPIRE_MINUTES :int = 30 
    REFRESH_TOKEN_EXPIRE_DAYS :int = 7
    DEBUG:bool = False


    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
         return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]
    
    DB_USER:str
    DB_PASSWORD:str
    DB_HOST:str
    DB_PORT:int = 5432
    DB_NAME:str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )
    
    REDIS_HOST: str 
    REDIS_PORT: int 
    @computed_field
    @property
    def REDIS_URL(self) -> RedisDsn:
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
        )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True
    )

    

settings = Settings()