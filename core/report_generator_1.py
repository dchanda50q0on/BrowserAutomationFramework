import json
import time
from datetime import datetime
from typing import Any, Dict
from core.html_reporter import HTMLReporter
from core.config import Config
from pydantic import BaseModel


class TestReport:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'summary': {'total': 0, 'passed': 0, 'failed': 0},
            'details': []
        }
        self.html_reporter = HTMLReporter()
        self.test_timers = {}

    def start_timer(self, test_name: str):
        self.test_timers[test_name] = time.time()

    def stop_timer(self, test_name: str) -> float:
        if test_name in self.test_timers:
            duration = time.time() - self.test_timers[test_name]
            del self.test_timers[test_name]
            return duration
        return 0.0

    def add_success(self, test_name: str, result: Any):
        duration = self.stop_timer(test_name)
        self.results['summary']['total'] += 1
        self.results['summary']['passed'] += 1

        # Convert Pydantic model to dict if needed
        result_data = result.dict() if isinstance(result, BaseModel) else result

        self.results['details'].append({
            'test_name': test_name,
            'status': 'passed',
            'result': result_data,
            'duration': round(duration, 2)
        })

    def add_failure(self, test_name: str, error: str):
        duration = self.stop_timer(test_name)
        self.results['summary']['total'] += 1
        self.results['summary']['failed'] += 1
        self.results['details'].append({
            'test_name': test_name,
            'status': 'failed',
            'error': error,
            'duration': round(duration, 2)
        })

    def generate_report(self, format: str = 'all') -> dict:
        if self.results['summary']['total'] == 0:
            print("⚠️ No test results to report")
            return self.results

        # Calculate pass rate
        total = self.results['summary']['total']
        passed = self.results['summary']['passed']
        self.results['summary']['pass_rate'] = round((passed / total * 100), 2) if total > 0 else 0

        # Generate reports
        if format in ('json', 'all'):
            report_path = Config.get_report_dir() / 'test_report.json'
            try:
                with open(report_path, 'w') as f:
                    json.dump(self.results, f, indent=2, default=self._json_serializer)
            except Exception as e:
                print(f"❌ Failed to generate JSON report: {str(e)}")

        if format in ('html', 'all'):
            try:
                html_path = self.html_reporter.generate_html_report(self.results)
                print(f"📊 HTML report generated: {html_path}")
            except Exception as e:
                print(f"❌ Failed to generate HTML report: {str(e)}")

        return self.results

    def _json_serializer(self, obj):
        """Custom JSON serializer for objects"""
        if isinstance(obj, BaseModel):
            return obj.dict()
        if hasattr(obj, 'isoformat'):  # Handle datetime objects
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")