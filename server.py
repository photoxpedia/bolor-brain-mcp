#!/usr/bin/env python3
"""
Bolor Brain HTTP API Server

Exposes the reasoning engines via REST API for external applications.

Usage:
    python server.py --port 8080

Author: Bolorerdene Bundgaa
        https://bolor.me
"""

import argparse
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Any
import threading

from modules import (
    HybridReasoner,
    Fact, Rule, FactType,
    Node, Edge,
    Case,
    Hypothesis,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global brain instance
brain = HybridReasoner()
brain_lock = threading.RLock()


class BrainAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Brain API."""

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _json_response(self, data: Any, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(data, default=str).encode())

    def _error_response(self, message: str, status=400):
        self._json_response({"error": message}, status)

    def _read_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body.decode())

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self._set_headers(200)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._json_response({
                "name": "Bolor Brain API",
                "version": "1.0.0",
                "endpoints": [
                    "POST /reason",
                    "POST /add_fact",
                    "POST /add_case",
                    "POST /find_similar",
                    "POST /generate_hypotheses",
                    "POST /test_hypothesis",
                    "GET /stats",
                    "GET /health",
                ]
            })

        elif path == "/health":
            self._json_response({"status": "healthy"})

        elif path == "/stats":
            with brain_lock:
                stats = brain.get_stats()
            self._json_response(stats)

        else:
            self._error_response("Not found", 404)

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_body()
        except json.JSONDecodeError:
            self._error_response("Invalid JSON")
            return

        try:
            if path == "/reason":
                self._handle_reason(body)
            elif path == "/quick_reason":
                self._handle_quick_reason(body)
            elif path == "/add_fact":
                self._handle_add_fact(body)
            elif path == "/add_rule":
                self._handle_add_rule(body)
            elif path == "/add_node":
                self._handle_add_node(body)
            elif path == "/add_edge":
                self._handle_add_edge(body)
            elif path == "/add_case":
                self._handle_add_case(body)
            elif path == "/find_similar":
                self._handle_find_similar(body)
            elif path == "/generate_hypotheses":
                self._handle_generate_hypotheses(body)
            elif path == "/test_hypothesis":
                self._handle_test_hypothesis(body)
            elif path == "/find_path":
                self._handle_find_path(body)
            elif path == "/forward_chain":
                self._handle_forward_chain(body)
            elif path == "/clear":
                self._handle_clear(body)
            else:
                self._error_response("Not found", 404)
        except Exception as e:
            logger.exception(f"Error handling {path}")
            self._error_response(str(e), 500)

    # === Handlers ===

    def _handle_reason(self, body: dict):
        """Main reasoning endpoint."""
        query = body.get("query", "")
        problem_type = body.get("type")
        context = body.get("context", {})

        with brain_lock:
            result = brain.reason({
                "query": query,
                "type": problem_type,
                "context": context,
            })

        self._json_response({
            "problem_type": result.problem_type.value,
            "approaches_used": [a.value for a in result.approaches_used],
            "confidence": result.confidence,
            "combined_result": result.combined_result,
            "reasoning_trace": result.reasoning_trace,
            "processing_time": result.processing_time,
        })

    def _handle_quick_reason(self, body: dict):
        """Quick reasoning with just a query string."""
        query = body.get("query", "")

        with brain_lock:
            result = brain.quick_reason(query)

        self._json_response({"result": result})

    def _handle_add_fact(self, body: dict):
        """Add a fact to the symbolic reasoner."""
        subject = body.get("subject")
        predicate = body.get("predicate")
        obj = body.get("object")
        confidence = body.get("confidence", 1.0)

        if not all([subject, predicate, obj]):
            self._error_response("Missing subject, predicate, or object")
            return

        fact = Fact(subject, predicate, obj, confidence=confidence)

        with brain_lock:
            brain.symbolic.add_fact(fact)

        self._json_response({"success": True, "fact_id": fact.id})

    def _handle_add_rule(self, body: dict):
        """Add a rule to the symbolic reasoner."""
        name = body.get("name")
        conclusion = body.get("conclusion")
        priority = body.get("priority", 0)

        if not all([name, conclusion]):
            self._error_response("Missing name or conclusion")
            return

        # Simple rule that always fires (for demo)
        rule = Rule(
            name=name,
            conditions=[lambda f: True],
            conclusion_template=conclusion,
            priority=priority,
        )

        with brain_lock:
            brain.symbolic.add_rule(rule)

        self._json_response({"success": True, "rule_name": name})

    def _handle_add_node(self, body: dict):
        """Add a node to the knowledge graph."""
        node_id = body.get("id")
        label = body.get("label", node_id)
        node_type = body.get("type", "concept")
        properties = body.get("properties", {})

        if not node_id:
            self._error_response("Missing node id")
            return

        node = Node(node_id, label, node_type, properties)

        with brain_lock:
            brain.kg.add_node(node)

        self._json_response({"success": True, "node_id": node_id})

    def _handle_add_edge(self, body: dict):
        """Add an edge to the knowledge graph."""
        source = body.get("source")
        target = body.get("target")
        relation = body.get("relation", "related_to")
        weight = body.get("weight", 1.0)

        if not all([source, target]):
            self._error_response("Missing source or target")
            return

        edge = Edge(source, target, relation, weight)

        with brain_lock:
            brain.kg.add_edge(edge)

        self._json_response({"success": True})

    def _handle_add_case(self, body: dict):
        """Add a case to the case-based reasoner."""
        problem = body.get("problem", {})
        solution = body.get("solution", {})
        outcome = body.get("outcome", {})
        success = body.get("success", True)
        tags = body.get("tags", [])

        with brain_lock:
            case = brain.cbr.retain(
                problem=problem,
                solution=solution,
                outcome=outcome,
                success=success,
                tags=tags,
            )

        self._json_response({"success": True, "case_id": case.id})

    def _handle_find_similar(self, body: dict):
        """Find similar cases."""
        problem = body.get("problem", {})
        k = body.get("k", 3)

        with brain_lock:
            matches = brain.cbr.retrieve(problem, k=k)

        results = []
        for match in matches:
            results.append({
                "case_id": match.case.id,
                "similarity": match.similarity,
                "problem": match.case.problem,
                "solution": match.case.solution,
                "outcome": match.case.outcome,
                "success": match.case.success,
            })

        self._json_response({"matches": results})

    def _handle_generate_hypotheses(self, body: dict):
        """Generate hypotheses for an observation."""
        observation = body.get("observation", "")
        max_hypotheses = body.get("max", 5)

        with brain_lock:
            hypotheses = brain.hypothesis.generate_hypotheses(
                observation,
                max_hypotheses=max_hypotheses
            )

        results = []
        for h in hypotheses:
            results.append({
                "id": h.id,
                "statement": h.statement,
                "confidence": h.confidence,
                "status": h.status,
            })

        self._json_response({"hypotheses": results})

    def _handle_test_hypothesis(self, body: dict):
        """Test a hypothesis."""
        hypothesis_id = body.get("hypothesis_id")

        if not hypothesis_id:
            self._error_response("Missing hypothesis_id")
            return

        with brain_lock:
            result = brain.hypothesis.test_hypothesis(hypothesis_id)

        if result:
            self._json_response({
                "supported": result.supports,
                "confidence": result.confidence,
                "evidence": result.evidence,
            })
        else:
            self._error_response("Hypothesis not found", 404)

    def _handle_find_path(self, body: dict):
        """Find path between two nodes in knowledge graph."""
        source = body.get("source")
        target = body.get("target")

        if not all([source, target]):
            self._error_response("Missing source or target")
            return

        with brain_lock:
            path_result = brain.kg.find_path(source, target)

        if path_result and path_result.found:
            self._json_response({
                "found": True,
                "path": path_result.path,
                "total_weight": path_result.total_weight,
            })
        else:
            self._json_response({"found": False, "path": []})

    def _handle_forward_chain(self, body: dict):
        """Run forward chaining."""
        with brain_lock:
            result = brain.symbolic.forward_chain()

        derived = []
        for fact in result.derived:
            derived.append({
                "subject": fact.subject,
                "predicate": fact.predicate,
                "object": fact.object,
                "confidence": fact.confidence,
            })

        self._json_response({
            "derived_count": len(derived),
            "derived": derived,
        })

    def _handle_clear(self, body: dict):
        """Clear all brain state."""
        with brain_lock:
            brain.clear()

        self._json_response({"success": True})

    def log_message(self, format, *args):
        """Custom log format."""
        logger.info(f"{self.address_string()} - {format % args}")


def run_server(port: int = 8080):
    """Run the HTTP server."""
    server_address = ("", port)
    httpd = HTTPServer(server_address, BrainAPIHandler)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  Bolor Brain API Server                                      ║
║  http://localhost:{port}                                        ║
╠══════════════════════════════════════════════════════════════╣
║  Endpoints:                                                  ║
║    POST /reason           - Main reasoning                   ║
║    POST /add_fact         - Add symbolic fact                ║
║    POST /add_case         - Store case for learning          ║
║    POST /find_similar     - Find similar cases               ║
║    POST /generate_hypotheses - Generate hypotheses           ║
║    GET  /stats            - Get brain statistics             ║
║    GET  /health           - Health check                     ║
╚══════════════════════════════════════════════════════════════╝
""")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bolor Brain API Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run on")
    args = parser.parse_args()

    run_server(args.port)
