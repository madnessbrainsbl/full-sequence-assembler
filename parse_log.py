#!/usr/bin/env python3
import json
import re

def parse_log_seq(fname):
    seq = []
    with open(fname, encoding='utf-8') as f:
        content = f.read()
    # Match tokens: control codes _xXX_ or other sequences separated by whitespace
    tokens = re.findall(r'(_x[0-9A-Fa-f]{2}_|\S+)', content)
    i = 1
    for token in tokens:
        raw = token.strip()
        if not raw:
            continue
        # Split code and params by comma
        if raw.startswith('_x') and raw.endswith('_'):
            code = raw
            params = []
        else:
            parts = raw.split(',')
            code = parts[0]
            params = parts[1:] if len(parts) > 1 else []
        entry = {"seq": i, "raw": raw, "code": code, "params": params}
        seq.append(entry)
        i += 1
    return seq

if __name__ == '__main__':
    seq = parse_log_seq('vendor-последовательность.txt')
    print(json.dumps(seq, ensure_ascii=False, indent=2)) 