from core.base_test import BaseTest
from pydantic import BaseModel


class JobSearchResult(BaseModel):
    search_term: str
    job_titles: list[str]


class TestAccentureJobSearch(BaseTest):
    def get_task(self) -> str:
        return (
            'Open a web browser\n'
            'Navigate to https://www.accenture.com/ca-en/careers\n'
            'On the Careers page, click Job Search Link\n'
            'In the search input field, type "SAP" and click Search\n'
            'Verify that the search results display at least one job listing with the title containing "SAP"'
        )

    def get_output_model(self) -> BaseModel:
        return JobSearchResult

    def validate_results(self, result: JobSearchResult):
        assert result.search_term.lower() == "sap", f"Expected search term to be 'SAP', got {result.search_term}"
        assert any("SAP" in title for title in result.job_titles), "No job titles containing 'SAP' found in the search results"