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
pip install -r requirements.txt
```

## Usage

### Basic

```bash
./drum.sh SRC_FILE INPUT_FILE
```

### Separately

Compiler:

```bash
python drumc.py SRC_FILE COMPILED_FILE
```


Machine:

```bash
python drumr.py COMPILED_FILE INPUT_FILE
```

