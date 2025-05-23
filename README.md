Framework for Automated Web & API Testing
===================================

Overview:
---------
This framework is designed for automated web testing using Agentic AI. It supports defining test cases in JSON format and executing them with validation against expected results. The framework leverages Pydantic for data validation and includes a base test class for reusable functionality.

Features:
---------
1. JSON-based test case definitions.
2. Pydantic models for structured output validation.
3. Easy-to-extend base test class.
4. Supports asynchronous test execution.

Project Structure:
------------------
- `tests/json_tests/`: Contains JSON files defining test cases.
- `tests/`: Contains Python test scripts for executing the test cases.
- `core/base_test.py`: Base class for reusable test functionality.

Requirements:
-------------
- Python 3.10 or higher
- pip (Python package manager)

Installation:
-------------
1. Clone the repository:
git clone <repository_url> cd <repository_directory>

2. Install dependencies:
pip install -r requirements.txt

Usage:
------
Define a test case in JSON format under `tests/json_tests/`.
   Example:
   ```json
   {
     "test_name": "SampleTest",
     "task": "Open a browser and perform actions",
     "output_model": {
       "key": "value_type"
     },
     "validation": {
       "key": "expected_value"
     }
   }

3. Create a corresponding Python test script in tests/ using the BaseTest class.
4. Run the test:
python <test_script>.py
Example:
To run the AccentureJobSearch test:
python tests/AccentureJobSearch.py


Contributing:
- Fork the repository.
- Create a new branch for your feature or bug fix.
- Submit a pull request with a detailed description.
License:
This project is licensed under the MIT License.
