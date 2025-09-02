#!/usr/bin/env python
"""
Comprehensive Test Runner

This script provides a comprehensive test runner for the Django E-commerce application
with options for running different types of tests and generating coverage reports.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import argparse
import subprocess
import time
from pathlib import Path


def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ecommerce.settings')
    django.setup()


def run_unit_tests():
    """Run unit tests for all features"""
    print(" Running Unit Tests...")
    print("=" * 50)
    
    test_modules = [
        'tests.authentication',
        'tests.products',
        'tests.orders',
        'tests.search',
        'tests.analytics',
        'tests.recommendations',
        'tests.performance',
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for module in test_modules:
        print(f"\n Testing {module}...")
        try:
            result = subprocess.run([
                sys.executable, 'manage.py', 'test', module, '--verbosity=2'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f" {module} - PASSED")
                passed_tests += 1
            else:
                print(f" {module} - FAILED")
                print(result.stdout)
                print(result.stderr)
                failed_tests += 1
            
            total_tests += 1
            
        except Exception as e:
            print(f" {module} - ERROR: {e}")
            failed_tests += 1
            total_tests += 1
    
    print(f"\n Unit Tests Summary:")
    print(f"Total: {total_tests}, Passed: {passed_tests}, Failed: {failed_tests}")
    return failed_tests == 0


def run_integration_tests():
    """Run integration tests"""
    print("\n Running Integration Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'test', 'tests.integration', '--verbosity=2'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(" Integration Tests - PASSED")
            return True
        else:
            print(" Integration Tests - FAILED")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f" Integration Tests - ERROR: {e}")
        return False


def run_performance_tests():
    """Run performance tests"""
    print("\n Running Performance Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'test', 'tests.performance', '--verbosity=2'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(" Performance Tests - PASSED")
            return True
        else:
            print(" Performance Tests - FAILED")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f" Performance Tests - ERROR: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n Running All Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'test', '--verbosity=2'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(" All Tests - PASSED")
            return True
        else:
            print(" All Tests - FAILED")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f" All Tests - ERROR: {e}")
        return False


def run_coverage_tests():
    """Run tests with coverage report"""
    print("\n Running Tests with Coverage...")
    print("=" * 50)
    
    try:
        # Install coverage if not already installed
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], 
                      capture_output=True)
        
        # Run tests with coverage
        result = subprocess.run([
            sys.executable, '-m', 'coverage', 'run', '--source=.', 
            'manage.py', 'test', '--verbosity=2'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(" Tests with Coverage - PASSED")
            
            # Generate coverage report
            print("\n Generating Coverage Report...")
            subprocess.run([sys.executable, '-m', 'coverage', 'report'])
            
            # Generate HTML coverage report
            print("\n Generating HTML Coverage Report...")
            subprocess.run([sys.executable, '-m', 'coverage', 'html'])
            print("HTML coverage report generated in htmlcov/")
            
            return True
        else:
            print(" Tests with Coverage - FAILED")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f" Tests with Coverage - ERROR: {e}")
        return False


def run_specific_test(test_path):
    """Run specific test"""
    print(f"\n Running Specific Test: {test_path}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'test', test_path, '--verbosity=2'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f" {test_path} - PASSED")
            return True
        else:
            print(f" {test_path} - FAILED")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f" {test_path} - ERROR: {e}")
        return False


def run_load_tests():
    """Run load tests (if available)"""
    print("\n Running Load Tests...")
    print("=" * 50)
    
    # This would typically use a tool like locust or similar
    print("  Load tests require additional setup (e.g., Locust)")
    print("   To run load tests, install locust and create load test files")
    return True


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Comprehensive Test Runner for Django E-commerce')
    parser.add_argument('--type', choices=[
        'unit', 'integration', 'performance', 'all', 'coverage', 'load'
    ], default='all', help='Type of tests to run')
    parser.add_argument('--test', help='Specific test to run (e.g., tests.authentication.test_jwt_auth)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup Django
    setup_django()
    
    print(" Django E-commerce Test Runner")
    print("=" * 50)
    print(f"Test Type: {args.type}")
    print(f"Verbose: {args.verbose}")
    print("=" * 50)
    
    start_time = time.time()
    success = False
    
    try:
        if args.test:
            success = run_specific_test(args.test)
        elif args.type == 'unit':
            success = run_unit_tests()
        elif args.type == 'integration':
            success = run_integration_tests()
        elif args.type == 'performance':
            success = run_performance_tests()
        elif args.type == 'coverage':
            success = run_coverage_tests()
        elif args.type == 'load':
            success = run_load_tests()
        elif args.type == 'all':
            success = run_all_tests()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n Total Time: {duration:.2f} seconds")
        
        if success:
            print("\n All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
