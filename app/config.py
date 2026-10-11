from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str = "localhost"
    database_port: str = "5432"
    database_password: str
    database_name: str
    database_username: str = "postgres"
    secret_key: str = "7vcn4hd537dhc0wp3l6bc63x85j67gg5fb384jd"
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()