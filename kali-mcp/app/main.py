from fastapi import FastAPI, Request
import random, asyncio

app = FastAPI(title="Dummy Kali-MCP")

@app.post("/run")
async def run_tool(req: Request):
    data = await req.json()
    tool = data.get("tool")
    args = data.get("args", {})

    # Simulate a delay (tool running)
    await asyncio.sleep(1.0)

    # Return dummy output text
    if tool == "nmap":
        top_ports = args.get("--top-ports", 10)
        ports = random.sample(range(20, 9000), int(top_ports))
        output = "\n".join([f"{p}/tcp open http" for p in ports])
    elif tool == "curl":
        output = "HTTP/1.1 200 OK\nServer: DummyServer/1.0"
    else:
        output = f"{tool} executed with args {args}."

    return {"stdout": output, "stderr": "", "status": "success"}
