from decouple import config


class Settings:
    BOT_TOKEN = config("BOT_TOKEN")
    API_URL = config("API_URL")


settings = Settings()
