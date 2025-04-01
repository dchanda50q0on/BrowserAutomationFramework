import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class Config:
    BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chromium')
    HEADLESS = os.getenv('HEADLESS', 'True') == 'True'
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    TEST_TIMEOUT = int(os.getenv('TEST_TIMEOUT', '60'))  # seconds

    @staticmethod
    def get_gemini_api_key() -> str:
        return os.getenv("GEMINI_API_KEY")