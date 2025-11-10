import time, requests, os, json

ORCH = os.getenv("ORCH_URL", "http://orchestrator:8000")
SHIM = os.getenv("SHIM_URL", "http://shim:8001")
SLEEP = int(os.getenv("RED_SLEEP", "6"))

def log(msg):
    print(f"[RED] {msg}", flush=True)

def get_state():
    r = requests.get(f"{ORCH}/state?agent=red", timeout=10)
    return r.json()

def call_shim_scan(target_node, top_ports=5):
    payload = {"tool":"nmap","args":{"target": target_node, "--top-ports": str(top_ports)}}
    r = requests.post(f"{SHIM}/tool_request", json=payload, timeout=30)
    return r.json()

def post_action(actor, action_type, target, params=None):
    payload = {"actor": actor, "type": action_type, "target": target, "params": params or {}}
    r = requests.post(f"{ORCH}/action", json=payload, timeout=10)
    return r.json()

def main_loop():
    log("starting red agent")
    while True:
        try:
            state = get_state()
            nodes = state.get("nodes", [])
            # simple logic: pick first web node not yet compromised
            target = None
            for n in nodes:
                if n.get("type") == "web_server":
                    target = n["id"]
                    break
            if not target:
                log("no target found, sleeping")
                time.sleep(SLEEP)
                continue

            log(f"scanning {target} via shim")
            shim_res = call_shim_scan(target)
            log(f"shim response: {json.dumps(shim_res)}")

            # If shim reports open ports, attempt exploit
            sanitized = shim_res.get("sanitized", {})
            open_ports = sanitized.get("open_ports", [])
            if open_ports:
                log(f"attempting exploit on {target} (ports: {open_ports})")
                res = post_action("red", "exploit", target, {"exploit_power": 1.0})
                log(f"exploit result: {res}")
            else:
                log(f"no ports found on {target}, skipping exploit")

        except Exception as e:
            log(f"error: {e}")

        # run once per episode; sleep then run again
        time.sleep(SLEEP)

if __name__ == "__main__":
    main_loop()
