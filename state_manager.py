"""
State Manager - REAL persistence for autonomous agent

Saves and loads agent state to/from disk using actual file I/O.
NO SIMULATION - Uses real file operations.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class StateManagerError(Exception):
    """State management errors"""
    pass


@dataclass
class PersistedState:
    """Agent state that gets persisted to disk"""
    session_id: str
    goal: str
    state: str  # AgentState enum value
    start_time: str  # ISO format
    current_task_id: Optional[str]

    # Task tracking
    tasks_total: int
    tasks_completed: int
    tasks_failed: int
    completed_task_ids: list
    failed_task_ids: list

    # Execution tracking
    learnings_count: int
    evolutions_count: int

    # Results
    execution_results: list
    learnings: Dict[str, Any]

    # Metadata
    last_saved: str  # ISO format
    save_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersistedState':
        """Create from dictionary"""
        return cls(**data)


class StateManager:
    """
    REAL file-based state persistence

    Uses actual file I/O to save/load agent state
    """

    def __init__(self, state_dir: str = None):
        """
        Initialize state manager

        Args:
            state_dir: Directory for state files (default: ./.agent_state)
        """
        self.state_dir = Path(state_dir or ".agent_state")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.current_session_id = None
        self.current_state_file = None

    def save_state(self, agent_data: Dict[str, Any]) -> str:
        """
        Save agent state to disk - REAL file operation

        Args:
            agent_data: Agent state data to persist

        Returns:
            Path to saved state file
        """
        # Generate session ID if not exists
        if not self.current_session_id:
            self.current_session_id = agent_data.get('session_id') or self._generate_session_id()

        # Create persisted state
        state = PersistedState(
            session_id=self.current_session_id,
            goal=agent_data.get('goal', ''),
            state=agent_data.get('state', 'IDLE'),
            start_time=agent_data.get('start_time', datetime.now().isoformat()),
            current_task_id=agent_data.get('current_task_id'),
            tasks_total=agent_data.get('tasks_total', 0),
            tasks_completed=agent_data.get('tasks_completed', 0),
            tasks_failed=agent_data.get('tasks_failed', 0),
            completed_task_ids=agent_data.get('completed_task_ids', []),
            failed_task_ids=agent_data.get('failed_task_ids', []),
            learnings_count=agent_data.get('learnings_count', 0),
            evolutions_count=agent_data.get('evolutions_count', 0),
            execution_results=agent_data.get('execution_results', []),
            learnings=agent_data.get('learnings', {}),
            last_saved=datetime.now().isoformat(),
            save_count=agent_data.get('save_count', 0) + 1
        )

        # Determine file path
        state_file = self.state_dir / f"{self.current_session_id}.json"
        self.current_state_file = state_file

        # REAL file write operation
        try:
            with open(state_file, 'w') as f:
                json.dump(state.to_dict(), f, indent=2)

            return str(state_file)

        except Exception as e:
            raise StateManagerError(f"Failed to save state: {e}")

    def load_state(self, session_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Load agent state from disk - REAL file operation

        Args:
            session_id: Session ID to load (if None, loads latest)

        Returns:
            Loaded state data or None if not found
        """
        if session_id:
            state_file = self.state_dir / f"{session_id}.json"
        else:
            # Find most recent state file
            state_file = self._find_latest_state()
            if not state_file:
                return None

        if not state_file.exists():
            return None

        # REAL file read operation
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)

            self.current_session_id = data['session_id']
            self.current_state_file = state_file

            return data

        except Exception as e:
            raise StateManagerError(f"Failed to load state: {e}")

    def delete_state(self, session_id: str) -> bool:
        """
        Delete saved state - REAL file operation

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        state_file = self.state_dir / f"{session_id}.json"

        if not state_file.exists():
            return False

        try:
            os.remove(state_file)

            if self.current_session_id == session_id:
                self.current_session_id = None
                self.current_state_file = None

            return True

        except Exception as e:
            raise StateManagerError(f"Failed to delete state: {e}")

    def list_sessions(self) -> list:
        """
        List all saved sessions - REAL file operation

        Returns:
            List of session info dicts
        """
        sessions = []

        # REAL directory listing
        for state_file in self.state_dir.glob("*.json"):
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)

                sessions.append({
                    'session_id': data['session_id'],
                    'goal': data['goal'],
                    'state': data['state'],
                    'start_time': data['start_time'],
                    'last_saved': data['last_saved'],
                    'tasks_completed': data['tasks_completed'],
                    'tasks_total': data['tasks_total'],
                    'file_path': str(state_file)
                })
            except Exception:
                # Skip corrupted files
                continue

        # Sort by last_saved (most recent first)
        sessions.sort(key=lambda x: x['last_saved'], reverse=True)

        return sessions

    def _find_latest_state(self) -> Optional[Path]:
        """Find the most recently saved state file"""
        state_files = list(self.state_dir.glob("*.json"))

        if not state_files:
            return None

        # Get file modification times
        latest = max(state_files, key=lambda f: f.stat().st_mtime)
        return latest

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"

    def get_state_size(self, session_id: str = None) -> int:
        """
        Get size of state file in bytes

        Args:
            session_id: Session ID (uses current if None)

        Returns:
            File size in bytes, or 0 if not found
        """
        if session_id:
            state_file = self.state_dir / f"{session_id}.json"
        else:
            state_file = self.current_state_file

        if state_file and state_file.exists():
            return state_file.stat().st_size

        return 0

    def cleanup_old_states(self, keep_recent: int = 10):
        """
        Clean up old state files, keeping only recent ones

        Args:
            keep_recent: Number of recent sessions to keep
        """
        sessions = self.list_sessions()

        # Delete all but the most recent
        for session in sessions[keep_recent:]:
            try:
                self.delete_state(session['session_id'])
            except Exception:
                # Continue on error
                pass


# Example usage
if __name__ == "__main__":
    # Create state manager
    manager = StateManager()

    # Save some state
    agent_data = {
        'goal': 'Build comprehensive documentation',
        'state': 'EXECUTING',
        'start_time': datetime.now().isoformat(),
        'tasks_total': 5,
        'tasks_completed': 2,
        'tasks_failed': 0,
        'completed_task_ids': ['task_1', 'task_2'],
        'failed_task_ids': [],
        'learnings_count': 2,
        'evolutions_count': 0,
        'execution_results': [],
        'learnings': {'patterns': []}
    }

    print("Saving state...")
    state_file = manager.save_state(agent_data)
    print(f"✅ State saved to: {state_file}")
    print(f"   Size: {manager.get_state_size()} bytes")

    # Load it back
    print("\nLoading state...")
    loaded = manager.load_state()
    print(f"✅ State loaded:")
    print(f"   Goal: {loaded['goal']}")
    print(f"   State: {loaded['state']}")
    print(f"   Progress: {loaded['tasks_completed']}/{loaded['tasks_total']}")

    # List all sessions
    print("\nAll sessions:")
    sessions = manager.list_sessions()
    for session in sessions:
        print(f"  - {session['session_id']}: {session['goal'][:50]}")
        print(f"    Progress: {session['tasks_completed']}/{session['tasks_total']}")

    print("\n✅ State persistence working with REAL file operations!")
