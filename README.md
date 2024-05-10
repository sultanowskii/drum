# drum

Drum programming language (with its own "compiler" & "runtime").

An assignment @ ITMO university. Report lives here: [report.md](report.md) (russian).

## Installation

```bash
# Download project
git clone https://github.com/sultanowskii/drum.git
cd drum

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependecies
python install -r requirements
```

## Usage

Compiler:

```bash
python drumc.py INPUT_FILE OUTPUT_FILE
```

`INPUT_FILE` is of `.dr`

`OUTPUT_FILE` is of `.drc`
