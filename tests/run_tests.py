#!/usr/bin/env python3
"""
Script to run API tests and generate a test report.
"""
import os
import sys
import unittest
import time
import json
from datetime import datetime

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_api_endpoints import APITestCase

def run_tests_with_report():
    """Run all API tests and generate a report."""
    # Create a test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(APITestCase)
    
    # Create a test result
    test_result = unittest.TestResult()
    
    # Start time
    start_time = time.time()
    
    # Run the tests
    test_suite.run(test_result)
    
    # End time
    end_time = time.time()
    
    # Calculate duration
    duration = end_time - start_time
    
    # Create report data
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": test_result.testsRun,
        "passed": test_result.testsRun - len(test_result.failures) - len(test_result.errors),
        "failed": len(test_result.failures),
        "errors": len(test_result.errors),
        "duration_seconds": round(duration, 2),
        "failures": [],
        "errors": []
    }
    
    # Add failure details
    for test, traceback in test_result.failures:
        report["failures"].append({
            "test": test.id(),
            "traceback": traceback
        })
    
    # Add error details
    for test, traceback in test_result.errors:
        report["errors"].append({
            "test": test.id(),
            "traceback": traceback
        })
    
    # Calculate success rate
    report["success_rate"] = round((report["passed"] / report["total_tests"]) * 100, 2)
    
    # Generate report file name
    report_file = os.path.join(
        os.path.dirname(__file__),
        f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    # Save the report
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n=== API Test Report ===")
    print(f"Total tests: {report['total_tests']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Errors: {report['errors']}")
    print(f"Success rate: {report['success_rate']}%")
    print(f"Duration: {report['duration_seconds']} seconds")
    print(f"Report saved to: {report_file}")
    
    # Return success/failure
    return len(test_result.failures) == 0 and len(test_result.errors) == 0

def generate_html_report(json_report_path):
    """Generate an HTML report from the JSON report."""
    with open(json_report_path, 'r') as f:
        report = json.load(f)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .summary {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px; }}
        .summary-item {{ flex: 1; min-width: 200px; background-color: #fff; border-radius: 5px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .summary-item.success {{ background-color: #d4edda; }}
        .summary-item.warning {{ background-color: #fff3cd; }}
        .summary-item.danger {{ background-color: #f8d7da; }}
        .summary-item h3 {{ margin-top: 0; }}
        .details {{ background-color: #fff; border-radius: 5px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .details h2 {{ margin-top: 0; }}
        pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        .failure-item, .error-item {{ margin-bottom: 20px; padding: 15px; border-radius: 5px; }}
        .failure-item {{ background-color: #fff3cd; }}
        .error-item {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>API Test Report</h1>
            <p>Generated on: {report['timestamp']}</p>
        </div>
        
        <div class="summary">
            <div class="summary-item {'success' if report['success_rate'] > 90 else 'warning' if report['success_rate'] > 70 else 'danger'}">
                <h3>Success Rate</h3>
                <p style="font-size: 24px; font-weight: bold;">{report['success_rate']}%</p>
            </div>
            <div class="summary-item">
                <h3>Total Tests</h3>
                <p style="font-size: 24px; font-weight: bold;">{report['total_tests']}</p>
            </div>
            <div class="summary-item success">
                <h3>Passed</h3>
                <p style="font-size: 24px; font-weight: bold;">{report['passed']}</p>
            </div>
            <div class="summary-item {'success' if report['failed'] == 0 else 'danger'}">
                <h3>Failed</h3>
                <p style="font-size: 24px; font-weight: bold;">{report['failed']}</p>
            </div>
            <div class="summary-item {'success' if report['errors'] == 0 else 'danger'}">
                <h3>Errors</h3>
                <p style="font-size: 24px; font-weight: bold;">{report['errors']}</p>
            </div>
            <div class="summary-item">
                <h3>Duration</h3>
                <p style="font-size: 24px; font-weight: bold;">{report['duration_seconds']} sec</p>
            </div>
        </div>
        
        <div class="details">
            <h2>Test Details</h2>
    """
    
    if report['failures']:
        html_content += """
            <h3>Failures</h3>
        """
        for failure in report['failures']:
            html_content += f"""
            <div class="failure-item">
                <h4>{failure['test']}</h4>
                <pre>{failure['traceback']}</pre>
            </div>
            """
    
    if report['errors']:
        html_content += """
            <h3>Errors</h3>
        """
        for error in report['errors']:
            html_content += f"""
            <div class="error-item">
                <h4>{error['test']}</h4>
                <pre>{error['traceback']}</pre>
            </div>
            """
    
    html_content += """
        </div>
    </div>
</body>
</html>
    """
    
    # Generate HTML report file name
    html_report_file = json_report_path.replace('.json', '.html')
    
    # Save the HTML report
    with open(html_report_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML report saved to: {html_report_file}")

if __name__ == '__main__':
    # Run tests and generate JSON report
    success = run_tests_with_report()
    
    # Find the most recent JSON report
    reports_dir = os.path.dirname(__file__)
    json_reports = [f for f in os.listdir(reports_dir) if f.startswith('test_report_') and f.endswith('.json')]
    if json_reports:
        latest_report = max(json_reports)
        json_report_path = os.path.join(reports_dir, latest_report)
        
        # Generate HTML report
        generate_html_report(json_report_path)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1) 