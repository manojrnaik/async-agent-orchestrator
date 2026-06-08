# project/models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class SubTask(BaseModel):
    task_id: str = Field(..., description="Unique identifier for the sub-task")
    agent_type: str = Field(..., description="Type of specialized agent needed: RISK, GROWTH, or LIQUIDITY")
    payload: str = Field(..., description="Specific instructions for this agent")

class RoutingPlan(BaseModel):
    rationale: str = Field(..., description="The high-level strategy for breakdown")
    tasks: List[SubTask] = Field(..., max_length=5)

class AgentOutput(BaseModel):
    task_id: str
    success: bool
    data: str
    tokens_used: int
    error_message: Optional[str] = None

class EvaluationResult(BaseModel):
    is_valid: bool = Field(..., description="True if output passes quality and structural checks")
    critique: Optional[str] = Field(None, description="Detailed actionable feedback if validation fails")
    re_route_required: bool = Field(False, description="Flag indicating if the router needs to re-run")
