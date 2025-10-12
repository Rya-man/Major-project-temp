import json, os, threading
LOG_FILE = os.getenv("ORCH_LOG", "/data/orch_logs.jsonl")
_lock = threading.Lock()

def persist_event(event: dict):
    with _lock:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(event) + "\n")
