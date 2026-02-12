# Bolor Brain Skills for Claude Code

These skills enhance Claude Code with structured reasoning workflows using Bolor Brain MCP tools.

## Available Skills

### `/reason` - Universal Reasoning Assistant
**Use when:** You need systematic analysis of any complex problem

- Auto-selects best reasoning approach
- Explains reasoning process clearly
- Provides confidence scores
- Offers to store successful solutions

**Example:**
```
/reason Why is Python popular for machine learning?
/reason Should I use async or sync code here?
/reason How are microservices and Docker related?
```

### `/debug` - Systematic Debugging
**Use when:** You have a bug, error, or unexpected behavior

- Searches past similar incidents
- Generates and tests hypotheses
- Provides specific fixes with verification steps
- Stores successful resolutions for learning

**Example:**
```
/debug API returns 500 errors under load
/debug Users can't log in after deployment
/debug Memory usage keeps growing
```

### `/decide` - Technical Decision Making
**Use when:** Choosing between technologies, architectures, or approaches

- Analyzes all context and constraints
- Shows trade-offs clearly
- References past successful decisions
- Provides evidence-based recommendations

**Example:**
```
/decide Should we use PostgreSQL or MongoDB?
/decide Monolith or microservices for our team?
/decide React or Vue for this project?
```

### `/learn-from` - Store Experience
**Use when:** You solved something and want the brain to learn from it

- Captures problem-solution-outcome
- Makes knowledge searchable
- Helps future similar issues
- Builds team institutional knowledge

**Example:**
```
/learn-from We fixed a race condition with mutex locks
/learn-from Next.js worked great for our SEO needs
/learn-from Microservices was too complex for our small team
```

## How to Use Skills

### 1. Install Bolor Brain MCP Server

See [MCP_SETUP.md](../MCP_SETUP.md) for installation instructions.

### 2. Skills Load Automatically

Once Bolor Brain is in your MCP config, the skills are available through Claude Code's skill system.

### 3. Invoke with /command

```
You: /debug My API is slow

Claude: [loads debug skill]
Let me systematically debug this. First, I need context:
- What endpoint?
- How slow?
- When did it start?
...
```

## Skill Workflow Examples

### Debugging Workflow

```
User: /debug checkout endpoint returns 500 errors

1. Claude gathers context
2. Searches past cases via reason_case_based
3. Generates hypotheses via reason_hypothesis
4. Combines findings via reason_hybrid
5. Presents diagnosis with confidence
6. Offers to store case after fix
```

### Decision Workflow

```
User: /decide should we use REST or GraphQL?

1. Claude asks for context (team, scale, needs)
2. Calls reason_hybrid with full context
3. Analyzes trade-offs
4. Presents recommendation with evidence
5. Shows what you're gaining/losing
6. Suggests next steps
```

### Learning Workflow

```
User: /learn-from we solved the N+1 query problem with dataloader

1. Claude extracts problem details
2. Captures solution specifics
3. Records outcome metrics
4. Stores case via store_case tool
5. Explains how it will help future queries
```

## Skill Customization

These skills are templates. You can:

1. **Fork and modify** - Adapt to your team's needs
2. **Add domain knowledge** - Include your specific patterns
3. **Customize prompts** - Match your team's terminology
4. **Create new skills** - Build domain-specific workflows

## Tips for Best Results

### 1. Provide Context
```
❌ /debug it's broken
✓ /debug checkout API returns 500 during peak hours, started after yesterday's deploy
```

### 2. Use the Right Skill
```
❌ /decide why is my app slow (use /debug)
✓ /debug why is my app slow
```

### 3. Follow Through
```
✓ After fixing: /learn-from [store the solution]
✓ This makes future debugging faster
```

### 4. Trust the Process
```
✓ Let skills gather context
✓ Answer clarifying questions
✓ Don't skip the systematic workflow
```

## Integration with Bolor Brain Tools

Each skill uses specific MCP tools:

| Skill | Primary Tools |
|-------|---------------|
| `/reason` | `reason_hybrid` (auto-selects others) |
| `/debug` | `reason_case_based`, `reason_hypothesis`, `reason_hybrid` |
| `/decide` | `reason_hybrid`, `reason_symbolic`, `reason_knowledge_graph` |
| `/learn-from` | `store_case`, `add_knowledge` |

## Creating Your Own Skills

Want to create domain-specific skills?

**Template:**
```markdown
---
name: your-skill-name
description: Short description of what it does
---

# Your Skill Title

[Instructions for Claude on how to use Bolor Brain tools for this specific workflow]

## When This Skill is Used

[User scenarios]

## Workflow

[Step-by-step process]

## Examples

[Real usage examples]
```

See existing skills for full examples.

## Troubleshooting

**Skill not loading:**
- Verify MCP server is running
- Check skill file syntax (YAML front matter)
- Restart Claude Code

**Poor results:**
- Add more context to your query
- Use more specific problem descriptions
- Store more cases to improve brain knowledge

**Want different behavior:**
- Fork the skill and modify
- Submit a PR with improvements
- Create issue with suggestions

## Contributing

Have improvements or new skills?
1. Fork the repo
2. Add/modify skills
3. Test with Claude Code
4. Submit PR

We especially welcome:
- Domain-specific skills (medical, legal, finance)
- Workflow optimizations
- Better prompting strategies
- More example use cases

## Support

- **Documentation:** [../MCP_SETUP.md](../MCP_SETUP.md)
- **Examples:** [../CLAUDE_CODE_EXAMPLES.md](../CLAUDE_CODE_EXAMPLES.md)
- **Issues:** [GitHub Issues](https://github.com/photoxpedia/bolor-brain-mcp/issues)

---

**Build systematic thinking into your development workflow with Bolor Brain skills.**
