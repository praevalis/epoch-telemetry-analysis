import urllib.parse
from typing import Literal

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: Literal['development', 'testing', 'production'] = 'development'

    DB_HOST: str = 'http://localhost'
    DB_PORT: str = '5432'
    DB_USERNAME: str = 'postgres'
    DB_PASSWORD: SecretStr = SecretStr('postgres')
    DB_NAME: str = 'epoch_db'

    @computed_field
    @property
    def DB_URL(self) -> str:
        password = self.DB_PASSWORD.get_secret_value()

        parsed_username = urllib.parse.quote_plus(self.DB_USERNAME)
        parsed_password = urllib.parse.quote_plus(password)

        ssl_param = ''
        if self.ENVIRONMENT == 'production':
            ssl_param = '?sslmode=require'

        return (
            f'postgresql+asyncpg://{parsed_username}:{parsed_password}'
            f'@{self.DB_HOST}:{self.DB_PORT}/${self.DB_NAME}{ssl_param}'
        )

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: str = '6379'
    REDIS_USERNAME: str = 'default'
    REDIS_PASSWORD: SecretStr = SecretStr('redis')
    REDIS_INDEX: str = '0'

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        password = self.REDIS_PASSWORD.get_secret_value()

        parsed_username = urllib.parse.quote_plus(self.REDIS_USERNAME)
        parsed_password = urllib.parse.quote_plus(password)

        protocol = 'rediss' if self.ENVIRONMENT == 'production' else 'redis'

        return (
            f'{protocol}://{parsed_username}:{parsed_password}'
            f'@{self.REDIS_HOST}:{self.REDIS_PASSWORD}/{self.REDIS_INDEX}'
        )
