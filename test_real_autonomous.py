#!/usr/bin/env python3
"""
Test autonomous agent with REAL task

Task: Create a GETTING_STARTED.md guide for the project
This tests the full autonomous loop with real goal
"""

import asyncio
from autonomous_loop import AutonomousAgent

async def main():
    """Run autonomous agent with real task"""

    # Initialize agent
    agent = AutonomousAgent()

    # Real task: Create getting started guide
    goal = """
    Create a GETTING_STARTED.md file for Bolor Brain MCP project.

    The guide should include:
    - Quick installation (3 steps max)
    - First autonomous task example
    - First reasoning task example
    - What to try next
    - Troubleshooting tips

    Target audience: Developers trying Bolor Brain for the first time.
    Keep it concise and actionable.
    """

    print("="*60)
    print("REAL AUTONOMOUS TASK TEST")
    print("="*60)
    print(f"\nGoal: Create GETTING_STARTED.md guide")
    print(f"\nStarting autonomous execution...\n")
    print("="*60)
    print()

    # Run autonomously
    try:
        report = await agent.run_autonomous(goal)

        print("\n" + "="*60)
        print("AUTONOMOUS EXECUTION COMPLETE")
        print("="*60)
        print(f"\n✅ Goal: {report['goal'][:50]}...")
        print(f"⏱️  Duration: {report['duration']}")
        print(f"📊 Tasks completed: {report['tasks_completed']}/{report['tasks_total']}")
        print(f"📈 Success rate: {report['success_rate']:.1%}")
        print(f"📚 Learnings stored: {report['learnings_count']}")
        print(f"🔄 Evolutions: {report['evolutions_count']}")

        # Check if file was created
        import os
        if os.path.exists("GETTING_STARTED.md"):
            print(f"\n✅ GETTING_STARTED.md created successfully!")

            # Show first few lines
            with open("GETTING_STARTED.md", "r") as f:
                lines = f.readlines()[:15]

            print(f"\nFirst 15 lines of created file:")
            print("-" * 60)
            for line in lines:
                print(line.rstrip())
            print("-" * 60)
        else:
            print(f"\n⚠️  GETTING_STARTED.md not found (simulated execution)")

        print(f"\n{'='*60}")
        print("TEST COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
