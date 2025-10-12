from fastapi import FastAPI, HTTPException
from .schemas import ToolRequest, ToolResponse
from .sanitizer import parse_and_sanitize
import requests, uuid, os

KALI_MCP_URL = os.getenv("KALI_MCP_URL", "http://kali-mcp:5000")
ORCH_URL = os.getenv("ORCH_URL", "http://orchestrator:8000")

app = FastAPI(title="Shim")

WHITELIST = {
    "nmap": ["--top-ports"],
    "curl": ["-I", "-X", "--max-time"]
}

def is_whitelisted(tool, args):
    return tool in WHITELIST and all(
        arg in WHITELIST[tool] or not arg.startswith("-") for arg in args.keys()
    )

@app.post("/tool_request", response_model=ToolResponse)
def tool_request(req: ToolRequest):
    if not is_whitelisted(req.tool, req.args):
        raise HTTPException(403, detail="Tool or argument not allowed")

    # simulate a dummy MCP reply (for now)
    raw_text = f"Simulated {req.tool} output on target {req.args}"
    sanitized = parse_and_sanitize(req.tool, raw_text)

    job_id = str(uuid.uuid4())
    result = {"job_id": job_id, "sanitized": sanitized}

    try:
        requests.post(f"{ORCH_URL}/ingest_tool_result", json=result, timeout=10)
    except Exception as e:
        print(f"Warning: failed to post to orchestrator: {e}")

    return result
