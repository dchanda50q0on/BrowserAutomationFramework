import asyncio
from typing import List, Type
from concurrent.futures import ThreadPoolExecutor
from .base_test import BaseTest
from .report_generator import TestReport
from .config import Config


class TestRunner:
    def __init__(self, max_workers: int = 4):
        self.report = TestReport()
        self.max_workers = max_workers

    async def _run_test_in_thread(self, test_class: Type[BaseTest]):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            await loop.run_in_executor(
                executor,
                lambda: asyncio.run(self.run_test(test_class))
            )

    async def run_test(self, test_class: Type[BaseTest]):
        test_name = test_class.__name__
        self.report.start_timer(test_name)
        test_instance = test_class()
        try:
            result = await test_instance.run()
            self.report.add_success(test_name, result)
        except Exception as e:
            self.report.add_failure(test_name, str(e))

    async def run_tests_parallel(self, test_classes: List[Type[BaseTest]], report_format: str = 'all'):
        tasks = [self._run_test_in_thread(test_class) for test_class in test_classes]
        await asyncio.gather(*tasks, return_exceptions=True)
        return self.report.generate_report(report_format)