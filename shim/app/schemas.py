from pydantic import BaseModel, Field
from typing import Dict, Any

class ToolRequest(BaseModel):
    tool: str = Field(..., description="Tool name, e.g., 'nmap'")
    args: Dict[str, Any] = Field(default_factory=dict)

class ToolResponse(BaseModel):
    job_id: str
    sanitized: Dict[str, Any]
