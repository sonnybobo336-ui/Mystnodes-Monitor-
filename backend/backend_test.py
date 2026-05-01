"""NodeForge Backend API Test Suite"""
import requests
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class NodeForgeAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests: List[Dict[str, Any]] = []
        self.passed_tests: List[str] = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_test(
        self, 
        name: str, 
        method: str, 
        endpoint: str, 
        expected_status: int = 200,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        timeout: int = 30,
        validate_response: Optional[callable] = None
    ) -> tuple[bool, Any]:
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        self.tests_run += 1
        
        self.log(f"Testing {name}...", "TEST")
        
        try:
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check status code
            status_ok = response.status_code == expected_status
            
            # Try to parse JSON
            try:
                response_data = response.json()
            except Exception:
                response_data = {"_raw": response.text[:500]}
            
            # Validate response if validator provided
            validation_ok = True
            validation_msg = ""
            if validate_response and status_ok:
                try:
                    validation_ok, validation_msg = validate_response(response_data)
                except Exception as e:
                    validation_ok = False
                    validation_msg = f"Validation error: {str(e)}"
            
            success = status_ok and validation_ok
            
            if success:
                self.tests_passed += 1
                self.passed_tests.append(name)
                self.log(f"✅ PASSED - {name} (Status: {response.status_code})", "PASS")
                if validation_msg:
                    self.log(f"   {validation_msg}", "INFO")
            else:
                error_info = {
                    "test": name,
                    "endpoint": endpoint,
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "validation_failed": not validation_ok,
                    "validation_msg": validation_msg,
                    "response_preview": str(response_data)[:300]
                }
                self.failed_tests.append(error_info)
                self.log(f"❌ FAILED - {name}", "FAIL")
                self.log(f"   Expected status: {expected_status}, Got: {response.status_code}", "FAIL")
                if not validation_ok:
                    self.log(f"   Validation failed: {validation_msg}", "FAIL")
                self.log(f"   Response preview: {str(response_data)[:200]}", "FAIL")
            
            return success, response_data
            
        except requests.exceptions.Timeout:
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": "Request timeout",
                "timeout": timeout
            })
            self.log(f"❌ FAILED - {name} (Timeout after {timeout}s)", "FAIL")
            return False, {}
        except Exception as e:
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": str(e)
            })
            self.log(f"❌ FAILED - {name} (Error: {str(e)})", "FAIL")
            return False, {}
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ({(self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0:.1f}%)")
        print(f"Failed: {len(self.failed_tests)} ({(len(self.failed_tests)/self.tests_run*100) if self.tests_run > 0 else 0:.1f}%)")
        
        if self.passed_tests:
            print("\n✅ PASSED TESTS:")
            for test in self.passed_tests:
                print(f"   - {test}")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for fail in self.failed_tests:
                print(f"   - {fail['test']}: {fail.get('error', fail.get('validation_msg', 'Status mismatch'))}")
        
        print("="*80 + "\n")


def main():
    # Use the public endpoint from frontend/.env
    BASE_URL = "https://debug-mode-12.preview.emergentagent.com/api"
    
    tester = NodeForgeAPITester(BASE_URL)
    
    print("\n" + "="*80)
    print("NodeForge Backend API Test Suite")
    print("="*80)
    print(f"Testing endpoint: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Test 1: Root health check
    tester.run_test(
        "Root Health Check",
        "GET",
        "/",
        expected_status=200,
        validate_response=lambda r: (
            r.get("name") == "NodeForge",
            f"name={r.get('name')}, status={r.get('status')}"
        )
    )
    
    # Test 2: Prices endpoint (CoinGecko)
    success, prices_data = tester.run_test(
        "Get Crypto Prices",
        "GET",
        "/prices",
        expected_status=200,
        validate_response=lambda r: (
            isinstance(r.get("prices"), list) and len(r.get("prices", [])) > 0,
            f"Found {len(r.get('prices', []))} prices"
        )
    )
    
    # Validate price structure
    if success and prices_data.get("prices"):
        expected_symbols = ["BTC", "ETH", "SOL", "MYST"]
        found_symbols = [p.get("symbol") for p in prices_data["prices"]]
        if all(sym in found_symbols for sym in expected_symbols):
            tester.log(f"   All expected symbols found: {expected_symbols}", "INFO")
        else:
            tester.log(f"   Missing symbols. Expected: {expected_symbols}, Found: {found_symbols}", "WARN")
    
    # Test 3: Wallets endpoint
    tester.run_test(
        "Get Wallet Balances",
        "GET",
        "/wallets",
        expected_status=200,
        validate_response=lambda r: (
            "addresses" in r and "balances" in r,
            f"addresses={len(r.get('addresses', []))}, balances={len(r.get('balances', []))}"
        )
    )
    
    # Test 4: Snapshot endpoint
    success, snapshot_data = tester.run_test(
        "Get Aggregated Snapshot",
        "GET",
        "/snapshot",
        expected_status=200,
        validate_response=lambda r: (
            "prices" in r and "derived" in r and "config" in r,
            f"Keys: {list(r.keys())[:5]}"
        )
    )
    
    # Test 5: Nodes endpoint (expected to return connected:false)
    success, nodes_data = tester.run_test(
        "Get Nodes Status",
        "GET",
        "/nodes",
        expected_status=200,
        validate_response=lambda r: (
            "connected" in r,
            f"connected={r.get('connected')}, hint={r.get('hint', 'N/A')[:50]}"
        )
    )
    
    # Verify Mystnodes is not connected (as expected)
    if success and nodes_data.get("connected") == False:
        tester.log("   ✓ Mystnodes correctly returns connected:false (no credentials)", "INFO")
    
    # Test 6: Earnings summary
    tester.run_test(
        "Get Earnings Summary",
        "GET",
        "/earnings/summary",
        expected_status=200,
        validate_response=lambda r: (
            "derived" in r,
            f"derived keys: {list(r.get('derived', {}).keys())[:5]}"
        )
    )
    
    # Test 7: Earnings timeseries
    tester.run_test(
        "Get Earnings Timeseries (30 days)",
        "GET",
        "/earnings/timeseries",
        params={"days": 30},
        expected_status=200,
        validate_response=lambda r: (
            "points" in r and isinstance(r.get("points"), list),
            f"points={len(r.get('points', []))}, myst_price_usd={r.get('myst_price_usd')}"
        )
    )
    
    # Test 8: AI insights generation (may take 5-15 seconds)
    tester.log("AI insights test may take 5-30 seconds...", "INFO")
    success, ai_data = tester.run_test(
        "Generate AI Insights",
        "POST",
        "/ai/insights",
        expected_status=200,
        timeout=45,  # Allow more time for LLM
        validate_response=lambda r: (
            "insights" in r,
            f"insights keys: {list(r.get('insights', {}).keys())}"
        )
    )
    
    # Validate AI insights structure
    if success and ai_data.get("insights"):
        insights = ai_data["insights"]
        expected_keys = ["summary", "recommendations", "underperformers"]
        found_keys = [k for k in expected_keys if k in insights]
        if len(found_keys) == len(expected_keys):
            tester.log(f"   ✓ AI insights has all expected keys: {expected_keys}", "INFO")
        else:
            tester.log(f"   ⚠ AI insights missing keys. Expected: {expected_keys}, Found: {found_keys}", "WARN")
    
    # Test 9: Get latest AI insights
    tester.run_test(
        "Get Latest AI Insights",
        "GET",
        "/ai/insights/latest",
        expected_status=200
    )
    
    # Test 10: Withdrawal state
    tester.run_test(
        "Get Withdrawal State",
        "GET",
        "/withdrawal/state",
        expected_status=200,
        validate_response=lambda r: (
            "interval_days" in r and "threshold_myst" in r,
            f"interval_days={r.get('interval_days')}, threshold_myst={r.get('threshold_myst')}"
        )
    )
    
    # Test 11: Trigger withdrawal check
    tester.run_test(
        "Trigger Withdrawal Check",
        "POST",
        "/withdrawal/run",
        expected_status=200,
        validate_response=lambda r: (
            r.get("ok") == True,
            f"ok={r.get('ok')}, result keys: {list(r.get('result', {}).keys())[:5]}"
        )
    )
    
    # Test 12: Get withdrawal log
    tester.run_test(
        "Get Withdrawal Log",
        "GET",
        "/withdrawal/log",
        params={"limit": 50},
        expected_status=200,
        validate_response=lambda r: (
            "items" in r and isinstance(r.get("items"), list),
            f"items count: {len(r.get('items', []))}"
        )
    )
    
    # Test 13: Get settings
    success, settings_data = tester.run_test(
        "Get Settings",
        "GET",
        "/settings",
        expected_status=200,
        validate_response=lambda r: (
            "mystnodes_connected" in r and "tailscale_connected" in r,
            f"mystnodes_connected={r.get('mystnodes_connected')}, tailscale_connected={r.get('tailscale_connected')}"
        )
    )
    
    # Test 14: Save settings (with minimal changes)
    tester.run_test(
        "Save Settings",
        "POST",
        "/settings/save",
        data={"auto_withdrawal_days": 5},
        expected_status=200
    )
    
    # Test 15: Test Mystnodes with fake credentials (should fail)
    success, myst_test = tester.run_test(
        "Test Mystnodes (fake credentials)",
        "POST",
        "/settings/test/mystnodes",
        data={"email": "test@example.com", "password": "wrongpass"},
        expected_status=200,
        validate_response=lambda r: (
            r.get("ok") == False and "error" in r,
            f"ok={r.get('ok')}, error present: {'error' in r}"
        )
    )
    
    if success and myst_test.get("ok") == False:
        tester.log("   ✓ Mystnodes test correctly returns ok:false for fake credentials", "INFO")
    
    # Test 16: Test Tailscale with fake key (should fail)
    success, ts_test = tester.run_test(
        "Test Tailscale (fake key)",
        "POST",
        "/settings/test/tailscale",
        data={"api_key": "fake_key_12345", "tailnet": "-"},
        expected_status=200,
        validate_response=lambda r: (
            r.get("ok") == False and "error" in r,
            f"ok={r.get('ok')}, error present: {'error' in r}"
        )
    )
    
    if success and ts_test.get("ok") == False:
        tester.log("   ✓ Tailscale test correctly returns ok:false for fake key", "INFO")
    
    # Print summary
    tester.print_summary()
    
    # Return exit code
    return 0 if len(tester.failed_tests) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
