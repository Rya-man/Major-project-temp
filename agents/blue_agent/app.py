import time, requests, os, json

ORCH = os.getenv("ORCH_URL", "http://orchestrator:8000")
SLEEP = int(os.getenv("BLUE_SLEEP", "8"))

def log(msg):
    print(f"[BLUE] {msg}", flush=True)

def get_state():
    r = requests.get(f"{ORCH}/state?agent=blue", timeout=10)
    return r.json()

def post_action(actor, action_type, target, params=None):
    payload = {"actor": actor, "type": action_type, "target": target, "params": params or {}}
    r = requests.post(f"{ORCH}/action", json=payload, timeout=10)
    return r.json()

def main_loop():
    log("starting blue agent")
    while True:
        try:
            state = get_state()
            nodes = state.get("nodes", [])
            for n in nodes:
                if n.get("compromised"):
                    target = n["id"]
                    log(f"detected compromise on {target}, isolating")
                    res = post_action("blue", "isolate", target, {"duration": 2})
                    log(f"isolate result: {res}")
                    # optionally patch after isolate
                    res2 = post_action("blue", "patch", target, {})
                    log(f"patch result: {res2}")
        except Exception as e:
            log(f"error: {e}")

        time.sleep(SLEEP)

if __name__ == "__main__":
    main_loop()
