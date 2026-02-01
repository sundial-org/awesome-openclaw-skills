# Configuration

## API Key Setup

The skill requires a search.ch API key stored in the `SEARCHCH_API_KEY` environment variable.

### Get an API Key

1. Visit https://search.ch/tel/api/getkey.en.html
2. Fill out the request form
3. Receive your API key via email

### Set the Environment Variable

**Temporary (current session):**
```bash
export SEARCHCH_API_KEY="your-api-key-here"
```

**Permanent (add to shell profile):**
```bash
# For bash (~/.bashrc or ~/.bash_profile)
echo 'export SEARCHCH_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# For zsh (~/.zshrc)
echo 'export SEARCHCH_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**For Clawdbot Gateway:**

Add to your gateway config or environment:
```yaml
env:
  SEARCHCH_API_KEY: "your-api-key-here"
```

## API Limits

- Without API key: Limited queries, no structured data
- With API key: More queries per day, full structured data (Atom feed)
- Maximum results per query: 200

## Troubleshooting

### "Invalid API key" error
- Verify the key is correctly set: `echo $SEARCHCH_API_KEY`
- Check for extra whitespace or quotes in the key
- Ensure the key hasn't expired

### "Network Error"
- Check internet connectivity
- Verify https://search.ch is accessible
- Check for firewall/proxy issues

### No results found
- Try broader search terms
- Remove location filter to search nationwide
- Check spelling (umlauts matter: ü, ö, ä)
- Try different name variations

## Terms of Use

By using the search.ch API, you agree to their terms:
https://search.ch/tel/api/terms.en.html

Key points:
- Attribution required for public-facing applications
- Rate limits apply
- Commercial use may require special agreement
