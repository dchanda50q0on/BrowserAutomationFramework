import asyncio
from core.test_runner import TestRunner
from core.test_discover import discover_tests


async def run_all_tests():
    test_classes = discover_tests()

    if not test_classes:
        print("❌ No tests found! Check:")
        print("1. Files must be named 'test_*.py'")
        print("2. Classes must inherit from BaseTest")
        print("3. All test directories need __init__.py")
        return

    print(f"🚀 Found {len(test_classes)} tests:")
    for test_class in test_classes:
        print(f"- {test_class.__name__} ({test_class.__module__})")

    test_runner = TestRunner(max_workers=3)
    await test_runner.run_tests_parallel(test_classes)


if __name__ == "__main__":
    asyncio.run(run_all_tests())