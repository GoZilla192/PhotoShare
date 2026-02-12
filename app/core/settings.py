import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	APP_NAME: str = "PhotoShare"
	DB_HOST: str
	DB_PORT: int
	DB_USER: str
	DB_PASSWORD: str
	DB_NAME: str
	DB_DRIVER: str = "postgresql+asyncpg"

	SECRET_KEY: str
	ALGORITHM: str
	ACCESS_TOKEN_EXPIRE_MINUTES: int

	# Cloudinary
	CLOUDINARY_NAME: str
	CLOUDINARY_API_KEY: str
	CLOUDINARY_API_SECRET: str
	CLOUDINARY_URL: str
	
	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8"
	)
	
	@property
	def database_url(self):
		return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
	
	model_config = SettingsConfigDict(
        env_file=(
            ".env.test"
            if os.getenv("ENV") == "test"
            else ".env"
        ),
        extra="ignore",
    )