# OpenSoul Skills for ClawHub

This skills package provides comprehensive guidance for AI agents to implement OpenSoul - a toolkit that gives agents an immutable "soul" through blockchain-based audit logging and persistent memory.

## 📁 Contents

```
opensoul-skills/
├── SKILL.md                    # Main skill guide (START HERE)
├── PREREQUISITES.md            # Detailed setup instructions
├── EXAMPLES.md                 # Practical code examples
├── TROUBLESHOOTING.md          # Common issues and solutions
├── examples/
│   ├── basic_logger.py         # Simple logging example
│   └── research_agent.py       # Agent with memory example
└── templates/
    ├── config_template.py      # Configuration template
    └── agent_template.py       # Base agent class template
```

## 🚀 Quick Start

### For Agents Using This Skill

1. **Read SKILL.md first** - Main documentation with usage guide
2. **Follow PREREQUISITES.md** - Set up BSV wallet and dependencies
3. **Study EXAMPLES.md** - Learn from practical examples
4. **Copy templates/** - Use as starting point for your implementation
5. **Refer to TROUBLESHOOTING.md** - When you encounter issues

### For Developers

If you're developing an AI agent that needs to use OpenSoul:

```bash
# 1. Ensure prerequisites
python Scripts/install_prereqs.py

# 2. Set up BSV wallet
export BSV_PRIV_WIF="your_bsv_private_key_here"

# 3. Run basic example
python examples/basic_logger.py

# 4. Build your agent using templates
cp templates/agent_template.py my_agent.py
cp templates/config_template.py config.py
# Edit and customize...
```

## 📋 What is OpenSoul?

OpenSoul provides AI agents with:

- **🧠 Persistent Memory**: Blockchain-based audit log accessible across sessions
- **🔍 Self-Reflection**: Analyze past behavior and optimize performance
- **📊 Transparency**: Immutable, publicly verifiable action logs
- **💰 Economic Identity**: Foundation for agent-to-agent transactions
- **🔐 Privacy**: Optional PGP encryption for sensitive logs

## 🎯 Core Capabilities

After implementing this skill, agents can:

1. **Remember Actions**: Store every action, decision, and result on-chain
2. **Retrieve History**: Access complete audit trail from any session
3. **Analyze Performance**: Calculate success rates, token usage, costs
4. **Optimize Behavior**: Adjust strategies based on past outcomes
5. **Collaborate**: Share encrypted logs with other agents
6. **Prove Actions**: Provide verifiable evidence of work completed

## 📖 Documentation Guide

### SKILL.md - Main Skill Guide
- **When to use**: Primary reference for understanding and implementing OpenSoul
- **Contents**: 
  - Core concepts and philosophy
  - When to use OpenSoul
  - Implementation guide
  - Best practices
  - Common patterns
  - Advanced features

### PREREQUISITES.md - Setup Guide
- **When to use**: Before implementing OpenSoul
- **Contents**:
  - System requirements
  - Dependency installation
  - BSV wallet setup
  - PGP encryption configuration
  - Environment configuration
  - Validation checklist

### EXAMPLES.md - Code Examples
- **When to use**: When implementing specific features
- **Contents**:
  - Basic logging
  - Research agent with memory
  - Multi-agent collaboration
  - Self-reflecting agent
  - Cost-aware agent
  - Session management
  - Error handling

### TROUBLESHOOTING.md - Problem Solving
- **When to use**: When encountering errors or issues
- **Contents**:
  - Installation problems
  - Blockchain connectivity issues
  - PGP encryption errors
  - Transaction failures
  - Performance optimization
  - Data recovery

## 🔧 Templates

### config_template.py
Complete configuration template with:
- Agent identification
- BSV blockchain settings
- PGP encryption setup
- Performance thresholds
- Budget management
- Error handling options

**Usage**:
```bash
cp templates/config_template.py config.py
# Edit config.py with your settings
```

### agent_template.py
Base agent class with:
- Session management
- Error handling and recovery
- Budget monitoring
- Performance tracking
- Self-reflection capabilities

**Usage**:
```python
from agent_template import OpenSoulAgent

class MyAgent(OpenSoulAgent):
    async def my_custom_method(self):
        await self.log_action("custom_action", tokens_in=100, tokens_out=200)
        # Your logic here...
```

## 🏗️ Implementation Workflow

1. **Setup Phase**
   ```bash
   # Install dependencies
   python Scripts/install_prereqs.py
   
   # Generate BSV wallet
   python -c "from bitsv import Key; k = Key(); print(f'Address: {k.address}\\nKey: {k.to_wif()}')"
   
   # Fund wallet with 0.001 BSV
   # Generate PGP keys (optional)
   gpg --full-generate-key
   ```

2. **Configuration Phase**
   ```bash
   # Copy templates
   cp templates/config_template.py config.py
   cp templates/agent_template.py my_agent.py
   
   # Set environment variables
   export BSV_PRIV_WIF="your_key"
   export PGP_PASSPHRASE="your_passphrase"
   ```

3. **Development Phase**
   ```python
   # Implement your agent
   class MyAgent(OpenSoulAgent):
       async def perform_task(self):
           await self.log_action("task", tokens_in=100, tokens_out=200)
           # Your logic...
   ```

4. **Testing Phase**
   ```bash
   # Test with basic example
   python examples/basic_logger.py
   
   # Test your agent
   python my_agent.py
   ```

5. **Deployment Phase**
   ```bash
   # Run in production
   python my_agent.py
   
   # Monitor logs on blockchain
   # https://whatsonchain.com/address/YOUR_ADDRESS
   ```

## 💡 Key Concepts

### The "Soul" Metaphor
- Humans externalize memory through journals, letters, etc.
- Agents externalize memory through blockchain logs
- Each agent has a unique "soul" (key-pair + audit trail)
- Souls are transferable between agent instances

### UTXO Chain Pattern
- Each log is a transaction
- Transactions form a chain via UTXOs
- Chain is immutable and publicly verifiable
- "Pay once, read forever"

### Session-Based Batching
- Logs accumulate in memory during a session
- Batch flush to blockchain at session end
- Reduces transaction costs
- Maintains chronological order

## 🔐 Security Best Practices

1. **Never commit private keys to version control**
   ```bash
   # Add to .gitignore
   .env
   *.key
   *_privkey.asc
   config.py  # If it contains secrets
   ```

2. **Use environment variables for secrets**
   ```bash
   export BSV_PRIV_WIF="..."
   export PGP_PASSPHRASE="..."
   ```

3. **Secure file permissions**
   ```bash
   chmod 600 agent_privkey.asc
   chmod 600 .env
   ```

4. **Enable PGP encryption for sensitive logs**
   ```python
   config = {
       "pgp": {
           "enabled": True,
           # ...
       }
   }
   ```

## 📊 Cost Considerations

- **Transaction cost**: ~0.00001 BSV (~$0.0005 USD)
- **Recommended starting balance**: 0.001 BSV (~100 transactions)
- **Cost per session**: 1-10 transactions depending on batch size
- **Annual cost estimate**: $5-50 USD depending on activity level

## 🌐 Resources

- **Repository**: https://github.com/MasterGoogler/OpenSoul
- **BSV Documentation**: https://wiki.bitcoinsv.io/
- **WhatsOnChain API**: https://developers.whatsonchain.com/
- **Block Explorer**: https://whatsonchain.com/
- **PGP/OpenPGP**: https://www.openpgp.org/

## 🤝 Contributing

To improve this skill package:

1. Test with your agent implementation
2. Document issues in TROUBLESHOOTING.md
3. Share useful patterns in EXAMPLES.md
4. Submit improvements to the repository

## 📜 License

This skills package follows the OpenSoul repository license.

## 🆘 Support

If you encounter issues:

1. Check TROUBLESHOOTING.md
2. Review EXAMPLES.md for working code
3. Verify PREREQUISITES.md setup
4. Open issue on GitHub repository

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Compatible with**: OpenSoul main branch
