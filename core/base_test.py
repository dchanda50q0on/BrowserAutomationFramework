import asyncio
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from browser_use.agent.service import Agent
from browser_use.controller.service import Controller
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr
from core.config import Config


class BaseTest(ABC):
    def __init__(self):
        self.screenshot_dir = Config.get_screenshot_dir()
        self.screenshot_dir.mkdir(exist_ok=True)
        self.controller = Controller(output_model=self.get_output_model())
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
        """Define the task instructions for the agent"""
        pass

    @abstractmethod
    def get_output_model(self) -> BaseModel:
        """Define the expected output Pydantic model"""
        pass

    @abstractmethod
    def validate_results(self, result: BaseModel):
        """Validate the test results"""
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

    async def run(self):
        """Execute the test using browser-use agent"""
        # Configure browser launch options through environment variables
        os.environ["BROWSER_HEADLESS"] = str(Config.HEADLESS).lower()
        os.environ["BROWSER_TYPE"] = Config.BROWSER_TYPE
        os.environ["BROWSER_TIMEOUT"] = str(Config.TEST_TIMEOUT * 1000)

        agent = Agent(
            self.get_task(),
            self.llm,
            controller=self.controller,
            use_vision=True
        )

        try:
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