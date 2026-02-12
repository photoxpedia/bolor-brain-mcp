#!/usr/bin/env python3
"""
Quick test to verify MCP server tools are properly defined.
"""

import asyncio
from mcp_server import BolorBrainServer

async def test_server():
    """Test that server initializes and has tools."""
    print("Testing Bolor Brain MCP Server...")

    server = BolorBrainServer()
    print("✓ Server initialized")

    # Check server attributes
    print(f"✓ Server name: {server.server.name}")

    # Verify key methods exist
    assert hasattr(server, '_reason_hybrid'), "Missing _reason_hybrid method"
    assert hasattr(server, '_reason_symbolic'), "Missing _reason_symbolic method"
    assert hasattr(server, '_reason_knowledge_graph'), "Missing _reason_knowledge_graph method"
    assert hasattr(server, '_reason_case_based'), "Missing _reason_case_based method"
    assert hasattr(server, '_reason_hypothesis'), "Missing _reason_hypothesis method"
    assert hasattr(server, '_reason_analogical'), "Missing _reason_analogical method"
    assert hasattr(server, '_store_case'), "Missing _store_case method"
    assert hasattr(server, '_add_knowledge'), "Missing _add_knowledge method"
    assert hasattr(server, '_get_stats'), "Missing _get_stats method"
    print("✓ All 9 tool methods present")

    # Test a simple reasoning call
    print("\n Testing hybrid reasoning...")
    result = await server._reason_hybrid({
        "query": "Why is Python popular?",
        "context": {}
    })
    print(f"✓ Reasoning works! Problem type: {result['problem_type']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Approaches used: {result['approaches_used']}")

    return True

if __name__ == "__main__":
    result = asyncio.run(test_server())
    if result:
        print("\n✓ MCP Server test PASSED")
    else:
        print("\n✗ MCP Server test FAILED")
        exit(1)
