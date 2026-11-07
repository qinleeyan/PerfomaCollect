## Task 1 – Project Skeleton

**Files modified / created**
- `src/main.py`: already contained the `if __name__ == "__main__":` guard (no change needed).
- `src/config/schema.py`: created with a minimal Pydantic placeholder model:
  ```python
  from pydantic import BaseModel
  
  class Settings(BaseModel):
      pass
  ```
- Verified that the package initialisers are empty (no content changes):
  - `src/__init__.py`
  - `src/app/__init__.py`
  - `src/config/__init__.py`
  - `src/providers/__init__.py`
  - `src/storage/__init__.py`

**Issues encountered**
- The `Write` tool does not accept a `mode` argument; the file was written successfully after removing that parameter.
- No other functional changes were required.

**Test verification**
All tests now pass:
```
python -m pytest tests/test_skeleton.py -q
... 3 passed
```

The project skeleton meets the specifications for Task 1.
