from core.base_test import BaseTest
from pydantic import BaseModel


class WcbPremiumResult(BaseModel):
    premium: str




class TestWcbPremium(BaseTest):
    def get_task(self) -> str:
        return (
            'Open browser and launch https://rm.wcb.ab.ca/WCB.RateManual.WebServer/'
            'Click Agriculture'
            'Click Crop Production'
            'Click Forage/ Peat Moss Processing - 01602'
            'Capture 2025 Premium Rate'
            'Close the Browser'
        )

    def get_output_model(self) -> BaseModel:
        return WcbPremiumResult

    def validate_results(self, result: WcbPremiumResult):
        assert '$2.41' in result.premium
