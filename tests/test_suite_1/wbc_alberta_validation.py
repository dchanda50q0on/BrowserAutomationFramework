from core.base_test import BaseTest
from pydantic import BaseModel
from typing import List


class WcbPremiumResult(BaseModel):
    url: str
    mandatory_fields: str
    spelling_accuracy: str
    date_format: str
    error_invalid_email: str
    error_invalid_phone: str
    error_invalid_date: str
    error_invalid_postal_code: str
    error_missing_mandatory_fields: str
    #success_message: str




class TestWcbPremium(BaseTest):
    def get_task(self) -> str:
        return (
            'Open browser and launch https://www.wcb.ab.ca/forms/ois_employer_sign_up.asp'
            'Act as a tester enter a range of 3 to 12 digits account number and validate if it accepts only 8 digits'
            'Act as a tester and validate date format'
            'Act as a tester and capture all mandatory fields'
            'Act as a tester and validate that user can not submit the form without filling all mandatory fields'
            'Act as a tester and validate all labels spelling and case sensitivity'
            'Act as a tester and validate that the form resets correctly when the reset button is clicked'
            'Act as a tester and validate that the form shows an error message for invalid email formats'
            'Act as a tester and validate that the form shows an error message for invalid phone number formats'
            'Act as a tester and validate that the form shows an error message for invalid date formats'
            'Act as a tester and validate that the form shows an error message for invalid postal code formats'
            'Act as a tester and validate that the form shows an error message for missing mandatory fields'
            'Don\'t click on submit button'
            'Close the Browser'
        )


    def get_output_model(self) -> BaseModel:
        return WcbPremiumResult

    def validate_results(self, result: WcbPremiumResult):
        assert 'wcb' in result.url
        #assert 'Form submitted successfully' in result.success_message
