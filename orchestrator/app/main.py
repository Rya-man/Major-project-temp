from fastapi import FastAPI, HTTPException
from .models import StateResponse, Action
from .utils import build_sample_network, sanitize_for_agent
from .executor import perform_exploit, perform_scan, perform_patch, perform_isolate
from .storage import persist_event
import networkx as nx
import time, uuid

app = FastAPI(title="Orchestrator")

# global network state (simple prototype)
G: nx.Graph = build_sample_network()
TIMESTEP = 0

@app.get("/health")
def health():
    return {"status":"ok", "t": int(time.time())}

@app.get("/state", response_model=StateResponse)
def get_state(agent: str = "red"):
    return sanitize_for_agent(G, agent)

@app.post("/action")
def post_action(action: Action):
    global TIMESTEP
    if action.target not in G.nodes:
        raise HTTPException(404, f"target {action.target} not found")

    node = G.nodes[action.target]
    outcome = {"action_id": str(uuid.uuid4()), "actor": action.actor, "type": action.type, "target": action.target, "timestamp": time.time()}

    if action.type == "scan":
        scan_res = perform_scan(node, action.params)
        outcome["result"] = scan_res
    elif action.type == "exploit":
        success, details = perform_exploit(node, action.params)
        outcome["result"] = {"success": success, **details}
    elif action.type == "patch":
        outcome["result"] = perform_patch(node, action.params)
    elif action.type == "isolate":
        outcome["result"] = perform_isolate(node, action.params)
    elif action.type == "noop":
        outcome["result"] = {"noop": True}
    else:
        raise HTTPException(400, "unknown action type")

    # append basic log to node
    node.setdefault("logs", []).append(outcome)
    persist_event({"type":"action", **outcome})
    TIMESTEP += 1
    # decrement isolation counters
    for n in G.nodes:
        nd = G.nodes[n]
        if nd.get("is_isolated_until"):
            nd["is_isolated_until"] = max(0, nd["is_isolated_until"] - 1)
            if nd["is_isolated_until"] == 0:
                nd["is_isolated"] = False

    return outcome

@app.post("/ingest_tool_result")
def ingest_tool_result(payload: dict):
    """
    Called by the shim. Payload must be a dict with
    { job_id, sanitized: {...}, target_node (optional) }
    """
    payload["received_at"] = time.time()
    # Just persist and optionally attach to node logs
    target = payload.get("target_node")
    if target and target in G.nodes:
        G.nodes[target].setdefault("logs", []).append({"tool_result": payload})
    persist_event({"type":"tool_result", **payload})
    return {"status":"ok"}
