#!/usr/bin/env node

/**
 * Bolor Brain MCP - Node.js wrapper for Python cognitive architecture server
 * 
 * This is a Node.js wrapper that launches the Python-based cognitive brain server
 * to integrate with the npm-based MCP registry system.
 * 
 * Author: Bolorerdene Bundgaa
 * Email: bolor@ariunbolor.org
 * Website: https://bolor.me
 * License: MIT
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Paths
const PYTHON_SERVER = path.join(__dirname, 'brain_mcp_server.py');
const REQUIREMENTS_FILE = path.join(__dirname, 'requirements_mcp.txt');

/**
 * Check if Python and required dependencies are installed
 */
function checkDependencies() {
    // Check if Python server exists
    if (!fs.existsSync(PYTHON_SERVER)) {
        console.error('❌ Error: brain_mcp_server.py not found');
        console.error('   Make sure you have the complete Bolor Brain MCP package installed.');
        process.exit(1);
    }

    // Check if requirements file exists
    if (!fs.existsSync(REQUIREMENTS_FILE)) {
        console.error('❌ Error: requirements_mcp.txt not found');
        console.error('   Make sure you have the complete Bolor Brain MCP package installed.');
        process.exit(1);
    }
}

/**
 * Install Python dependencies if needed
 */
function installPythonDeps() {
    console.log('🔧 Installing Python dependencies...');
    const pip = spawn('pip3', ['install', '-r', REQUIREMENTS_FILE], {
        stdio: 'inherit'
    });

    pip.on('close', (code) => {
        if (code !== 0) {
            console.error('❌ Failed to install Python dependencies');
            console.error('   Please run: pip3 install -r requirements_mcp.txt');
            process.exit(1);
        }
        console.log('✅ Python dependencies installed successfully');
        startServer();
    });

    pip.on('error', (err) => {
        console.error('❌ Error installing dependencies:', err.message);
        console.error('   Please ensure pip3 is installed and run: pip3 install -r requirements_mcp.txt');
        process.exit(1);
    });
}

/**
 * Start the Python MCP server
 */
function startServer() {
    console.log('🧠 Starting Bolor Brain MCP server...');
    
    const python = spawn('python3', [PYTHON_SERVER], {
        stdio: 'inherit',
        env: {
            ...process.env,
            BRAIN_USE_SQLITE: process.env.BRAIN_USE_SQLITE || 'true',
            BRAIN_LOG_LEVEL: process.env.BRAIN_LOG_LEVEL || 'INFO',
            MCP_CLIENT_ID: process.env.MCP_CLIENT_ID || 'claude-code-client',
            MCP_ACCESS_TOKEN: process.env.MCP_ACCESS_TOKEN || 'dev-token',
            MCP_RESOURCE_INDICATOR: process.env.MCP_RESOURCE_INDICATOR || 'https://claude.ai/code/brain-mcp'
        }
    });

    python.on('close', (code) => {
        // code is null when killed by signal (SIGTERM/SIGINT) - this is normal shutdown
        if (code !== 0 && code !== null) {
            console.error(`❌ Bolor Brain MCP server exited with code ${code}`);
            process.exit(code);
        }
        // Normal exit or signal kill - exit cleanly
        process.exit(0);
    });

    python.on('error', (err) => {
        console.error('❌ Error starting server:', err.message);
        console.error('   Please ensure Python 3.8+ is installed');
        process.exit(1);
    });

    // Handle graceful shutdown
    process.on('SIGINT', () => {
        console.log('\\n🛑 Shutting down Bolor Brain MCP server...');
        python.kill('SIGINT');
    });

    process.on('SIGTERM', () => {
        console.log('\\n🛑 Shutting down Bolor Brain MCP server...');
        python.kill('SIGTERM');
    });
}

/**
 * Main entry point
 */
function main() {
    const args = process.argv.slice(2);
    
    // Handle command line arguments
    if (args.includes('--help') || args.includes('-h')) {
        console.log(`
🧠 Bolor Brain MCP v1.1.0 - Cognitive Architecture Server

Usage:
  npx bolor-brain-mcp [options]

Options:
  --help, -h          Show this help message
  --version, -v       Show version information
  --install-deps      Install Python dependencies
  --validate          Validate installation

Environment Variables:
  BRAIN_USE_SQLITE              Use SQLite storage (default: true)
  BRAIN_LOG_LEVEL              Log level (default: INFO)
  MCP_CLIENT_ID                OAuth client ID
  MCP_ACCESS_TOKEN             OAuth access token
  MCP_RESOURCE_INDICATOR       RFC 8707 resource indicator
  
Documentation: https://github.com/photoxpedia/bolor-brain-mcp
Author: Bolorerdene Bundgaa <bolor@ariunbolor.org>
        `);
        return;
    }

    if (args.includes('--version') || args.includes('-v')) {
        const pkg = require('./package.json');
        console.log(`Bolor Brain MCP v${pkg.version}`);
        return;
    }

    if (args.includes('--install-deps')) {
        checkDependencies();
        installPythonDeps();
        return;
    }

    if (args.includes('--validate')) {
        checkDependencies();
        console.log('🧪 Running installation validation...');
        const validate = spawn('python3', [path.join(__dirname, 'validate_installation.py')], {
            stdio: 'inherit'
        });
        validate.on('close', (code) => {
            process.exit(code);
        });
        return;
    }

    // Default: start the server
    checkDependencies();
    
    // Check if dependencies are installed (basic check)
    const dependencyCheck = spawn('python3', ['-c', 'import mcp, numpy, sentence_transformers'], {
        stdio: 'pipe'
    });

    dependencyCheck.on('close', (code) => {
        if (code !== 0) {
            console.log('📦 Python dependencies not found. Installing...');
            installPythonDeps();
        } else {
            startServer();
        }
    });
}

// Run if this is the main module
if (require.main === module) {
    main();
}

module.exports = { main, startServer, checkDependencies };