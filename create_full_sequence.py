import json

# Read all sendDiagCmd calls from commands_seq.txt
with open('commands_seq.txt', 'r') as f:
    script_commands = f.read()

# Read all log commands from log_commands.json
with open('log_commands.json', 'r') as f:
    log_commands = json.load(f)

# Format log commands
log_formatted = "\n\nLOG COMMANDS\n" + "\n".join([f"{cmd['seq']}: {cmd['raw']} {cmd['params']}" for cmd in log_commands])

# Combine both lists
full_sequence = script_commands + log_formatted

# Write the full sequence to file
with open('full_sequence.txt', 'w') as f:
    f.write(full_sequence)

print("Created full_sequence.txt with", len(script_commands.splitlines()), "script commands and", len(log_commands), "log commands") 