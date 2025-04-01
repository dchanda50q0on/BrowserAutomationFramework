import importlib
import pkgutil
from pathlib import Path
from typing import List, Type
from core.base_test import BaseTest


def discover_tests(base_path: str = "tests") -> List[Type[BaseTest]]:
    """Improved test discovery that handles nested directories"""
    test_classes = []
    tests_path = Path(base_path)

    # Recursively find all test files
    for path in tests_path.rglob("test_*.py"):
        try:
            # Convert path to module format (tests.subdir.test_file)
            module_path = str(path.with_suffix('')).replace('\\', '.')
            module = importlib.import_module(module_path)

            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and
                        issubclass(obj, BaseTest) and
                        obj != BaseTest):
                    test_classes.append(obj)

        except ImportError as e:
            print(f"⚠️ Could not import {path.name}: {str(e)}")

    return test_classes