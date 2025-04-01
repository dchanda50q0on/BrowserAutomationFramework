import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from browser_use.agent.service import Agent
from browser_use.controller.service import Controller
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr
import os
from pathlib import Path
from datetime import datetime


class BaseTest(ABC):
    def __init__(self):
        self.controller = Controller(output_model=self.get_output_model())
        self.llm = self._initialize_llm()
        self.screenshot_dir = "screenshots"
        Path(self.screenshot_dir).mkdir(exist_ok=True)

    def _initialize_llm(self):
        os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
        return ChatGoogleGenerativeAI(
            model='gemini-1.5-flash',
            api_key=SecretStr(os.environ["GEMINI_API_KEY"])
        )

    async def _take_screenshot(self, agent: Agent, filename: str):
        try:
            if hasattr(agent, 'page') and agent.page:
                screenshot_path = Path(self.screenshot_dir) / filename
                await agent.page.screenshot(path=str(screenshot_path), full_page=True)
                return str(screenshot_path)
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
        return None

    @abstractmethod
    def get_task(self) -> str:
        pass

    @abstractmethod
    def get_output_model(self) -> BaseModel:
        pass

    @abstractmethod
    def validate_results(self, result: BaseModel):
        pass

    async def run(self):
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
            raise
        finally:
            if hasattr(agent, 'close_browser'):
                await agent.close_browser()