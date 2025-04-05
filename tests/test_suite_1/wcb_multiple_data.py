from core.base_test import BaseTest
from pydantic import BaseModel
from typing import Dict, List
import csv
import os


class WcbPremiumResult(BaseModel):
    premium_rate: str
    industry_code: str


class TestWcbPremium(BaseTest):
    CSV_FILE_PATH = os.path.join('test_cases', 'wcb_premium_test_cases.csv')

    def get_task(self) -> str:
        # Load all test cases
        test_cases = self._load_test_cases()

        # Build one comprehensive task that covers all cases
        task_lines = ['Open browser and launch https://rm.wcb.ab.ca/WCB.RateManual.WebServer']

        for case in test_cases:
            task_lines.extend([
                f'Click {case["search_item"]}',
                f'Click {case["sub_item"]}',
                f'Click {case["sub_sub_item"]}',
                'Verify current page',
                'Store premium data for validation',
                'Go back to homepage'
            ])

        task_lines.append('Close the Browser')
        return '\n'.join(task_lines)

    def _load_test_cases(self) -> List[Dict[str, str]]:
        test_cases = []
        if not os.path.exists(self.CSV_FILE_PATH):
            raise FileNotFoundError(f"CSV file not found at {self.CSV_FILE_PATH}")

        with open(self.CSV_FILE_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                test_cases.append({
                    'search_item': row['SearchItem'],
                    'sub_item': row['SubItem'],
                    'sub_sub_item': row['SubSubItem'],
                    'expected_premium_rate': row['ExpectedPremiumRate'],
                    'expected_industry_code': row['ExpectedIndustryCode']
                })
        return test_cases

    def get_output_model(self) -> BaseModel:
        return WcbPremiumResult

    def validate_results(self, result: WcbPremiumResult):
        test_cases = self._load_test_cases()
        all_rates = result.premium_rate if isinstance(result.premium_rate, list) else [result.premium_rate]
        all_codes = result.industry_code if isinstance(result.industry_code, list) else [result.industry_code]

        for i, case in enumerate(test_cases):
            assert case['expected_premium_rate'] in all_rates[i], \
                f"Test case {i + 1}: Expected rate {case['expected_premium_rate']} not found"
            assert case['expected_industry_code'] in all_codes[i], \
                f"Test case {i + 1}: Expected code {case['expected_industry_code']} not found"