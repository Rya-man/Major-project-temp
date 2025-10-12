import networkx as nx
from typing import Dict, Any
from .models import NodeView

def build_sample_network() -> nx.Graph:
    G = nx.Graph()
    G.add_node("web-01", type="web_server", services=["http","ssh"], security_level=3, compromised=False, logs=[])
    G.add_node("db-01", type="database", services=["mysql"], security_level=4, compromised=False, logs=[])
    G.add_edge("web-01", "db-01")
    return G

def sanitize_for_agent(G: nx.Graph, agent: str) -> Dict[str, Any]:
    # basic policy: red sees node metadata but not credentials or full logs
    nodes = []
    for n in G.nodes():
        nd = G.nodes[n]
        nodes.append({
            "id": n,
            "type": nd.get("type"),
            "services": nd.get("services") if agent=="red" or agent=="blue" else [],
            "security_level": nd.get("security_level") if agent=="blue" else None,
            "compromised": nd.get("compromised", False)
        })
    return {"nodes": nodes}
