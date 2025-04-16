import asyncio
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Type, Dict
from dotenv import load_dotenv

from browser_use.agent.service import Agent
from browser_use.controller.service import Controller
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr
from core.config import Config

# Load environment variables from .env file
load_dotenv()


class BaseTest(ABC):
    def __init__(self):
        self.screenshot_dir = Config.get_screenshot_dir()
        self.screenshot_dir.mkdir(exist_ok=True)

        # Load credentials from environment variables
        self.credentials: Dict[str, str] = {
            'username': os.getenv('TEST_USERNAME', ''),
            'password': os.getenv('TEST_PASSWORD', '')
        }

        # Validate credentials
        if not all(self.credentials.values()):
            raise ValueError(
                "Missing credentials in environment variables. "
                "Please set TEST_USERNAME and TEST_PASSWORD in .env file"
            )

        self.login_selectors: Dict[str, str] = {
            'username': '#username',
            'password': '#password',
            'submit': '#submit',
            'success_message': 'text=Congratulations'
        }
        self._login_url = ''
        self._post_login_url = ''

        output_model_class = self.get_output_model()
        self.controller = Controller(output_model=output_model_class)
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the Gemini LLM"""
        os.environ["GEMINI_API_KEY"] = Config.get_gemini_api_key()
        return ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL,
            api_key=SecretStr(os.environ["GEMINI_API_KEY"])
        )

    @abstractmethod
    def get_task(self) -> str:
        """Define the task instructions for the agent (without credentials)"""
        pass

    @abstractmethod
    def get_output_model(self) -> Type[BaseModel]:
        """Return the output model CLASS (not instance)"""
        pass

    @abstractmethod
    def validate_results(self, result: BaseModel):
        """Validate the test results against the output model"""
        pass

    async def _take_screenshot(self, agent: Agent, filename: str) -> Optional[str]:
        """Take screenshot of the current page"""
        try:
            if hasattr(agent, 'page') and agent.page:
                screenshot_path = self.screenshot_dir / filename
                await agent.page.screenshot(
                    path=str(screenshot_path),
                    full_page=True
                )
                return str(screenshot_path)
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
        return None

    async def _perform_secure_login(self, page):
        """Execute login completely outside agent system"""
        if not self.credentials or not self._login_url:
            return

        try:
            # Load login page with timeout
            await page.goto(self._login_url, wait_until="networkidle", timeout=10000)

            # Verify all required elements exist
            for field, selector in self.login_selectors.items():
                if field in ['username', 'password', 'submit']:
                    if not await page.query_selector(selector):
                        raise ValueError(f"Login field not found: {field} ({selector})")

            # Execute login via direct Playwright commands
            await page.fill(self.login_selectors['username'], self.credentials['username'])
            await page.fill(self.login_selectors['password'], self.credentials['password'])

            # Wait for navigation to complete
            async with page.expect_navigation(timeout=10000):
                await page.click(self.login_selectors['submit'])

            # Verify successful login
            await page.wait_for_selector(
                self.login_selectors['success_message'],
                timeout=5000,
                state="visible"
            )

        except Exception as e:
            print(f"SECURE LOGIN FAILED: {e}")
            await self._take_screenshot(None, "login_failure.png")
            raise RuntimeError("Secure login system failed") from e

    async def run(self):
        """Execute the test with secure credential handling"""
        os.environ["PLAYWRIGHT_HEADLESS"] = "1"
        os.environ["BROWSER_TYPE"] = os.getenv("BROWSER_TYPE", "firefox")

        agent = Agent(
            self.get_task(),  # Credential-free task
            self.llm,
            controller=self.controller,
            use_vision=False,
        )

        try:
            # Phase 1: Browser Launch
            if hasattr(agent, 'start'):
                await agent.start()

            # Phase 2: Secure Login (Bypass Agent Completely)
            if hasattr(agent, 'page') and self.credentials:
                await self._perform_secure_login(agent.page)

            # Phase 3: Agent Continues Post-Login
            history = await agent.run()
            history.save_to_file(f'history_{self.__class__.__name__}.json')

            test_result = history.final_result()
            validated_result = self.get_output_model().model_validate_json(test_result)
            self.validate_results(validated_result)
            return validated_result

        except Exception as e:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_file = f"failure_{self.__class__.__name__}_{timestamp}.png"
            await self._take_screenshot(agent, screenshot_file)
            raise RuntimeError(f"Test failed: {str(e)}") from e

        finally:
            if hasattr(agent, 'close_browser'):
                await agent.close_browser()
            elif hasattr(agent, 'close'):
                await agent.close()