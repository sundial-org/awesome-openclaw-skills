# ShapeScale Stripe Extensions - Usage Examples

This document provides detailed examples for the ShapeScale-specific commands.

## Clinic Operations

### Create a Standard Clinic

```bash
./shapescale-ext.sh clinic create "Bay Area Wellness"
# Creates customer with standard template (deposit: 5000 cents)
```

### Create a Premium Clinic

```bash
./shapescale-ext.sh clinic create "Elite Fitness Center" premium
# Creates customer with premium template (deposit: 10000 cents)
```

### List All Clinics

```bash
./shapescale-ext.sh clinic list
# Returns all customers with metadata.type=clinic
```

## Subscription Operations

### Create Monthly Subscription

```bash
./shapescale-ext.sh subscription create cus_ABC123 monthly
# Creates $399/month subscription
```

### Create Annual Subscription

```bash
./shapescale-ext.sh subscription create cus_ABC123 annual
# Creates $3,990/year subscription
```

### List Customer Subscriptions

```bash
./shapescale-ext.sh subscription list cus_ABC123
```

### Cancel Subscription

```bash
./shapescale-ext.sh subscription cancel sub_XYZ789
```

## Invoice Operations

### Generate Invoice for Order

```bash
./shapescale-ext.sh invoice generate cus_ABC123 ORDER-2026-001
# Creates invoice with order reference
```

## Order Operations

### Check Order Payment Status

```bash
./shapescale-ext.sh order status ORDER-2026-001
# Searches for payment with metadata.order_id=ORDER-2026-001
```

## Workflow Examples

### Complete Clinic Onboarding

```bash
# 1. Create clinic customer
./shapescale-ext.sh clinic create "New Practice" standard

# 2. Create subscription (using returned customer ID)
./shapescale-ext.sh subscription create cus_XXXXX annual

# 3. Generate first invoice
./shapescale-ext.sh invoice generate cus_XXXXX ORDER-001
```

### Process Refund

```bash
# 1. Check order status to find payment
./shapescale-ext.sh order status ORDER-2026-001

# 2. Get payment intent ID from result
# 3. Refund via universal command
../stripe.sh payment refund pi_XXXXX
```

## Testing Webhooks Locally

```bash
# Terminal 1: Listen for webhooks
../stripe.sh webhook listen 300

# Terminal 2: Trigger test event
../stripe.sh webhook trigger payment_intent.succeeded
```
