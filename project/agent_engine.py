# project/agent_engine.py
import asyncio
import uuid
import logging
from typing import List
from project.models import RoutingPlan, SubTask, AgentOutput, EvaluationResult

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
logger = logging.getLogger("ProductionAgentEngine")

class TokenBudgetExceededException(Exception):
    """Raised when mid-flight token consumption violates business logic safety caps."""
    pass

class AsyncAgentEngine:
    def __init__(self, token_budget_cap: int = 15000):
        self.token_budget_cap = token_budget_cap
        self.cumulative_tokens = 0
        self.max_retries = 2

    async def _mock_llm_call_span(self, prompt: str, schema: type, simulated_cost: int) -> tuple:
        """Simulates an asynchronous tracer-monitored call to an upstream LLM provider."""
        # Simulated OpenTelemetry / Langfuse Tracing Context Initialization
        logger.info(f"Tracing Span Start: open_llm_call for schema {schema.__name__}")
        await asyncio.sleep(0.1) # Simulate network I/O
        
        self.cumulative_tokens += simulated_cost
        if self.cumulative_tokens > self.token_budget_cap:
            raise TokenBudgetExceededException(
                f"Hard stop: Token consumption reached {self.cumulative_tokens}, exceeding cap of {self.token_budget_cap}"
            )
            
        logger.info("Tracing Span End: open_llm_call success")
        return "".name, simulated_cost

    async def route_input(self, user_query: str, feedback: Optional[str] = None) -> RoutingPlan:
        """Analyzes incoming prompt and dynamically fans out sub-tasks."""
        logger.info(f"Routing logic initialized. Feedback loop active: {feedback is not None}")
        # Simulating robust Pydantic structural generation from LLM
        await self._mock_llm_call_span(user_query, RoutingPlan, simulated_cost=1200)
        
        return RoutingPlan(
            rationale="Parallel extraction of multi-dimensional financial factors.",
            tasks=[
                SubTask(task_id="t-1", agent_type="RISK", payload=f"Analyze risk boundaries for: {user_query}"),
                SubTask(task_id="t-2", agent_type="GROWTH", payload=f"Analyze upside metrics for: {user_query}")
            ]
        )

    async def execute_specialized_agent(self, task: SubTask) -> AgentOutput:
        """Executes targeted domain analytical operations with asynchronous isolation."""
        try:
            logger.info(f"Worker spinning up for task {task.task_id} [{task.agent_type}]")
            # Simulating specific network latency per sub-agent
            if task.agent_type == "RISK":
                await asyncio.sleep(0.2)
                _, cost = await self._mock_llm_call_span(task.payload, AgentOutput, simulated_cost=3500)
                return AgentOutput(task_id=task.task_id, success=True, data="Risk exposure is quantified at alpha=0.04.", tokens_used=cost)
            elif task.agent_type == "GROWTH":
                await asyncio.sleep(0.1)
                _, cost = await self._mock_llm_call_span(task.payload, AgentOutput, simulated_cost=4200)
                return AgentOutput(task_id=task.task_id, success=True, data="CAGR forecast maintains a steady 14.2% vector.", tokens_used=cost)
            else:
                return AgentOutput(task_id=task.task_id, success=False, data="", tokens_used=0, error_message="Unknown worker type")
        except Exception as e:
            logger.error(f"Execution failure on worker {task.task_id}: {str(e)}")
            return AgentOutput(task_id=task.task_id, success=False, data="", tokens_used=0, error_message=str(e))

    async def evaluate_outputs(self, outputs: List[AgentOutput]) -> EvaluationResult:
        """Evaluates output accuracy and formats actionable critique loops."""
        await self._mock_llm_call_span(str(outputs), EvaluationResult, simulated_cost=800)
        
        for out in outputs:
            if not out.success:
                return EvaluationResult(is_valid=False, critique=f"Task {out.task_id} failed: {out.error_message}", re_route_required=True)
            if "alpha" in out.data and "0.04" in out.data:
                # Mocking a business criteria rule failure to trigger exactly one clean retry loop
                return EvaluationResult(is_valid=False, critique="Risk assessment is too broad. Specify asset beta values.", re_route_required=False)
                
        return EvaluationResult(is_valid=True)

    async def orchestrate_workflow(self, query: str) -> str:
        """Main non-blocking execution cycle with budget protection and self-correction."""
        retry_count = 0
        current_feedback = None
        
        while retry_count <= self.max_retries:
            try:
                logger.info(f"Orchestration cycle active. Step iteration: {retry_count}")
                # 1. Routing phase
                plan = await self.route_input(query, feedback=current_feedback)
                
                # 2. Parallel fan-out execution execution step
                tasks = [self.execute_specialized_agent(t) for t in plan.tasks]
                results: List[AgentOutput] = await asyncio.gather(*tasks)
                
                # 3. Dynamic evaluation check
                evaluation = await self.evaluate_outputs(results)
                
                if evaluation.is_valid:
                    logger.info("Workflow execution verified by Evaluator.")
                    return f"Verified Output: {'; '.join([r.data for r in results])}"
                
                logger.warning(f"Evaluator rejected output. Critique provided: {evaluation.critique}")
                current_feedback = evaluation.critique
                retry_count += 1
                
            except TokenBudgetExceededException as budget_err:
                logger.critical(f"Circuit breaker tripped: {str(budget_err)}")
                return "Fallback Degraded Output: Processing halted due to strict token budget guardrails."
            except Exception as system_err:
                logger.critical(f"Unhandled pipeline exception: {str(system_err)}")
                return f"Fallback Error State: {str(system_err)}"

        return "Fallback Degraded Output: Max orchestration retry thresholds breached without validation clearance."

# Execution block to prove run stability
if __name__ == "__main__":
    engine = AsyncAgentEngine(token_budget_cap=20000)
    final_payload = asyncio.run(engine.orchestrate_workflow("Analyze Q3 Tech Portfolio Exposure"))
    print(f"\nExecution Result Buffer:\n{final_payload}")
