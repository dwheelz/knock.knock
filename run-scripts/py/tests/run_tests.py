"""Runs the unit tests"""

import os
from pathlib import Path
from unittest import TestLoader, TextTestRunner

TESTCASE_DIR = os.path.join(os.path.abspath(Path(__file__).parent), "test_cases")

def discover_and_run(start_dir: str = TESTCASE_DIR, pattern: str = "test_*.py"):
    """Discovers and runs all unit tests from the specified DIR
    Args:
        start_dir (str, optional): The DIR to scan. Defaults to 'tests/'.
        pattern (str, optional): The naming convention for test files. Defaults to 'test*.py'.
    Returns:
        runner.run: The result of the test cases
    """
    tests = TestLoader().discover(start_dir, pattern=pattern)
    runner = TextTestRunner(verbosity=2)
    return runner.run(tests)

if __name__ == "__main__":
    discover_and_run()
