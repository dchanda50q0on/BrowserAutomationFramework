import asyncio
import sys
from core.test_runner import TestRunner
from core.test_discover import discover_tests


async def main():
    test_classes = discover_tests()

    if not test_classes:
        print("❌ No tests found!")
        return False

    print(f"🚀 Found {len(test_classes)} tests:")
    for test_class in test_classes:
        print(f"- {test_class.__name__}")

    runner = TestRunner(max_workers=3)
    success = await runner.run_tests_parallel(test_classes)
    return success


if __name__ == "__main__":
    exit_code = 0 if asyncio.run(main()) else 1
    sys.exit(exit_code)