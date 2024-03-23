from environs import Env
from dataclasses import dataclass


@dataclass
class Bot:
    bot_token: str
    admin_id: int


@dataclass
class Settings:
    bot: Bot


def get_settings(path):
    env = Env()
    env.read_env(path=path)
    return Settings(
        bot=Bot(
            bot_token=env.str("TOKEN"),
            admin_id=env.int("ADMIN_ID")
        )
    )


settings = get_settings('input')
