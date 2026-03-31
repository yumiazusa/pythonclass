from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Edu Code Platform API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "edu_user"
    mysql_password: str = "edu_password"
    mysql_db: str = "edu_code_platform"
    jwt_secret_key: str = "please-change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    code_run_timeout_seconds: int = 15
    code_run_max_output_chars: int = 20000
    code_run_temp_dir: str = "/tmp/edu_code_runner"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
            "?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
