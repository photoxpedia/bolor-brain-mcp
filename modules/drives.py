"""
Bolor Brain Intrinsic Drives System
====================================
Cross-tier motivation layer providing:
- Curiosity: Need to explore and learn
- Novelty: Need for new experiences
- Competence: Need to master skills
- Connection: Need for social interaction
- Stability: Need for predictability

Drives are advisory - they influence but don't mandate decisions.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class DriveType(Enum):
    """Types of intrinsic drives"""
    CURIOSITY = "curiosity"      # Need to explore/learn new things
    NOVELTY = "novelty"          # Need for new/varied experiences
    COMPETENCE = "competence"    # Need to master skills and improve
    CONNECTION = "connection"    # Need for social interaction
    STABILITY = "stability"      # Need for predictability and safety


@dataclass
class IntrinsicDrive:
    """
    A single intrinsic drive with homeostatic regulation.

    The drive level increases over time when unsatisfied (like hunger).
    Actions that satisfy the drive reduce its level back toward baseline.
    """
    name: str
    current_level: float = 0.5      # Current "need" level (0-1)
    baseline: float = 0.3           # Homeostatic setpoint to return to
    decay_rate: float = 0.01        # How fast drive increases when unsatisfied (per minute)
    satisfaction_rate: float = 0.2  # How much a satisfying action reduces the level
    last_satisfied: float = field(default_factory=time.time)
    satisfaction_count: int = 0     # Total times this drive was satisfied

    def update(self, elapsed_minutes: float) -> float:
        """
        Update drive level based on time elapsed.
        Returns the new level.
        """
        # Drive increases over time (like hunger)
        increase = self.decay_rate * elapsed_minutes

        # Pull toward baseline when below it
        if self.current_level < self.baseline:
            self.current_level = min(self.baseline,
                                    self.current_level + increase * 0.5)
        else:
            # Increase above baseline when unsatisfied
            self.current_level = min(1.0, self.current_level + increase)

        return self.current_level

    def satisfy(self, amount: float = None) -> float:
        """
        Satisfy this drive, reducing its level.
        Returns the new level.
        """
        reduction = amount if amount is not None else self.satisfaction_rate
        self.current_level = max(0.0, self.current_level - reduction)
        self.last_satisfied = time.time()
        self.satisfaction_count += 1
        return self.current_level

    def get_urgency(self) -> float:
        """
        Get urgency level (0-1).
        Higher values mean the drive needs attention.
        """
        # Urgency increases exponentially as level approaches 1
        if self.current_level <= self.baseline:
            return 0.0
        excess = self.current_level - self.baseline
        max_excess = 1.0 - self.baseline
        return (excess / max_excess) ** 1.5  # Exponential urgency

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "name": self.name,
            "current_level": self.current_level,
            "baseline": self.baseline,
            "decay_rate": self.decay_rate,
            "satisfaction_rate": self.satisfaction_rate,
            "last_satisfied": self.last_satisfied,
            "satisfaction_count": self.satisfaction_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntrinsicDrive':
        """Create from dictionary"""
        return cls(**data)


# Default drive configurations
DEFAULT_DRIVE_CONFIGS = {
    DriveType.CURIOSITY: {
        "baseline": 0.4,        # Naturally curious
        "decay_rate": 0.015,    # Builds moderately fast
        "satisfaction_rate": 0.25
    },
    DriveType.NOVELTY: {
        "baseline": 0.3,
        "decay_rate": 0.02,     # Builds faster
        "satisfaction_rate": 0.3
    },
    DriveType.COMPETENCE: {
        "baseline": 0.35,
        "decay_rate": 0.008,    # Builds slowly
        "satisfaction_rate": 0.15
    },
    DriveType.CONNECTION: {
        "baseline": 0.25,
        "decay_rate": 0.01,
        "satisfaction_rate": 0.2
    },
    DriveType.STABILITY: {
        "baseline": 0.5,        # Strong need for stability
        "decay_rate": 0.005,    # Builds very slowly
        "satisfaction_rate": 0.1
    }
}


# Actions and their drive satisfaction mappings
ACTION_DRIVE_SATISFACTION = {
    # Learning actions satisfy curiosity
    "learn": {DriveType.CURIOSITY: 0.3, DriveType.COMPETENCE: 0.1},
    "explore": {DriveType.CURIOSITY: 0.25, DriveType.NOVELTY: 0.2},
    "research": {DriveType.CURIOSITY: 0.35, DriveType.COMPETENCE: 0.15},
    "question": {DriveType.CURIOSITY: 0.2},

    # Novel experiences
    "new_experience": {DriveType.NOVELTY: 0.35},
    "discover": {DriveType.NOVELTY: 0.3, DriveType.CURIOSITY: 0.2},
    "experiment": {DriveType.NOVELTY: 0.25, DriveType.CURIOSITY: 0.15},
    "create": {DriveType.NOVELTY: 0.2, DriveType.COMPETENCE: 0.2},

    # Competence building
    "practice": {DriveType.COMPETENCE: 0.3},
    "master": {DriveType.COMPETENCE: 0.4},
    "improve": {DriveType.COMPETENCE: 0.25},
    "solve_problem": {DriveType.COMPETENCE: 0.35, DriveType.CURIOSITY: 0.1},
    "succeed": {DriveType.COMPETENCE: 0.3},
    "fail_and_learn": {DriveType.COMPETENCE: 0.15, DriveType.CURIOSITY: 0.1},

    # Social connection
    "interact": {DriveType.CONNECTION: 0.25},
    "collaborate": {DriveType.CONNECTION: 0.35, DriveType.COMPETENCE: 0.1},
    "help": {DriveType.CONNECTION: 0.3},
    "communicate": {DriveType.CONNECTION: 0.2},
    "receive_feedback": {DriveType.CONNECTION: 0.2, DriveType.COMPETENCE: 0.15},

    # Stability and predictability
    "routine": {DriveType.STABILITY: 0.2},
    "familiar_task": {DriveType.STABILITY: 0.15},
    "confirm_understanding": {DriveType.STABILITY: 0.25},
    "validate": {DriveType.STABILITY: 0.2},
    "organize": {DriveType.STABILITY: 0.2},
}


class DriveState:
    """
    Manages the complete state of all intrinsic drives.
    """

    def __init__(self, initial_state: Dict[str, Dict] = None):
        self._drives: Dict[DriveType, IntrinsicDrive] = {}
        self._last_update = time.time()

        # Initialize drives
        for drive_type in DriveType:
            config = DEFAULT_DRIVE_CONFIGS[drive_type].copy()
            if initial_state and drive_type.value in initial_state:
                # Restore from saved state
                saved = initial_state[drive_type.value]
                self._drives[drive_type] = IntrinsicDrive.from_dict(saved)
            else:
                # Create new drive with default config
                self._drives[drive_type] = IntrinsicDrive(
                    name=drive_type.value,
                    current_level=config["baseline"],
                    **config
                )

    def update_all(self) -> Dict[str, float]:
        """
        Update all drives based on elapsed time.
        Returns current levels for all drives.
        """
        now = time.time()
        elapsed_minutes = (now - self._last_update) / 60
        self._last_update = now

        levels = {}
        for drive_type, drive in self._drives.items():
            drive.update(elapsed_minutes)
            levels[drive_type.value] = drive.current_level

        return levels

    def satisfy_drive(self, drive_type: DriveType, amount: float = None) -> float:
        """Satisfy a specific drive"""
        if drive_type in self._drives:
            return self._drives[drive_type].satisfy(amount)
        return 0.0

    def satisfy_from_action(self, action: str) -> Dict[str, float]:
        """
        Satisfy drives based on an action taken.
        Returns dict of drive -> new_level for affected drives.
        """
        results = {}

        # Find matching action pattern
        action_lower = action.lower()
        matched_satisfaction = None

        # Try exact match first
        if action_lower in ACTION_DRIVE_SATISFACTION:
            matched_satisfaction = ACTION_DRIVE_SATISFACTION[action_lower]
        else:
            # Try partial match
            for action_key, satisfaction in ACTION_DRIVE_SATISFACTION.items():
                if action_key in action_lower or action_lower in action_key:
                    matched_satisfaction = satisfaction
                    break

        if matched_satisfaction:
            for drive_type, amount in matched_satisfaction.items():
                new_level = self.satisfy_drive(drive_type, amount)
                results[drive_type.value] = new_level

        return results

    def get_dominant_drive(self) -> Tuple[DriveType, float]:
        """
        Get the drive with highest urgency.
        Returns (drive_type, urgency_level).
        """
        self.update_all()

        max_urgency = -1
        dominant = None

        for drive_type, drive in self._drives.items():
            urgency = drive.get_urgency()
            if urgency > max_urgency:
                max_urgency = urgency
                dominant = drive_type

        return dominant, max_urgency

    def get_all_drives(self) -> Dict[str, Dict[str, float]]:
        """Get current state of all drives"""
        self.update_all()
        return {
            drive_type.value: {
                "level": drive.current_level,
                "baseline": drive.baseline,
                "urgency": drive.get_urgency(),
                "satisfaction_count": drive.satisfaction_count
            }
            for drive_type, drive in self._drives.items()
        }

    def get_drive(self, drive_type: DriveType) -> Optional[IntrinsicDrive]:
        """Get a specific drive"""
        return self._drives.get(drive_type)

    def get_drive_weighted_priority(self, options: List[Dict[str, Any]],
                                   drive_key: str = "satisfies_drives") -> List[Dict[str, Any]]:
        """
        Rank options by how well they satisfy current urgent drives.

        Each option should have a drive_key field mapping drive names to satisfaction amounts.
        E.g., {"satisfies_drives": {"curiosity": 0.3, "novelty": 0.2}}

        Returns options sorted by weighted priority (highest first).
        """
        self.update_all()

        scored_options = []
        for option in options:
            satisfaction_map = option.get(drive_key, {})
            score = 0.0

            for drive_name, satisfaction in satisfaction_map.items():
                try:
                    drive_type = DriveType(drive_name)
                    drive = self._drives.get(drive_type)
                    if drive:
                        # Weight satisfaction by urgency
                        urgency = drive.get_urgency()
                        score += satisfaction * (1 + urgency * 2)  # Boost by urgency
                except ValueError:
                    continue

            scored_options.append((score, option))

        # Sort by score descending
        scored_options.sort(key=lambda x: x[0], reverse=True)

        return [opt for _, opt in scored_options]

    def to_dict(self) -> Dict[str, Dict]:
        """Convert full state to dictionary for persistence"""
        return {
            drive_type.value: drive.to_dict()
            for drive_type, drive in self._drives.items()
        }

    def should_explore(self, novelty_threshold: float = 0.6,
                      curiosity_threshold: float = 0.6) -> bool:
        """
        Check if drives suggest exploring something new.
        """
        self.update_all()

        novelty = self._drives[DriveType.NOVELTY].current_level
        curiosity = self._drives[DriveType.CURIOSITY].current_level

        return novelty > novelty_threshold or curiosity > curiosity_threshold

    def should_consolidate(self, stability_threshold: float = 0.7) -> bool:
        """
        Check if drives suggest consolidating/organizing.
        """
        self.update_all()
        stability = self._drives[DriveType.STABILITY].current_level
        return stability > stability_threshold

    def get_suggested_actions(self, top_n: int = 3) -> List[str]:
        """
        Get suggested actions based on current drive urgencies.
        """
        self.update_all()

        # Get urgency-weighted actions
        action_scores = {}

        for action, satisfactions in ACTION_DRIVE_SATISFACTION.items():
            score = 0.0
            for drive_type, amount in satisfactions.items():
                drive = self._drives.get(drive_type)
                if drive:
                    urgency = drive.get_urgency()
                    score += amount * (1 + urgency * 3)

            action_scores[action] = score

        # Sort by score and return top N
        sorted_actions = sorted(action_scores.items(),
                               key=lambda x: x[1], reverse=True)

        return [action for action, _ in sorted_actions[:top_n]]


class DriveManager:
    """
    High-level manager for the drive system.
    Integrates with memory and cognitive systems.
    """

    def __init__(self, self_model_store=None):
        """
        Initialize drive manager.

        Args:
            self_model_store: Optional SelfModelStore to persist drive state
        """
        self._self_model_store = self_model_store

        # Load initial state from self model if available
        initial_state = None
        if self_model_store:
            initial_state = self_model_store.get_drive_state()

        self._state = DriveState(initial_state)
        self._action_history: List[Tuple[float, str, Dict]] = []  # (timestamp, action, results)

    def record_action(self, action: str, metadata: Dict = None) -> Dict[str, float]:
        """
        Record an action and update drives accordingly.
        Returns dict of affected drives and their new levels.
        """
        results = self._state.satisfy_from_action(action)

        # Record in history
        self._action_history.append((time.time(), action, results))

        # Keep only last 100 actions
        if len(self._action_history) > 100:
            self._action_history = self._action_history[-100:]

        # Persist if we have a self model store
        if self._self_model_store:
            self._self_model_store.update_drive_state(self._state.to_dict())

        logger.debug(f"Action '{action}' satisfied drives: {results}")

        return results

    def record_outcome(self, outcome: str, reward: float) -> Dict[str, float]:
        """
        Record an outcome and its reward signal.
        Positive rewards satisfy competence, negative increase learning drive.
        """
        results = {}

        if reward > 0.5:
            # Success - satisfy competence
            results.update(self._state.satisfy_from_action("succeed"))
        elif reward < -0.5:
            # Failure - satisfies curiosity (learning from failure)
            results.update(self._state.satisfy_from_action("fail_and_learn"))

        if self._self_model_store:
            self._self_model_store.update_drive_state(self._state.to_dict())

        return results

    def get_motivation_context(self) -> Dict[str, Any]:
        """
        Get current motivation context for use in decision making.
        """
        dominant, urgency = self._state.get_dominant_drive()

        return {
            "dominant_drive": dominant.value if dominant else None,
            "dominant_urgency": urgency,
            "all_drives": self._state.get_all_drives(),
            "suggested_actions": self._state.get_suggested_actions(3),
            "should_explore": self._state.should_explore(),
            "should_consolidate": self._state.should_consolidate()
        }

    def get_state(self) -> DriveState:
        """Get the current drive state"""
        return self._state

    def boost_curiosity(self, amount: float = 0.2):
        """
        Artificially boost curiosity (e.g., when encountering something interesting).
        """
        drive = self._state.get_drive(DriveType.CURIOSITY)
        if drive:
            drive.current_level = min(1.0, drive.current_level + amount)

    def boost_novelty(self, amount: float = 0.2):
        """
        Artificially boost novelty drive (e.g., after repetitive tasks).
        """
        drive = self._state.get_drive(DriveType.NOVELTY)
        if drive:
            drive.current_level = min(1.0, drive.current_level + amount)

    def trigger_stability_need(self, amount: float = 0.3):
        """
        Trigger stability need (e.g., after unexpected events).
        """
        drive = self._state.get_drive(DriveType.STABILITY)
        if drive:
            drive.current_level = min(1.0, drive.current_level + amount)

    def prioritize_options(self, options: List[Dict],
                          drive_key: str = "satisfies_drives") -> List[Dict]:
        """
        Prioritize options based on current drive state.
        """
        return self._state.get_drive_weighted_priority(options, drive_key)

    def get_recent_actions(self, count: int = 10) -> List[Tuple[float, str, Dict]]:
        """Get recent action history"""
        return self._action_history[-count:]


# =============================================================================
# DRIVE-AWARE UTILITIES
# =============================================================================

def tag_memory_with_drive(drive_state: DriveState,
                         memory_content: str,
                         memory_type: str) -> Optional[str]:
    """
    Determine which drive a memory storage might satisfy.
    Returns the most relevant drive name or None.
    """
    content_lower = memory_content.lower()

    # Keyword-based drive detection
    curiosity_keywords = ["learn", "discover", "understand", "why", "how", "what",
                         "explore", "research", "investigate", "question"]
    novelty_keywords = ["new", "first", "never", "unique", "different", "unusual",
                       "surprising", "unexpected"]
    competence_keywords = ["solved", "completed", "achieved", "mastered", "improved",
                          "success", "accomplish", "skill", "ability"]
    connection_keywords = ["user", "help", "assist", "collaborate", "together",
                          "feedback", "communicate", "interact"]
    stability_keywords = ["confirm", "verify", "validate", "consistent", "stable",
                         "reliable", "familiar", "routine"]

    # Score each drive
    scores = {
        DriveType.CURIOSITY: sum(1 for kw in curiosity_keywords if kw in content_lower),
        DriveType.NOVELTY: sum(1 for kw in novelty_keywords if kw in content_lower),
        DriveType.COMPETENCE: sum(1 for kw in competence_keywords if kw in content_lower),
        DriveType.CONNECTION: sum(1 for kw in connection_keywords if kw in content_lower),
        DriveType.STABILITY: sum(1 for kw in stability_keywords if kw in content_lower),
    }

    # Return drive with highest score if any
    max_score = max(scores.values())
    if max_score > 0:
        for drive_type, score in scores.items():
            if score == max_score:
                return drive_type.value

    return None


def boost_memory_by_drive(episode_list: List, drive_state: DriveState,
                         boost_factor: float = 0.2) -> List:
    """
    Boost retrieval scores of memories that align with current dominant drive.

    Expects episodes with 'drive_satisfied' field.
    Returns sorted list with boosted scores.
    """
    dominant, urgency = drive_state.get_dominant_drive()

    if not dominant or urgency < 0.3:
        return episode_list  # No significant urgency

    boosted = []
    for episode in episode_list:
        score = getattr(episode, 'strength', 1.0)

        # Boost if this episode satisfied the dominant drive
        if hasattr(episode, 'drive_satisfied'):
            if episode.drive_satisfied == dominant.value:
                score += boost_factor * (1 + urgency)

        boosted.append((score, episode))

    # Sort by boosted score
    boosted.sort(key=lambda x: x[0], reverse=True)

    return [ep for _, ep in boosted]
