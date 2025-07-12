# app/agent.py

from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

# --- 1. Define Agent State ---
# This is the data structure that will be passed between nodes in our graph.
class BusinessAnalysisState(TypedDict):
    daily_data: Dict[str, Any]
    previous_day_data: Dict[str, Any]
    calculated_metrics: Dict[str, Any]
    recommendations: Dict[str, Any]


# --- 2. Define Graph Nodes ---
# Each function represents a single step in our agent's process.

def processing_node(state: BusinessAnalysisState) -> BusinessAnalysisState:
    """
    Calculates key business metrics based on the input data.
    This node takes the raw data and transforms it into actionable metrics.
    """
    daily_data = state["daily_data"]
    prev_data = state["previous_day_data"]

    # Safety check to prevent division by zero errors.
    if any(v == 0 for v in [prev_data["revenue"], prev_data["cost"], prev_data["number_of_customers"]]):
        raise ValueError("Previous day's data cannot contain zero values for calculations.")

    # Core metric calculations
    daily_profit = daily_data["revenue"] - daily_data["cost"]
    revenue_change = ((daily_data["revenue"] - prev_data["revenue"]) / prev_data["revenue"]) * 100
    cost_change = ((daily_data["cost"] - prev_data["cost"]) / prev_data["cost"]) * 100
    daily_cac = daily_data["cost"] / daily_data["number_of_customers"]
    prev_cac = prev_data["cost"] / prev_data["number_of_customers"]
    cac_change = ((daily_cac - prev_cac) / prev_cac) * 100

    # Store the results in the state
    calculated_metrics = {
        "daily_profit": daily_profit,
        "profit_status": "Profitable" if daily_profit > 0 else "Loss",
        "revenue_percentage_change": round(revenue_change, 2),
        "cost_percentage_change": round(cost_change, 2),
        "daily_cac": round(daily_cac, 2),
        "cac_percentage_change": round(cac_change, 2)
    }
    return {**state, "calculated_metrics": calculated_metrics}


def recommendation_node(state: BusinessAnalysisState) -> BusinessAnalysisState:
    """
    Generates human-readable warnings and recommendations based on the calculated metrics.
    This node represents the "decision-making" part of the agent.
    """
    metrics = state["calculated_metrics"]
    recs = []
    warnings = []

    # Apply business logic to generate advice.
    if metrics["profit_status"] == "Loss":
        recs.append("Reduce costs or find ways to increase revenue.")
        warnings.append(f"Profit is negative: ${metrics['daily_profit']}.")

    if metrics["cac_percentage_change"] > 20:
        recs.append("Review marketing campaigns as CAC increased significantly.")
        warnings.append(f"CAC increased by {metrics['cac_percentage_change']}% (>20% threshold).")

    if metrics["revenue_percentage_change"] > 10:
        recs.append("Consider increasing advertising budget to capitalize on growth.")

    # Provide a default message if no specific conditions are met.
    if not recs:
        recs.append("Business metrics are stable. Continue monitoring.")

    # Structure the final output for the user.
    final_output = {
        "profit_loss_status": metrics["profit_status"],
        "alerts_or_warnings": warnings,
        "decision_making_recommendations": recs
    }
    return {**state, "recommendations": final_output}


# --- 3. Define the Agent Graph Factory ---
def create_business_agent():
    """
    Builds and compiles the LangGraph agent.
    This function defines the structure and flow of the agent.
    """
    workflow = StateGraph(BusinessAnalysisState)

    # Add the functions as nodes to the graph.
    workflow.add_node("processing", processing_node)
    workflow.add_node("recommendation", recommendation_node)

    # Define the graph's flow of control.
    workflow.set_entry_point("processing")
    workflow.add_edge("processing", "recommendation")
    workflow.add_edge("recommendation", END)

    # Compile the graph into a runnable object.
    return workflow.compile()


# --- 4. Create the 'graph' Variable ---
# This is the crucial line that makes the agent compatible with the LangGraph CLI.
# The `langgraph.json` file specifically looks for a variable named 'graph' in this file.
# We call our factory function to create the agent and assign it to this variable.
graph = create_business_agent()