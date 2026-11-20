# PerfomaCollect

PerfomaCollect is a dual-model Terminal User Interface (TUI) application designed for automated generation of Question & Answer datasets.

## Core Capabilities

- **Separated Model Roles**:
  - **Question Model**: Formulates diverse questions based on a topic input.
  - **Answer Model**: Answers questions independently without access to the initial topic prompt.
- **Custom Answer Formats**: Supports `Markdown`, unformatted `Plain Text`, and structured `JSON`.
- **Export Options**: Streams records directly to `.jsonl`, `.json`, `.csv`, or `.xlsx`.
- **Safe Interruption**: Stop generation at any time with `Ctrl+C` or `Escape` while keeping all written records.

## Visual Overview

Screenshots available in `src/images/`:

- **Main Menu**: `src/images/1.png`
- **Model Setup**: `src/images/2.png`, `src/images/3.png`
- **Validation**: `src/images/4.png`, `src/images/5.png`
- **Ready State**: `src/images/6.png`, `src/images/7.png`
- **Configuration**: `src/images/8.png`, `src/images/9.png`
- **Live Generation**: `src/images/10.png`, `src/images/11.png`

## Getting Started

### Prerequisites

- Python 3.10+

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Usage

```bash
python3 main.py
```

## License

This project is licensed under the MIT License. Refer to the LICENSE file for details.
