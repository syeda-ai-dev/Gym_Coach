import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.openai_api_key = os.getenv("OPENAI_API_KEY")
            cls._instance.openai_endpoint = os.getenv("OPENAI_ENDPOINT")
            cls._instance.model_name = os.getenv("MODEL")
        return cls._instance