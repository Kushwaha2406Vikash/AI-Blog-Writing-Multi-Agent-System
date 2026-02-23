from langgraph.graph import StateGraph, START, END 
from core.state import State 
from node.Router import router_node,route_next 
from node.Research import research_node 
from node.Orchestrator import orchestrator_node ,fanout
from node.worker import worker_node 
from node.Reducer import reducer_node
from langsmith import traceable


@traceable(name="graph_node")
def create_app() -> any:
    """
    Builds and returns the compiled LangGraph application.
    """
    g = StateGraph(State)

    g.add_node("router", router_node)
    g.add_node("research", research_node)
    g.add_node("orchestrator", orchestrator_node)
    g.add_node("worker", worker_node)
    g.add_node("reducer", reducer_node)

    g.add_edge(START, "router")
    g.add_conditional_edges("router", route_next, {"research": "research", "orchestrator": "orchestrator"})
    g.add_edge("research", "orchestrator")

    g.add_conditional_edges("orchestrator", fanout, ["worker"])
    g.add_edge("worker", "reducer")
    g.add_edge("reducer", END)

    return g.compile()
