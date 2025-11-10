from fastapi import FastAPI, HTTPException
from .schemas import ToolRequest, ToolResponse
from .sanitizer import parse_and_sanitize
import requests, uuid, os

KALI_MCP_URL = os.getenv("KALI_MCP_URL", "http://kali-mcp:5000")
ORCH_URL = os.getenv("ORCH_URL", "http://orchestrator:8000")

app = FastAPI(title="Shim")

WHITELIST = {
    "nmap": ["--top-ports","target"],
    "curl": ["-I", "-X", "--max-time","target"]
}

def is_whitelisted(tool, args: dict):
    for k in args.keys():
        if k.startswith("-") and k not in WHITELIST.get(tool,[]):
            return False
        if not k.startswith("-") and k!="target":
            return False
        
    return tool in WHITELIST

@app.post("/tool_request", response_model=ToolResponse)
def tool_request(req: ToolRequest):
    if not is_whitelisted(req.tool, req.args):
        raise HTTPException(403, detail="Tool or argument not allowed")

    try:
        mcp_resp = requests.post(
            f"{KALI_MCP_URL}/run",
            json={"tool":req.tool,"args":req.args},
            timeout=30
        )
        mcp_resp.raise_for_status()
        payload = mcp_resp.json()
        raw_text = payload.get("stdout","")
    except Exception as e:
        raise HTTPException(502,detail=f"Kali MCP call failed: {e}")
    
    sanitized = parse_and_sanitize(req.tool,raw_text)
    job_id = str(uuid.uuid4())
    result = {"job_id":job_id,"sanitized":sanitized}

    try:
        requests.post(f"{ORCH_URL}/ingest_tool_result", json=result, timeout=10)
    except Exception:
        pass

    return result
