# Common Issues & Solutions 🛠️

This guide covers the most frequently encountered issues when working with Bolor Brain MCP and provides step-by-step solutions.

## 🚨 Quick Diagnostic Commands

Before diving into specific issues, run these diagnostic commands to get system overview:

```bash
# System health check
python test.py

# Server status check
curl -s http://localhost:3000/health | jq

# Check logs for errors
tail -n 50 logs/error.log

# Verify dependencies
npm list --depth=0
pip list | grep -E "(sqlite|asyncio)"
```

---

## 💾 Memory System Issues

### Issue: "no such module: fts5" Error

**Symptoms**: 
```
sqlite3.OperationalError: no such module: fts5
```

**Cause**: SQLite installation lacks FTS5 (Full-Text Search) support

**Solutions**:

#### Option 1: Update SQLite (Recommended)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install sqlite3 libsqlite3-dev

# macOS with Homebrew
brew update
brew install sqlite

# CentOS/RHEL
sudo yum update
sudo yum install sqlite-devel

# Verify FTS5 support
sqlite3 -cmd ".load fts5" -cmd ".exit" 2>/dev/null && echo "FTS5 supported" || echo "FTS5 not supported"
```

#### Option 2: Compile SQLite with FTS5
```bash
# Download and compile SQLite with FTS5
wget https://sqlite.org/2024/sqlite-autoconf-3440200.tar.gz
tar xzf sqlite-autoconf-3440200.tar.gz
cd sqlite-autoconf-3440200
./configure --enable-fts5
make
sudo make install
```

#### Option 3: Use Alternative Installation
```bash
# Install via conda (if using Anaconda)
conda install -c conda-forge sqlite

# Or use alternative Python SQLite
pip uninstall sqlite3  # If installed
pip install pysqlite3-binary
```

### Issue: Database Corruption

**Symptoms**:
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solutions**:

#### Backup and Repair
```bash
# Create backup
cp memory.db memory_backup.db

# Attempt repair
sqlite3 memory.db ".recover" | sqlite3 memory_repaired.db

# If repair works, replace original
mv memory_repaired.db memory.db
```

#### Fresh Database
```bash
# Remove corrupted database
rm memory.db

# Restart brain to recreate
python -c "
from modules.memory import AdvancedMemorySystem
import asyncio
async def recreate():
    memory = AdvancedMemorySystem()
    print('Database recreated successfully')
asyncio.run(recreate())
"
```

### Issue: Memory Operations Too Slow

**Symptoms**: Memory storage/retrieval takes >5 seconds

**Diagnostic**:
```python
import time
import asyncio
from modules.memory import AdvancedMemorySystem

async def test_performance():
    memory = AdvancedMemorySystem()
    
    # Test storage speed
    start = time.time()
    memory_id = await memory.store_memory("Test content", "episodic", 0.5)
    storage_time = time.time() - start
    
    # Test retrieval speed  
    start = time.time()
    memories = await memory.retrieve_memories("Test", 1)
    retrieval_time = time.time() - start
    
    print(f"Storage time: {storage_time:.3f}s")
    print(f"Retrieval time: {retrieval_time:.3f}s")
    
    if storage_time > 1.0:
        print("⚠️ Storage is slow")
    if retrieval_time > 1.0:
        print("⚠️ Retrieval is slow")

asyncio.run(test_performance())
```

**Solutions**:

#### Optimize Database
```bash
# Vacuum database
sqlite3 memory.db "VACUUM;"

# Reindex FTS5
sqlite3 memory.db "INSERT INTO memory_search(memory_search) VALUES('rebuild');"

# Analyze query plans
sqlite3 memory.db "EXPLAIN QUERY PLAN SELECT * FROM memories WHERE content MATCH 'test';"
```

#### Increase Memory Cache
```python
# Add to memory module initialization
import sqlite3
conn = sqlite3.connect("memory.db")
conn.execute("PRAGMA cache_size=10000;")  # Increase cache
conn.execute("PRAGMA temp_store=memory;")  # Use memory for temp
```

---

## 🤔 Reasoning Engine Issues

### Issue: Reasoning Timeout

**Symptoms**:
```
asyncio.TimeoutError: Reasoning operation timed out after 30 seconds
```

**Diagnostic**:
```python
async def test_reasoning_performance():
    from server import BrainMCP
    import time
    
    brain = BrainMCP()
    await brain.initialize()
    
    problems = [
        "Simple test problem",
        "Analyze the impact of quantum computing on cryptography and propose mitigation strategies for current encryption systems while considering the timeline for quantum supremacy and the development of post-quantum cryptographic algorithms",
        "What is 2+2?"
    ]
    
    for problem in problems:
        start = time.time()
        try:
            result = await brain.solve_complex_problem(problem)
            duration = time.time() - start
            print(f"Problem: {problem[:50]}...")
            print(f"Duration: {duration:.2f}s")
            print(f"Strategy: {result.strategy}")
            print(f"Success: ✅")
        except asyncio.TimeoutError:
            duration = time.time() - start
            print(f"Problem: {problem[:50]}...")
            print(f"Duration: {duration:.2f}s (TIMEOUT)")
            print(f"Success: ❌")
        print("-" * 50)

asyncio.run(test_reasoning_performance())
```

**Solutions**:

#### Increase Timeout
```python
# Method 1: Environment variable
import os
os.environ['REASONING_TIMEOUT'] = '60'  # 60 seconds

# Method 2: Direct configuration
brain.advanced_reasoning.reasoning_timeout = 60

# Method 3: Per-operation timeout
result = await brain.solve_complex_problem(
    problem, 
    context={'timeout': 60}
)
```

#### Break Complex Problems Down
```python
# Instead of one complex problem
complex_problem = "Analyze quantum computing impact and propose solutions"

# Break into smaller problems
sub_problems = [
    "What is the current state of quantum computing?",
    "How does quantum computing threaten current cryptography?", 
    "What are post-quantum cryptographic algorithms?",
    "What is the timeline for quantum supremacy?",
    "How can organizations prepare for the quantum threat?"
]

results = []
for sub_problem in sub_problems:
    result = await brain.solve_complex_problem(sub_problem)
    results.append(result)

# Then synthesize
synthesis_problem = f"Synthesize these insights: {'; '.join([r.final_conclusion for r in results])}"
final_result = await brain.solve_complex_problem(synthesis_problem)
```

### Issue: Low Reasoning Confidence

**Symptoms**: Reasoning confidence consistently below 0.6

**Diagnostic**:
```python
async def analyze_reasoning_confidence():
    brain = BrainMCP()
    await brain.initialize()
    
    test_problems = [
        "How to optimize database performance?",
        "What are the ethical implications of AI?",
        "Design a user authentication system",
        "Create an innovative mobile app feature",
        "Evaluate this business strategy: focus on subscription model"
    ]
    
    for problem in test_problems:
        result = await brain.solve_complex_problem(problem)
        print(f"Problem: {problem}")
        print(f"Strategy: {result.strategy}")
        print(f"Confidence: {result.overall_confidence:.3f}")
        print(f"Steps: {len(result.steps)}")
        
        # Analyze step confidence
        step_confidences = [step.confidence for step in result.steps]
        print(f"Step confidence range: {min(step_confidences):.3f} - {max(step_confidences):.3f}")
        print("-" * 50)

asyncio.run(analyze_reasoning_confidence())
```

**Solutions**:

#### Provide Rich Context
```python
# Instead of basic problem
problem = "How to optimize database performance?"

# Provide rich context
context = {
    "database_type": "postgresql", 
    "current_performance": "slow_queries_over_5s",
    "data_size": "100GB",
    "query_types": ["analytical", "transactional"],
    "constraints": ["budget_limited", "minimal_downtime"],
    "current_setup": "single_server_no_indexing"
}

result = await brain.solve_complex_problem(problem, context)
# Confidence should be higher with rich context
```

#### Pre-load Relevant Memories
```python
# Store relevant background knowledge
await brain.store_memory(
    "Database optimization involves indexing, query optimization, hardware scaling, and connection pooling",
    "semantic", 
    0.9,
    {"domain": "database", "topic": "optimization"}
)

await brain.store_memory(
    "PostgreSQL specific optimizations include shared_buffers tuning, effective_cache_size, and vacuum optimization",
    "procedural",
    0.8,
    {"database": "postgresql", "type": "optimization"}
)

# Then solve problem - should have higher confidence
result = await brain.solve_complex_problem(problem, context)
```

---

## 🔮 Predictive Intelligence Issues

### Issue: No Predictions Generated

**Symptoms**: `predict_user_needs()` returns empty list

**Diagnostic**:
```python
async def test_prediction_system():
    brain = BrainMCP()
    await brain.initialize()
    
    # Test with minimal context
    minimal_context = {"activity": "testing"}
    predictions1 = await brain.predict_user_needs(minimal_context)
    print(f"Minimal context predictions: {len(predictions1)}")
    
    # Test with rich context  
    rich_context = {
        "current_activity": "debugging_python_code",
        "time_of_day": "afternoon",
        "recent_topics": ["error_handling", "unit_testing", "performance"],
        "experience_level": "intermediate",
        "available_time": "2_hours",
        "preferred_learning_style": "hands_on"
    }
    predictions2 = await brain.predict_user_needs(rich_context, history_depth=5)
    print(f"Rich context predictions: {len(predictions2)}")
    
    # Check reasoning history
    if hasattr(brain, 'advanced_reasoning'):
        reasoning_count = len(brain.advanced_reasoning.reasoning_history)
        print(f"Reasoning history count: {reasoning_count}")

asyncio.run(test_prediction_system())
```

**Solutions**:

#### Build Reasoning History
```python
# Predictions improve with reasoning history
problems_to_build_history = [
    "How to debug Python code effectively?",
    "What are best practices for unit testing?", 
    "How to optimize Python performance?",
    "What tools help with code debugging?",
    "How to handle errors gracefully in Python?"
]

for problem in problems_to_build_history:
    await brain.solve_complex_problem(problem)

# Now try predictions again
predictions = await brain.predict_user_needs(rich_context)
print(f"Predictions after history: {len(predictions)}")
```

#### Provide Temporal Context
```python
import time

# Add temporal information
context_with_time = {
    **rich_context,
    "session_start_time": time.time() - 3600,  # 1 hour ago
    "recent_session_pattern": "morning_learning_afternoon_coding",
    "typical_session_length": "3_hours",
    "energy_level": "high"
}

predictions = await brain.predict_user_needs(context_with_time)
```

### Issue: Irrelevant Predictions

**Symptoms**: Predictions don't match user context or needs

**Solutions**:

#### Filter and Rank Predictions
```python
def filter_relevant_predictions(predictions, user_context):
    """Filter predictions based on user context relevance"""
    
    relevant_predictions = []
    context_keywords = set(user_context.get("recent_topics", []))
    current_activity = user_context.get("current_activity", "").lower()
    
    for pred in predictions:
        content_keywords = set(pred.predicted_content.lower().split())
        
        # Check relevance score
        relevance_score = len(context_keywords.intersection(content_keywords)) / len(context_keywords) if context_keywords else 0
        
        # Check activity alignment
        activity_match = current_activity in pred.predicted_content.lower()
        
        # Keep if confident, relevant, or activity-aligned
        if (pred.confidence > 0.7) or (relevance_score > 0.3) or activity_match:
            relevant_predictions.append(pred)
    
    return sorted(relevant_predictions, key=lambda p: p.confidence, reverse=True)

# Use filtered predictions
all_predictions = await brain.predict_user_needs(context)
relevant_predictions = filter_relevant_predictions(all_predictions, context)
```

---

## 🧬 Evolutionary Intelligence Issues

### Issue: Capabilities Not Evolving

**Symptoms**: `evolve_cognitive_capabilities()` returns unchanged values

**Diagnostic**:
```python
async def test_evolution():
    brain = BrainMCP()
    await brain.initialize()
    
    initial_state = {
        "programming": 0.5,
        "creativity": 0.4,
        "problem_solving": 0.6
    }
    
    print(f"Initial state: {initial_state}")
    
    evolved_state = await brain.evolve_cognitive_capabilities(
        current_state=initial_state,
        target_improvements=["creativity", "problem_solving"],
        evolution_cycles=5
    )
    
    print(f"Evolved state: {evolved_state}")
    
    # Check for changes
    changes = {k: evolved_state[k] - initial_state[k] for k in initial_state}
    print(f"Changes: {changes}")
    
    if all(change < 0.01 for change in changes.values()):
        print("⚠️ No significant evolution occurred")
    else:
        print("✅ Evolution detected")

asyncio.run(test_evolution())
```

**Solutions**:

#### Increase Evolution Parameters
```python
# Increase mutation rate and cycles
evolved_state = await brain.evolve_cognitive_capabilities(
    current_state=initial_state,
    target_improvements=["creativity", "problem_solving"],
    evolution_cycles=10,
    mutation_rate=0.2  # If supported
)
```

#### Provide Evolution Context
```python
# Add context for better evolution
evolution_context = {
    **initial_state,
    "learning_experiences": ["completed_course", "solved_difficult_problem"],
    "practice_hours": 50,
    "feedback_quality": "positive",
    "challenge_level": "appropriate"
}

evolved_state = await brain.evolve_cognitive_capabilities(evolution_context)
```

---

## 🌐 Network & Integration Issues

### Issue: MCP Server Connection Failed

**Symptoms**: 
```
ConnectionError: Unable to connect to MCP server at localhost:3000
```

**Diagnostic**:
```bash
# Check if server is running
curl -f http://localhost:3000/health

# Check port usage
netstat -tlnp | grep :3000
lsof -i :3000

# Check server logs
tail -f logs/server.log

# Test with telnet
telnet localhost 3000
```

**Solutions**:

#### Start/Restart Server
```bash
# Kill existing process
pkill -f "node index.js"

# Start fresh
npm start

# Or with debugging
DEBUG=* npm start
```

#### Check Port Conflicts
```bash
# Find process using port 3000
lsof -ti:3000

# Kill conflicting process
kill $(lsof -ti:3000)

# Or use different port
PORT=3001 npm start
```

#### Firewall Issues
```bash
# Check firewall status (Ubuntu/Debian)
sudo ufw status

# Allow port if needed
sudo ufw allow 3000

# Check iptables (CentOS/RHEL)
sudo iptables -L | grep 3000
```

### Issue: Claude Desktop Integration Failed

**Symptoms**: Claude Desktop shows "MCP server failed to start"

**Diagnostic**:
```bash
# Check Claude Desktop logs (macOS)
tail -f ~/Library/Logs/Claude/mcp-server.log

# Check configuration syntax
cat ~/.claude/config.json | jq .

# Test configuration manually
cd /path/to/bolor-brain-mcp
node index.js --test
```

**Solutions**:

#### Fix Configuration Path
```json
{
  "mcpServers": {
    "bolor-brain": {
      "command": "node",
      "args": ["index.js"],
      "cwd": "/absolute/path/to/bolor-brain-mcp",
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

#### Add Error Handling
```javascript
// In index.js, add better error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});
```

---

## 📊 Performance Issues

### Issue: High Memory Usage

**Symptoms**: Node.js process using >2GB RAM

**Diagnostic**:
```bash
# Monitor memory usage
ps aux | grep node
top -p $(pgrep node)

# Check Node.js heap usage
node --inspect index.js
# Then connect with Chrome DevTools
```

**Solutions**:

#### Increase Node.js Memory Limit
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm start
```

#### Add Memory Cleanup
```javascript
// Add to server
setInterval(() => {
  if (global.gc) {
    global.gc();
  }
}, 30000); // Force GC every 30 seconds

// Start with garbage collection
node --expose-gc index.js
```

#### Optimize Memory System
```python
# Add memory cleanup to brain
class BrainMCP:
    async def cleanup_memory(self):
        """Clean up old, low-importance memories"""
        if hasattr(self, 'memory'):
            # Remove memories older than 90 days with importance < 0.3
            cutoff_time = time.time() - (90 * 24 * 60 * 60)
            await self.memory.cleanup_old_memories(cutoff_time, min_importance=0.3)
```

### Issue: Slow Response Times

**Symptoms**: API responses taking >5 seconds

**Diagnostic**:
```python
import time
import asyncio

async def benchmark_operations():
    brain = BrainMCP()
    await brain.initialize()
    
    operations = [
        ("Memory Storage", lambda: brain.store_memory("Test content", "episodic", 0.5)),
        ("Memory Retrieval", lambda: brain.retrieve_memories("test", 5)),
        ("Basic Reasoning", lambda: brain.solve_complex_problem("What is 2+2?")),
        ("Complex Reasoning", lambda: brain.solve_complex_problem("Analyze the pros and cons of remote work")),
        ("Prediction", lambda: brain.predict_user_needs({"activity": "testing"}))
    ]
    
    for name, operation in operations:
        start = time.time()
        try:
            await operation()
            duration = time.time() - start
            status = "✅" if duration < 2.0 else "⚠️" if duration < 5.0 else "❌"
            print(f"{status} {name}: {duration:.3f}s")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

asyncio.run(benchmark_operations())
```

**Solutions**:

#### Add Caching
```python
from functools import lru_cache

class CachedBrain(BrainMCP):
    @lru_cache(maxsize=100)
    def cached_reasoning(self, problem_hash):
        # Cache reasoning results for repeated problems
        pass
    
    async def solve_complex_problem(self, problem, context=None):
        problem_hash = hash(problem + str(context))
        cached_result = self.cached_reasoning(problem_hash)
        if cached_result:
            return cached_result
        
        result = await super().solve_complex_problem(problem, context)
        self.cached_reasoning(problem_hash, result)
        return result
```

#### Optimize Database Queries
```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp);

-- Optimize FTS5 table
CREATE INDEX IF NOT EXISTS idx_memory_search_content ON memory_search(content);
```

---

## 🔧 Development & Debugging

### Issue: Import Errors

**Symptoms**: 
```
ModuleNotFoundError: No module named 'modules.memory'
```

**Solutions**:

#### Check Python Path
```bash
# Ensure you're in the correct directory
pwd
ls modules/

# Add to Python path if needed
export PYTHONPATH="${PYTHONPATH}:/path/to/bolor-brain-mcp"

# Or use relative imports
python -m server
```

#### Virtual Environment Issues
```bash
# Activate virtual environment
source venv/bin/activate

# Verify environment
which python
which pip

# Reinstall dependencies
pip install -r requirements_mcp.txt
```

### Issue: Debug Mode Not Working

**Solutions**:

#### Enable Debug Logging
```bash
# Set debug environment
export DEBUG=bolor-brain:*
export LOG_LEVEL=debug

# Start with debugging
node --inspect=0.0.0.0:9229 index.js
```

#### Add Debug Prints
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In modules
logger = logging.getLogger(__name__)
logger.debug(f"Processing: {variable}")
```

---

## 🚨 Emergency Recovery

### Complete System Reset

If nothing else works, perform a complete system reset:

```bash
# 1. Stop all processes
pkill -f "node index.js"
pkill -f "python"

# 2. Backup data
cp -r data/ data_backup/
cp -r logs/ logs_backup/

# 3. Clean installation
rm -rf node_modules/
rm -rf venv/
rm memory.db

# 4. Fresh install
python -m venv venv
source venv/bin/activate
pip install -r requirements_mcp.txt
npm install

# 5. Test basic functionality
python test.py

# 6. Start server
npm start
```

### Data Recovery

If you lose important memories:

```bash
# Check for backup files
ls data_backup/
ls *.db.backup

# Recover from WAL file
sqlite3 memory.db ".recover" > recovered_data.sql
sqlite3 new_memory.db < recovered_data.sql
```

---

## 📞 Getting Help

### Information to Collect Before Asking for Help

```bash
# System information
echo "OS: $(uname -a)"
echo "Node.js: $(node --version)"
echo "Python: $(python --version)"
echo "npm: $(npm --version)"

# Project information
echo "Project directory: $(pwd)"
echo "Git commit: $(git rev-parse HEAD)"
echo "File permissions: $(ls -la)"

# Runtime information
echo "Memory usage: $(free -h)"
echo "Disk space: $(df -h .)"
echo "Running processes: $(ps aux | grep -E '(node|python)')"

# Recent logs
echo "Recent errors:"
tail -n 20 logs/error.log
```

### Support Channels

1. **GitHub Issues**: Report bugs and feature requests
2. **Documentation**: Check all documentation in `docs/` 
3. **Community**: Join discussions and get help
4. **Professional Support**: For enterprise deployments

---

**🚀 Issues resolved? Great! Continue exploring [Advanced Topics](../advanced/) or check out [Performance Optimization](../development/performance.md)! 🧠✨**