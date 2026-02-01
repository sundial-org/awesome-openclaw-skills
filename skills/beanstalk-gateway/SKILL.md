# Beanstalk Gateway

Connect your local Clawdbot to [beans.talk](https://beans.talk) for remote monitoring and control.

## Install

```bash
npm install -g beanstalk-gateway
```

## Setup

1. Go to [beans.talk](https://beans.talk) and click "Connect Gateway"
2. Copy the setup command
3. Run it on your machine
4. Done!

## Manual Usage

```bash
# Configure
beanstalk-gateway configure --url wss://... --token gt_...

# Start
beanstalk-gateway start

# Check local Clawdbot status  
beanstalk-gateway status
```

## More Info

- [npm package](https://www.npmjs.com/package/beanstalk-gateway)
- [GitHub](https://github.com/tommygeoco/beanstalk-gateway)
