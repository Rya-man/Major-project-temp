import random
from typing import Tuple

def exploit_success_probability(security_level: int, exploit_power: float = 1.0) -> float:
    """
    Example: P = exploit_power * (1 / (1 + security_level/2)) * noise
    """
    noise = random.uniform(0.85, 1.15)
    return max(0.0, min(1.0, exploit_power * (1.0 / (1.0 + security_level/2.0)) * noise))

def perform_exploit(node: dict, params: dict) -> Tuple[bool, dict]:
    sec = node.get("security_level", 3)
    power = params.get("exploit_power", 1.0)
    p = exploit_success_probability(sec, power)
    success = random.random() < p
    details = {"p_success": p}
    if success:
        node["compromised"] = True
    return success, details

def perform_scan(node: dict, params: dict) -> dict:
    # Return service list (maybe with noise)
    services = node.get("services", [])
    # optionally hide some services based on security_level or random false negatives
    return {"services": services}

def perform_patch(node: dict, params: dict) -> dict:
    node["security_level"] = min(node.get("security_level", 3) + 1, 10)
    return {"new_security_level": node["security_level"]}

def perform_isolate(node: dict, params: dict) -> dict:
    node["is_isolated"] = True
    node["is_isolated_until"] = params.get("duration", 3)  # timesteps
    return {"isolated": True}
