# **Test Generation Assistant**

Generate Python test cases for browser automation using this framework:

### **Rules:**
1. Extend `BaseTest` from `core.base_test`.
2. Use Pydantic models for results.
3. Follow the exact format below.
4. Include assertions for validation steps.

### **Example Test:**
```python
from core.base_test import BaseTest
from pydantic import BaseModel

class TestSearchResult(BaseModel):
    page_title: str
    page_url: str

class TestGoogleSearch(BaseTest):
    def get_task(self) -> str:
        return """1. Open google.com
2. Search for {search_term}
3. Click first result"""
    
    def get_output_model(self) -> BaseModel:
        return TestSearchResult
    
    def validate_results(self, result: TestSearchResult):
        assert "Python" in result.page_title
        assert "http" in result.page_url
```

### **CSV Input:**
```
{input_csv}
```