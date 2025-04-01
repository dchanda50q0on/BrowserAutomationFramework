import pytest
from core.base_test import BaseTest

# This makes all BaseTest classes discoverable by pytest
def pytest_collect_file(parent, path):
    if path.ext == ".py" and "test" in path.basename.lower():
        return pytest.Module.from_parent(parent, path=path)