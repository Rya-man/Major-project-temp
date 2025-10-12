from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class NodeView(BaseModel):
    id: str
    type: str
    services: List[str]
    security_level: int
    compromised: bool

class StateResponse(BaseModel):
    nodes: List[NodeView]

class Action(BaseModel):
    actor: str           # "red" or "blue"
    type: str            # "scan","exploit","patch","isolate","deploy_decoy","noop"
    target: str
    params: Dict[str, Any] = {}
