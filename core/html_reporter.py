from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from core.config import Config
import os
import json
from typing import Optional


class HTMLReporter:
    def __init__(self):
        # Ensure template directory exists
        template_dir = Config.get_template_dir()
        template_dir.mkdir(exist_ok=True)

        # Create default template if it doesn't exist
        self._ensure_default_template(template_dir)

        self.env = Environment(loader=FileSystemLoader(template_dir))
        # Replace the lambda with a proper function that handles indentation
        self.env.filters['tojson'] = self._json_filter

    def _json_filter(self, data):
        """Custom JSON filter that handles indentation"""
        return json.dumps(data, indent=2)

    def _ensure_default_template(self, template_dir: Path):
        default_template = template_dir / "report_template.html"
        if not default_template.exists():
            with open(default_template, 'w') as f:
                f.write("""<!DOCTYPE html>
<html>
<!-- Default template content goes here -->
</html>""")

    def generate_html_report(self, json_report: dict) -> str:
        # Add screenshot paths to failed tests
        for test in json_report['details']:
            if test['status'] == 'failed':
                test_name = test['test_name']
                screenshot = self._find_latest_screenshot(test_name)
                if screenshot:
                    test['screenshot'] = os.path.relpath(screenshot, start=Config.get_report_dir())

        template = self.env.get_template("report_template.html")
        report_html = template.render(report=json_report)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Config.get_report_dir() / f"report_{timestamp}.html"

        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w') as f:
            f.write(report_html)

        return str(report_file)

    def _find_latest_screenshot(self, test_name: str) -> Optional[str]:
        screenshot_files = list(Config.get_screenshot_dir().glob(f"failure_{test_name}_*.png"))
        if screenshot_files:
            return str(max(screenshot_files, key=lambda f: f.stat().st_ctime))
        return None