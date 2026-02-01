---
name: fluxA-x402-payment
description: A FluxA Agent Wallet skill that enables agents to request budgets, sign x402 payments, and call paid endpoints autonomously. It walks through the full flow—from mandate creation to X-PAYMENT execution—so agents can perform paid actions without human intervention.
---

## Quick Start
Step 1: Apply for a budget mandate
<!--  -->
```bash
# You **MUST** estimate a **total budget** for this task, as it may involve calling tools that require payment via the FluxA Wallet.
# It is recommended to budget **1.5×** the estimated cost.
# NOTE: Before executing this command, you need to tell the user: **“To complete this task, I need to request a budget of xx USD. The exact amount spent will depend on actual execution, but I cannot spend more than this amount, and it may not be fully used.”**

node ./scripts/fluxa-cli.bundle.js mandate-create --desc "{what task}" --amount 50000
# - desc: Describe what task this budget is being requested for on behalf of the user
# - amount: The USDC amount in the smallest unit (6 decimals). For example, 1_000_000 represents 1 USDC.

# NOTE
# You need to remember the mandate ID to request the actual payment later, and ask the user to approve the authorization.
# You can wait about 10 seconds and then check the status using this method.
node ./scripts/fluxa-cli.bundle.js mandate-status --id <mandate-id>
```

Step 2: Use the budget mandate to request a payment signature (payment mandate)

```
node ./scripts/fluxa-cli.bundle.js x402-v3 \
    --mandate <MANDATE_ID> \
    --payload '<JSON>'

# Get `data.xPaymentB64` from response as PAYMENT_MANDATE
# This PAYMENT_MANDATE is sent to the server via the **X-Payment HTTP header** to complete the payment.
curl -H "X-PAYMENT: $PAYMENT_MANDATE" https://api.example.com/paid-endpoint

```


## Example

```
node ./scripts/fluxa-cli.bundle.js x402-v3 \
--mandate mand_Yfbpmb9PVZl05VaeR9nvQg \
--payload '{
  "x402Version": 1,
  "accepts": [{
    "scheme": "exact",
    ...
    "extra": {
      "name": "USD Coin",
      "version": "2"
    }
  }]
}'

## output:
{
  "success": true,
  "data": {
    "X-PAYMENT": "base64-encoded-payment-header..."
  }
}
```

## Others

* Error handing during payment flow(fluxa-cli or server error): see ./error-handle.md 

