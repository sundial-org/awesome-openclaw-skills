# Troubleshooting

## Common Issues

### "Device not found"
- Use partial name matching (case-insensitive)
- Try `python3 scripts/govee.py list` to see exact device names
- Example: "lamp" matches "RGBICW Floor Lamp Basic"

### API Errors (HTTP 4xx/5xx)
- Verify API key is valid and not expired
- Check API key format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Ensure account has active Govee devices

### ModuleNotFoundError: No module named 'requests'
```bash
pip3 install requests
```

### Permission Denied
```bash
chmod +x scripts/govee.py
```

## Debug Mode

Add `--debug` flag for verbose output (if supported) or check stderr:
```bash
python3 scripts/govee.py list 2>&1
```

## API Key Issues

If you get authentication errors:
1. Log into [Govee Developer Portal](https://developer.govee.com/)
2. Navigate to API Keys section
3. Generate a new key if current one is invalid
4. Update environment variable: `export GOVEE_API_KEY="new-key"`
