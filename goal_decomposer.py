"""
Goal Decomposer - Breaks high-level goals into actionable tasks

Uses Bolor Brain for analysis + NSAF for clustering
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class TaskCluster:
    """A cluster of related subtasks"""
    description: str
    type: str  # read, write, analyze, create, deploy, etc.
    priority: int = 5
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class TaskPlan:
    """Complete decomposed plan"""
    goal: str
    tasks: List[TaskCluster]
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    estimated_duration: str = "Unknown"
    schedule: Any = None


class GoalDecomposer:
    """
    Breaks high-level goals into actionable tasks

    Example:
        Input: "Build documentation for Bolor Brain MCP"
        Output: [Read codebase, Generate arch docs, Create API ref, ...]
    """

    def __init__(self, brain_client=None, nsaf_client=None):
        self.brain = brain_client
        self.nsaf = nsaf_client

    def decompose(self, goal: str) -> TaskPlan:
        """
        Decompose goal into actionable tasks

        Args:
            goal: High-level goal description

        Returns:
            TaskPlan with decomposed tasks and dependencies
        """
        # 1. Analyze goal using Bolor Brain
        analysis = self._analyze_goal(goal)

        # 2. Generate subtasks
        subtasks = self._generate_subtasks(goal, analysis)

        # 3. Identify dependencies
        dependencies = self._identify_dependencies(subtasks)

        # 4. Cluster related tasks (using NSAF if available)
        task_clusters = self._cluster_tasks(subtasks, dependencies)

        return TaskPlan(
            goal=goal,
            tasks=task_clusters,
            dependencies=dependencies,
            estimated_duration=self._estimate_duration(task_clusters)
        )

    def _analyze_goal(self, goal: str) -> Dict[str, Any]:
        """Analyze goal to understand requirements"""
        if not self.brain:
            return {"type": "general", "complexity": "medium"}

        # In production, use Bolor Brain:
        # analysis = self.brain.reason_hybrid({
        #     "query": f"Analyze this goal: {goal}",
        #     "context": {"type": "goal_analysis"}
        # })
        # return analysis.insights

        # Simple heuristic analysis
        goal_lower = goal.lower()

        goal_type = "general"
        if any(word in goal_lower for word in ['build', 'create', 'generate']):
            goal_type = "creation"
        elif any(word in goal_lower for word in ['fix', 'debug', 'resolve']):
            goal_type = "debugging"
        elif any(word in goal_lower for word in ['optimize', 'improve', 'enhance']):
            goal_type = "optimization"

        complexity = "medium"
        if any(word in goal_lower for word in ['simple', 'quick', 'basic']):
            complexity = "low"
        elif any(word in goal_lower for word in ['complex', 'comprehensive', 'full']):
            complexity = "high"

        return {
            "type": goal_type,
            "complexity": complexity,
            "keywords": self._extract_keywords(goal)
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        # Simplified keyword extraction
        important_words = []
        words = text.lower().split()

        keywords = ['documentation', 'api', 'architecture', 'examples',
                   'guide', 'reference', 'tutorial', 'test', 'deploy']

        for word in words:
            for keyword in keywords:
                if keyword in word:
                    important_words.append(keyword)

        return list(set(important_words))

    def _generate_subtasks(self, goal: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate subtasks from goal"""
        subtasks = []

        # Common patterns for different goal types
        if "documentation" in analysis.get("keywords", []):
            subtasks.extend([
                {"description": "Read and analyze codebase", "type": "read", "priority": 9},
                {"description": "Generate architecture documentation", "type": "write", "priority": 8},
                {"description": "Create API reference", "type": "write", "priority": 7},
                {"description": "Write usage examples", "type": "write", "priority": 6},
                {"description": "Create integration guides", "type": "write", "priority": 5},
            ])

        elif analysis["type"] == "debugging":
            subtasks.extend([
                {"description": "Reproduce the issue", "type": "test", "priority": 9},
                {"description": "Analyze error logs", "type": "read", "priority": 8},
                {"description": "Generate hypotheses", "type": "analyze", "priority": 7},
                {"description": "Test hypotheses", "type": "test", "priority": 6},
                {"description": "Implement fix", "type": "write", "priority": 5},
                {"description": "Verify fix", "type": "test", "priority": 4},
            ])

        elif analysis["type"] == "optimization":
            subtasks.extend([
                {"description": "Profile current performance", "type": "analyze", "priority": 9},
                {"description": "Identify bottlenecks", "type": "analyze", "priority": 8},
                {"description": "Generate optimization strategies", "type": "analyze", "priority": 7},
                {"description": "Implement optimizations", "type": "write", "priority": 6},
                {"description": "Benchmark improvements", "type": "test", "priority": 5},
            ])

        else:
            # Generic decomposition
            subtasks.extend([
                {"description": "Analyze requirements", "type": "analyze", "priority": 9},
                {"description": "Design solution", "type": "analyze", "priority": 8},
                {"description": "Implement solution", "type": "write", "priority": 7},
                {"description": "Test solution", "type": "test", "priority": 6},
            ])

        return subtasks

    def _identify_dependencies(self, subtasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Identify dependencies between tasks"""
        dependencies = {}

        for i, task in enumerate(subtasks):
            task_id = f"task_{i+1}"

            # Common dependency patterns
            if task["type"] == "write" and i > 0:
                # Writing usually depends on prior analysis/reading
                prev_analyze = [f"task_{j+1}" for j, t in enumerate(subtasks[:i])
                              if t["type"] in ["read", "analyze"]]
                if prev_analyze:
                    dependencies[task_id] = [prev_analyze[0]]

            elif task["type"] == "test" and i > 0:
                # Testing depends on implementation
                prev_write = [f"task_{j+1}" for j, t in enumerate(subtasks[:i])
                            if t["type"] == "write"]
                if prev_write:
                    dependencies[task_id] = [prev_write[-1]]

        return dependencies

    def _cluster_tasks(self, subtasks: List[Dict[str, Any]],
                      dependencies: Dict[str, List[str]]) -> List[TaskCluster]:
        """Cluster related tasks"""
        clusters = []

        for i, task in enumerate(subtasks):
            task_id = f"task_{i+1}"

            cluster = TaskCluster(
                description=task["description"],
                type=task["type"],
                priority=task.get("priority", 5),
                dependencies=dependencies.get(task_id, []),
                tags=[task["type"]]
            )

            clusters.append(cluster)

        return clusters

    def _estimate_duration(self, clusters: List[TaskCluster]) -> str:
        """Estimate total duration"""
        # Simplified estimation
        total_tasks = len(clusters)

        if total_tasks <= 3:
            return "~1-2 hours"
        elif total_tasks <= 6:
            return "~3-5 hours"
        else:
            return "~1-2 days"


# Example usage
if __name__ == "__main__":
    decomposer = GoalDecomposer()

    goals = [
        "Build comprehensive documentation for Bolor Brain MCP",
        "Debug memory leak in production API",
        "Optimize database query performance"
    ]

    for goal in goals:
        print(f"\n{'='*60}")
        print(f"Goal: {goal}")
        print(f"{'='*60}\n")

        plan = decomposer.decompose(goal)

        print(f"Estimated duration: {plan.estimated_duration}")
        print(f"Total tasks: {len(plan.tasks)}\n")

        print("Tasks:")
        for i, task in enumerate(plan.tasks, 1):
            deps = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
            print(f"  {i}. [{task.type}] {task.description} (priority: {task.priority}){deps}")
