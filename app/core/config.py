from pydantic import BaseSettings


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"

    app_host: str = "0.0.0.0"
    app_port: int = 8000

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "luanfba71@gmail.com"
    smtp_password: str = "dmfe ojoj evbx qmln"
    smtp_from: str = "luanfba71@gmail.com"
    smtp_tls: bool = True
    notify_email: str = "luanfba.araujo@hotmail.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
