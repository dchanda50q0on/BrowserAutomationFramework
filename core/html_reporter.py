import json
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os
from typing import Optional  # Add this import


class HTMLReporter:
    def __init__(self):
        self.report_dir = "reports"
        self.template_dir = "report_templates"
        self.screenshot_dir = "screenshots"
        Path(self.report_dir).mkdir(exist_ok=True)
        Path(self.template_dir).mkdir(exist_ok=True)

        # Create default template if it doesn't exist
        self._create_default_template()

        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def _create_default_template(self):
        default_template = Path(self.template_dir) / "report_template.html"
        if not default_template.exists():
            template_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Automation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .test-card { border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 10px; }
        .passed { border-left: 5px solid #4CAF50; }
        .failed { border-left: 5px solid #F44336; }
        .test-title { font-weight: bold; margin-bottom: 10px; }
        .screenshot { max-width: 100%; margin-top: 10px; border: 1px solid #ddd; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto; }
        .timestamp { color: #666; font-size: 0.9em; }
        .summary-item { display: inline-block; margin-right: 20px; }
        .summary-value { font-weight: bold; font-size: 1.2em; }
    </style>
</head>
<body>
    <h1>Test Automation Report</h1>
    <div class="timestamp">Generated on: {{ report.timestamp }}</div>

    <div class="summary">
        <h2>Summary</h2>
        <div>
            <span class="summary-item">Total: <span class="summary-value">{{ report.summary.total }}</span></span>
            <span class="summary-item">Passed: <span class="summary-value" style="color: #4CAF50;">{{ report.summary.passed }}</span></span>
            <span class="summary-item">Failed: <span class="summary-value" style="color: #F44336;">{{ report.summary.failed }}</span></span>
            <span class="summary-item">Pass Rate: <span class="summary-value">{{ "%.2f"|format(report.summary.passed / report.summary.total * 100) }}%</span></span>
        </div>
    </div>

    <h2>Test Details</h2>
    {% for test in report.details %}
    <div class="test-card {{ test.status }}">
        <div class="test-title">{{ test.test_name }} - <span style="color: {% if test.status == 'passed' %}#4CAF50{% else %}#F44336{% endif %};">{{ test.status|upper }}</span></div>

        {% if test.status == 'failed' %}
            <div><strong>Error:</strong> {{ test.error }}</div>
            {% if test.screenshot %}
                <div><strong>Screenshot:</strong></div>
                <img src="{{ test.screenshot }}" class="screenshot" alt="Failure screenshot">
            {% endif %}
        {% else %}
            <pre>{{ test.result|tojson(indent=2) }}</pre>
        {% endif %}

        <div class="timestamp">Duration: {{ test.duration }} seconds</div>
    </div>
    {% endfor %}
</body>
</html>"""
            with open(default_template, 'w') as f:
                f.write(template_content)

    def generate_html_report(self, json_report: dict):
        # Add screenshot paths to failed tests
        for test in json_report['details']:
            if test['status'] == 'failed':
                test_name = test['test_name']
                # Find the most recent screenshot for this test
                screenshot = self._find_latest_screenshot(test_name)
                if screenshot:
                    # Convert to relative path for HTML
                    test['screenshot'] = os.path.relpath(screenshot, start=self.report_dir)

        template = self.env.get_template("report_template.html")
        report_html = template.render(report=json_report)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(self.report_dir) / f"report_{timestamp}.html"

        with open(report_file, 'w') as f:
            f.write(report_html)

        return str(report_file)

    def _find_latest_screenshot(self, test_name: str) -> Optional[str]:
        screenshot_files = list(Path(self.screenshot_dir).glob(f"failure_{test_name}_*.png"))
        if screenshot_files:
            latest = max(screenshot_files, key=lambda f: f.stat().st_ctime)
            return str(latest)
        return None