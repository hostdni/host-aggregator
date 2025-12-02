#!/usr/bin/env python3
"""
Test script for host aggregator functionality.
"""

import csv
import os
import subprocess
import sys


def test_script_execution():
    """Test that the script runs without errors."""
    print("Testing script execution...")
    try:
        result = subprocess.run(
            [sys.executable, "host_aggregator.py"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print("✅ Script executed successfully")
            return True
        else:
            print(f"❌ Script failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Script timed out")
        return False
    except Exception as e:
        print(f"❌ Script execution failed: {e}")
        return False


def test_csv_output():
    """Test that CSV files are created with correct format."""
    print("Testing CSV output...")

    # Check if latest.csv exists
    if not os.path.exists("latest.csv"):
        print("❌ latest.csv not found")
        return False

    # Check CSV format
    try:
        with open("latest.csv", "r") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            expected_headers = [
                "entry",
                "category",
                "action",
                "description",
                "risk",
                "is_enabled",
            ]

            if headers != expected_headers:
                print(f"❌ CSV headers don't match expected: {headers}")
                return False

            # Check first few rows
            rows = list(reader)[:5]
            if not rows:
                print("❌ No data rows found")
                return False

            # Validate data structure
            for row in rows:
                if not all(key in row for key in expected_headers):
                    print(f"❌ Missing required fields in row: {row}")
                    return False

                if row["action"] != "block":
                    print(f"❌ Unexpected action value: {row['action']}")
                    return False

                if row["is_enabled"] != "True":
                    print(
                        f"❌ Unexpected is_enabled value: {row['is_enabled']}"
                    )
                    return False

            print("✅ CSV output format is correct")
            return True

    except Exception as e:
        print(f"❌ CSV validation failed: {e}")
        return False


def test_data_quality():
    """Test data quality metrics."""
    print("Testing data quality...")

    try:
        with open("latest.csv", "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Count entries by category
            categories = {}
            for row in rows:
                cat = row["category"]
                categories[cat] = categories.get(cat, 0) + 1

            print(f"Total entries: {len(rows)}")
            print("Category distribution:")
            for cat, count in sorted(categories.items()):
                print(f"  {cat}: {count}")

            # Check for expected categories
            expected_categories = [
                "Adware & Malware",
                "Fake news",
                "Gambling",
                "Porn",
                "Social",
            ]
            missing_categories = set(expected_categories) - set(
                categories.keys()
            )
            if missing_categories:
                print(f"❌ Missing expected categories: {missing_categories}")
                return False

            print("✅ Data quality checks passed")
            return True

    except Exception as e:
        print(f"❌ Data quality check failed: {e}")
        return False


def cleanup():
    """Clean up test files."""
    test_files = ["latest.csv", "host_entries_*.csv"]
    for pattern in test_files:
        if "*" in pattern:
            import glob

            for file in glob.glob(pattern):
                os.remove(file)
        elif os.path.exists(pattern):
            os.remove(pattern)


def main():
    """Run all tests."""
    print("Running host aggregator tests...\n")

    tests = [test_script_execution, test_csv_output, test_data_quality]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Tests completed: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed!")
        cleanup()
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
