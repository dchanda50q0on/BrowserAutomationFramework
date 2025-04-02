import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Browser Configuration
    BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chromium')
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    TEST_TIMEOUT = int(os.getenv('TEST_TIMEOUT', '60'))  # seconds

    # Gemini Configuration
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

    @staticmethod
    def get_screenshot_dir() -> Path:
        return Path(__file__).parent.parent / 'screenshots'

    @staticmethod
    def get_report_dir() -> Path:
        return Path(__file__).parent.parent / 'reports'

    @staticmethod
    def get_template_dir() -> Path:
        return Path(__file__).parent.parent / 'report_templates'

    @staticmethod
    def get_gemini_api_key() -> str:
        return os.getenv("GEMINI_API_KEY")