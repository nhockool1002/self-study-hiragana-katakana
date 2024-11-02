# Self-Study Hiragana and Katakana

## Introduction

This is a simple application for self-study of Hiragana and Katakana characters. It randomly displays a character on the screen, allowing you to practice and listen to the pronunciation.

## Installation

### Prerequisites

- Python 3.x
- Virtualenv (optional, but recommended)

### Setup Virtual Environment

Create and activate a virtual environment to isolate the project dependencies:

```bash
# Install Qt & pygame (*)
pip install --upgrade PyQt6 pygame

# Add QT
vi ~/.bash_profile
vi ~/.zshrc

# Apply setup env
source ~/.bash_profile
source ~/.zshrc

# Create virtual environment (optional)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate (MacOS/Linux)
venv\Scripts\activate (Windows)

# Install Dependencies
pip install -r requirements.txt
```

### Usage
```bash
python learn.py
```
