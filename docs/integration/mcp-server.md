# MCP Server Configuration 🔧

This guide covers comprehensive setup and configuration of the Bolor Brain MCP server, from basic installation to advanced production deployments.

## 🎯 Overview

The MCP (Model Context Protocol) server provides standardized access to all 7 cognitive tiers through a unified API interface. It bridges the gap between the cognitive architecture and external applications.

### Architecture
```
External Applications (Claude Desktop, Custom Clients)
                    ↓
           MCP Protocol Layer
                    ↓
         Bolor Brain MCP Server
                    ↓
    7-Tier Cognitive Architecture
```

---

## 🚀 Quick Setup

### 1. Basic Configuration

Create or verify `server.json`:

```json
{
  "name": "bolor-brain",
  "version": "1.2.0", 
  "description": "7-Tier Universal Intelligence MCP Server",
  "author": "Bolorerdene Bundgaa",
  "license": "MIT",
  "main": "index.js",
  "cognitive_tiers": 7,
  "tools": {
    "store_memory": {
      "description": "Store information in brain memory",
      "parameters": ["content", "memory_type", "importance", "metadata"]
    },
    "retrieve_memories": {
      "description": "Retrieve memories by query",
      "parameters": ["query", "limit", "memory_type"]
    },
    "solve_problem": {
      "description": "Solve complex problems with advanced reasoning",
      "parameters": ["problem", "context"]
    },
    "predict_needs": {
      "description": "Predict user needs and future requirements", 
      "parameters": ["current_context", "history_depth"]
    },
    "analyze_performance": {
      "description": "Analyze cognitive performance",
      "parameters": ["performance_data"]
    },
    "evolve_capabilities": {
      "description": "Evolve cognitive capabilities",
      "parameters": ["current_state", "target_improvements", "evolution_cycles"]
    },
    "join_network": {
      "description": "Join collective consciousness network",
      "parameters": ["network_id", "contribution_level"]
    },
    "orchestrate_reality": {
      "description": "Orchestrate reality through quantum fields",
      "parameters": ["intention", "scope"]
    },
    "access_wisdom": {
      "description": "Access universal wisdom and consciousness",
      "parameters": ["query", "wisdom_level"]
    }
  },
  "configuration": {
    "max_memory_size": 10000,
    "reasoning_timeout": 30,
    "prediction_horizon": 7,
    "meta_optimization_frequency": "daily",
    "evolution_cycles": 5,
    "collective_network_enabled": false,
    "universal_access_enabled": true,
    "debug_mode": false,
    "log_level": "INFO"
  }
}
```

### 2. Start the Server

```bash
# Install dependencies
npm install

# Start in development mode
npm run dev

# Start in production mode  
npm start

# Start with custom config
node index.js --config=custom-server.json
```

### 3. Verify Server Status

```bash
# Check server health
curl http://localhost:3000/health

# Get server info
curl http://localhost:3000/info

# List available tools
curl http://localhost:3000/tools
```

---

## ⚙️ Advanced Configuration

### Environment Variables

Create `.env` file for environment-specific settings:

```bash
# Server Configuration
PORT=3000
HOST=localhost
NODE_ENV=production

# Database Settings
DATABASE_PATH=./data/memory.db
DATABASE_BACKUP_ENABLED=true
DATABASE_BACKUP_INTERVAL=24h

# Brain Configuration
MAX_MEMORY_SIZE=15000
REASONING_TIMEOUT=45
PREDICTION_HORIZON=14
EVOLUTION_MUTATION_RATE=0.1

# Security Settings
API_KEY_REQUIRED=true
API_KEY=your-secure-api-key-here
RATE_LIMITING_ENABLED=true
MAX_REQUESTS_PER_MINUTE=100

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE_ENABLED=true
LOG_FILE_PATH=./logs/brain-mcp.log
LOG_ROTATION_ENABLED=true

# Cognitive Tier Settings
MEMORY_TIER_ENABLED=true
REASONING_TIER_ENABLED=true
PREDICTIVE_TIER_ENABLED=true
METACOGNITIVE_TIER_ENABLED=true
EVOLUTIONARY_TIER_ENABLED=true
COLLECTIVE_TIER_ENABLED=false
ORCHESTRATION_TIER_ENABLED=true
UNIVERSAL_TIER_ENABLED=true

# Advanced Features
QUANTUM_SIMULATION_ENABLED=false
COLLECTIVE_NETWORK_HOST=collective.example.com
COLLECTIVE_NETWORK_PORT=8080
UNIVERSAL_FIELD_ACCESS_KEY=your-universal-key

# Performance Settings
WORKER_THREADS=4
MEMORY_CACHE_SIZE=1000
REASONING_CACHE_SIZE=500
PREDICTION_CACHE_SIZE=300

# Monitoring & Analytics
METRICS_ENABLED=true
METRICS_ENDPOINT=/metrics
HEALTH_CHECK_INTERVAL=30s
PERFORMANCE_MONITORING=true
```

### Custom Configuration File

Create `config/production.json` for production settings:

```json
{
  "server": {
    "port": 3000,
    "host": "0.0.0.0",
    "cors": {
      "enabled": true,
      "origins": ["https://claude.ai", "https://your-app.com"]
    },
    "ssl": {
      "enabled": true,
      "cert_path": "./certs/server.crt",
      "key_path": "./certs/server.key"
    }
  },
  "brain": {
    "max_memory_size": 50000,
    "reasoning_strategies": {
      "analytical": { "enabled": true, "timeout": 30 },
      "creative": { "enabled": true, "timeout": 45 },
      "critical": { "enabled": true, "timeout": 35 },
      "systems": { "enabled": true, "timeout": 50 },
      "ethical": { "enabled": true, "timeout": 40 },
      "intuitive": { "enabled": true, "timeout": 25 }
    },
    "predictive": {
      "prediction_window": "14_days",
      "confidence_threshold": 0.6,
      "max_predictions": 10
    },
    "metacognitive": {
      "optimization_frequency": "hourly",
      "performance_threshold": 0.8,
      "adaptation_rate": 0.1
    },
    "evolutionary": {
      "mutation_rate": 0.05,
      "evolution_cycles": 10,
      "fitness_threshold": 0.85
    },
    "collective": {
      "network_enabled": false,
      "max_nodes": 100,
      "sync_interval": "15_minutes"
    },
    "universal": {
      "access_level": "intermediate",
      "wisdom_cache_enabled": true,
      "reality_sync_enabled": true
    }
  },
  "database": {
    "path": "./data/production/memory.db",
    "backup": {
      "enabled": true,
      "interval": "6h",
      "retention_days": 30,
      "compression": true
    },
    "optimization": {
      "auto_vacuum": true,
      "cache_size": 10000,
      "journal_mode": "WAL"
    }
  },
  "security": {
    "api_key_required": true,
    "rate_limiting": {
      "enabled": true,
      "max_requests_per_minute": 200,
      "max_requests_per_hour": 5000
    },
    "input_validation": {
      "max_content_length": 10000,
      "sanitize_inputs": true,
      "blocked_patterns": ["<script>", "javascript:", "data:"]
    }
  },
  "monitoring": {
    "metrics_enabled": true,
    "health_checks": {
      "enabled": true,
      "interval": "30s",
      "endpoints": ["/health", "/memory-health", "/reasoning-health"]
    },
    "logging": {
      "level": "INFO",
      "file_enabled": true,
      "file_path": "./logs/production.log",
      "rotation": {
        "enabled": true,
        "max_size": "100MB",
        "max_files": 10
      }
    }
  },
  "performance": {
    "clustering": {
      "enabled": true,
      "workers": 4
    },
    "caching": {
      "memory_cache": {
        "enabled": true,
        "max_size": 5000,
        "ttl": "1h"
      },
      "reasoning_cache": {
        "enabled": true,
        "max_size": 1000,
        "ttl": "30m"
      },
      "prediction_cache": {
        "enabled": true,
        "max_size": 500,
        "ttl": "15m"
      }
    }
  }
}
```

---

## 🔌 MCP Tool Registration

### Tool Definition Structure

Each cognitive capability is exposed as an MCP tool:

```javascript
// index.js - Tool registration
const tools = {
  store_memory: {
    name: "store_memory",
    description: "Store information in the brain's memory system",
    inputSchema: {
      type: "object",
      properties: {
        content: {
          type: "string",
          description: "Content to store in memory"
        },
        memory_type: {
          type: "string", 
          enum: ["episodic", "semantic", "procedural"],
          default: "episodic"
        },
        importance: {
          type: "number",
          minimum: 0,
          maximum: 1,
          default: 0.5
        },
        metadata: {
          type: "object",
          description: "Additional metadata for the memory"
        }
      },
      required: ["content"]
    }
  },
  
  solve_problem: {
    name: "solve_problem",
    description: "Solve complex problems using advanced reasoning",
    inputSchema: {
      type: "object",
      properties: {
        problem: {
          type: "string",
          description: "Problem statement to solve"
        },
        context: {
          type: "object",
          description: "Additional context for reasoning"
        }
      },
      required: ["problem"]
    }
  },
  
  predict_needs: {
    name: "predict_needs",
    description: "Predict user needs based on context and patterns",
    inputSchema: {
      type: "object",
      properties: {
        current_context: {
          type: "object",
          description: "Current user/system context"
        },
        history_depth: {
          type: "integer",
          minimum: 1,
          maximum: 50,
          default: 10
        }
      },
      required: ["current_context"]
    }
  }
  
  // ... additional tools for all 17 capabilities
};
```

### Custom Tool Implementation

Add custom tools for specific use cases:

```javascript
// Custom tool for domain-specific reasoning
const customTools = {
  medical_diagnosis: {
    name: "medical_diagnosis",
    description: "Analyze medical symptoms using specialized reasoning",
    inputSchema: {
      type: "object",
      properties: {
        symptoms: {
          type: "array",
          items: { type: "string" }
        },
        patient_history: {
          type: "object"
        },
        specialist_domain: {
          type: "string",
          enum: ["cardiology", "neurology", "oncology", "general"]
        }
      },
      required: ["symptoms"]
    },
    handler: async (args) => {
      // Custom implementation using brain's reasoning
      const context = {
        domain: "medical",
        specialization: args.specialist_domain,
        patient_data: args.patient_history
      };
      
      const problem = `Analyze these symptoms: ${args.symptoms.join(', ')}`;
      return await brain.solve_complex_problem(problem, context);
    }
  }
};
```

---

## 🔐 Security Configuration

### API Key Authentication

```javascript
// Middleware for API key authentication
const authenticateApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  
  if (!apiKey || apiKey !== process.env.API_KEY) {
    return res.status(401).json({
      error: "Unauthorized",
      message: "Valid API key required"
    });
  }
  
  next();
};

// Apply to all MCP endpoints
app.use('/mcp', authenticateApiKey);
```

### Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

// Configure rate limiting
const mcpLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    error: "Too many requests",
    message: "Rate limit exceeded. Please try again later."
  },
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/mcp', mcpLimiter);
```

### Input Validation

```javascript
const validator = require('express-validator');

// Validation middleware for memory storage
const validateMemoryInput = [
  validator.body('content')
    .isLength({ min: 1, max: 10000 })
    .withMessage('Content must be between 1 and 10000 characters'),
  validator.body('memory_type')
    .isIn(['episodic', 'semantic', 'procedural'])
    .withMessage('Invalid memory type'),
  validator.body('importance')
    .isFloat({ min: 0, max: 1 })
    .withMessage('Importance must be between 0 and 1'),
  
  (req, res, next) => {
    const errors = validator.validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: "Validation failed",
        details: errors.array()
      });
    }
    next();
  }
];
```

---

## 📊 Monitoring & Logging

### Health Check Endpoints

```javascript
// Basic health check
app.get('/health', (req, res) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: packageInfo.version
  });
});

// Detailed system health
app.get('/health/detailed', async (req, res) => {
  try {
    const memoryHealth = await checkMemorySystem();
    const reasoningHealth = await checkReasoningSystem();
    const brainStats = brain.get_system_statistics();
    
    res.json({
      status: "healthy",
      components: {
        memory: memoryHealth,
        reasoning: reasoningHealth,
        database: await checkDatabase(),
        cognitive_tiers: brainStats.tier_status
      },
      performance: {
        memory_usage: process.memoryUsage(),
        cpu_usage: process.cpuUsage(),
        response_times: getResponseTimes()
      }
    });
  } catch (error) {
    res.status(503).json({
      status: "unhealthy",
      error: error.message
    });
  }
});
```

### Performance Metrics

```javascript
const prometheus = require('prom-client');

// Create metrics
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_ms',
  help: 'Duration of HTTP requests in ms',
  labelNames: ['method', 'route', 'status'],
  buckets: [1, 5, 15, 50, 100, 500, 1000]
});

const mcpToolUsage = new prometheus.Counter({
  name: 'mcp_tool_usage_total',
  help: 'Total number of MCP tool invocations',
  labelNames: ['tool_name', 'status']
});

const cognitiveTierPerformance = new prometheus.Histogram({
  name: 'cognitive_tier_operation_duration_ms', 
  help: 'Duration of cognitive tier operations in ms',
  labelNames: ['tier', 'operation'],
  buckets: [10, 50, 100, 500, 1000, 5000]
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', prometheus.register.contentType);
  res.end(await prometheus.register.metrics());
});
```

### Structured Logging

```javascript
const winston = require('winston');

// Configure logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { 
    service: 'bolor-brain-mcp',
    version: packageInfo.version 
  },
  transports: [
    new winston.transports.File({ 
      filename: './logs/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: './logs/combined.log' 
    })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

// Log MCP operations
app.use('/mcp', (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info('MCP operation completed', {
      method: req.method,
      url: req.url,
      status: res.statusCode,
      duration: duration,
      user_agent: req.get('User-Agent'),
      ip: req.ip
    });
  });
  
  next();
});
```

---

## 🚀 Performance Optimization

### Clustering for High Load

```javascript
// cluster.js - Multi-process setup
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
  console.log(`Master ${process.pid} is running`);
  
  // Fork workers
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died`);
    cluster.fork(); // Restart worker
  });
} else {
  // Workers can share any TCP port
  require('./index.js');
  console.log(`Worker ${process.pid} started`);
}
```

### Caching Layer

```javascript
const NodeCache = require('node-cache');

// Create caches for different operations
const memoryCache = new NodeCache({ 
  stdTTL: 3600,    // 1 hour TTL
  checkperiod: 600  // Check for expired keys every 10 minutes
});

const reasoningCache = new NodeCache({ 
  stdTTL: 1800,    // 30 minutes TTL
  checkperiod: 300  // Check every 5 minutes
});

const predictionCache = new NodeCache({
  stdTTL: 900,     // 15 minutes TTL
  checkperiod: 120  // Check every 2 minutes
});

// Cache middleware
const cacheMiddleware = (cache, keyGenerator) => {
  return (req, res, next) => {
    const key = keyGenerator(req);
    const cached = cache.get(key);
    
    if (cached) {
      return res.json(cached);
    }
    
    // Store original json method
    const originalJson = res.json;
    res.json = function(data) {
      cache.set(key, data);
      return originalJson.call(this, data);
    };
    
    next();
  };
};
```

### Database Optimization

```javascript
// database-config.js
const sqlite3 = require('sqlite3').verbose();

const optimizeDatabase = async (db) => {
  // WAL mode for better concurrency
  await db.exec('PRAGMA journal_mode=WAL;');
  
  // Increase cache size
  await db.exec('PRAGMA cache_size=10000;');
  
  // Optimize for read-heavy workloads
  await db.exec('PRAGMA temp_store=memory;');
  
  // Enable auto-vacuum
  await db.exec('PRAGMA auto_vacuum=INCREMENTAL;');
  
  // Set synchronous mode for performance
  await db.exec('PRAGMA synchronous=NORMAL;');
  
  console.log('Database optimized for performance');
};
```

---

## 🐳 Docker Configuration

### Dockerfile

```dockerfile
FROM node:18-alpine

# Create app directory
WORKDIR /app

# Install Python for brain modules
RUN apk add --no-cache python3 py3-pip sqlite

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data /app/logs

# Set permissions
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node health-check.js

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  bolor-brain-mcp:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_PATH=/app/data/memory.db
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
  # Optional: Add reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - bolor-brain-mcp
    restart: unless-stopped
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: Server won't start
```bash
# Check logs
tail -f logs/error.log

# Verify port availability
netstat -tlnp | grep :3000

# Check file permissions
ls -la index.js
```

#### Issue: Memory errors
```bash
# Monitor memory usage
ps aux | grep node

# Check database size
du -h data/memory.db

# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
```

#### Issue: Slow responses
```bash
# Check system resources
top
df -h

# Monitor database performance
sqlite3 data/memory.db ".timer on" "SELECT COUNT(*) FROM memories;"

# Enable performance monitoring
export PERFORMANCE_MONITORING=true
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set environment variable
export DEBUG=bolor-brain:*

# Or use debug configuration
node index.js --debug --log-level=debug
```

---

**🚀 Ready for production deployment? Continue to [Production Deployment](deployment.md) or explore [Claude Desktop Integration](claude-desktop.md)! 🧠✨**