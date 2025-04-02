import importlib
from pathlib import Path
from typing import List, Type
from core.base_test import BaseTest

def discover_tests(base_path: str = "tests") -> List[Type[BaseTest]]:
    """Discover all test classes inheriting from BaseTest"""
    test_classes = []
    tests_path = Path(base_path)

    for test_file in tests_path.rglob("test_*.py"):
        try:
            module_path = ".".join(test_file.with_suffix('').parts)
            module = importlib.import_module(module_path)

            for name, obj in vars(module).items():
                if (isinstance(obj, type) and
                        issubclass(obj, BaseTest) and
                        obj != BaseTest):
                    test_classes.append(obj)
        except ImportError as e:
            print(f"⚠️ Could not import {test_file.name}: {str(e)}")

    return test_classes