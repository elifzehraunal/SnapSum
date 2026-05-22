import json
from pathlib import Path

log_path = Path(r"C:\Users\ibrah\.gemini\antigravity\brain\18e42bcc-a503-434e-a26a-1c24cc8322c3\.system_generated\logs\transcript.jsonl")

if not log_path.exists():
    print("Log path does not exist")
    exit(1)

print("Searching transcript...")
count = 0
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        if "FilePicker" in line or "overlay" in line:
            try:
                data = json.loads(line)
                # print type and step_index and snippet of content
                content = data.get("content", "")
                if isinstance(content, str) and len(content) > 200:
                    content = content[:200] + "..."
                print(f"Step {data.get('step_index')}: Type={data.get('type')}, Status={data.get('status')}, Snippet={content}")
                count += 1
                if count > 30:
                    print("Too many matches, stopping...")
                    break
            except Exception as e:
                pass
