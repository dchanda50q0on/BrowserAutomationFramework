import asyncio
from typing import List, Type
from core.base_test import BaseTest
from core.report_generator import TestReport


class TestRunner:
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.report = TestReport()
        self.semaphore = asyncio.Semaphore(max_workers)

    async def _execute_test(self, test_class: Type[BaseTest]):
        async with self.semaphore:
            test_name = test_class.__name__
            self.report.start_timer(test_name)

            try:
                test_instance = test_class()
                result = await test_instance.run()
                self.report.add_success(test_name, result)
            except Exception as e:
                self.report.add_failure(test_name, str(e))
            finally:
                if hasattr(test_instance, 'controller'):
                    await test_instance.controller.close()

    async def run_tests_parallel(self, test_classes: List[Type[BaseTest]]) -> bool:
        tasks = [self._execute_test(tc) for tc in test_classes]
        await asyncio.gather(*tasks, return_exceptions=True)

        report_data = self.report.generate_report('all')
        return report_data['summary']['failed'] == 0