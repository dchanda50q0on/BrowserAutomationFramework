from core.base_test import BaseTest
from pydantic import BaseModel


class ApiResponse(BaseModel):
     fact: str
     length:int


class TestApiCat(BaseTest):
    def get_task(self) -> str:
        return (
            'Launch browser and access https://catfact.ninja/fact\n'
            'Review the response and capture fact and length\n'
            'Close the browser'
        )

    def get_output_model(self) -> BaseModel:
        return ApiResponse

    def validate_results(self, result: ApiResponse):
        assert result.fact != "", "Fact should not be empty"
        assert result.length > 0, f"Length should be positive, got {result.length}"