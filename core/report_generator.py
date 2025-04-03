import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from core.config import Config
from pydantic import BaseModel


class TestReport:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "details": []
        }
        self.test_timers = {}

    def start_timer(self, test_name: str):
        """Start a timer for a test."""
        self.test_timers[test_name] = time.time()

    def stop_timer(self, test_name: str) -> float:
        """Stop the timer and return the test duration."""
        if test_name in self.test_timers:
            duration = time.time() - self.test_timers[test_name]
            del self.test_timers[test_name]
            return duration
        return 0.0

    def add_success(self, test_name: str, result: Any):
        """Record a successful test result."""
        duration = self.stop_timer(test_name)
        self.results["summary"]["total"] += 1
        self.results["summary"]["passed"] += 1

        # Convert Pydantic model to dictionary if applicable
        result_data = result.dict() if isinstance(result, BaseModel) else result

        self.results["details"].append({
            "test_name": test_name,
            "status": "passed",
            "result": result_data,
            "duration": round(duration, 2)
        })

    def add_failure(self, test_name: str, error: str):
        """Record a failed test result."""
        duration = self.stop_timer(test_name)
        self.results["summary"]["total"] += 1
        self.results["summary"]["failed"] += 1

        self.results["details"].append({
            "test_name": test_name,
            "status": "failed",
            "error": error,
            "duration": round(duration, 2)
        })

    def generate_report(self, format: str = "all") -> dict:
        """Generate reports in JSON and HTML formats with timestamped filenames."""
        if self.results["summary"]["total"] == 0:
            print("⚠️ No test results to report")
            return self.results

        # Calculate pass rate
        total = self.results["summary"]["total"]
        passed = self.results["summary"]["passed"]
        self.results["summary"]["pass_rate"] = round((passed / total * 100), 2) if total > 0 else 0

        # Generate timestamp for filenames (format: YYYYMMDD_HHMMSS)
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Config.get_report_dir()
        report_dir.mkdir(exist_ok=True)  # Ensure directory exists

        # Generate JSON report
        if format in ("json", "all"):
            json_path = report_dir / f"test_report_{file_timestamp}.json"
            try:
                with open(json_path, "w") as f:
                    json.dump(self.results, f, indent=2, default=self._json_serializer)
                print(f"📄 JSON report generated: {json_path}")
            except Exception as e:
                print(f"❌ Failed to generate JSON report: {str(e)}")

        # Generate HTML report
        if format in ("html", "all"):
            html_path = report_dir / f"test_report_{file_timestamp}.html"
            try:
                html_content = self._generate_html_content()
                with open(html_path, "w") as f:
                    f.write(html_content)
                print(f"📊 HTML report generated: {html_path}")
            except Exception as e:
                print(f"❌ Failed to generate HTML report: {str(e)}")

        return self.results

    def _generate_html_content(self) -> str:
        """Generate HTML content for the report."""
        timestamp = datetime.fromisoformat(self.results["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

        html_content = f"""
        <html>
        <head>
            <title>Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h2 {{ color: #333; }}
                .report-header {{ margin-bottom: 20px; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
                details {{ margin-bottom: 10px; padding: 5px; border: 1px solid #ccc; border-radius: 5px; background: #f9f9f9; }}
                summary {{ cursor: pointer; font-size: 1.1em; font-weight: bold; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                pre {{ background: #eef; padding: 10px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }}
            </style>
        </head>
        <body>
            <div class="report-header">
                <h2>Test Execution Report</h2>
                <p class="timestamp">Report generated at: {timestamp}</p>
                <p><b>Total Tests:</b> {self.results["summary"]["total"]} | 
                   <b>Passed:</b> {self.results["summary"]["passed"]} | 
                   <b>Failed:</b> {self.results["summary"]["failed"]} | 
                   <b>Pass Rate:</b> {self.results["summary"].get("pass_rate", 0)}%</p>
            </div>
        """

        for test in self.results["details"]:
            status = test["status"]
            color = "green" if status == "passed" else "red"
            duration = test["duration"]
            result_data = json.dumps(test.get("result", test.get("error", "")), indent=2)

            html_content += f"""
            <details>
                <summary>Test: {test["test_name"]} - <span style="color:{color};">{status}</span></summary>
                <pre>Duration: {duration} seconds</pre>
                <pre>{result_data}</pre>
            </details>
            """

        html_content += "</body></html>"
        return html_content

    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime and Pydantic models."""
        if isinstance(obj, BaseModel):
            return obj.dict()
        if hasattr(obj, "isoformat"):  # Handle datetime objects
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")