#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { config } from "dotenv";

// Load environment variables
config();

const TENANT_ID = process.env.TENANT_ID!;
const CLIENT_ID = process.env.CLIENT_ID!;
const CLIENT_SECRET = process.env.CLIENT_SECRET!;
const DEFAULT_USER = process.env.DEFAULT_USER || "";

const GRAPH_BASE = "https://graph.microsoft.com/v1.0";

// Token cache
let tokenCache: { token: string; expires: number } | null = null;

async function getAccessToken(): Promise<string> {
  if (tokenCache && tokenCache.expires > Date.now()) {
    return tokenCache.token;
  }

  const response = await fetch(
    `https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        scope: "https://graph.microsoft.com/.default",
        grant_type: "client_credentials",
      }),
    }
  );

  const data = await response.json();
  if (data.error) {
    throw new Error(`Auth error: ${data.error_description}`);
  }

  tokenCache = {
    token: data.access_token,
    expires: Date.now() + (data.expires_in - 60) * 1000,
  };

  return data.access_token;
}

async function graphRequest(
  endpoint: string,
  method: string = "GET",
  body?: any
): Promise<any> {
  const token = await getAccessToken();
  const options: RequestInit = {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`${GRAPH_BASE}${endpoint}`, options);
  
  if (response.status === 204) {
    return { success: true };
  }
  
  const data = await response.json();
  
  if (data.error) {
    throw new Error(`Graph API error: ${data.error.message}`);
  }
  
  return data;
}

// Define all tools
const tools: Tool[] = [
  // === MAIL TOOLS ===
  {
    name: "m365_mail_list",
    description: "List emails from a user's mailbox",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email (default: configured user)" },
        folder: { type: "string", description: "Folder name (inbox, sentitems, drafts)", default: "inbox" },
        top: { type: "number", description: "Number of emails to return", default: 10 },
        filter: { type: "string", description: "OData filter (e.g., 'isRead eq false')" },
      },
    },
  },
  {
    name: "m365_mail_read",
    description: "Read a specific email by ID",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        messageId: { type: "string", description: "Message ID" },
      },
      required: ["messageId"],
    },
  },
  {
    name: "m365_mail_send",
    description: "Send an email",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "Sender email (must have SendAs permission)" },
        to: { type: "string", description: "Recipient email(s), comma-separated" },
        subject: { type: "string", description: "Email subject" },
        body: { type: "string", description: "Email body (HTML supported)" },
        cc: { type: "string", description: "CC recipients, comma-separated" },
      },
      required: ["to", "subject", "body"],
    },
  },
  {
    name: "m365_mail_search",
    description: "Search emails",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        query: { type: "string", description: "Search query" },
        top: { type: "number", description: "Number of results", default: 10 },
      },
      required: ["query"],
    },
  },

  // === CALENDAR TOOLS ===
  {
    name: "m365_calendar_list",
    description: "List calendar events",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        startDateTime: { type: "string", description: "Start date (ISO format)" },
        endDateTime: { type: "string", description: "End date (ISO format)" },
        top: { type: "number", description: "Number of events", default: 10 },
      },
    },
  },
  {
    name: "m365_calendar_create",
    description: "Create a calendar event",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        subject: { type: "string", description: "Event subject" },
        start: { type: "string", description: "Start datetime (ISO format)" },
        end: { type: "string", description: "End datetime (ISO format)" },
        body: { type: "string", description: "Event description" },
        location: { type: "string", description: "Event location" },
        attendees: { type: "string", description: "Attendee emails, comma-separated" },
        isOnline: { type: "boolean", description: "Create Teams meeting", default: false },
      },
      required: ["subject", "start", "end"],
    },
  },
  {
    name: "m365_calendar_availability",
    description: "Check user availability / free-busy status",
    inputSchema: {
      type: "object",
      properties: {
        users: { type: "string", description: "User emails to check, comma-separated" },
        startDateTime: { type: "string", description: "Start datetime (ISO format)" },
        endDateTime: { type: "string", description: "End datetime (ISO format)" },
      },
      required: ["users", "startDateTime", "endDateTime"],
    },
  },

  // === ONEDRIVE TOOLS ===
  {
    name: "m365_files_list",
    description: "List files and folders in OneDrive",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        path: { type: "string", description: "Folder path (empty for root)", default: "" },
        top: { type: "number", description: "Number of items", default: 20 },
      },
    },
  },
  {
    name: "m365_files_search",
    description: "Search for files in OneDrive",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        query: { type: "string", description: "Search query" },
        top: { type: "number", description: "Number of results", default: 10 },
      },
      required: ["query"],
    },
  },
  {
    name: "m365_files_read",
    description: "Read file content (text files only)",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        itemId: { type: "string", description: "File item ID" },
      },
      required: ["itemId"],
    },
  },
  {
    name: "m365_files_info",
    description: "Get file/folder metadata",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        itemId: { type: "string", description: "Item ID" },
      },
      required: ["itemId"],
    },
  },

  // === TASKS TOOLS ===
  {
    name: "m365_tasks_lists",
    description: "List all task lists (To-Do)",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
      },
    },
  },
  {
    name: "m365_tasks_list",
    description: "List tasks in a task list",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        listId: { type: "string", description: "Task list ID (use m365_tasks_lists to get)" },
        top: { type: "number", description: "Number of tasks", default: 20 },
      },
      required: ["listId"],
    },
  },
  {
    name: "m365_tasks_create",
    description: "Create a new task",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        listId: { type: "string", description: "Task list ID" },
        title: { type: "string", description: "Task title" },
        body: { type: "string", description: "Task description" },
        dueDateTime: { type: "string", description: "Due date (ISO format)" },
        importance: { type: "string", description: "low, normal, or high", default: "normal" },
      },
      required: ["listId", "title"],
    },
  },

  // === TEAMS TOOLS ===
  {
    name: "m365_teams_chats",
    description: "List user's Teams chats",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        top: { type: "number", description: "Number of chats", default: 20 },
      },
    },
  },
  {
    name: "m365_teams_messages",
    description: "Get messages from a Teams chat",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        chatId: { type: "string", description: "Chat ID" },
        top: { type: "number", description: "Number of messages", default: 20 },
      },
      required: ["chatId"],
    },
  },
  {
    name: "m365_teams_send",
    description: "Send a message to a Teams chat",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email" },
        chatId: { type: "string", description: "Chat ID" },
        message: { type: "string", description: "Message content" },
      },
      required: ["chatId", "message"],
    },
  },

  // === USER TOOLS ===
  {
    name: "m365_users_list",
    description: "List organization users",
    inputSchema: {
      type: "object",
      properties: {
        top: { type: "number", description: "Number of users", default: 20 },
        filter: { type: "string", description: "OData filter" },
      },
    },
  },
  {
    name: "m365_user_info",
    description: "Get user profile information",
    inputSchema: {
      type: "object",
      properties: {
        user: { type: "string", description: "User email or ID" },
      },
      required: ["user"],
    },
  },
];

// Tool handler implementations
async function handleTool(name: string, args: any): Promise<string> {
  const user = args.user || DEFAULT_USER;

  switch (name) {
    // === MAIL ===
    case "m365_mail_list": {
      const folder = args.folder || "inbox";
      const top = args.top || 10;
      let endpoint = `/users/${user}/mailFolders/${folder}/messages?$top=${top}&$select=id,subject,from,receivedDateTime,isRead,bodyPreview`;
      if (args.filter) endpoint += `&$filter=${encodeURIComponent(args.filter)}`;
      const data = await graphRequest(endpoint);
      return JSON.stringify(data.value.map((m: any) => ({
        id: m.id,
        subject: m.subject,
        from: m.from?.emailAddress?.address,
        received: m.receivedDateTime,
        isRead: m.isRead,
        preview: m.bodyPreview?.substring(0, 200),
      })), null, 2);
    }

    case "m365_mail_read": {
      const data = await graphRequest(`/users/${user}/messages/${args.messageId}`);
      return JSON.stringify({
        id: data.id,
        subject: data.subject,
        from: data.from?.emailAddress,
        to: data.toRecipients?.map((r: any) => r.emailAddress),
        received: data.receivedDateTime,
        body: data.body?.content,
      }, null, 2);
    }

    case "m365_mail_send": {
      const toRecipients = args.to.split(",").map((email: string) => ({
        emailAddress: { address: email.trim() },
      }));
      const message: any = {
        subject: args.subject,
        body: { contentType: "HTML", content: args.body },
        toRecipients,
      };
      if (args.cc) {
        message.ccRecipients = args.cc.split(",").map((email: string) => ({
          emailAddress: { address: email.trim() },
        }));
      }
      await graphRequest(`/users/${user}/sendMail`, "POST", { message });
      return JSON.stringify({ success: true, message: "Email sent successfully" });
    }

    case "m365_mail_search": {
      const data = await graphRequest(
        `/users/${user}/messages?$search="${encodeURIComponent(args.query)}"&$top=${args.top || 10}&$select=id,subject,from,receivedDateTime,bodyPreview`
      );
      return JSON.stringify(data.value, null, 2);
    }

    // === CALENDAR ===
    case "m365_calendar_list": {
      let endpoint = `/users/${user}/events?$top=${args.top || 10}&$select=id,subject,start,end,location,isOnlineMeeting,onlineMeetingUrl&$orderby=start/dateTime`;
      if (args.startDateTime && args.endDateTime) {
        endpoint = `/users/${user}/calendarView?startDateTime=${args.startDateTime}&endDateTime=${args.endDateTime}&$top=${args.top || 10}&$select=id,subject,start,end,location,isOnlineMeeting`;
      }
      const data = await graphRequest(endpoint);
      return JSON.stringify(data.value.map((e: any) => ({
        id: e.id,
        subject: e.subject,
        start: e.start,
        end: e.end,
        location: e.location?.displayName,
        isOnline: e.isOnlineMeeting,
        meetingUrl: e.onlineMeetingUrl,
      })), null, 2);
    }

    case "m365_calendar_create": {
      const event: any = {
        subject: args.subject,
        start: { dateTime: args.start, timeZone: "UTC" },
        end: { dateTime: args.end, timeZone: "UTC" },
      };
      if (args.body) event.body = { contentType: "HTML", content: args.body };
      if (args.location) event.location = { displayName: args.location };
      if (args.attendees) {
        event.attendees = args.attendees.split(",").map((email: string) => ({
          emailAddress: { address: email.trim() },
          type: "required",
        }));
      }
      if (args.isOnline) event.isOnlineMeeting = true;
      
      const data = await graphRequest(`/users/${user}/events`, "POST", event);
      return JSON.stringify({
        id: data.id,
        subject: data.subject,
        webLink: data.webLink,
        onlineMeetingUrl: data.onlineMeetingUrl,
      }, null, 2);
    }

    case "m365_calendar_availability": {
      const schedules = args.users.split(",").map((u: string) => u.trim());
      const data = await graphRequest(`/users/${user}/calendar/getSchedule`, "POST", {
        schedules,
        startTime: { dateTime: args.startDateTime, timeZone: "UTC" },
        endTime: { dateTime: args.endDateTime, timeZone: "UTC" },
      });
      return JSON.stringify(data.value, null, 2);
    }

    // === ONEDRIVE ===
    case "m365_files_list": {
      const path = args.path ? `:/${args.path}:` : "";
      const endpoint = `/users/${user}/drive/root${path}/children?$top=${args.top || 20}&$select=id,name,size,folder,file,webUrl,lastModifiedDateTime`;
      const data = await graphRequest(endpoint);
      return JSON.stringify(data.value.map((f: any) => ({
        id: f.id,
        name: f.name,
        size: f.size,
        isFolder: !!f.folder,
        mimeType: f.file?.mimeType,
        webUrl: f.webUrl,
        modified: f.lastModifiedDateTime,
      })), null, 2);
    }

    case "m365_files_search": {
      const data = await graphRequest(`/users/${user}/drive/root/search(q='${encodeURIComponent(args.query)}')?$top=${args.top || 10}`);
      return JSON.stringify(data.value.map((f: any) => ({
        id: f.id,
        name: f.name,
        path: f.parentReference?.path,
        webUrl: f.webUrl,
      })), null, 2);
    }

    case "m365_files_read": {
      const token = await getAccessToken();
      const metaResponse = await graphRequest(`/users/${user}/drive/items/${args.itemId}`);
      const downloadUrl = metaResponse["@microsoft.graph.downloadUrl"];
      
      const contentResponse = await fetch(downloadUrl);
      const content = await contentResponse.text();
      return content.substring(0, 50000); // Limit content size
    }

    case "m365_files_info": {
      const data = await graphRequest(`/users/${user}/drive/items/${args.itemId}`);
      return JSON.stringify(data, null, 2);
    }

    // === TASKS ===
    case "m365_tasks_lists": {
      const data = await graphRequest(`/users/${user}/todo/lists`);
      return JSON.stringify(data.value.map((l: any) => ({
        id: l.id,
        displayName: l.displayName,
        isOwner: l.isOwner,
      })), null, 2);
    }

    case "m365_tasks_list": {
      const listId = encodeURIComponent(args.listId);
      const data = await graphRequest(`/users/${user}/todo/lists/${listId}/tasks?$top=${args.top || 20}`);
      return JSON.stringify(data.value.map((t: any) => ({
        id: t.id,
        title: t.title,
        status: t.status,
        importance: t.importance,
        dueDateTime: t.dueDateTime,
        body: t.body?.content,
      })), null, 2);
    }

    case "m365_tasks_create": {
      const listId = encodeURIComponent(args.listId);
      const task: any = {
        title: args.title,
        importance: args.importance || "normal",
      };
      if (args.body) task.body = { contentType: "text", content: args.body };
      if (args.dueDateTime) task.dueDateTime = { dateTime: args.dueDateTime, timeZone: "UTC" };
      
      const data = await graphRequest(`/users/${user}/todo/lists/${listId}/tasks`, "POST", task);
      return JSON.stringify({ id: data.id, title: data.title, status: data.status }, null, 2);
    }

    // === TEAMS ===
    case "m365_teams_chats": {
      const data = await graphRequest(`/users/${user}/chats?$top=${args.top || 20}&$expand=members`);
      return JSON.stringify(data.value.map((c: any) => ({
        id: c.id,
        topic: c.topic,
        chatType: c.chatType,
        members: c.members?.map((m: any) => m.displayName),
      })), null, 2);
    }

    case "m365_teams_messages": {
      const data = await graphRequest(`/users/${user}/chats/${args.chatId}/messages?$top=${args.top || 20}`);
      return JSON.stringify(data.value.map((m: any) => ({
        id: m.id,
        from: m.from?.user?.displayName,
        content: m.body?.content,
        createdDateTime: m.createdDateTime,
      })), null, 2);
    }

    case "m365_teams_send": {
      const data = await graphRequest(`/users/${user}/chats/${args.chatId}/messages`, "POST", {
        body: { content: args.message },
      });
      return JSON.stringify({ id: data.id, success: true }, null, 2);
    }

    // === USERS ===
    case "m365_users_list": {
      let endpoint = `/users?$top=${args.top || 20}&$select=id,displayName,mail,userPrincipalName,jobTitle`;
      if (args.filter) endpoint += `&$filter=${encodeURIComponent(args.filter)}`;
      const data = await graphRequest(endpoint);
      return JSON.stringify(data.value, null, 2);
    }

    case "m365_user_info": {
      const data = await graphRequest(`/users/${args.user}?$select=id,displayName,mail,userPrincipalName,jobTitle,department,officeLocation,mobilePhone`);
      return JSON.stringify(data, null, 2);
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// Create and run the MCP server
const server = new Server(
  { name: "mcp-microsoft365", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const result = await handleTool(request.params.name, request.params.arguments || {});
    return {
      content: [{ type: "text", text: result }],
    };
  } catch (error: any) {
    return {
      content: [{ type: "text", text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP Microsoft 365 Server running on stdio");
}

main().catch(console.error);
