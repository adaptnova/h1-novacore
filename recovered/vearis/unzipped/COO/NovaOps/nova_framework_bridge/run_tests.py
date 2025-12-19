#!/usr/bin/env python3
"""
Test runner script for Nova Framework Bridge.
Executes test suite with coverage reporting and performance profiling.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

def setup_environment():
    """Set up test environment."""
    # Add src directory to Python path
    src_dir = Path(__file__).parent / 'src'
    sys.path.append(str(src_dir))

    # Create necessary directories
    dirs = ['logs', 'coverage_html', 'test_results']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)

def run_tests(args):
    """Run test suite with specified options."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Base pytest command
    cmd = [
        'pytest',
        '--verbose',
        '--tb=short',
        f'--cov={args.source}',
        '--cov-report=term-missing',
        f'--cov-report=html:coverage_html/coverage_{timestamp}',
        f'--junit-xml=test_results/test_results_{timestamp}.xml',
    ]

    # Add optional arguments
    if args.failfast:
        cmd.append('--exitfirst')

    if args.durations:
        cmd.extend(['--durations=10'])

    if args.last_failed:
        cmd.append('--lf')

    if args.markers:
        cmd.extend(['-m', args.markers])

    # Add test paths
    cmd.extend(args.test_paths)

    # Run tests
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code: {e.returncode}")
        sys.exit(e.returncode)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run Nova Framework Bridge test suite'
    )

    parser.add_argument(
        '--source',
        default='src',
        help='Source directory to measure coverage'
    )

    parser.add_argument(
        '--failfast',
        action='store_true',
        help='Stop on first failure'
    )

    parser.add_argument(
        '--durations',
        action='store_true',
        help='Show slowest test durations'
    )

    parser.add_argument(
        '--last-failed',
        action='store_true',
        help='Run only failed tests'
    )

    parser.add_argument(
        '--markers',
        help='Only run tests with specified markers'
    )

    parser.add_argument(
        'test_paths',
        nargs='*',
        default=['tests'],
        help='Paths to test files or directories'
    )

    args = parser.parse_args()

    # Set up environment
    setup_environment()

    # Print test configuration
    print("\nNova Framework Bridge Test Runner")
    print("================================")
    print(f"Source directory: {args.source}")
    print(f"Test paths: {', '.join(args.test_paths)}")
    if args.markers:
        print(f"Test markers: {args.markers}")
    print("\nRunning tests...\n")

    # Run tests
    run_tests(args)

if __name__ == '__main__':
    main()