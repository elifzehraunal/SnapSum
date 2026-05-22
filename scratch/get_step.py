import json
from pathlib import Path

log_path = Path(r"C:\Users\ibrah\Documents\GitHub\SnapSum\scratch\search_logs.py")
# We want to read from the transcript.jsonl instead
transcript_path = Path(r"C:\Users\ibrah\.gemini\antigravity\brain\18e42bcc-a503-434e-a26a-1c24cc8322c3\.system_generated\logs\transcript.jsonl")

steps_to_inspect = [485, 486, 591, 595]

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            idx = data.get("step_index")
            if idx in steps_to_inspect:
                print(f"\n--- STEP {idx} ({data.get('type')}) ---")
                tool_calls = data.get("tool_calls", [])
                if tool_calls:
                    print("Tool Calls:")
                    for tc in tool_calls:
                        print(f"Name: {tc.get('name')}")
                        args = tc.get("args", {})
                        if "ReplacementContent" in args:
                            print(f"ReplacementContent:\n{args.get('ReplacementContent')}")
                        if "TargetContent" in args:
                            print(f"TargetContent:\n{args.get('TargetContent')}")
                        if "CodeContent" in args:
                            print(f"CodeContent:\n{args.get('CodeContent')[:400]}")
                else:
                    print(f"Content: {data.get('content')[:1000]}")
        except Exception as e:
            pass
