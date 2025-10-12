import re

def parse_and_sanitize(tool: str, raw_output: str) -> dict:
    if tool == "nmap":
        ports = re.findall(r"(\d+)/tcp\s+open", raw_output)
        return {"open_ports": [int(p) for p in ports]}
    elif tool == "curl":
        match = re.search(r"HTTP/1.[01]\s+(\d+)", raw_output)
        return {"status_code": int(match.group(1)) if match else None}
    else:
        return {"summary": raw_output[:200]}
