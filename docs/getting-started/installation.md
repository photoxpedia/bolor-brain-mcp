# Installation Guide 🚀

This guide walks you through installing and setting up Bolor Brain MCP from basic installation to advanced deployment scenarios.

## 📋 Prerequisites

### System Requirements
- **Python 3.8+** (Python 3.9+ recommended)
- **Node.js 16+** (for MCP server functionality)
- **Git** (for cloning repository)
- **SQLite 3.35+** (usually included with Python)
- **Minimum 2GB RAM** (4GB+ recommended for advanced tiers)
- **Minimum 1GB disk space**

### Operating System Support
- ✅ **Linux** (Ubuntu 20.04+, CentOS 8+)
- ✅ **macOS** (10.15+, Apple Silicon supported)
- ✅ **Windows** (Windows 10+, WSL2 recommended)

## 🎯 Quick Installation (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/photoxpedia/bolor-brain-mcp.git
cd bolor-brain-mcp
```

### 2. Install Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements_mcp.txt
```

### 3. Install Node.js Dependencies
```bash
npm install
```

### 4. Verify Installation
```bash
# Test the cognitive modules
python test.py

# Expected output:
# 🧠 Bolor Brain MCP - Modular Architecture Test Suite
# ============================================================
# ✅ All 7-tier cognitive modules imported successfully
# ... (testing all 7 tiers)
# 📈 Overall Success Rate: 100.0%
# 🌟 Modular architecture is ready for deployment!
```

### 5. Start MCP Server
```bash
node index.js
```

🎉 **Success!** Your Bolor Brain MCP system is now running and ready for cognitive operations.

---

## 📦 Detailed Installation Steps

### Python Environment Setup

#### Option 1: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv bolor-brain-env

# Activate virtual environment
# Linux/macOS:
source bolor-brain-env/bin/activate
# Windows:
bolor-brain-env\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements_mcp.txt
```

#### Option 2: Using Conda
```bash
# Create conda environment
conda create -n bolor-brain python=3.9
conda activate bolor-brain

# Install dependencies
pip install -r requirements_mcp.txt
```

#### Option 3: System-wide Installation (Not Recommended)
```bash
pip install -r requirements_mcp.txt
```

### Node.js Setup

#### Option 1: Using Node Version Manager (Recommended)
```bash
# Install nvm (Linux/macOS)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Restart terminal or source profile
source ~/.bashrc

# Install and use Node.js
nvm install 18
nvm use 18

# Install dependencies
npm install
```

#### Option 2: Direct Installation
Download Node.js from [nodejs.org](https://nodejs.org/) and install, then:
```bash
npm install
```

---

## 🔧 Configuration

### Database Setup
The system uses SQLite with FTS5 support. No additional setup required, but you can customize:

```python
# In modules/memory.py, modify these settings:
DATABASE_PATH = "memory.db"  # Custom database location
MEMORY_TABLE = "memories"    # Custom table name
```

### MCP Server Configuration
Edit `server.json` to customize MCP server behavior:

```json
{
  "name": "bolor-brain",
  "version": "1.2.0",
  "description": "7-Tier Universal Intelligence MCP Server",
  "tools": {
    "cognitive_tiers": 7,
    "max_reasoning_depth": 10,
    "memory_retention_days": 365
  }
}
```

### Environment Variables
Create `.env` file for custom configuration:

```bash
# Database settings
DATABASE_PATH=./data/memory.db
LOG_LEVEL=INFO

# Cognitive settings
MAX_MEMORY_SIZE=10000
REASONING_TIMEOUT=30
PREDICTION_HORIZON=7

# Advanced settings
QUANTUM_SIMULATION=true
COLLECTIVE_NETWORK=false
UNIVERSAL_ACCESS=true
```

---

## 🧪 Verification & Testing

### Basic Functionality Test
```bash
python test.py
```

### Individual Module Testing
```bash
# Test specific cognitive tiers
python -c "from modules.memory import AdvancedMemorySystem; print('Memory module OK')"
python -c "from modules.reasoning import AdvancedReasoningEngine; print('Reasoning module OK')"
python -c "from modules.predictive import PredictiveIntelligenceEngine; print('Predictive module OK')"
```

### MCP Server Test
```bash
# Start server in test mode
node index.js --test

# Or test with curl
curl -X POST http://localhost:3000/test -H "Content-Type: application/json" -d '{"test": true}'
```

### Memory System Test
```bash
python -c "
import asyncio
from modules.memory import AdvancedMemorySystem

async def test_memory():
    memory = AdvancedMemorySystem()
    await memory.store_memory('Test memory', 'episodic', 0.8)
    results = await memory.retrieve_memories('Test', 1)
    print(f'Memory test: {len(results)} memories retrieved')

asyncio.run(test_memory())
"
```

---

## 🐳 Docker Installation (Alternative)

### Quick Docker Setup
```bash
# Build Docker image
docker build -t bolor-brain-mcp .

# Run container
docker run -p 3000:3000 -v $(pwd)/data:/app/data bolor-brain-mcp
```

### Docker Compose
Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  bolor-brain:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_PATH=/app/data/memory.db
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

---

## 🔍 Troubleshooting Installation

### Common Issues

#### Python Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

#### SQLite FTS5 Not Available
```bash
# Error: no such module: fts5
# Solution: Update SQLite or use system package
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install sqlite3

# macOS with Homebrew:
brew install sqlite
```

#### Node.js Version Issues
```bash
# Error: Unsupported Node.js version
# Solution: Use Node 16+
node --version  # Check version
nvm install 18  # Install newer version
```

#### Permission Errors
```bash
# Error: Permission denied
# Solution: Fix file permissions
chmod +x index.js
chown -R $USER:$USER .
```

#### Memory/Performance Issues
```bash
# Error: Out of memory during tests
# Solution: Increase system memory or reduce test scope
export NODE_OPTIONS="--max-old-space-size=4096"
```

### Getting Help

1. **Check Logs**: Look for error details in console output
2. **Verify Dependencies**: Ensure all prerequisites are installed
3. **Check Permissions**: Verify read/write access to directories
4. **Test Isolation**: Try each component separately
5. **Environment**: Ensure clean virtual environment

### Diagnostic Commands
```bash
# System info
python --version
node --version
npm --version
sqlite3 --version

# Dependency check
pip list | grep -E "(sqlite|asyncio|uuid)"
npm list

# File permissions
ls -la
ls -la modules/

# Memory usage
free -h  # Linux
vm_stat  # macOS
```

---

## 🚀 Next Steps

After successful installation:

1. **Quick Start**: Follow [Quick Start Tutorial](quickstart.md)
2. **Basic Examples**: Try [Basic Examples](examples.md)
3. **Architecture**: Read [System Overview](../architecture/overview.md)
4. **Integration**: Setup [Claude Desktop Integration](../integration/claude-desktop.md)

---

**✅ Installation complete! Ready to explore 7-tier cognitive architecture? Continue to [Quick Start Tutorial](quickstart.md)! 🧠✨**