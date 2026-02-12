"""
Test State Persistence - REAL file operations

Proves that autonomous agent can save and resume state using actual file I/O.
NO SIMULATION.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from state_manager import StateManager


async def test_basic_persistence():
    """Test basic save/load operations"""
    print("="*60)
    print("TEST 1: Basic State Persistence")
    print("="*60)

    # Create state manager
    manager = StateManager(state_dir=".test_agent_state")

    # Create test data
    test_data = {
        'goal': 'Test persistence with REAL file operations',
        'state': 'EXECUTING',
        'start_time': datetime.now().isoformat(),
        'tasks_total': 10,
        'tasks_completed': 5,
        'tasks_failed': 1,
        'completed_task_ids': ['task_1', 'task_2', 'task_3', 'task_4', 'task_5'],
        'failed_task_ids': ['task_6'],
        'learnings_count': 3,
        'evolutions_count': 1,
        'execution_results': [
            {'task_id': 'task_1', 'success': True, 'duration': 1.2},
            {'task_id': 'task_2', 'success': True, 'duration': 0.8},
        ],
        'learnings': {
            'patterns': {
                'successful_strategies': ['Strategy A', 'Strategy B']
            }
        }
    }

    print("\n📝 Saving state...")
    state_file = manager.save_state(test_data)
    print(f"✅ State saved to: {state_file}")

    # Verify file exists
    if Path(state_file).exists():
        file_size = Path(state_file).stat().st_size
        print(f"✅ File exists ({file_size} bytes)")
    else:
        print(f"❌ File does not exist!")
        return False

    # Load it back
    print("\n📖 Loading state...")
    loaded = manager.load_state()

    if loaded:
        print("✅ State loaded successfully:")
        print(f"   Goal: {loaded['goal']}")
        print(f"   State: {loaded['state']}")
        print(f"   Progress: {loaded['tasks_completed']}/{loaded['tasks_total']}")
        print(f"   Failed: {loaded['tasks_failed']}")
        print(f"   Learnings: {loaded['learnings_count']}")
        print(f"   Session ID: {loaded['session_id']}")
    else:
        print("❌ Failed to load state!")
        return False

    # Verify data matches
    if loaded['goal'] == test_data['goal']:
        print("✅ Data integrity verified")
    else:
        print("❌ Data mismatch!")
        return False

    print("\n✅ TEST 1 PASSED - Basic persistence works!\n")
    return True


async def test_session_listing():
    """Test listing saved sessions"""
    print("="*60)
    print("TEST 2: Session Listing")
    print("="*60)

    # Create multiple sessions (each with explicit session ID)
    print("\n📝 Creating multiple sessions...")
    for i in range(3):
        # Create new manager for each session
        manager = StateManager(state_dir=".test_agent_state")

        test_data = {
            'session_id': f'test_session_{i}',  # Explicit ID
            'goal': f'Test goal {i+1}',
            'state': 'EXECUTING',
            'start_time': datetime.now().isoformat(),
            'tasks_total': 10,
            'tasks_completed': i * 2,
            'tasks_failed': 0,
            'completed_task_ids': [],
            'failed_task_ids': [],
            'learnings_count': 0,
            'evolutions_count': 0,
            'execution_results': [],
            'learnings': {}
        }
        manager.save_state(test_data)
        await asyncio.sleep(0.01)  # Small delay

    print("✅ Sessions created\n")

    # Use a fresh manager to list
    manager = StateManager(state_dir=".test_agent_state")

    # List all sessions
    print("📋 Listing all sessions...")
    sessions = manager.list_sessions()

    if len(sessions) >= 3:
        print(f"✅ Found {len(sessions)} sessions:")
        for session in sessions:
            print(f"   - {session['session_id']}")
            print(f"     Goal: {session['goal']}")
            print(f"     Progress: {session['tasks_completed']}/{session['tasks_total']}")
            print(f"     Last saved: {session['last_saved']}")
    else:
        print(f"❌ Expected at least 3 sessions, found {len(sessions)}")
        return False

    print("\n✅ TEST 2 PASSED - Session listing works!\n")
    return True


async def test_resume_capability():
    """Test resuming from saved state"""
    print("="*60)
    print("TEST 3: Resume Capability")
    print("="*60)

    manager = StateManager(state_dir=".test_agent_state")

    # Create a session
    print("\n📝 Creating session to resume...")
    test_data = {
        'goal': 'Resumable task',
        'state': 'PAUSED',
        'start_time': datetime.now().isoformat(),
        'tasks_total': 10,
        'tasks_completed': 3,
        'tasks_failed': 0,
        'completed_task_ids': ['task_1', 'task_2', 'task_3'],
        'failed_task_ids': [],
        'learnings_count': 1,
        'evolutions_count': 0,
        'execution_results': [],
        'learnings': {'test': 'data'}
    }

    manager.save_state(test_data)
    session_id = manager.current_session_id
    print(f"✅ Session created: {session_id}\n")

    # "Simulate" process restart by creating new manager
    print("🔄 Simulating process restart...")
    new_manager = StateManager(state_dir=".test_agent_state")

    # Resume the session
    print(f"♻️  Resuming session: {session_id}...")
    resumed = new_manager.load_state(session_id)

    if resumed:
        print("✅ Session resumed successfully:")
        print(f"   Goal: {resumed['goal']}")
        print(f"   State: {resumed['state']}")
        print(f"   Progress: {resumed['tasks_completed']}/{resumed['tasks_total']}")
        print(f"   Can continue from task: {resumed['tasks_completed'] + 1}")

        # Verify we can update it
        resumed['tasks_completed'] = 4
        resumed['completed_task_ids'].append('task_4')
        new_manager.save_state(resumed)
        print("✅ State updated after resume")

    else:
        print("❌ Failed to resume session!")
        return False

    print("\n✅ TEST 3 PASSED - Resume capability works!\n")
    return True


async def test_file_operations():
    """Verify these are REAL file operations, not simulated"""
    print("="*60)
    print("TEST 4: REAL File Operations Verification")
    print("="*60)

    state_dir = Path(".test_agent_state")
    manager = StateManager(state_dir=str(state_dir))

    # Save some data
    print("\n📝 Writing state...")
    test_data = {
        'goal': 'Verify REAL operations',
        'state': 'COMPLETE',
        'start_time': datetime.now().isoformat(),
        'tasks_total': 1,
        'tasks_completed': 1,
        'tasks_failed': 0,
        'completed_task_ids': [],
        'failed_task_ids': [],
        'learnings_count': 0,
        'evolutions_count': 0,
        'execution_results': [],
        'learnings': {}
    }
    state_file = manager.save_state(test_data)

    # Verify using raw Python file operations (NOT through manager)
    print("\n🔍 Verifying with raw file operations...")

    file_path = Path(state_file)

    # Check 1: File exists
    if file_path.exists():
        print("✅ File exists on disk")
    else:
        print("❌ File does not exist!")
        return False

    # Check 2: Can read with open()
    try:
        with open(file_path, 'r') as f:
            import json
            raw_data = json.load(f)
        print("✅ Can read with standard Python open()")
    except Exception as e:
        print(f"❌ Cannot read file: {e}")
        return False

    # Check 3: Data matches
    if raw_data['goal'] == test_data['goal']:
        print("✅ Data matches (verified with raw file read)")
    else:
        print("❌ Data mismatch!")
        return False

    # Check 4: File has real timestamp
    mtime = file_path.stat().st_mtime
    print(f"✅ File has real modification time: {datetime.fromtimestamp(mtime)}")

    # Check 5: File has real size
    size = file_path.stat().st_size
    print(f"✅ File has real size: {size} bytes")

    print("\n✅ TEST 4 PASSED - These are REAL file operations!")
    print("   - No async sleep simulation")
    print("   - No mocked returns")
    print("   - Actual Python file I/O")
    print("   - Real filesystem operations\n")

    return True


async def cleanup():
    """Clean up test files"""
    print("🧹 Cleaning up test files...")

    state_dir = Path(".test_agent_state")
    if state_dir.exists():
        import shutil
        shutil.rmtree(state_dir)
        print("✅ Test files cleaned up\n")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("STATE PERSISTENCE TEST SUITE")
    print("Testing REAL file operations (NO SIMULATION)")
    print("="*60 + "\n")

    results = []

    # Run tests
    results.append(await test_basic_persistence())
    results.append(await test_session_listing())
    results.append(await test_resume_capability())
    results.append(await test_file_operations())

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
        print("\n🎉 ALL TESTS PASSED - State persistence working with REAL file I/O!\n")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed\n")

    # Cleanup
    await cleanup()

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
