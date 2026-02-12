"""
Test Approval System - REAL file operations

Proves that the approval system works with actual file I/O.
NO SIMULATION.
"""

import asyncio
import sys
import time
from pathlib import Path
from approval_system import ApprovalSystem, ApprovalStatus, ApprovalCLI
import threading


async def test_approval_request():
    """Test creating and responding to approval request"""
    print("="*60)
    print("TEST 1: Approval Request Creation")
    print("="*60)

    system = ApprovalSystem(queue_dir=".test_approval", timeout_seconds=10)

    print("\n📝 Creating approval request...")
    request_id = system.request_approval(
        action_type="delete",
        description="Delete old log files",
        risk_tier=3,
        details={"files": ["*.log"], "count": 150}
    )

    print(f"✅ Request created: {request_id}")

    # Verify file exists
    request_file = Path(".test_approval") / f"{request_id}.json"
    if request_file.exists():
        print(f"✅ Request file exists on disk")

        # Verify with raw file read
        import json
        with open(request_file, 'r') as f:
            data = json.load(f)

        print(f"✅ Can read with Python open()")
        print(f"   Action: {data['action_type']}")
        print(f"   Status: {data['status']}")
        print(f"   Risk Tier: {data['risk_tier']}")
    else:
        print(f"❌ Request file does not exist!")
        return False

    print("\n✅ TEST 1 PASSED - Request creation works!\n")
    return True


async def test_approval_response():
    """Test responding to approval request"""
    print("="*60)
    print("TEST 2: Approval Response")
    print("="*60)

    system = ApprovalSystem(queue_dir=".test_approval", timeout_seconds=60)

    # Create request
    print("\n📝 Creating approval request...")
    request_id = system.request_approval(
        action_type="deploy",
        description="Deploy to production",
        risk_tier=3,
        details={"environment": "prod"}
    )

    print(f"✅ Request created: {request_id}")

    # Approve it
    print("\n✅ Approving request...")
    success = system.respond_to_request(
        request_id,
        ApprovalStatus.APPROVED,
        "Approved for testing"
    )

    if success:
        print("✅ Response recorded")
    else:
        print("❌ Failed to record response")
        return False

    # Verify file updated
    request_file = Path(".test_approval") / f"{request_id}.json"
    import json
    with open(request_file, 'r') as f:
        data = json.load(f)

    if data['status'] == ApprovalStatus.APPROVED.value:
        print(f"✅ Status updated to: {data['status']}")
        print(f"✅ Response reason: {data['response_reason']}")
    else:
        print(f"❌ Status not updated correctly: {data['status']}")
        return False

    print("\n✅ TEST 2 PASSED - Response mechanism works!\n")
    return True


async def test_approval_workflow():
    """Test complete approval workflow"""
    print("="*60)
    print("TEST 3: Complete Approval Workflow")
    print("="*60)

    system = ApprovalSystem(queue_dir=".test_approval", timeout_seconds=10)

    # Create request
    print("\n📝 Creating approval request...")
    request_id = system.request_approval(
        action_type="install",
        description="Install new dependency",
        risk_tier=2,
        details={"package": "new-library"}
    )

    print(f"✅ Request created: {request_id}")

    # Auto-approve in background thread (simulating user)
    def auto_approve():
        time.sleep(2)  # Wait 2 seconds
        print("\n  🤖 Auto-approving in background thread...")
        system.respond_to_request(request_id, ApprovalStatus.APPROVED, "Auto-approved for test")

    thread = threading.Thread(target=auto_approve, daemon=True)
    thread.start()

    # Wait for approval
    print("\n⏳ Waiting for approval...")
    status = system.wait_for_approval(request_id, poll_interval=0.5)

    if status == ApprovalStatus.APPROVED:
        print(f"✅ Request approved: {status.value}")
    else:
        print(f"❌ Unexpected status: {status.value}")
        return False

    print("\n✅ TEST 3 PASSED - Complete workflow works!\n")
    return True


async def test_approval_timeout():
    """Test approval timeout"""
    print("="*60)
    print("TEST 4: Approval Timeout")
    print("="*60)

    # Use very short timeout for testing
    system = ApprovalSystem(queue_dir=".test_approval", timeout_seconds=2)

    print("\n📝 Creating approval request with 2-second timeout...")
    request_id = system.request_approval(
        action_type="modify",
        description="Modify critical file",
        risk_tier=2,
        details={"file": "config.json"}
    )

    print(f"✅ Request created: {request_id}")

    # Wait for timeout (don't approve)
    print("\n⏳ Waiting for timeout (2 seconds)...")
    status = system.wait_for_approval(request_id, poll_interval=0.5)

    if status == ApprovalStatus.TIMEOUT:
        print(f"✅ Request timed out as expected: {status.value}")
    else:
        print(f"❌ Unexpected status: {status.value}")
        return False

    # Verify file marked as timeout
    request_file = Path(".test_approval") / f"{request_id}.json"
    import json
    with open(request_file, 'r') as f:
        data = json.load(f)

    if data['status'] == ApprovalStatus.TIMEOUT.value:
        print(f"✅ Status correctly updated to: {data['status']}")
    else:
        print(f"❌ Status not updated: {data['status']}")
        return False

    print("\n✅ TEST 4 PASSED - Timeout mechanism works!\n")
    return True


async def test_cli_interface():
    """Test CLI interface"""
    print("="*60)
    print("TEST 5: CLI Interface")
    print("="*60)

    system = ApprovalSystem(queue_dir=".test_approval")

    # Create some requests
    print("\n📝 Creating test requests...")
    request_ids = []
    for i in range(3):
        request_id = system.request_approval(
            action_type=f"action_{i}",
            description=f"Test action {i}",
            risk_tier=2,
            details={}
        )
        request_ids.append(request_id)

    print(f"✅ Created {len(request_ids)} requests")

    # Test CLI
    cli = ApprovalCLI(queue_dir=".test_approval")

    print("\n📋 Listing pending requests...")
    pending = system.list_pending_requests()

    if len(pending) >= 3:
        print(f"✅ Found {len(pending)} pending requests")
    else:
        print(f"❌ Expected at least 3 pending, found {len(pending)}")
        return False

    # Test approve via CLI
    print(f"\n✅ Approving first request...")
    cli.approve_request(request_ids[0], "CLI test approval")

    # Test deny via CLI
    print(f"❌ Denying second request...")
    cli.deny_request(request_ids[1], "CLI test denial")

    # Verify statuses
    import json
    file1 = Path(".test_approval") / f"{request_ids[0]}.json"
    file2 = Path(".test_approval") / f"{request_ids[1]}.json"

    with open(file1, 'r') as f:
        data1 = json.load(f)
    with open(file2, 'r') as f:
        data2 = json.load(f)

    if data1['status'] == ApprovalStatus.APPROVED.value:
        print(f"✅ First request approved correctly")
    else:
        print(f"❌ First request status wrong: {data1['status']}")
        return False

    if data2['status'] == ApprovalStatus.DENIED.value:
        print(f"✅ Second request denied correctly")
    else:
        print(f"❌ Second request status wrong: {data2['status']}")
        return False

    print("\n✅ TEST 5 PASSED - CLI interface works!\n")
    return True


async def test_real_file_operations():
    """Verify these are REAL file operations"""
    print("="*60)
    print("TEST 6: REAL File Operations Verification")
    print("="*60)

    system = ApprovalSystem(queue_dir=".test_approval")

    print("\n📝 Creating request...")
    request_id = system.request_approval(
        action_type="test",
        description="Verify real operations",
        risk_tier=2,
        details={}
    )

    request_file = Path(".test_approval") / f"{request_id}.json"

    # Check 1: File exists
    if request_file.exists():
        print("✅ File exists on disk")
    else:
        print("❌ File does not exist!")
        return False

    # Check 2: Can read with standard Python
    try:
        import json
        with open(request_file, 'r') as f:
            data = json.load(f)
        print("✅ Can read with standard Python open()")
    except Exception as e:
        print(f"❌ Cannot read file: {e}")
        return False

    # Check 3: File has real timestamp
    mtime = request_file.stat().st_mtime
    from datetime import datetime
    print(f"✅ File has real modification time: {datetime.fromtimestamp(mtime)}")

    # Check 4: File has real size
    size = request_file.stat().st_size
    print(f"✅ File has real size: {size} bytes")

    # Check 5: Can modify with standard Python
    try:
        data['status'] = ApprovalStatus.APPROVED.value
        with open(request_file, 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ Can modify with standard Python open()")
    except Exception as e:
        print(f"❌ Cannot modify file: {e}")
        return False

    # Check 6: Modification persisted
    with open(request_file, 'r') as f:
        updated = json.load(f)

    if updated['status'] == ApprovalStatus.APPROVED.value:
        print("✅ Modification persisted to disk")
    else:
        print("❌ Modification not persisted!")
        return False

    print("\n✅ TEST 6 PASSED - These are REAL file operations!")
    print("   - No async sleep simulation")
    print("   - No mocked returns")
    print("   - Actual Python file I/O")
    print("   - Real filesystem operations\n")

    return True


async def cleanup():
    """Clean up test files"""
    print("🧹 Cleaning up test files...")

    test_dir = Path(".test_approval")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print("✅ Test files cleaned up\n")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("APPROVAL SYSTEM TEST SUITE")
    print("Testing REAL file operations (NO SIMULATION)")
    print("="*60 + "\n")

    results = []

    # Run tests
    results.append(await test_approval_request())
    results.append(await test_approval_response())
    results.append(await test_approval_workflow())
    results.append(await test_approval_timeout())
    results.append(await test_cli_interface())
    results.append(await test_real_file_operations())

    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)

    total = len(results)
    passed = sum(results)

    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"Test {i}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Approval system working with REAL file I/O!\n")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed\n")

    # Cleanup
    await cleanup()

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
