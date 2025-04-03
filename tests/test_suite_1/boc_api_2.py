from core.base_test import BaseTest
from pydantic import BaseModel
import aiohttp
from typing import Dict, List, Optional, Union
from datetime import datetime


class SeriesDimension(BaseModel):
    key: str
    name: str


class SeriesDetail(BaseModel):
    label: str
    description: str
    dimension: SeriesDimension


class BankOfCanadaFXResponse(BaseModel):
    terms: Dict[str, str]
    seriesDetail: Dict[str, SeriesDetail]
    observations: List[Dict[str, Optional[Union[str, Dict[str, str]]]]]


class TestBankOfCanadaFXAPI(BaseTest):
    def get_task(self) -> str:
        return (
            "Fetch FX rates data from Bank of Canada API\n"
            "Validate response structure and check for CNY/CAD exchange rate data"
        )

    def get_output_model(self) -> BaseModel:
        return BankOfCanadaFXResponse

    def validate_results(self, result: BankOfCanadaFXResponse):
        # Basic validations
        assert isinstance(result.terms, dict), "Terms should be a dictionary"
        assert "url" in result.terms, "Terms should contain URL"
        assert len(result.observations) > 0, "No observations found"

        # Target currency validation
        target_currency = "FXCNYCAD"
        assert target_currency in result.seriesDetail, f"Currency pair {target_currency} not found"

        # Validate observations
        date_format = "%Y-%m-%d"
        valid_observations = 0

        for obs in result.observations:
            try:
                date = obs.get('d')
                if date:
                    datetime.strptime(date, date_format)

                rate_value = obs.get(target_currency)
                # Handle both string and {'v': string} formats
                rate = None
                if isinstance(rate_value, dict) and 'v' in rate_value:
                    rate = rate_value['v']
                elif isinstance(rate_value, str):
                    rate = rate_value

                if rate and float(rate) > 0:
                    valid_observations += 1
            except (ValueError, TypeError):
                continue

        assert valid_observations > 0, f"No valid {target_currency} observations found"

        print(f"\n✅ Validation passed for {target_currency}:")
        print(f"Series Detail: {result.seriesDetail.get(target_currency)}")
        print(f"Found {valid_observations} valid observations")

        # Print first valid observation
        first_valid = None
        for obs in result.observations:
            date = obs.get('d')
            rate_value = obs.get(target_currency)
            if date and rate_value:
                # Handle both string and {'v': string} formats
                rate = rate_value['v'] if isinstance(rate_value, dict) else rate_value
                first_valid = {'d': date, target_currency: rate}
                break

        if first_valid:
            print(f"First observation: {first_valid['d']} - {first_valid[target_currency]}")

    async def run(self):
        url = "https://www.bankofcanada.ca/valet/observations/group/FX_RATES_DAILY/json"
        params = {
            "start_date": "2023-01-23",
            "end_date": "2023-07-19",
            "order_dir": "asc"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                validated = self.get_output_model().model_validate(data)
                self.validate_results(validated)
                return validated