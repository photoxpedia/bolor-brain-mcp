# 📦 Installation Guide - Bolor Brain MCP

Complete installation guide for getting Bolor Brain MCP running on your system.

## 🚀 Quick Installation

### Option 1: Standard Setup (Recommended)

1. **Install Python Dependencies**
```bash
pip install mcp numpy sentence-transformers
```

2. **Download Bolor Brain MCP**
```bash
git clone https://github.com/photoxpedia/bolor-brain-mcp.git
cd bolor-brain-mcp
```

3. **Validate Installation**
```bash
python3 validate_installation.py
```
**Expected:** `🎉 Bolor Brain MCP is fully functional!`

4. **Add to Claude Code**
Add to your Claude Code MCP configuration:
```json
{
  "mcpServers": {
    "bolor-brain-mcp": {
      "command": "python3",
      "args": ["brain_mcp_server.py"],
      "cwd": "/path/to/bolor-brain-mcp"
    }
  }
}
```

### Option 2: Minimal Setup (Core Features Only)

If you only need basic memory functions without semantic similarity:

```bash
pip install mcp numpy
git clone https://github.com/photoxpedia/bolor-brain-mcp.git
cd bolor-brain-mcp
python3 validate_installation.py
```

## 🔧 Detailed Installation

### Step 1: System Requirements

**Check Python Version:**
```bash
python3 --version
# Should be 3.8 or higher
```

**Check Available Memory:**
```bash
# Minimum: 512MB RAM
# Recommended: 4GB+ RAM
```

### Step 2: Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv brain-mcp-env

# Activate virtual environment
# On macOS/Linux:
source brain-mcp-env/bin/activate

# On Windows:
brain-mcp-env\Scripts\activate
```

### Step 3: Install Dependencies

**Core Dependencies:**
```bash
pip install mcp>=0.1.0
pip install numpy>=1.21.0
```

**Enhanced Features (Recommended):**
```bash
pip install sentence-transformers>=2.2.0
# This enables semantic similarity and vector embeddings
# Will also install: torch, transformers, scikit-learn, scipy
```

**Alternative Installation:**
```bash
# Install all at once
pip install -r requirements_mcp.txt
```

### Step 4: Download and Setup

**Clone Repository:**
```bash
git clone https://github.com/photoxpedia/bolor-brain-mcp.git
cd bolor-brain-mcp
```

**Verify File Structure:**
```
bolor-brain-mcp/
├── brain_mcp_server.py          # Main MCP server
├── validate_installation.py     # Installation validator
├── test_e2e_bulletproof.py     # Comprehensive tests
├── mcp_config.json             # Claude Code configuration
├── requirements_mcp.txt        # Dependencies
├── README.md                   # Documentation
└── brain_mcp_storage/          # Will be created on first run
```

## ✅ Validation & Testing

### Validation Test
```bash
python3 validate_installation.py
```

**Expected Output:**
```
🚀 Bolor Brain MCP Installation Validation
==================================================
Author: Bolorerdene Bundgaa | https://bolor.me
==================================================

1. Checking file structure...
   ✅ brain_mcp_server.py
   ✅ README.md
   [... all files checked ...]

6. Validating configuration files...
   ✅ Configuration files valid

🎉 Bolor Brain MCP is fully functional and ready for use!
```

### Comprehensive Testing
```bash
python3 test_e2e_bulletproof.py
```

**Expected Output:**
```
🧠 Bolor Brain MCP Server Test Suite

[13 tests running...]

🏁 BULLETPROOF TEST RESULTS
============================================================
✅ PASSED: 13
❌ FAILED: 0
📊 TOTAL: 13
📈 SUCCESS RATE: 100.0%

🚀 SYSTEM READY FOR DEPLOYMENT!
```

### Quick Demo Test
```bash
python3 brain_mcp_server.py
```

**Expected Output:**
```
MCP not available. Install with: pip install mcp
This module provides Bolor Brain MCP cognitive tools for MCP integration.
Author: Bolorerdene Bundgaa | https://bolor.me

🧠 Brain Demo:
Vector embedding model loaded
Enhanced Brain initialized with 0 memories
[Demo showing memory storage and retrieval]
```

## ⚙️ Claude Code Integration

### Configuration File Location

**macOS/Linux:**
```bash
~/.claude/mcp_servers.json
```

**Windows:**
```bash
%USERPROFILE%\.claude\mcp_servers.json
```

### Configuration Content

**Create or edit the configuration file:**
```json
{
  "mcpServers": {
    "bolor-brain-mcp": {
      "command": "python3",
      "args": ["brain_mcp_server.py"],
      "cwd": "/absolute/path/to/bolor-brain-mcp",
      "env": {
        "BRAIN_STORAGE_PATH": "./brain_mcp_storage",
        "BRAIN_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/bolor-brain-mcp` with your actual installation path.

### Verify Claude Code Integration

1. **Restart Claude Code** after adding the configuration
2. **Check MCP Tools** - You should see 7 new brain tools available
3. **Test Basic Function:**
   ```
   Use the store_memory tool to save: "Installation successful!"
   ```

## 🛠️ Customization

### Storage Location
```python
# Default: ./brain_mcp_storage
# Custom location:
export BRAIN_STORAGE_PATH="/custom/path/brain_storage"
```

### Performance Tuning

**For Better Performance:**
```bash
# Install with CUDA support (if you have GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Use faster embedding model
export EMBEDDING_MODEL="all-MiniLM-L6-v2"  # Default, fast
# export EMBEDDING_MODEL="all-mpnet-base-v2"  # Slower but more accurate
```

**For Lower Memory Usage:**
```python
# In brain_mcp_server.py, you can modify:
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
# To use smaller model:
# embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # 128 dimensions
```

## 🐛 Troubleshooting

### Common Issues

**1. "MCP not available" Error**
```bash
pip install mcp
```

**2. "sentence-transformers not available" Warning**
```bash
# This is optional, but for full functionality:
pip install sentence-transformers
```

**3. Permission Denied on Storage**
```bash
# Make sure storage directory is writable
chmod 755 ./brain_mcp_storage
```

**4. Python Version Issues**
```bash
# Check Python version
python3 --version

# If too old, update Python or use Python 3.8+
# On macOS with Homebrew:
brew install python@3.9

# On Ubuntu:
sudo apt update
sudo apt install python3.9
```

**5. Memory/Performance Issues**
```bash
# Reduce memory usage by disabling embeddings:
export DISABLE_EMBEDDINGS=true
python3 brain_mcp_server.py
```

### Logs and Debugging

**Enable Debug Logging:**
```bash
export BRAIN_LOG_LEVEL=DEBUG
python3 brain_mcp_server.py
```

**Check Installation Details:**
```bash
python3 -c "
import brain_mcp_server
print('Brain MCP Server loaded successfully')
print(f'Embedding available: {brain_mcp_server.EMBEDDINGS_AVAILABLE}')
print(f'Numpy available: {brain_mcp_server.NUMPY_AVAILABLE}')
"
```

### Getting Help

**Check System Status:**
```bash
python3 validate_installation.py
```

**Test Individual Components:**
```bash
# Test core functionality
python3 -c "from brain_mcp_server import SimpleBrain; print('✅ Core brain works')"

# Test embeddings
python3 -c "from sentence_transformers import SentenceTransformer; print('✅ Embeddings work')"

# Test MCP
python3 -c "import mcp; print('✅ MCP available')"
```

## 🔄 Updates & Maintenance

### Updating Bolor Brain MCP
```bash
cd bolor-brain-mcp
git pull origin main

# Run validation after update
python3 validate_installation.py
```

### Backup Your Brain Data
```bash
# Backup your memories before updating
cp -r brain_mcp_storage brain_mcp_storage.backup

# After successful update, old backup can be removed
rm -rf brain_mcp_storage.backup
```

## 📞 Support

If you encounter issues:

1. **Check this guide** - Most common issues are covered here
2. **Run validation** - `python3 validate_installation.py`
3. **Check GitHub Issues** - https://github.com/photoxpedia/bolor-brain-mcp/issues
4. **Contact support** - bolor@ariunbolor.org

---

**🎉 Congratulations! You now have a cognitive brain for Claude Code!**

Start by storing your first memory:
```python
brain.store_memory("I successfully installed Bolor Brain MCP!", "episodic", importance=1.0)
```