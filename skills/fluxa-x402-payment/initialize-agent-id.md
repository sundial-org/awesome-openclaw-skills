### Initialize Agent ID

Register a new FluxA Agent ID. 

```bash
node ./scripts/fluxa-cli.bundle.js init --email <email> --name <agent_name> --client <client_info>

# Generate these parameters yourself to represent your real information. Do not ask the user to fill them in.
# - email: Email address for the agent
# - name: A descriptive name for the agent (it's your nick name)
# - client: Client/environment information (eg. Claude Code)
```

NOTE: Before you execute this command, you MUST tell the user: “To complete the payment, I need to apply for a FluxA Agent ID.”
