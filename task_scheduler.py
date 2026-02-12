"""
Task Scheduler - Manages task execution over time

Like OpenClaw's scheduler but with Bolor Brain reasoning for prioritization
"""

from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class ScheduledTask:
    """A task in the schedule"""
    id: str
    description: str
    type: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1-10, higher = more important
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    dependencies: List[str] = field(default_factory=list)  # Task IDs that must complete first
    status: TaskStatus = TaskStatus.PENDING
    strategy: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Execution tracking
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    actual_duration: Optional[timedelta] = None
    error: Optional[str] = None
    result: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "description": self.description,
            "type": self.type,
            "context": self.context,
            "priority": self.priority,
            "status": self.status.value,
            "dependencies": self.dependencies
        }


class TaskScheduler:
    """
    Schedules and manages task execution over time

    Features:
    - Dependency management
    - Priority-based scheduling
    - Bolor Brain integration for intelligent prioritization
    - Progress tracking
    """

    def __init__(self, brain_client=None):
        """
        Initialize task scheduler

        Args:
            brain_client: Bolor Brain client for intelligent decisions
        """
        self.brain = brain_client
        self.tasks: List[ScheduledTask] = []
        self.completed_tasks: List[ScheduledTask] = []
        self.failed_tasks: List[ScheduledTask] = []

    def create_schedule(self, task_clusters: List[Any]) -> 'TaskSchedule':
        """
        Create execution schedule from task clusters

        Args:
            task_clusters: Task clusters from NSAF decomposition

        Returns:
            TaskSchedule with optimized task ordering
        """
        scheduled_tasks = []

        for i, cluster in enumerate(task_clusters):
            # Estimate duration using Bolor Brain (if available)
            estimated_duration = self._estimate_duration(cluster)

            # Determine priority
            priority = self._calculate_priority(cluster)

            # Create scheduled task
            task = ScheduledTask(
                id=f"task_{i+1}",
                description=getattr(cluster, 'description', str(cluster)),
                type=getattr(cluster, 'type', 'general'),
                context=getattr(cluster, 'context', {}),
                priority=priority,
                estimated_duration=estimated_duration,
                dependencies=getattr(cluster, 'dependencies', []),
                strategy=getattr(cluster, 'strategy', None),
                tags=getattr(cluster, 'tags', [])
            )

            scheduled_tasks.append(task)

        self.tasks = scheduled_tasks

        # Optimize schedule
        self._optimize_schedule()

        return TaskSchedule(
            tasks=self.tasks,
            estimated_duration=self._calculate_total_duration()
        )

    def _estimate_duration(self, cluster: Any) -> timedelta:
        """
        Estimate task duration using Bolor Brain case-based reasoning

        Looks for similar past tasks and uses their duration
        """
        if not self.brain:
            # Default estimate
            return timedelta(minutes=10)

        # In production, would use Bolor Brain's case-based reasoner:
        # similar_cases = self.brain.reason_case_based({
        #     "query": f"How long does {cluster.description} take?",
        #     "retrieve_top_k": 5
        # })
        #
        # if similar_cases:
        #     avg_duration = mean([c.outcome['duration'] for c in similar_cases])
        #     return timedelta(seconds=avg_duration)

        # For now, use simple heuristic
        description = str(cluster).lower()

        if any(word in description for word in ['read', 'analyze', 'review']):
            return timedelta(minutes=5)
        elif any(word in description for word in ['write', 'create', 'generate']):
            return timedelta(minutes=15)
        elif any(word in description for word in ['deploy', 'test', 'verify']):
            return timedelta(minutes=20)
        else:
            return timedelta(minutes=10)

    def _calculate_priority(self, cluster: Any) -> int:
        """
        Calculate task priority (1-10)

        Uses Bolor Brain to reason about importance
        """
        # Check if priority already set
        if hasattr(cluster, 'priority'):
            return cluster.priority

        # Default priority
        priority = 5

        # Boost priority for certain types
        description = str(cluster).lower()

        if any(word in description for word in ['critical', 'urgent', 'blocker']):
            priority = 9
        elif any(word in description for word in ['important', 'core']):
            priority = 7
        elif any(word in description for word in ['nice-to-have', 'optional']):
            priority = 3

        return priority

    def _optimize_schedule(self):
        """
        Optimize task ordering considering:
        - Dependencies (must respect)
        - Priority (prefer higher)
        - Parallelization opportunities
        """
        # Topological sort for dependency ordering
        self.tasks = self._topological_sort(self.tasks)

    def _topological_sort(self, tasks: List[ScheduledTask]) -> List[ScheduledTask]:
        """
        Sort tasks respecting dependencies

        Tasks with no dependencies come first
        """
        # Create dependency graph
        task_map = {task.id: task for task in tasks}
        in_degree = {task.id: 0 for task in tasks}

        for task in tasks:
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[task.id] += 1

        # Kahn's algorithm for topological sort
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        sorted_tasks = []

        while queue:
            # Among ready tasks, pick highest priority
            queue.sort(key=lambda tid: task_map[tid].priority, reverse=True)
            current_id = queue.pop(0)
            current_task = task_map[current_id]
            sorted_tasks.append(current_task)

            # Update dependencies
            for task in tasks:
                if current_id in task.dependencies:
                    in_degree[task.id] -= 1
                    if in_degree[task.id] == 0:
                        queue.append(task.id)

        return sorted_tasks

    def _calculate_total_duration(self) -> timedelta:
        """Calculate total estimated duration"""
        # Simplified: sum all durations (assumes sequential)
        # In reality, could parallelize independent tasks
        return sum((task.estimated_duration for task in self.tasks), timedelta())

    def get_next_task(self) -> Optional[ScheduledTask]:
        """
        Get next task to execute

        Returns:
            Next task that is ready (dependencies met), or None
        """
        ready_tasks = [task for task in self.tasks
                      if task.status == TaskStatus.PENDING and self._dependencies_met(task)]

        if not ready_tasks:
            return None

        # If Bolor Brain available, use it to decide priority
        if self.brain and len(ready_tasks) > 1:
            return self._brain_select_task(ready_tasks)

        # Otherwise, pick highest priority
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        next_task = ready_tasks[0]
        next_task.status = TaskStatus.RUNNING
        next_task.start_time = datetime.now()

        return next_task

    def _dependencies_met(self, task: ScheduledTask) -> bool:
        """Check if all dependencies are completed"""
        if not task.dependencies:
            return True

        completed_ids = {t.id for t in self.completed_tasks}
        return all(dep in completed_ids for dep in task.dependencies)

    def _brain_select_task(self, ready_tasks: List[ScheduledTask]) -> ScheduledTask:
        """
        Use Bolor Brain to intelligently select next task

        Considers: priority, context, current state, past performance
        """
        # In production, would use Bolor Brain:
        # decision = self.brain.reason_hybrid({
        #     "query": "Which task should I do next?",
        #     "context": {
        #         "tasks": [t.to_dict() for t in ready_tasks],
        #         "current_state": self.get_progress()
        #     }
        # })
        # return decision.recommended_task

        # For now, simple priority sort
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        next_task = ready_tasks[0]
        next_task.status = TaskStatus.RUNNING
        next_task.start_time = datetime.now()

        return next_task

    def mark_complete(self, task: ScheduledTask):
        """Mark task as completed"""
        task.status = TaskStatus.COMPLETED
        task.end_time = datetime.now()
        task.actual_duration = task.end_time - task.start_time

        # Move to completed list
        self.tasks.remove(task)
        self.completed_tasks.append(task)

    def mark_failed(self, task: ScheduledTask, error: str):
        """Mark task as failed"""
        task.status = TaskStatus.FAILED
        task.end_time = datetime.now()
        task.error = error

        # Move to failed list
        self.tasks.remove(task)
        self.failed_tasks.append(task)

    def is_complete(self) -> bool:
        """Check if all tasks are complete"""
        return len(self.tasks) == 0

    def get_progress(self) -> float:
        """Get completion progress (0.0 to 1.0)"""
        total = len(self.tasks) + len(self.completed_tasks) + len(self.failed_tasks)
        if total == 0:
            return 1.0
        return len(self.completed_tasks) / total

    def update_strategy(self, improved_strategy: Any):
        """
        Update remaining tasks with improved strategy from NSAF evolution

        Args:
            improved_strategy: Evolved strategy from NSAF
        """
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                task.strategy = improved_strategy
                print(f"  📈 Updated strategy for: {task.description}")

    def get_stats(self) -> Dict[str, Any]:
        """Get schedule statistics"""
        return {
            "total": len(self.tasks) + len(self.completed_tasks) + len(self.failed_tasks),
            "pending": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
            "running": len([t for t in self.tasks if t.status == TaskStatus.RUNNING]),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "progress": self.get_progress(),
            "estimated_remaining": self._calculate_total_duration()
        }


@dataclass
class TaskSchedule:
    """Complete execution schedule"""
    tasks: List[ScheduledTask]
    estimated_duration: timedelta
    created_at: datetime = field(default_factory=datetime.now)

    def __str__(self):
        return f"TaskSchedule({len(self.tasks)} tasks, {self.estimated_duration})"


# Example usage
if __name__ == "__main__":
    # Create mock task clusters
    @dataclass
    class MockCluster:
        description: str
        type: str
        priority: int = 5
        dependencies: List[str] = field(default_factory=list)

    clusters = [
        MockCluster("Read project codebase", "read", 8, []),
        MockCluster("Generate architecture docs", "write", 7, ["task_1"]),
        MockCluster("Create API reference", "write", 6, ["task_1"]),
        MockCluster("Write usage examples", "write", 5, ["task_2", "task_3"]),
        MockCluster("Generate diagrams", "create", 4, ["task_2"]),
    ]

    scheduler = TaskScheduler()
    schedule = scheduler.create_schedule(clusters)

    print(f"Schedule created: {schedule}")
    print(f"\nTask execution order:")
    for i, task in enumerate(schedule.tasks, 1):
        print(f"{i}. {task.description} (priority: {task.priority})")

    # Simulate execution
    print(f"\n--- Simulating Execution ---\n")
    while not scheduler.is_complete():
        task = scheduler.get_next_task()
        if task:
            print(f"Executing: {task.description}")
            scheduler.mark_complete(task)
            print(f"Progress: {scheduler.get_progress():.1%}\n")

    print(f"✅ All tasks complete!")
    print(f"Stats: {scheduler.get_stats()}")
