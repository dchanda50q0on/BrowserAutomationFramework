from core.base_test import BaseTest
from pydantic import BaseModel


class LoginResult(BaseModel):
    success_message: str
    page_title: str


class TestLogin(BaseTest):
    def __init__(self):
        super().__init__()
        # Selectors can be updated if different
        self.login_selectors.update({
            'username': '#username',
            'password': '#password',
            'submit': '#submit'
        })

    def get_task(self) -> str:
        return (
            'Navigate to https://practicetestautomation.com/practice-test-login/\n'
            'The system will automatically handle login securely\n'
            'Verify the presence of a success message\n'
            'Extract the success message and page title\n'
            'Close the browser'
        )

    def get_output_model(self) -> BaseModel:
        return LoginResult

    def validate_results(self, result: LoginResult):
        assert 'successfully logged in' in result.success_message.lower()
        assert 'practice test' in result.page_title.lower()