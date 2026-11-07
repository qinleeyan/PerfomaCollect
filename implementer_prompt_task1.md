# Task 1: Project Skeleton (Implementation)

**Goal:** Create the initial Python package skeleton for the Dual‑Model Dataset Generator.

**Files to create/modify:**
- Create: `src/__init__.py` (already exists – verify it’s empty/boilerplate)
- Create: `src/main.py` (already exists – add `if __name__ == "__main__"` guard)
- Create: `src/app/__init__.py`
- Create: `src/config/__init__.py`
- Create: `src/config/schema.py`
- Create: `src/providers/__init__.py`
- Create: `src/storage/__init__.py`
- Create: `pyproject.toml`
- Create: `requirements.txt`

**Existing state (as of this dispatch):**
- `src/__init__.py` – empty file (created)
- `src/main.py` – contains `main()` function but **missing** `if __name__ == "__main__"` guard
- All other directories and config files are empty or missing
- `pyproject.toml` – exists with basic build config
- `requirements.txt` – exists

**Requirements (must implement):**
1. Add `if __name__ == "__main__"` guard to `src/main.py` so running `python -m src.main` works
2. Ensure `src/__init__.py` is a valid package init file
3. Create `src/app/__init__.py`, `src/config/__init__.py`, `src/providers/__init__.py`, `src/storage/__init__.py` as empty package init files
4. Populate `src/config/schema.py` with a minimal Pydantic BaseModel placeholder (e.g., `class Settings(BaseModel): pass`)
5. Verify `pyproject.toml` references the correct package structure
6. Verify `requirements.txt` lists the dependencies needed for MVP

**Test coverage (will be verified after implementation):**
- `tests/test_skeleton.py` must pass all 3 tests after Task 1 completion

**Deliverables for the implementer:**
- Modified/created files as listed above
- A brief report of what was done (file paths, any issues encountered)
- The report should be saved to `tests/task1-report.md`

**Constraints:**
- Do NOT add any functionality beyond the skeleton – no config loading, no provider clients, no TUI yet
- Keep all changes minimal and focused on the package structure only
- Use UTF‑8 encoding for all files
- Follow the existing code style (bare minimum, no unnecessary comments)