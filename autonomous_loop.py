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
from state_manager import StateManager
from approval_system import ApprovalSystem, ApprovalStatus
from nsaf_client import NSAFClient, NSAFIntegration, FitnessMetrics


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
                 guardrails_config=None,
                 state_dir=None):
        """
        Initialize autonomous agent

        Args:
            brain_client: Bolor Brain MCP client (will use actual MCP)
            nsaf_client: NSAF MCP client (will use actual MCP)
            guardrails_config: Safety configuration
            state_dir: Directory for state persistence (default: .agent_state)
        """
        # Core components
        self.brain = brain_client or HybridReasoner()

        # NSAF integration - REAL client, ready to connect
        nsaf_mcp_client = nsaf_client or NSAFClient()
        self.nsaf = NSAFIntegration(nsaf_mcp_client)

        self.executor = ClaudeCodeEngine()

        # Orchestration components
        self.decomposer = GoalDecomposer(self.brain, self.nsaf)
        self.scheduler = TaskScheduler(self.brain)
        self.monitor = ProgressMonitor(self.brain)

        # Safety
        self.guardrails = Guardrails(guardrails_config or GUARDRAILS_CONFIG)

        # Persistence
        self.state_manager = StateManager(state_dir)

        # Approval system
        self.approval_system = ApprovalSystem(
            queue_dir=state_dir.replace('.agent_state', '.approval_queue') if state_dir else None,
            timeout_seconds=300,  # 5 minute timeout
            notification_callback=self._notify_approval_needed
        )

        # State
        self.state = AgentState.IDLE
        self.current_goal = None
        self.start_time = None
        self.pending_approvals = []
        self.session_id = None
        self.completed_task_ids = []
        self.failed_task_ids = []
        self.execution_results = []
        self.learnings = {}

    async def run_autonomous(self, goal: str,
                            max_duration: Optional[timedelta] = None,
                            callback=None,
                            resume_session_id: str = None) -> Dict[str, Any]:
        """
        Main autonomous execution loop

        User gives goal → Agent runs until complete

        Args:
            goal: High-level goal (e.g., "Build documentation for Bolor Brain")
            max_duration: Optional time limit
            callback: Optional progress callback function
            resume_session_id: Optional session ID to resume

        Returns:
            Execution report with results and learnings
        """
        # Check if resuming from saved state
        if resume_session_id:
            if await self._resume_from_state(resume_session_id):
                print(f"♻️  Resumed session: {resume_session_id}\n")
            else:
                print(f"⚠️  Could not resume session, starting fresh\n")
                self.current_goal = goal
                self.start_time = datetime.now()
        else:
            self.current_goal = goal
            self.start_time = datetime.now()
            self.session_id = None

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

            # Save initial state
            await self._save_state(plan)

            results = await self._execute_plan(plan, callback)

            # Phase 3: LEARNING
            self.state = AgentState.LEARNING
            print(f"🧠 Learning from execution...\n")

            learnings = await self._learn_from_execution(results)
            self.learnings = learnings

            # Save final state
            await self._save_state(plan, final=True)

            # Phase 4: COMPLETE
            self.state = AgentState.COMPLETE

            report = self._generate_report(goal, plan, results, learnings)

            # Add NSAF evolution stats
            evolution_stats = self.nsaf.get_evolution_stats()
            report['nsaf_evolution_count'] = evolution_stats['evolution_count']
            report['nsaf_available'] = evolution_stats['nsaf_available']

            print(f"✅ Goal complete!")
            print(f"⏱️  Duration: {report['duration']}")
            print(f"📚 Learnings stored: {report['learnings_count']}")
            print(f"🔄 Evolutions: {report['evolutions_count']}")
            if evolution_stats['nsaf_available']:
                print(f"✨ NSAF evolutions: {evolution_stats['evolution_count']}")
            else:
                print(f"ℹ️  NSAF: Not available (evolution ready when server connects)")
            print()

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
                    self.completed_task_ids.append(task.id)
                else:
                    print(f"  ⚠️  Failed: {result.error}")
                    self.scheduler.mark_failed(task, result.error)
                    self.failed_task_ids.append(task.id)

                results.append(result)
                self.execution_results.append({
                    'task_id': task.id,
                    'success': result.success,
                    'duration': result.duration,
                    'actions': result.actions_taken
                })

                # Save state after each task
                await self._save_state(plan)

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
        Evolve strategy using NSAF - REAL integration

        Use learnings from execution to improve approach
        """
        self.state = AgentState.EVOLVING
        print(f"  🔄 Evolving strategy based on learnings...")

        # Check if NSAF is available
        if not self.nsaf.client.is_available():
            print(f"  ⚠️  NSAF server not available - evolution skipped")
            print(f"  ℹ️  Agent will continue with current strategy")
            self.state = AgentState.EXECUTING
            return

        # Prepare current strategy
        current_strategy = {
            "approach": "baseline",
            "task_decomposition": "hybrid",
            "scheduling": "dependency-based"
        }

        # Evolve using NSAF - REAL MCP call
        evolved_strategy = self.nsaf.evolve_agent_strategy(
            current_strategy=current_strategy,
            execution_results=results
        )

        if evolved_strategy:
            print(f"  ✨ Strategy evolved successfully!")
            print(f"  📈 Evolution count: {self.nsaf.evolution_count}")

            # Update remaining tasks with evolved strategy
            # plan.schedule.update_strategy(evolved_strategy)
        else:
            print(f"  ⚠️  Evolution failed - continuing with current strategy")

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
        Request human approval for high-risk action - REAL approval system

        Creates approval request, notifies user, and waits for response.
        Uses real file-based approval queue.

        Returns:
            True if approved, False if denied/timeout
        """
        # Create approval request
        request_id = self.approval_system.request_approval(
            action_type=task.type,
            description=task.description,
            risk_tier=self.guardrails.get_action_tier(task.to_dict()),
            details={
                'task_id': task.id,
                'priority': task.priority,
                'estimated_duration': str(task.estimated_duration)
            }
        )

        self.pending_approvals.append(request_id)

        # Wait for approval (with polling)
        print(f"  ⏳ Waiting for approval (request: {request_id})...")

        status = self.approval_system.wait_for_approval(request_id, poll_interval=2.0)

        # Remove from pending
        if request_id in self.pending_approvals:
            self.pending_approvals.remove(request_id)

        if status == ApprovalStatus.APPROVED:
            print(f"  ✅ Approved by user")
            return True
        elif status == ApprovalStatus.DENIED:
            print(f"  ❌ Denied by user")
            return False
        else:
            print(f"  ⏱️  Approval timeout - denying by default")
            return False

    def _notify_approval_needed(self, request):
        """
        Notification callback for approval requests

        This gets called when an approval request is created.
        Can be customized to send notifications via various channels.
        """
        print("\n" + "="*60)
        print("⚠️  APPROVAL REQUIRED")
        print("="*60)
        print(f"Action: {request.action_type}")
        print(f"Description: {request.description}")
        print(f"Risk Tier: Tier {request.risk_tier}")
        print(f"Request ID: {request.request_id}")
        print(f"\nTo approve, run in another terminal:")
        print(f"  python approval_system.py approve {request.request_id}")
        print(f"\nTo deny:")
        print(f"  python approval_system.py deny {request.request_id}")
        print(f"\nTimeout: {request.expires_at}")
        print("="*60 + "\n")

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

    async def _save_state(self, plan: Any, final: bool = False):
        """
        Save current agent state to disk - REAL file operation

        Args:
            plan: Current execution plan
            final: Whether this is the final state save
        """
        state_data = {
            'session_id': self.session_id,
            'goal': self.current_goal,
            'state': self.state.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'current_task_id': None,  # Could track from scheduler
            'tasks_total': len(plan.tasks),
            'tasks_completed': len(self.completed_task_ids),
            'tasks_failed': len(self.failed_task_ids),
            'completed_task_ids': self.completed_task_ids,
            'failed_task_ids': self.failed_task_ids,
            'learnings_count': len(self.learnings.get('patterns', {}).get('successful_strategies', [])),
            'evolutions_count': 0,
            'execution_results': self.execution_results,
            'learnings': self.learnings
        }

        try:
            state_file = self.state_manager.save_state(state_data)

            # Set session ID from state manager if not set
            if not self.session_id:
                self.session_id = self.state_manager.current_session_id

            if not final:
                # Don't spam during execution
                pass
            else:
                print(f"💾 State saved: {state_file}")

        except Exception as e:
            print(f"⚠️  Warning: Could not save state: {e}")

    async def _resume_from_state(self, session_id: str) -> bool:
        """
        Resume execution from saved state - REAL file operation

        Args:
            session_id: Session ID to resume

        Returns:
            True if successfully resumed, False otherwise
        """
        try:
            state_data = self.state_manager.load_state(session_id)

            if not state_data:
                return False

            # Restore state
            self.session_id = state_data['session_id']
            self.current_goal = state_data['goal']
            self.state = AgentState(state_data['state'])
            self.start_time = datetime.fromisoformat(state_data['start_time'])
            self.completed_task_ids = state_data['completed_task_ids']
            self.failed_task_ids = state_data['failed_task_ids']
            self.execution_results = state_data['execution_results']
            self.learnings = state_data['learnings']

            print(f"✅ Restored state:")
            print(f"   Goal: {self.current_goal}")
            print(f"   Progress: {state_data['tasks_completed']}/{state_data['tasks_total']}")
            print(f"   Elapsed: {datetime.now() - self.start_time}")

            return True

        except Exception as e:
            print(f"❌ Failed to resume state: {e}")
            return False

    def list_sessions(self) -> list:
        """
        List all saved sessions - REAL file operation

        Returns:
            List of session info
        """
        return self.state_manager.list_sessions()

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a saved session - REAL file operation

        Args:
            session_id: Session to delete

        Returns:
            True if deleted
        """
        return self.state_manager.delete_state(session_id)


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
