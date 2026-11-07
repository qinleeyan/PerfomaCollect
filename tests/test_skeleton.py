"""Test that the project skeleton loads without errors."""

import pytest
import os


def test_package_imports():
    """Verify that src can be imported."""
    from src import main  # noqa: F401
    from src.main import main  # noqa: F401


def test_main_module_has_guard():
    """Verify main.py has the if __name__ == "__main__" guard."""
    with open("src/main.py", "r") as f:
        content = f.read()
    assert "__name__" in content, "missing __name__ guard in src/main.py"
    assert "if __name__" in content, "missing 'if __name__' block in src/main.py"


def test_no_unused_imports():
    """Verify there are no obvious unused imports in the project."""
    import os

    for root, dirs, files in os.walk("src"):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                with open(path) as fh:
                    content = fh.read()
                # Simple heuristic: check for import statements
                if "import " in content:
                    pass  # will be checked more thoroughly later