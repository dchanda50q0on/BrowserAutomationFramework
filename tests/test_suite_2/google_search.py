from core.base_test import BaseTest
from pydantic import BaseModel


class GoogleSearchResult(BaseModel):
    search_query: str
    first_result_title: str
    first_result_url: str


class TestGoogleSearch(BaseTest):
    def get_task(self) -> str:
        return (
            'Open google.com\n'
            'Search for "Python programming"\n'
            'Get the title and URL of the first result\n'
            'Close the browser'
        )

    def get_output_model(self) -> BaseModel:
        return GoogleSearchResult

    def validate_results(self, result: GoogleSearchResult):
        assert 'python' in result.first_result_title.lower()
        assert result.first_result_url.startswith('http')