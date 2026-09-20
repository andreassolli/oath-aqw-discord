#!/usr/bin/env python3
"""
Extract specific "cmd" messages from a reassembled TCP stream dump
and save them as a JSON array.

Usage:
    python3 extract_messages.py stream_dump.txt output.json

Where stream_dump.txt is produced with, e.g.:
    tshark -r session.pcap -q -z follow,tcp,ascii,0 > stream_dump.txt
"""

import json
import sys

WANTED_CMDS = {"updateClass", "sAct", "aura+p"}


def extract_messages(data: str):
    decoder = json.JSONDecoder()
    pos = 0
    results = []

    while pos < len(data):
        start = data.find('{"t":"xt"', pos)
        if start == -1:
            break
        try:
            obj, end = decoder.raw_decode(data, start)
        except json.JSONDecodeError:
            # Not a valid JSON object starting here; move forward one
            # character and keep scanning rather than getting stuck.
            pos = start + 1
            continue

        cmd = obj.get("b", {}).get("o", {}).get("cmd")
        if cmd in WANTED_CMDS:
            results.append(obj)

        pos = end

    return results


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_stream.txt> <output.json>")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        data = f.read()

    messages = extract_messages(data)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

    print(f"Found {len(messages)} matching messages. Saved to {output_path}")


if __name__ == "__main__":
    main()
