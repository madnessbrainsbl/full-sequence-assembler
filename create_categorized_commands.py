import json

# Define command categories
# Based on the documentation and analysis
INIT_TEST_COMMANDS = {
    '_x1A_', '_x02_', '_x14_', 'J', ':', 'W0', '/'
}

CALIBRATION_COMMANDS = {
    'm', 'U', '+', 't', 's', 'w', 'r', 'x', 'V', 'G', 'Q', 'N', 'I', 'B'
}

DEFECT_COMMANDS = {
    'b', 'f', 'E'
}

# Load parsed log commands from file
with open('log_commands.json', 'r') as f:
    log_commands = json.load(f)

# Read extracted script commands from file
with open('commands_seq.txt', 'r') as f:
    script_commands_raw = f.readlines()

# Process script commands for categorization
script_commands = []
for line in script_commands_raw:
    parts = line.strip().split('  ')
    if len(parts) >= 3:
        path_line, cmd, params = parts
        if cmd == "None":
            cmd = ""
        script_commands.append({
            "source": path_line,
            "cmd": cmd,
            "params": params
        })

# Function to categorize a command
def categorize_command(cmd):
    # Check command prefixes for categorization
    first_char = cmd[0] if cmd else ""
    
    # Special case for log commands where we've already extracted the command code
    if first_char in INIT_TEST_COMMANDS or cmd in INIT_TEST_COMMANDS:
        return "initialization"
    elif first_char in CALIBRATION_COMMANDS or cmd in CALIBRATION_COMMANDS:
        return "calibration"
    elif first_char in DEFECT_COMMANDS or cmd in DEFECT_COMMANDS:
        return "defect"
    else:
        return "unknown"  # Default category

# Categorize log commands
categories = {
    "initialization": [],
    "calibration": [],
    "defect": [],
    "unknown": []
}

# Process log commands
for cmd in log_commands:
    category = categorize_command(cmd["code"])
    categories[category].append({
        "type": "log",
        "seq": cmd["seq"],
        "raw": cmd["raw"],
        "params": cmd["params"]
    })

# Process script commands
for cmd in script_commands:
    category = categorize_command(cmd["cmd"])
    categories[category].append({
        "type": "script",
        "source": cmd["source"],
        "cmd": cmd["cmd"],
        "params": cmd["params"]
    })

# Write categorized commands to a file
with open('categorized_commands.txt', 'w') as f:
    f.write("=== VENDOR COMMANDS CATEGORIZATION ===\n\n")
    
    f.write("1. INITIALIZATION AND TESTING COMMANDS\n")
    f.write(f"Total: {len(categories['initialization'])}\n")
    f.write("----------------------------------------\n")
    for cmd in categories['initialization']:
        if cmd["type"] == "log":
            f.write(f"LOG {cmd['seq']}: {cmd['raw']} {cmd['params']}\n")
        else:
            f.write(f"SCRIPT {cmd['source']}: {cmd['cmd']} {cmd['params']}\n")
    
    f.write("\n2. CALIBRATION COMMANDS\n")
    f.write(f"Total: {len(categories['calibration'])}\n")
    f.write("----------------------------------------\n")
    for cmd in categories['calibration']:
        if cmd["type"] == "log":
            f.write(f"LOG {cmd['seq']}: {cmd['raw']} {cmd['params']}\n")
        else:
            f.write(f"SCRIPT {cmd['source']}: {cmd['cmd']} {cmd['params']}\n")
    
    f.write("\n3. DEFECT HANDLING COMMANDS\n")
    f.write(f"Total: {len(categories['defect'])}\n")
    f.write("----------------------------------------\n")
    for cmd in categories['defect']:
        if cmd["type"] == "log":
            f.write(f"LOG {cmd['seq']}: {cmd['raw']} {cmd['params']}\n")
        else:
            f.write(f"SCRIPT {cmd['source']}: {cmd['cmd']} {cmd['params']}\n")
    
    if categories['unknown']:
        f.write("\n4. UNKNOWN CATEGORY COMMANDS\n")
        f.write(f"Total: {len(categories['unknown'])}\n")
        f.write("----------------------------------------\n")
        for cmd in categories['unknown']:
            if cmd["type"] == "log":
                f.write(f"LOG {cmd['seq']}: {cmd['raw']} {cmd['params']}\n")
            else:
                f.write(f"SCRIPT {cmd['source']}: {cmd['cmd']} {cmd['params']}\n")
    
    total = sum(len(cat) for cat in categories.values())
    f.write(f"\nTOTAL COMMANDS: {total}\n")

print(f"Created categorized_commands.txt with categorized commands:")
for category, cmds in categories.items():
    print(f"  {category}: {len(cmds)}")
print(f"Total: {sum(len(cat) for cat in categories.values())}") 