"""
Approval System - REAL notification and approval handling

Implements the approval notification system for high-risk autonomous actions.
Uses REAL file operations for approval requests and responses.

NO SIMULATION - Uses actual file I/O for approval queue.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum


class ApprovalStatus(Enum):
    """Approval request status"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"


@dataclass
class ApprovalRequest:
    """Approval request data"""
    request_id: str
    action_type: str
    description: str
    risk_tier: int
    details: Dict[str, Any]
    created_at: str
    expires_at: str
    status: str
    response_at: Optional[str] = None
    response_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApprovalRequest':
        """Create from dictionary"""
        return cls(**data)


class ApprovalSystem:
    """
    REAL file-based approval system

    Approval flow:
    1. Agent creates approval request (writes to queue)
    2. System notifies user (optional callback)
    3. User approves/denies (writes response)
    4. Agent reads response and proceeds
    """

    def __init__(self,
                 queue_dir: str = None,
                 timeout_seconds: int = 300,
                 notification_callback: Callable = None):
        """
        Initialize approval system

        Args:
            queue_dir: Directory for approval queue (default: .approval_queue)
            timeout_seconds: Approval timeout in seconds (default: 5 minutes)
            notification_callback: Optional function to notify user
        """
        self.queue_dir = Path(queue_dir or ".approval_queue")
        self.queue_dir.mkdir(parents=True, exist_ok=True)

        self.timeout_seconds = timeout_seconds
        self.notification_callback = notification_callback

        self.pending_requests = {}

    def request_approval(self,
                        action_type: str,
                        description: str,
                        risk_tier: int,
                        details: Dict[str, Any] = None) -> str:
        """
        Request approval for high-risk action - REAL file operation

        Args:
            action_type: Type of action (e.g., "delete", "deploy")
            description: Human-readable description
            risk_tier: Risk tier (2 or 3)
            details: Additional action details

        Returns:
            Request ID
        """
        # Generate request ID
        request_id = self._generate_request_id()

        # Create approval request
        created_at = datetime.now()
        expires_at = created_at + timedelta(seconds=self.timeout_seconds)

        request = ApprovalRequest(
            request_id=request_id,
            action_type=action_type,
            description=description,
            risk_tier=risk_tier,
            details=details or {},
            created_at=created_at.isoformat(),
            expires_at=expires_at.isoformat(),
            status=ApprovalStatus.PENDING.value
        )

        # Save to queue - REAL file write
        request_file = self.queue_dir / f"{request_id}.json"
        with open(request_file, 'w') as f:
            json.dump(request.to_dict(), f, indent=2)

        # Track pending request
        self.pending_requests[request_id] = request

        # Notify user (if callback provided)
        if self.notification_callback:
            try:
                self.notification_callback(request)
            except Exception as e:
                print(f"Warning: Notification callback failed: {e}")

        return request_id

    def wait_for_approval(self,
                         request_id: str,
                         poll_interval: float = 1.0) -> ApprovalStatus:
        """
        Wait for approval response - REAL file operation

        Polls the approval file for status updates.

        Args:
            request_id: Request ID to wait for
            poll_interval: Seconds between polls

        Returns:
            Final approval status
        """
        request_file = self.queue_dir / f"{request_id}.json"

        if not request_file.exists():
            return ApprovalStatus.TIMEOUT

        # Poll for response
        start_time = time.time()

        while True:
            # REAL file read
            try:
                with open(request_file, 'r') as f:
                    data = json.load(f)

                request = ApprovalRequest.from_dict(data)

                # Check if responded
                if request.status != ApprovalStatus.PENDING.value:
                    return ApprovalStatus(request.status)

                # Check if expired
                expires_at = datetime.fromisoformat(request.expires_at)
                if datetime.now() > expires_at:
                    # Mark as timeout
                    self.respond_to_request(request_id, ApprovalStatus.TIMEOUT,
                                           "Request timed out")
                    return ApprovalStatus.TIMEOUT

                # Check if we've been polling too long (safety check)
                if time.time() - start_time > self.timeout_seconds + 10:
                    return ApprovalStatus.TIMEOUT

                # Wait before next poll
                time.sleep(poll_interval)

            except Exception as e:
                print(f"Error reading approval file: {e}")
                return ApprovalStatus.TIMEOUT

    def respond_to_request(self,
                          request_id: str,
                          status: ApprovalStatus,
                          reason: str = None) -> bool:
        """
        Respond to approval request - REAL file operation

        Args:
            request_id: Request ID
            status: Approval status (APPROVED/DENIED/TIMEOUT)
            reason: Optional reason for decision

        Returns:
            True if response saved successfully
        """
        request_file = self.queue_dir / f"{request_id}.json"

        if not request_file.exists():
            return False

        try:
            # REAL file read
            with open(request_file, 'r') as f:
                data = json.load(f)

            # Update status
            data['status'] = status.value
            data['response_at'] = datetime.now().isoformat()
            data['response_reason'] = reason

            # REAL file write
            with open(request_file, 'w') as f:
                json.dump(data, f, indent=2)

            # Update pending requests
            if request_id in self.pending_requests:
                self.pending_requests[request_id].status = status.value

            return True

        except Exception as e:
            print(f"Error responding to approval: {e}")
            return False

    def list_pending_requests(self) -> list:
        """
        List all pending approval requests - REAL file operation

        Returns:
            List of pending requests
        """
        pending = []

        # REAL directory listing
        for request_file in self.queue_dir.glob("*.json"):
            try:
                with open(request_file, 'r') as f:
                    data = json.load(f)

                request = ApprovalRequest.from_dict(data)

                if request.status == ApprovalStatus.PENDING.value:
                    # Check if expired
                    expires_at = datetime.fromisoformat(request.expires_at)
                    if datetime.now() > expires_at:
                        # Mark as timeout
                        self.respond_to_request(request.request_id,
                                              ApprovalStatus.TIMEOUT,
                                              "Expired")
                    else:
                        pending.append(request.to_dict())

            except Exception:
                # Skip corrupted files
                continue

        # Sort by created_at
        pending.sort(key=lambda x: x['created_at'], reverse=True)

        return pending

    def cleanup_old_requests(self, days_old: int = 7):
        """
        Clean up old approval requests - REAL file operation

        Args:
            days_old: Delete requests older than this many days
        """
        cutoff = datetime.now() - timedelta(days=days_old)

        for request_file in self.queue_dir.glob("*.json"):
            try:
                # Check file modification time
                mtime = datetime.fromtimestamp(request_file.stat().st_mtime)

                if mtime < cutoff:
                    request_file.unlink()

            except Exception:
                # Continue on error
                pass

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"approval_{timestamp}"


# CLI Tool for Manual Approval
class ApprovalCLI:
    """Command-line interface for approving requests"""

    def __init__(self, queue_dir: str = None):
        self.system = ApprovalSystem(queue_dir)

    def show_pending(self):
        """Show all pending approval requests"""
        pending = self.system.list_pending_requests()

        if not pending:
            print("No pending approval requests")
            return

        print("\n" + "="*60)
        print("PENDING APPROVAL REQUESTS")
        print("="*60 + "\n")

        for i, request in enumerate(pending, 1):
            print(f"{i}. Request ID: {request['request_id']}")
            print(f"   Action: {request['action_type']}")
            print(f"   Description: {request['description']}")
            print(f"   Risk Tier: {request['risk_tier']}")
            print(f"   Created: {request['created_at']}")
            print(f"   Expires: {request['expires_at']}")
            if request['details']:
                print(f"   Details: {request['details']}")
            print()

    def approve_request(self, request_id: str, reason: str = None):
        """Approve a request"""
        success = self.system.respond_to_request(
            request_id,
            ApprovalStatus.APPROVED,
            reason or "Approved by user"
        )

        if success:
            print(f"✅ Request {request_id} APPROVED")
        else:
            print(f"❌ Failed to approve request {request_id}")

    def deny_request(self, request_id: str, reason: str = None):
        """Deny a request"""
        success = self.system.respond_to_request(
            request_id,
            ApprovalStatus.DENIED,
            reason or "Denied by user"
        )

        if success:
            print(f"❌ Request {request_id} DENIED")
        else:
            print(f"❌ Failed to deny request {request_id}")


# Example usage
if __name__ == "__main__":
    import sys

    # Create approval system
    def notify_user(request: ApprovalRequest):
        """Example notification callback"""
        print("\n" + "="*60)
        print("⚠️  APPROVAL REQUIRED")
        print("="*60)
        print(f"Action: {request.action_type}")
        print(f"Description: {request.description}")
        print(f"Risk Tier: {request.risk_tier}")
        print(f"Request ID: {request.request_id}")
        print(f"Expires: {request.expires_at}")
        print("\nTo approve:")
        print(f"  python approval_system.py approve {request.request_id}")
        print("To deny:")
        print(f"  python approval_system.py deny {request.request_id}")
        print("="*60 + "\n")

    # Check command line args
    if len(sys.argv) > 1:
        # CLI mode
        cli = ApprovalCLI()

        command = sys.argv[1]

        if command == "list":
            cli.show_pending()

        elif command == "approve" and len(sys.argv) > 2:
            request_id = sys.argv[2]
            reason = sys.argv[3] if len(sys.argv) > 3 else None
            cli.approve_request(request_id, reason)

        elif command == "deny" and len(sys.argv) > 2:
            request_id = sys.argv[2]
            reason = sys.argv[3] if len(sys.argv) > 3 else None
            cli.deny_request(request_id, reason)

        else:
            print("Usage:")
            print("  python approval_system.py list")
            print("  python approval_system.py approve <request_id> [reason]")
            print("  python approval_system.py deny <request_id> [reason]")

    else:
        # Demo mode
        print("Testing approval system...")

        system = ApprovalSystem(
            queue_dir=".test_approval_queue",
            timeout_seconds=30,
            notification_callback=notify_user
        )

        # Request approval
        print("Creating approval request...")
        request_id = system.request_approval(
            action_type="delete",
            description="Delete old log files (>30 days)",
            risk_tier=3,
            details={"files": ["*.log"], "path": "/var/logs"}
        )

        print(f"\nRequest created: {request_id}")
        print("\nWaiting for approval (30 seconds timeout)...")
        print("Run in another terminal:")
        print(f"  python approval_system.py approve {request_id}")

        # Wait for approval (this will timeout in demo)
        status = system.wait_for_approval(request_id, poll_interval=1.0)

        print(f"\nFinal status: {status.value}")

        # Cleanup
        print("\nCleaning up test files...")
        import shutil
        shutil.rmtree(".test_approval_queue", ignore_errors=True)
        print("✅ Done")
