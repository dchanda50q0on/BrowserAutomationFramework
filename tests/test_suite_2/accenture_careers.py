from core.base_test import BaseTest
from pydantic import BaseModel


class CareerPageResult(BaseModel):
    search: str
    click: str
    tab: str
    chat: str
    close: str
    url: str
    title: str


class TestAccentureCareers(BaseTest):
    def get_task(self) -> str:
        return (
            'Open google.com and search for Accenture Canada\n'
            'Click on the first link\n'
            'Click on the Careers Tab\n'
            'Click Search Jobs\n'
            'Get URL and title of the page\n'
            'Search for Curan Tech Lead role\n'
            'Close the browser'
        )

    def get_output_model(self) -> BaseModel:
        return CareerPageResult

    def validate_results(self, result: CareerPageResult):
        assert 'Search Jobs' in result.title
        assert 'accenture.com/ca-en/careers' in result.url.lower()