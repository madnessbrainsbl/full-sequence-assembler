
## Overview

`full-sequence-assembler` is a lightweight Python utility that merges diagnostic command sequences from two sources—a script file and a log file—into a single, comprehensive command sequence. This can be useful for development, debugging, or auditing diagnostic workflows.

## Features

- Read script commands from `commands_seq.txt` (plain text).
- Read log commands from `log_commands.json` (JSON array of objects with `seq`, `raw`, and `params` fields).
- Format log commands with sequence numbers and parameters.
- Combine both script and log commands into one ordered sequence.
- Output the merged sequence to `full_sequence.txt`.

## Prerequisites

- Python 3.6 or higher

## Installation

```bash
# Clone the repository
git clone https://github.com/madnessbrainsbl/full-sequence-assembler.git
cd full-sequence-assembler
```

## Usage

1. Ensure the following files are present at the project root:
   - `commands_seq.txt` (your scripted diagnostic commands)
   - `log_commands.json` (raw log commands in JSON format)
2. Run the merge script:

   ```bash
   python create_full_sequence.py
   ```

3. After execution, you will find `full_sequence.txt` in the project directory containing the combined command sequence.

## Input & Output

| File                  | Format        | Description                                      |
|-----------------------|---------------|--------------------------------------------------|
| `commands_seq.txt`    | Plain text    | Scripted diagnostic commands (one per line).     |
| `log_commands.json`   | JSON          | Array of log commands with sequence metadata.    |
| `full_sequence.txt`   | Plain text    | Merged output combining both command sources.    |


