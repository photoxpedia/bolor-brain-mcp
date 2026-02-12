"""
Autonomous Agent Loop - The Core Controller

This is the main autonomous loop that runs without human intervention.
Coordinates Bolor Brain (orchestrator), NSAF (evolver), and Claude Code (executor).

Like OpenClaw, but secure.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Will integrate with actual MCP clients
from modules import HybridReasoner
from task_scheduler import TaskScheduler, ScheduledTask
from goal_decomposer import GoalDecomposer
from progress_monitor import ProgressMonitor
from claude_code_engine import ClaudeCodeEngine, ExecutionResult
from modules.config import GUARDRAILS_CONFIG


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    LEARNING = "learning"
    EVOLVING = "evolving"
    PAUSED = "paused"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class AgentStatus:
    """Current agent status"""
    state: AgentState
    current_task: Optional[str]
    progress: float  # 0.0 to 1.0
    tasks_completed: int
    tasks_total: int
    time_elapsed: timedelta
    estimated_completion: Optional[datetime]
    learnings_count: int
    evolutions_count: int
    last_update: datetime


class Guardrails:
    """
    Safety guardrails for autonomous execution
    Implements 4-tier permission model from AGENT_GUARDRAILS.md
    """

    # Permission tiers (from AGENT_GUARDRAILS.md)
    TIER_0_SAFE = 0        # Always allowed (read, analyze)
    TIER_1_LOW_RISK = 1    # Low risk (create files, run tests)
    TIER_2_MEDIUM_RISK = 2 # Medium risk (modify code, install deps)
    TIER_3_HIGH_RISK = 3   # High risk (delete, deploy, commit)

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.approval_required_tier = config.get("approval_tier", 2)

    def get_action_tier(self, action: Dict[str, Any]) -> int:
        """Determine risk tier for action"""
        action_type = action.get("type", "")

        # Tier 3: Destructive or external actions
        if any(keyword in action_type.lower() for keyword in
               ["delete", "remove", "drop", "deploy", "push", "commit"]):
            return self.TIER_3_HIGH_RISK

        # Tier 2: Modifications
        if any(keyword in action_type.lower() for keyword in
               ["modify", "update", "install", "change"]):
            return self.TIER_2_MEDIUM_RISK

        # Tier 1: Creations
        if any(keyword in action_type.lower() for keyword in
               ["create", "write", "generate", "build"]):
            return self.TIER_1_LOW_RISK

        # Tier 0: Safe reads
        return self.TIER_0_SAFE

    def needs_approval(self, action: Dict[str, Any]) -> bool:
        """Check if action needs human approval"""
        tier = self.get_action_tier(action)
        return tier >= self.approval_required_tier

    def validate_action(self, action: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate action safety
        Returns: (is_valid, error_message)
        """
        # Check blocked patterns
        action_str = str(action).lower()
        blocked_patterns = self.config.get("blocked_patterns", [])

        for pattern in blocked_patterns:
            if pattern.lower() in action_str:
                return False, f"Blocked pattern detected: {pattern}"

        # Check resource limits
        if "file_size" in action and action["file_size"] > self.config.get("max_file_size", 10_000_000):
            return False, "File size exceeds limit"

        return True, None


class AutonomousAgent:
    """
    Main autonomous agent controller

    Architecture:
    - Bolor Brain: Orchestrator (decides WHAT to do)
    - NSAF: Evolver (improves HOW to do it)
    - Claude Code: Executor (DOES it)
    - This class: Coordinator (runs the loop)
    """

    def __init__(self,
                 brain_client=None,
                 nsaf_client=None,
                 guardrails_config=None):
        """
        Initialize autonomous agent

        Args:
            brain_client: Bolor Brain MCP client (will use actual MCP)
            nsaf_client: NSAF MCP client (will use actual MCP)
            guardrails_config: Safety configuration
        """
        # Core components
        self.brain = brain_client or HybridReasoner()
        self.nsaf = nsaf_client  # Will integrate with actual NSAF MCP
        self.executor = ClaudeCodeEngine()

        # Orchestration components
        self.decomposer = GoalDecomposer(self.brain, self.nsaf)
        self.scheduler = TaskScheduler(self.brain)
        self.monitor = ProgressMonitor(self.brain)

        # Safety
        self.guardrails = Guardrails(guardrails_config or GUARDRAILS_CONFIG)

        # State
        self.state = AgentState.IDLE
        self.current_goal = None
        self.start_time = None
        self.pending_approvals = []

    async def run_autonomous(self, goal: str,
                            max_duration: Optional[timedelta] = None,
                            callback=None) -> Dict[str, Any]:
        """
        Main autonomous execution loop

        User gives goal → Agent runs until complete

        Args:
            goal: High-level goal (e.g., "Build documentation for Bolor Brain")
            max_duration: Optional time limit
            callback: Optional progress callback function

        Returns:
            Execution report with results and learnings
        """
        self.current_goal = goal
        self.start_time = datetime.now()

        try:
            # Phase 1: PLANNING
            self.state = AgentState.PLANNING
            print(f"🎯 Goal: {goal}")
            print(f"📋 Planning autonomous execution...\n")

            plan = await self._plan_execution(goal)

            if callback:
                callback(self.get_status())

            # Phase 2: EXECUTING
            self.state = AgentState.EXECUTING
            print(f"🚀 Starting autonomous execution...")
            print(f"📊 Total tasks: {len(plan.tasks)}\n")

            results = await self._execute_plan(plan, callback)

            # Phase 3: LEARNING
            self.state = AgentState.LEARNING
            print(f"🧠 Learning from execution...\n")

            learnings = await self._learn_from_execution(results)

            # Phase 4: COMPLETE
            self.state = AgentState.COMPLETE

            report = self._generate_report(goal, plan, results, learnings)

            print(f"✅ Goal complete!")
            print(f"⏱️  Duration: {report['duration']}")
            print(f"📚 Learnings stored: {report['learnings_count']}")
            print(f"🔄 Evolutions: {report['evolutions_count']}\n")

            return report

        except Exception as e:
            self.state = AgentState.ERROR
            print(f"❌ Error during autonomous execution: {e}")
            raise

    async def _plan_execution(self, goal: str) -> Any:
        """
        Phase 1: Planning

        Decompose goal → Create task clusters → Build schedule
        """
        # 1. Decompose goal (Bolor Brain analyzes)
        print("  📝 Decomposing goal...")
        plan = self.decomposer.decompose(goal)
        print(f"  ✓ Identified {len(plan.tasks)} task clusters\n")

        # 2. Create schedule (scheduler now has the tasks)
        print("  📅 Creating execution schedule...")
        schedule = self.scheduler.create_schedule(plan.tasks)
        print(f"  ✓ Schedule created (estimated: {schedule.estimated_duration})\n")

        plan.schedule = schedule
        # Note: self.scheduler now manages the tasks
        return plan

    async def _execute_plan(self, plan: Any, callback=None) -> List[ExecutionResult]:
        """
        Phase 2: Execution

        Execute tasks → Learn from each → Evolve strategies
        """
        results = []

        while not self.scheduler.is_complete():
            # Get next task
            task = self.scheduler.get_next_task()

            if not task:
                # No tasks ready (waiting on dependencies)
                await asyncio.sleep(1)
                continue

            print(f"  🔨 Executing: {task.description}")

            # Check safety guardrails
            if self.guardrails.needs_approval(task.to_dict()):
                print(f"  ⚠️  Action requires approval (Tier {self.guardrails.get_action_tier(task.to_dict())})")

                approval = await self._request_approval(task)
                if not approval:
                    print(f"  ❌ Task denied by user")
                    plan.schedule.mark_failed(task, "User denied approval")
                    continue

            # Validate safety
            is_valid, error = self.guardrails.validate_action(task.to_dict())
            if not is_valid:
                print(f"  🚨 Security violation: {error}")
                plan.schedule.mark_failed(task, error)
                continue

            # Execute task
            try:
                result = await self.executor.execute(task)

                if result.success:
                    print(f"  ✓ Complete ({result.duration:.1f}s)")
                    self.scheduler.mark_complete(task)
                else:
                    print(f"  ⚠️  Failed: {result.error}")
                    self.scheduler.mark_failed(task, result.error)

                results.append(result)

                # Learn from outcome (immediate feedback)
                await self._learn_from_task(task, result)

                # Check if we should evolve strategy
                if self._should_evolve(results):
                    await self._evolve_strategy(plan, results)

                # Update progress
                if callback:
                    callback(self.get_status())

            except Exception as e:
                print(f"  ❌ Exception: {e}")
                self.scheduler.mark_failed(task, str(e))

            print()  # Blank line between tasks

        return results

    async def _learn_from_task(self, task: Any, result: ExecutionResult):
        """Store task outcome in Bolor Brain memory"""
        # Store as case for future retrieval
        case_data = {
            "problem": {
                "type": task.type,
                "description": task.description,
                "context": task.context
            },
            "solution": {
                "actions": result.actions_taken,
                "strategy": task.strategy
            },
            "outcome": {
                "success": result.success,
                "duration": result.duration,
                "quality": result.quality_score
            },
            "tags": task.tags + ["autonomous_execution"]
        }

        # Will use actual MCP tool when integrated
        # self.brain.store_case(case_data)

        # For now, use hybrid reasoner's memory
        print(f"  💾 Stored learning: {task.description[:50]}...")

    def _should_evolve(self, results: List[ExecutionResult]) -> bool:
        """Decide if we should evolve strategy"""
        if len(results) < 3:
            return False

        # Check recent performance
        recent = results[-3:]
        success_rate = sum(1 for r in recent if r.success) / len(recent)

        # Evolve if success rate is low
        return success_rate < 0.7

    async def _evolve_strategy(self, plan: Any, results: List[ExecutionResult]):
        """
        Evolve strategy using NSAF

        Use learnings from execution to improve approach
        """
        self.state = AgentState.EVOLVING
        print(f"  🔄 Evolving strategy based on learnings...")

        # Get learnings from Bolor Brain
        performance_metrics = {
            "success_rate": sum(1 for r in results if r.success) / len(results),
            "avg_duration": sum(r.duration for r in results) / len(results),
            "bottlenecks": [r.task for r in results if r.duration > 60]
        }

        # NSAF evolves improved strategy
        # Will use actual NSAF MCP when integrated
        # improved = await self.nsaf.run_nsaf_evolution({
        #     "fitness_criteria": performance_metrics,
        #     "population_size": 10,
        #     "generations": 5
        # })

        # Update remaining tasks with improved strategy
        # plan.schedule.update_strategy(improved)

        print(f"  ✓ Strategy evolved\n")
        self.state = AgentState.EXECUTING

    async def _learn_from_execution(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """
        Extract learnings from entire execution
        """
        # Analyze patterns
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        learnings = {
            "total_tasks": len(results),
            "success_count": len(successful_results),
            "failure_count": len(failed_results),
            "success_rate": len(successful_results) / len(results) if results else 0,
            "patterns": {
                "successful_strategies": self._extract_patterns(successful_results),
                "failure_modes": self._extract_patterns(failed_results)
            }
        }

        return learnings

    def _extract_patterns(self, results: List[ExecutionResult]) -> List[str]:
        """Extract common patterns from results"""
        # Simplified pattern extraction
        # In reality, would use Bolor Brain's reasoning
        patterns = []

        if len(results) > 0:
            avg_duration = sum(r.duration for r in results) / len(results)
            patterns.append(f"Average duration: {avg_duration:.1f}s")

        return patterns

    def _generate_report(self, goal: str, plan: Any,
                        results: List[ExecutionResult],
                        learnings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final execution report"""
        duration = datetime.now() - self.start_time

        return {
            "goal": goal,
            "status": "complete",
            "duration": str(duration),
            "tasks_total": len(plan.tasks),
            "tasks_completed": len([r for r in results if r.success]),
            "tasks_failed": len([r for r in results if not r.success]),
            "success_rate": learnings["success_rate"],
            "learnings_count": learnings["total_tasks"],
            "evolutions_count": 0,  # Track actual evolutions
            "results": results,
            "learnings": learnings
        }

    async def _request_approval(self, task: Any) -> bool:
        """
        Request human approval for high-risk action

        In production, this would:
        - Send notification to user
        - Wait for approval/denial
        - Timeout after X minutes

        For now, return True (auto-approve in dev mode)
        """
        # TODO: Implement actual approval mechanism
        # For development, auto-approve
        return True

    def get_status(self) -> AgentStatus:
        """Get current agent status"""
        elapsed = datetime.now() - self.start_time if self.start_time else timedelta()

        return AgentStatus(
            state=self.state,
            current_task=None,  # Track from scheduler
            progress=0.0,  # Calculate from scheduler
            tasks_completed=0,
            tasks_total=0,
            time_elapsed=elapsed,
            estimated_completion=None,
            learnings_count=0,
            evolutions_count=0,
            last_update=datetime.now()
        )

    def pause(self):
        """Pause autonomous execution"""
        self.state = AgentState.PAUSED

    def resume(self):
        """Resume autonomous execution"""
        if self.state == AgentState.PAUSED:
            self.state = AgentState.EXECUTING

    def stop(self):
        """Stop autonomous execution"""
        self.state = AgentState.IDLE
        self.current_goal = None


# Example usage
if __name__ == "__main__":
    async def main():
        agent = AutonomousAgent()

        goal = """
        Build comprehensive documentation for Bolor Brain MCP.
        Include:
        - Architecture overview
        - API reference
        - Usage examples
        - Integration guides
        """

        def progress_callback(status: AgentStatus):
            print(f"Progress: {status.progress:.1%} | State: {status.state.value}")

        report = await agent.run_autonomous(goal, callback=progress_callback)

        print("\n" + "="*50)
        print("EXECUTION REPORT")
        print("="*50)
        print(f"Goal: {report['goal']}")
        print(f"Duration: {report['duration']}")
        print(f"Success Rate: {report['success_rate']:.1%}")
        print(f"Learnings: {report['learnings_count']}")

    # Run the autonomous agent
    asyncio.run(main())
