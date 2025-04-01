from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import time
from .html_reporter import HTMLReporter


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
        self.results['details'].append({
            'test_name': test_name,
            'status': 'passed',
            'result': result.dict() if hasattr(result, 'dict') else str(result),
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

    def generate_report(self, format: str = 'all'):
        # Ensure we have at least one test
        if self.results['summary']['total'] == 0:
            self.results['summary'] = {'total': 0, 'passed': 0, 'failed': 0}
            print("⚠️ No test results to report")
            return self.results

        # Safe division for pass rate
        total = self.results['summary']['total']
        passed = self.results['summary']['passed']
        self.results['summary']['pass_rate'] = (passed / total * 100) if total > 0 else 0

        if format in ('json', 'all'):
            with open('test_report.json', 'w') as f:
                json.dump(self.results, f, indent=2)

        if format in ('html', 'all'):
            try:
                html_report_path = self.html_reporter.generate_html_report(self.results)
                print(f"📊 HTML report generated: {html_report_path}")
            except Exception as e:
                print(f"❌ Failed to generate HTML report: {str(e)}")



        return self.results