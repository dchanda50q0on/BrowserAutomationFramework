from core.base_test import BaseTest
from pydantic import BaseModel
import aiohttp
from typing import Dict


class GroupItem(BaseModel):
    label: str
    description: str


class BankOfCanadaResponse(BaseModel):
    terms: dict  # {"url": "..."}
    groups: Dict[str, GroupItem]  # Dynamic group IDs


class TestBankOfCanadaAPI(BaseTest):
    def get_task(self) -> str:
        return (
            "Fetch JSON from https://www.bankofcanada.ca/valet/lists/groups/json\n"
            "Validate the response structure and check for specific financial data groups."
        )

    def get_output_model(self) -> BaseModel:
        return BankOfCanadaResponse

    def validate_results(self, result: BankOfCanadaResponse):
        # Basic validations
        assert isinstance(result.terms, dict), "Terms should be a dictionary"
        assert "url" in result.terms, "Terms should contain URL"
        assert len(result.groups) > 0, "No groups found in response"

        # Specific validation for FSR_2020_C14 field
        target_field = "FSR_2020_C14"
        assert target_field in result.groups, f"Expected field '{target_field}' not found"

        fsr_item = result.groups[target_field]
        assert "mortgage arrears" in fsr_item.label.lower(), \
            f"Expected 'mortgage arrears' in label, got: {fsr_item.label}"
        assert "policy" in fsr_item.description.lower(), \
            f"Expected 'policy' in description, got: {fsr_item.description}"

        print(f"\n✅ Validation passed for {target_field}:")
        print(f"Label: {fsr_item.label}")
        print(f"Description: {fsr_item.description}")

    async def run(self):
        url = "https://www.bankofcanada.ca/valet/lists/groups/json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                validated = self.get_output_model().model_validate(data)
                self.validate_results(validated)
                return validated