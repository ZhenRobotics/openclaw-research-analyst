#!/usr/bin/env python3
"""
OpenClaw Research Analyst - China Market Integration Test Suite
测试所有5个中文数据源的可访问性、数据准确性和网络可靠性
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add parent directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
sys.path.insert(0, ROOT_DIR)

class ChinaMarketTester:
    """China market data sources comprehensive tester"""

    def __init__(self):
        self.results = {
            'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sources': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            },
            'performance': {},
            'issues': []
        }

    def log(self, message: str, level: str = "INFO"):
        """Log test message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")

    def run_script(self, script_path: str, args: List[str] = None, timeout: int = 60) -> Tuple[bool, Optional[Dict], float, str]:
        """
        Run a Python script and measure performance

        Returns:
            (success, data, duration, error_message)
        """
        start_time = time.time()
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=ROOT_DIR
            )
            duration = time.time() - start_time

            if result.returncode != 0:
                return False, None, duration, result.stderr

            try:
                data = json.loads(result.stdout)
                return True, data, duration, ""
            except json.JSONDecodeError as e:
                return False, None, duration, f"JSON parse error: {e}"

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return False, None, duration, f"Timeout after {timeout}s"
        except Exception as e:
            duration = time.time() - start_time
            return False, None, duration, str(e)

    def test_eastmoney(self) -> Dict:
        """Test 东方财富 (Eastmoney) data source"""
        self.log("Testing 东方财富 (Eastmoney)...")
        source_result = {
            'name': '东方财富',
            'status': 'UNKNOWN',
            'tests': {},
            'performance': {},
            'issues': []
        }

        script = os.path.join(SCRIPTS_DIR, 'cn_market_rankings.py')

        # Test 1: Accessibility
        success, data, duration, error = self.run_script(script, timeout=45)
        source_result['performance']['fetch_duration'] = f"{duration:.2f}s"

        if not success:
            source_result['status'] = 'FAIL'
            source_result['issues'].append(f"Failed to fetch data: {error}")
            source_result['tests']['accessibility'] = 'FAIL'
            return source_result

        source_result['tests']['accessibility'] = 'PASS'

        # Test 2: Data structure validation
        required_keys = ['a_share', 'hong_kong']
        has_structure = all(key in data for key in required_keys)
        source_result['tests']['data_structure'] = 'PASS' if has_structure else 'FAIL'

        if not has_structure:
            source_result['issues'].append(f"Missing required keys: {required_keys}")

        # Test 3: A-share data completeness
        a_share = data.get('a_share', {})
        top_gainers = a_share.get('top_gainers', [])
        top_amount = a_share.get('top_amount', [])

        if len(top_gainers) > 0 and len(top_amount) > 0:
            source_result['tests']['a_share_data'] = 'PASS'
            source_result['data_quality'] = {
                'top_gainers_count': len(top_gainers),
                'top_amount_count': len(top_amount)
            }
        else:
            source_result['tests']['a_share_data'] = 'FAIL'
            source_result['issues'].append("A-share data is empty")

        # Test 4: Data field validation
        if top_gainers:
            sample = top_gainers[0]
            required_fields = ['code', 'name', 'price', 'pct', 'amount']
            has_fields = all(field in sample for field in required_fields)
            source_result['tests']['data_fields'] = 'PASS' if has_fields else 'FAIL'

            if not has_fields:
                source_result['issues'].append(f"Missing fields in data: {required_fields}")

        # Test 5: Data accuracy validation
        if top_gainers:
            sample = top_gainers[0]
            price = sample.get('price')
            pct = sample.get('pct')

            accuracy_issues = []
            if price is not None and (not isinstance(price, (int, float)) or price <= 0):
                accuracy_issues.append(f"Invalid price: {price}")
            if pct is not None and not isinstance(pct, (int, float)):
                accuracy_issues.append(f"Invalid pct: {pct}")

            if accuracy_issues:
                source_result['tests']['data_accuracy'] = 'FAIL'
                source_result['issues'].extend(accuracy_issues)
            else:
                source_result['tests']['data_accuracy'] = 'PASS'

        # Overall status
        all_pass = all(v == 'PASS' for v in source_result['tests'].values())
        source_result['status'] = 'PASS' if all_pass else 'WARN' if source_result['tests']['accessibility'] == 'PASS' else 'FAIL'

        return source_result

    def test_sina(self) -> Dict:
        """Test 新浪财经 (Sina Finance) data source"""
        self.log("Testing 新浪财经 (Sina Finance)...")
        source_result = {
            'name': '新浪财经',
            'status': 'UNKNOWN',
            'tests': {},
            'performance': {},
            'issues': []
        }

        script = os.path.join(SCRIPTS_DIR, 'cn_stock_quotes.py')
        test_tickers = ['600519', '000001', 'HK.00700']  # 贵州茅台, 平安银行, 腾讯

        # Test 1: Accessibility
        success, data, duration, error = self.run_script(script, args=test_tickers, timeout=45)
        source_result['performance']['fetch_duration'] = f"{duration:.2f}s"

        if not success:
            source_result['status'] = 'FAIL'
            source_result['issues'].append(f"Failed to fetch data: {error}")
            source_result['tests']['accessibility'] = 'FAIL'
            return source_result

        source_result['tests']['accessibility'] = 'PASS'

        # Test 2: Data structure validation
        quotes = data.get('quotes', [])
        source_result['tests']['data_structure'] = 'PASS' if 'quotes' in data else 'FAIL'

        # Test 3: Quote completeness
        if len(quotes) == len(test_tickers):
            source_result['tests']['quote_completeness'] = 'PASS'
            source_result['data_quality'] = {'quotes_returned': len(quotes)}
        else:
            source_result['tests']['quote_completeness'] = 'WARN'
            source_result['issues'].append(f"Expected {len(test_tickers)} quotes, got {len(quotes)}")

        # Test 4: Ticker format conversion
        if quotes:
            sample = quotes[0]
            has_symbol = 'symbol' in sample
            source_result['tests']['ticker_format'] = 'PASS' if has_symbol else 'FAIL'

        # Test 5: Data accuracy
        if quotes:
            sample = quotes[0]
            required_fields = ['symbol', 'name', 'price']
            has_fields = all(field in sample for field in required_fields)
            source_result['tests']['data_fields'] = 'PASS' if has_fields else 'FAIL'

            price = sample.get('price')
            if price is not None and (not isinstance(price, (int, float)) or price <= 0):
                source_result['tests']['data_accuracy'] = 'FAIL'
                source_result['issues'].append(f"Invalid price data: {price}")
            else:
                source_result['tests']['data_accuracy'] = 'PASS'

        # Overall status
        critical_pass = source_result['tests'].get('accessibility') == 'PASS' and source_result['tests'].get('data_structure') == 'PASS'
        source_result['status'] = 'PASS' if critical_pass else 'FAIL'

        return source_result

    def test_cls(self) -> Dict:
        """Test 财联社 (CLS) data source"""
        self.log("Testing 财联社 (CLS Telegraph)...")
        source_result = {
            'name': '财联社',
            'status': 'UNKNOWN',
            'tests': {},
            'performance': {},
            'issues': []
        }

        script = os.path.join(SCRIPTS_DIR, 'cn_cls_telegraph.py')

        # Test 1: Accessibility
        success, data, duration, error = self.run_script(script, timeout=30)
        source_result['performance']['fetch_duration'] = f"{duration:.2f}s"

        if not success:
            source_result['status'] = 'WARN'  # CLS can be flaky
            source_result['issues'].append(f"Failed to fetch data (expected for anti-crawling): {error}")
            source_result['tests']['accessibility'] = 'FAIL'
            return source_result

        source_result['tests']['accessibility'] = 'PASS'

        # Test 2: Data structure
        required_keys = ['telegraph', 'depth', 'timestamp']
        has_structure = all(key in data for key in required_keys)
        source_result['tests']['data_structure'] = 'PASS' if has_structure else 'FAIL'

        # Test 3: Telegraph data
        telegraph = data.get('telegraph', [])
        if len(telegraph) > 0:
            source_result['tests']['telegraph_data'] = 'PASS'
            source_result['data_quality'] = {
                'telegraph_count': len(telegraph),
                'depth_count': len(data.get('depth', []))
            }
        else:
            source_result['tests']['telegraph_data'] = 'WARN'
            source_result['issues'].append("No telegraph data (may be anti-crawling)")

        # Test 4: Related codes extraction
        if telegraph:
            sample = telegraph[0]
            if 'related_codes' in sample:
                source_result['tests']['code_extraction'] = 'PASS'
            else:
                source_result['tests']['code_extraction'] = 'WARN'

        # Overall status
        source_result['status'] = 'PASS' if source_result['tests'].get('accessibility') == 'PASS' else 'WARN'

        return source_result

    def test_tencent(self) -> Dict:
        """Test 腾讯财经 (Tencent Finance) data source"""
        self.log("Testing 腾讯财经 (Tencent Finance)...")
        source_result = {
            'name': '腾讯财经',
            'status': 'UNKNOWN',
            'tests': {},
            'performance': {},
            'issues': []
        }

        script = os.path.join(SCRIPTS_DIR, 'cn_tencent_moneyflow.py')

        # Test 1: Accessibility
        success, data, duration, error = self.run_script(script, timeout=30)
        source_result['performance']['fetch_duration'] = f"{duration:.2f}s"

        if not success:
            source_result['status'] = 'WARN'
            source_result['issues'].append(f"Failed to fetch data: {error}")
            source_result['tests']['accessibility'] = 'FAIL'
            return source_result

        source_result['tests']['accessibility'] = 'PASS'

        # Test 2: Data structure
        required_keys = ['hot_stocks', 'concept_plates', 'money_flow']
        has_structure = all(key in data for key in required_keys)
        source_result['tests']['data_structure'] = 'PASS' if has_structure else 'FAIL'

        # Test 3: Money flow data
        money_flow = data.get('money_flow', {})
        inflow = money_flow.get('top_inflow', [])
        outflow = money_flow.get('top_outflow', [])

        if len(inflow) > 0 or len(outflow) > 0:
            source_result['tests']['money_flow_data'] = 'PASS'
            source_result['data_quality'] = {
                'inflow_count': len(inflow),
                'outflow_count': len(outflow),
                'hot_stocks_count': len(data.get('hot_stocks', []))
            }
        else:
            source_result['tests']['money_flow_data'] = 'WARN'
            source_result['issues'].append("No money flow data available")

        # Test 4: Net inflow calculation
        if inflow:
            sample = inflow[0]
            net_inflow = sample.get('net_inflow')
            if net_inflow is not None and net_inflow > 0:
                source_result['tests']['inflow_calculation'] = 'PASS'
            else:
                source_result['tests']['inflow_calculation'] = 'FAIL'
                source_result['issues'].append(f"Invalid net_inflow: {net_inflow}")

        # Overall status
        source_result['status'] = 'PASS' if source_result['tests'].get('accessibility') == 'PASS' else 'WARN'

        return source_result

    def test_10jqka(self) -> Dict:
        """Test 同花顺 (10jqka) data source"""
        self.log("Testing 同花顺 (10jqka)...")
        source_result = {
            'name': '同花顺',
            'status': 'UNKNOWN',
            'tests': {},
            'performance': {},
            'issues': []
        }

        script = os.path.join(SCRIPTS_DIR, 'cn_ths_diagnosis.py')

        # Test 1: Accessibility
        success, data, duration, error = self.run_script(script, timeout=30)
        source_result['performance']['fetch_duration'] = f"{duration:.2f}s"

        if not success:
            source_result['status'] = 'WARN'
            source_result['issues'].append(f"Failed to fetch data: {error}")
            source_result['tests']['accessibility'] = 'FAIL'
            return source_result

        source_result['tests']['accessibility'] = 'PASS'

        # Test 2: Data structure
        required_keys = ['hot_stocks', 'industry_ranking']
        has_structure = all(key in data for key in required_keys)
        source_result['tests']['data_structure'] = 'PASS' if has_structure else 'FAIL'

        # Test 3: Industry ranking data
        industry = data.get('industry_ranking', [])
        if len(industry) > 0:
            source_result['tests']['industry_data'] = 'PASS'
            source_result['data_quality'] = {
                'industry_count': len(industry),
                'hot_stocks_count': len(data.get('hot_stocks', []))
            }
        else:
            source_result['tests']['industry_data'] = 'WARN'
            source_result['issues'].append("No industry ranking data")

        # Overall status
        source_result['status'] = 'PASS' if source_result['tests'].get('accessibility') == 'PASS' else 'WARN'

        return source_result

    def test_integrated_report(self) -> Dict:
        """Test integrated market report generation"""
        self.log("Testing integrated market report generation...")
        report_result = {
            'name': 'Integrated Report',
            'status': 'UNKNOWN',
            'tests': {},
            'performance': {},
            'issues': []
        }

        script = os.path.join(SCRIPTS_DIR, 'cn_market_report.py')

        # Test 1: Report generation
        success, data, duration, error = self.run_script(script, timeout=180)
        report_result['performance']['generation_duration'] = f"{duration:.2f}s"

        if not success:
            report_result['status'] = 'FAIL'
            report_result['issues'].append(f"Report generation failed: {error}")
            report_result['tests']['generation'] = 'FAIL'
            return report_result

        report_result['tests']['generation'] = 'PASS'

        # Test 2: Output files validation
        digest_md = data.get('digest_md')
        if digest_md and os.path.exists(digest_md):
            report_result['tests']['markdown_output'] = 'PASS'

            # Check file size
            file_size = os.path.getsize(digest_md)
            report_result['data_quality'] = {'digest_file_size': f"{file_size} bytes"}

            if file_size < 100:
                report_result['issues'].append(f"Digest file too small: {file_size} bytes")
        else:
            report_result['tests']['markdown_output'] = 'FAIL'
            report_result['issues'].append("Markdown digest file not generated")

        # Test 3: JSON outputs
        json_files = [
            data.get('hot_json'),
            data.get('watchlist_json'),
            data.get('cls_json'),
            data.get('tencent_json'),
            data.get('jqka_json')
        ]

        existing_files = [f for f in json_files if f and os.path.exists(f)]
        report_result['tests']['json_outputs'] = 'PASS' if len(existing_files) >= 3 else 'WARN'
        report_result['data_quality']['json_files_generated'] = len(existing_files)

        # Test 4: Data sources attribution
        data_sources = data.get('data_sources', {})
        if len(data_sources) == 5:
            report_result['tests']['data_sources'] = 'PASS'
        else:
            report_result['tests']['data_sources'] = 'WARN'
            report_result['issues'].append(f"Expected 5 data sources, got {len(data_sources)}")

        # Overall status
        critical_pass = report_result['tests'].get('generation') == 'PASS' and report_result['tests'].get('markdown_output') == 'PASS'
        report_result['status'] = 'PASS' if critical_pass else 'FAIL'

        return report_result

    def run_all_tests(self):
        """Run all China market integration tests"""
        self.log("=" * 60)
        self.log("OpenClaw Research Analyst - China Market Test Suite")
        self.log("=" * 60)

        # Test individual sources
        sources = [
            ('eastmoney', self.test_eastmoney),
            ('sina', self.test_sina),
            ('cls', self.test_cls),
            ('tencent', self.test_tencent),
            ('10jqka', self.test_10jqka)
        ]

        for source_name, test_func in sources:
            try:
                result = test_func()
                self.results['sources'][source_name] = result

                # Update summary
                for test_result in result['tests'].values():
                    self.results['summary']['total_tests'] += 1
                    if test_result == 'PASS':
                        self.results['summary']['passed'] += 1
                    elif test_result == 'FAIL':
                        self.results['summary']['failed'] += 1
                    elif test_result == 'WARN':
                        self.results['summary']['warnings'] += 1

                self.log(f"{result['name']}: {result['status']}")

            except Exception as e:
                self.log(f"Error testing {source_name}: {e}", level="ERROR")
                self.results['issues'].append(f"{source_name} test crashed: {e}")

        # Test integrated report
        try:
            report_result = self.test_integrated_report()
            self.results['integrated_report'] = report_result

            for test_result in report_result['tests'].values():
                self.results['summary']['total_tests'] += 1
                if test_result == 'PASS':
                    self.results['summary']['passed'] += 1
                elif test_result == 'FAIL':
                    self.results['summary']['failed'] += 1
                elif test_result == 'WARN':
                    self.results['summary']['warnings'] += 1

            self.log(f"Integrated Report: {report_result['status']}")

        except Exception as e:
            self.log(f"Error testing integrated report: {e}", level="ERROR")
            self.results['issues'].append(f"Integrated report test crashed: {e}")

        # Calculate pass rate
        total = self.results['summary']['total_tests']
        passed = self.results['summary']['passed']
        self.results['summary']['pass_rate'] = f"{(passed/total*100):.1f}%" if total > 0 else "0%"

        self.log("=" * 60)
        self.log(f"Tests completed: {passed}/{total} passed ({self.results['summary']['pass_rate']})")
        self.log("=" * 60)

        return self.results

    def save_report(self, output_path: str):
        """Save test report to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        self.log(f"Test report saved to: {output_path}")


def main():
    """Main test execution"""
    tester = ChinaMarketTester()
    results = tester.run_all_tests()

    # Save results
    reports_dir = os.path.join(ROOT_DIR, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(reports_dir, f'cn_market_test_report_{timestamp}.json')
    tester.save_report(report_path)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Warnings: {results['summary']['warnings']}")
    print(f"Pass Rate: {results['summary']['pass_rate']}")
    print("\nSOURCE STATUS:")

    for source_name, source_data in results['sources'].items():
        status_icon = "✓" if source_data['status'] == 'PASS' else "⚠" if source_data['status'] == 'WARN' else "✗"
        print(f"  {status_icon} {source_data['name']}: {source_data['status']}")

    if results.get('integrated_report'):
        status_icon = "✓" if results['integrated_report']['status'] == 'PASS' else "✗"
        print(f"  {status_icon} Integrated Report: {results['integrated_report']['status']}")

    print("\n" + "=" * 60)

    # Exit code based on critical failures
    critical_failures = results['summary']['failed']
    sys.exit(0 if critical_failures == 0 else 1)


if __name__ == '__main__':
    main()
