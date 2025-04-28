from core.base_test import BaseTest
from pydantic import BaseModel


class CnTestResult(BaseModel):
    url: str
    title: str
    menu_items_visible: bool
    links_visible: bool
    links_clickable: bool
    cn_ceo: str


class TestCnWebsite(BaseTest):
    def get_task(self) -> str:
        return (
            'Open browser and navigate to https://www.cn.ca/en/'
            'Verify that all top navigation menu items are visible and clickable'
            'Verify that all links are visible and clickable'
            'From the website learn about CN Leadership and find who is the CEO and President'
            'Close the Browser'
        )

    def get_output_model(self) -> BaseModel:
        return CnTestResult

    def validate_results(self, result: CnTestResult):
        assert 'Tracy Robinson' in result.cn_ceo
