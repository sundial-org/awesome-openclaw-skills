## fluxa-cli error

* x402 command

  - **FluxA Agent ID not initialized**: see ./initialize-agent-id.md to initialize fluxa-cli.
  - **Other errors**: if it is a clearly identified fluxa-cli error, explain it to the user. If it is an unknown error, retry once. If it remains unknown, inform the user that the **FluxA Wallet is temporarily unavailable** and ask them to try again later.



## Server error

If you encounter an error after passing **X-Payment** as an HTTP header, refer to this troubleshooting guide.

- **Insufficient gas**: x402 payments do **not** require the payer to pay gas fees. This error is likely caused by a **server-side payment gateway issue**. Retry twice. If it still fails, inform the user that the **server payment gateway is unavailable** and ask them to try again later.

* **Other errors**: if it is a clearly identified server error, explain it to the user. If it is an unknown error, retry once. If it remains unknown, inform the user that the **Server is temporarily unavailable** and ask them to try again later.