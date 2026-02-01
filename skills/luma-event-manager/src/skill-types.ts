// Generated from skill.json - DO NOT EDIT
// This file provides type definitions for skill.json

export interface ToolParameter {
  type: string;
  description?: string;
  enum?: string[];
}

export interface ToolParameters {
  type: "object";
  properties: Record<string, ToolParameter>;
  required?: string[];
}

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: ToolParameters;
}

export interface SkillJson {
  tools: Record<string, ToolDefinition>;
}

export const tools: Record<string, ToolDefinition> = {
  luma_host_events: {
    name: "luma_host_events",
    description: "List all events the user is hosting",
    parameters: {
      type: "object",
      properties: {
        status: {
          type: "string",
          description: "Filter by event status"
        }
      }
    }
  },
  luma_host_event: {
    name: "luma_host_event",
    description: "Get detailed information about a hosted event",
    parameters: {
      type: "object",
      properties: {
        event_id: {
          type: "string",
          description: "Luma event ID"
        }
      },
      required: ["event_id"]
    }
  },
  luma_host_guests: {
    name: "luma_host_guests",
    description: "View guest list for a hosted event",
    parameters: {
      type: "object",
      properties: {
        event_id: {
          type: "string",
          description: "Luma event ID"
        }
      },
      required: ["event_id"]
    }
  },
  luma_events_near: {
    name: "luma_events_near",
    description: "Discover events near a location",
    parameters: {
      type: "object",
      properties: {
        location: {
          type: "string",
          description: "Location (city, address, etc.)"
        },
        radius_miles: {
          type: "number",
          description: "Search radius in miles (default: 25)"
        },
        start_date: {
          type: "string",
          description: "Start date filter (ISO format)"
        },
        end_date: {
          type: "string",
          description: "End date filter (ISO format)"
        }
      },
      required: ["location"]
    }
  },
  luma_events_on: {
    name: "luma_events_on",
    description: "Find events on a specific date",
    parameters: {
      type: "object",
      properties: {
        date: {
          type: "string",
          description: "Date (today, tomorrow, or YYYY-MM-DD)"
        }
      },
      required: ["date"]
    }
  },
  luma_my_events: {
    name: "luma_my_events",
    description: "List events the user has RSVP'd to",
    parameters: {
      type: "object",
      properties: {}
    }
  },
  luma_event_details: {
    name: "luma_event_details",
    description: "Get detailed information about an event",
    parameters: {
      type: "object",
      properties: {
        event_id: {
          type: "string",
          description: "Luma event ID"
        }
      },
      required: ["event_id"]
    }
  },
  luma_rsvp: {
    name: "luma_rsvp",
    description: "RSVP to an event",
    parameters: {
      type: "object",
      properties: {
        event_id: {
          type: "string",
          description: "Luma event ID"
        },
        response: {
          type: "string",
          enum: ["yes", "no", "maybe", "waitlist"],
          description: "RSVP response (yes, no, maybe, waitlist)"
        }
      },
      required: ["event_id", "response"]
    }
  },
  luma_add_calendar: {
    name: "luma_add_calendar",
    description: "Add event to Google Calendar",
    parameters: {
      type: "object",
      properties: {
        event_id: {
          type: "string",
          description: "Luma event ID"
        },
        account: {
          type: "string",
          description: "Google account email for gog CLI"
        },
        calendar_id: {
          type: "string",
          description: "Google Calendar ID (default: primary)"
        }
      },
      required: ["event_id"]
    }
  },
  luma_search: {
    name: "luma_search",
    description: "Search events by topic, theme, or keyword",
    parameters: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query (topic, theme, keyword)"
        },
        location: {
          type: "string",
          description: "Optional location to narrow results"
        }
      },
      required: ["query"]
    }
  },
  luma_configure: {
    name: "luma_configure",
    description: "Configure Luma API key",
    parameters: {
      type: "object",
      properties: {}
    }
  },
  luma_status: {
    name: "luma_status",
    description: "Check Luma connection status",
    parameters: {
      type: "object",
      properties: {}
    }
  },
  luma_help: {
    name: "luma_help",
    description: "Show help for Luma skill",
    parameters: {
      type: "object",
      properties: {}
    }
  }
};
