#!/usr/bin/env npx ts-node

/**
 * create-email.ts
 * 
 * Create and manage disposable email accounts via Mail.tm API.
 * Allows agents to create email addresses, check messages, and store credentials.
 * 
 * Usage:
 *   npx ts-node create-email.ts                    # Create new email account
 *   npx ts-node create-email.ts list               # List stored email accounts
 *   npx ts-node create-email.ts messages <email>   # Check messages for an email
 *   npx ts-node create-email.ts read <messageId>   # Read a specific message
 * 
 * Environment:
 *   No environment variables required (Mail.tm is free)
 */

import * as fs from "fs";
import * as path from "path";

const MAIL_TM_API = "https://api.mail.tm";
const CREDENTIALS_FILE = ".agent-emails.json";

interface EmailAccount {
  address: string;
  password: string;
  token: string;
  accountId: string;
  createdAt: string;
  purpose?: string;
}

interface EmailCredentials {
  email_accounts: EmailAccount[];
}

interface MailTmDomain {
  id: string;
  domain: string;
  isActive: boolean;
}

interface MailTmMessage {
  id: string;
  from: { name: string; address: string };
  to: Array<{ name: string; address: string }>;
  subject: string;
  intro?: string;
  text?: string;
  html?: string[];
  seen: boolean;
  hasAttachments: boolean;
  createdAt: string;
}

interface CreateEmailResult {
  success: boolean;
  account?: EmailAccount;
  error?: string;
}

interface MessagesResult {
  success: boolean;
  messages?: MailTmMessage[];
  error?: string;
}

// Generate a random string for unique email addresses
function generateRandomString(length: number = 10): string {
  const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// Generate a secure password
function generatePassword(length: number = 16): string {
  const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// Get the path to the credentials file
function getCredentialsPath(): string {
  return path.join(process.cwd(), CREDENTIALS_FILE);
}

// Load stored credentials
function loadCredentials(): EmailCredentials {
  const filePath = getCredentialsPath();
  if (fs.existsSync(filePath)) {
    try {
      const data = fs.readFileSync(filePath, "utf-8");
      return JSON.parse(data);
    } catch {
      return { email_accounts: [] };
    }
  }
  return { email_accounts: [] };
}

// Save credentials
function saveCredentials(credentials: EmailCredentials): void {
  const filePath = getCredentialsPath();
  fs.writeFileSync(filePath, JSON.stringify(credentials, null, 2));
}

// Get available domains from Mail.tm
async function getDomains(): Promise<MailTmDomain[]> {
  const response = await fetch(`${MAIL_TM_API}/domains`);
  const data = await response.json();
  return data["hydra:member"] || [];
}

// Create a new email account
async function createEmailAccount(customAddress?: string): Promise<CreateEmailResult> {
  try {
    // Get available domains
    const domains = await getDomains();
    if (domains.length === 0) {
      return { success: false, error: "No available domains from Mail.tm" };
    }

    const domain = domains[0].domain;
    const localPart = customAddress || `agent-${generateRandomString()}`;
    const address = `${localPart}@${domain}`;
    const password = generatePassword();

    // Create account
    const createResponse = await fetch(`${MAIL_TM_API}/accounts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ address, password })
    });

    if (!createResponse.ok) {
      const errorData = await createResponse.json();
      return { 
        success: false, 
        error: errorData?.["hydra:description"] || `Failed to create account: ${createResponse.status}` 
      };
    }

    const accountData = await createResponse.json();

    // Get authentication token
    const tokenResponse = await fetch(`${MAIL_TM_API}/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ address, password })
    });

    if (!tokenResponse.ok) {
      return { success: false, error: "Failed to get authentication token" };
    }

    const tokenData = await tokenResponse.json();

    const account: EmailAccount = {
      address,
      password,
      token: tokenData.token,
      accountId: accountData.id,
      createdAt: new Date().toISOString()
    };

    // Save to credentials file
    const credentials = loadCredentials();
    credentials.email_accounts.push(account);
    saveCredentials(credentials);

    return { success: true, account };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error occurred"
    };
  }
}

// Get messages for an email account
async function getMessages(emailAddress: string): Promise<MessagesResult> {
  const credentials = loadCredentials();
  const account = credentials.email_accounts.find(a => a.address === emailAddress);

  if (!account) {
    return { success: false, error: `No stored credentials for ${emailAddress}` };
  }

  try {
    // Refresh token if needed
    const tokenResponse = await fetch(`${MAIL_TM_API}/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ address: account.address, password: account.password })
    });

    if (!tokenResponse.ok) {
      return { success: false, error: "Failed to authenticate" };
    }

    const tokenData = await tokenResponse.json();
    const token = tokenData.token;

    // Update stored token
    account.token = token;
    saveCredentials(credentials);

    // Fetch messages
    const messagesResponse = await fetch(`${MAIL_TM_API}/messages`, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!messagesResponse.ok) {
      return { success: false, error: `Failed to fetch messages: ${messagesResponse.status}` };
    }

    const messagesData = await messagesResponse.json();
    return { success: true, messages: messagesData["hydra:member"] || [] };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error occurred"
    };
  }
}

// Read a specific message
async function readMessage(emailAddress: string, messageId: string): Promise<{ success: boolean; message?: MailTmMessage; error?: string }> {
  const credentials = loadCredentials();
  const account = credentials.email_accounts.find(a => a.address === emailAddress);

  if (!account) {
    return { success: false, error: `No stored credentials for ${emailAddress}` };
  }

  try {
    // Refresh token
    const tokenResponse = await fetch(`${MAIL_TM_API}/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ address: account.address, password: account.password })
    });

    if (!tokenResponse.ok) {
      return { success: false, error: "Failed to authenticate" };
    }

    const tokenData = await tokenResponse.json();
    const token = tokenData.token;

    // Fetch message
    const messageResponse = await fetch(`${MAIL_TM_API}/messages/${messageId}`, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!messageResponse.ok) {
      return { success: false, error: `Failed to fetch message: ${messageResponse.status}` };
    }

    const message = await messageResponse.json();
    return { success: true, message };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error occurred"
    };
  }
}

// List stored email accounts
function listEmailAccounts(): EmailAccount[] {
  const credentials = loadCredentials();
  return credentials.email_accounts;
}

// CLI execution
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case "list": {
      console.log("Stored email accounts:\n");
      const accounts = listEmailAccounts();
      
      if (accounts.length === 0) {
        console.log("No email accounts stored.");
        console.log("Run without arguments to create a new email account.");
      } else {
        accounts.forEach((account, index) => {
          console.log(`${index + 1}. ${account.address}`);
          console.log(`   Created: ${account.createdAt}`);
          if (account.purpose) {
            console.log(`   Purpose: ${account.purpose}`);
          }
          console.log();
        });
      }
      break;
    }

    case "messages": {
      const email = args[1];
      if (!email) {
        console.error("Error: Please provide an email address");
        console.log("Usage: npx ts-node create-email.ts messages <email>");
        process.exit(1);
      }

      console.log(`Checking messages for: ${email}\n`);
      const result = await getMessages(email);

      if (result.success && result.messages) {
        if (result.messages.length === 0) {
          console.log("No messages in inbox.");
        } else {
          console.log(`Found ${result.messages.length} message(s):\n`);
          result.messages.forEach((msg, index) => {
            console.log(`${index + 1}. From: ${msg.from.address}`);
            console.log(`   Subject: ${msg.subject}`);
            console.log(`   Date: ${msg.createdAt}`);
            console.log(`   ID: ${msg.id}`);
            if (msg.intro) {
              console.log(`   Preview: ${msg.intro.substring(0, 100)}...`);
            }
            console.log();
          });
        }
      } else {
        console.error("Error:", result.error);
        process.exit(1);
      }
      break;
    }

    case "read": {
      const email = args[1];
      const messageId = args[2];
      
      if (!email || !messageId) {
        console.error("Error: Please provide email address and message ID");
        console.log("Usage: npx ts-node create-email.ts read <email> <messageId>");
        process.exit(1);
      }

      console.log(`Reading message ${messageId}...\n`);
      const result = await readMessage(email, messageId);

      if (result.success && result.message) {
        const msg = result.message;
        console.log(`From: ${msg.from.name} <${msg.from.address}>`);
        console.log(`Subject: ${msg.subject}`);
        console.log(`Date: ${msg.createdAt}`);
        console.log(`\n--- Message Content ---\n`);
        console.log(msg.text || "(No text content)");
      } else {
        console.error("Error:", result.error);
        process.exit(1);
      }
      break;
    }

    default: {
      // Create new email account
      const customAddress = command;
      
      console.log("Creating new disposable email account...\n");
      const result = await createEmailAccount(customAddress);

      if (result.success && result.account) {
        console.log("✓ Email account created successfully!\n");
        console.log(`  Address:  ${result.account.address}`);
        console.log(`  Password: ${result.account.password}`);
        console.log(`  Token:    ${result.account.token.substring(0, 20)}...`);
        console.log(`\nCredentials saved to: ${CREDENTIALS_FILE}`);
        console.log(`\nUse this email for signups, then check messages with:`);
        console.log(`  npx ts-node create-email.ts messages ${result.account.address}`);
      } else {
        console.error("✗ Failed to create email account");
        console.error("Error:", result.error);
        process.exit(1);
      }
      break;
    }
  }
}

// Export for use as a module
export { createEmailAccount, getMessages, readMessage, listEmailAccounts, EmailAccount };

// Run CLI if executed directly
main().catch(console.error);
