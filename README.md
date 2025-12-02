# 2025_October_CTF

Notes, scripts, and artifacts for October 2025 CTF.

## Structure
- `writeups/`: Challenge-by-challenge notes and solutions
- `scripts/`: Utilities for analysis/automation
- `artifacts/`: PCAPs, memory/disk images, samples (tracked via Git LFS)
- `notes/`: General reconnaissance, quick commands, references

## Environment
- Python 3.11
- Tools: tshark, Wireshark, binwalk, ghidra, etc.

## How to run
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt