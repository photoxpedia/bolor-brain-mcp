"""
Progress Monitor - Agent self-awareness and progress tracking
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class Checkpoint:
    """Progress checkpoint"""
    timestamp: datetime
    progress: float
    tasks_completed: int
    current_task: str
    notes: str


class ProgressMonitor:
    """Monitors agent's own progress - self-aware execution"""

    def __init__(self, brain_client=None):
        self.brain = brain_client
        self.start_time = None
        self.checkpoints: List[Checkpoint] = []
        self.planned_milestones = []

    def start(self, goal: str, total_tasks: int):
        """Start monitoring"""
        self.start_time = datetime.now()
        self.goal = goal
        self.total_tasks = total_tasks

    def checkpoint(self, tasks_completed: int, current_task: str, notes: str = ""):
        """Record progress checkpoint"""
        progress = tasks_completed / self.total_tasks if self.total_tasks > 0 else 0

        cp = Checkpoint(
            timestamp=datetime.now(),
            progress=progress,
            tasks_completed=tasks_completed,
            current_task=current_task,
            notes=notes
        )

        self.checkpoints.append(cp)

    def check_progress(self, current_state: Dict[str, Any]) -> str:
        """
        Agent checks its own progress

        Returns: "on_track", "ahead", "behind", or adjustment recommendations
        """
        if not self.checkpoints:
            return "on_track"

        latest = self.checkpoints[-1]
        elapsed = datetime.now() - self.start_time
        expected_progress = self._calculate_expected_progress(elapsed)

        if latest.progress < expected_progress - 0.15:
            return "behind"
        elif latest.progress > expected_progress + 0.15:
            return "ahead"
        else:
            return "on_track"

    def _calculate_expected_progress(self, elapsed: timedelta) -> float:
        """Calculate where we should be based on time elapsed"""
        # Simplified: assume linear progress
        # In reality, would use historical data from Bolor Brain
        if not hasattr(self, 'estimated_duration'):
            return 0.5  # Unknown, assume 50%

        return min(1.0, elapsed.total_seconds() / self.estimated_duration.total_seconds())

    def get_report(self) -> Dict[str, Any]:
        """Generate progress report"""
        if not self.checkpoints:
            return {"status": "not_started"}

        latest = self.checkpoints[-1]
        elapsed = datetime.now() - self.start_time

        return {
            "progress": f"{latest.progress:.1%}",
            "tasks_completed": latest.tasks_completed,
            "tasks_total": self.total_tasks,
            "time_elapsed": str(elapsed),
            "current_task": latest.current_task,
            "status": self.check_progress({}),
            "checkpoints": len(self.checkpoints)
        }


# Example
if __name__ == "__main__":
    monitor = ProgressMonitor()
    monitor.start("Build documentation", total_tasks=5)

    import time

    tasks = ["Read codebase", "Generate arch docs", "Create API ref", "Write examples", "Final review"]

    for i, task in enumerate(tasks):
        time.sleep(0.5)  # Simulate work
        monitor.checkpoint(i+1, task, "Completed successfully")
        print(f"Progress: {monitor.get_report()}")

    print(f"\n✅ Final report:")
    print(monitor.get_report())
