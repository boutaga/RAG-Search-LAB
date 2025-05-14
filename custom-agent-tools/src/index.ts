#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

/**
 * In-memory storage for chat logs, tickets, feedback, and problem links.
 * In a real implementation, this would be backed by a database.
 */
const chatLogs: Record<string, { conversationId: string; role: string; content: string; createdAt: string }> = {};
const tickets: Record<string, { ticketId: string; title: string; status: string; assignee: string; notes: string[] }> = {};
const feedbacks: Record<string, { logId: string; rating: number; comments: string; createdAt: string }> = {};
const problemLinks: Record<string, { ticketId: string; problemId: string; linkType: string; createdAt: string }> = {};

/**
 * Create an MCP server with capabilities for chat logs, tickets, feedback, and problem links as resources,
 * and tools to add new chat logs, update tickets, perform search, submit feedback, and link problems.
 */
const server = new Server(
  {
    name: "SD-MCP",
    version: "0.6.0",
  },
  {
    capabilities: {
      resources: {},
      tools: {},
    },
  }
);

// Handler for listing all resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  const chatLogResources = Object.entries(chatLogs).map(([id, log]) => ({
    uri: `chatlog:///${id}`,
    mimeType: "text/plain",
    name: `Chat log ${id}`,
    description: `Chat log from conversation ${log.conversationId} by ${log.role}`,
  }));

  const ticketResources = Object.entries(tickets).map(([id, ticket]) => ({
    uri: `ticket:///${id}`,
    mimeType: "text/plain",
    name: `Ticket ${id}: ${ticket.title}`,
    description: `Ticket status: ${ticket.status}, assignee: ${ticket.assignee}`,
  }));

  const feedbackResources = Object.entries(feedbacks).map(([id, fb]) => ({
    uri: `feedback:///${id}`,
    mimeType: "text/plain",
    name: `Feedback ${id}`,
    description: `Feedback for log ${fb.logId} with rating ${fb.rating}`,
  }));

  const problemLinkResources = Object.entries(problemLinks).map(([id, link]) => ({
    uri: `problemlink:///${id}`,
    mimeType: "text/plain",
    name: `Problem Link ${id}`,
    description: `Link between ticket ${link.ticketId} and problem ${link.problemId} (${link.linkType})`,
  }));

  return {
    resources: [...chatLogResources, ...ticketResources, ...feedbackResources, ...problemLinkResources],
  };
});

// Handler for reading a specific resource
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const url = new URL(request.params.uri);
  const id = url.pathname.replace(/^\//, '');
  if (request.params.uri.startsWith("chatlog://")) {
    const log = chatLogs[id];
    if (!log) {
      throw new Error(`Chat log ${id} not found`);
    }
    return {
      contents: [{
        uri: request.params.uri,
        mimeType: "text/plain",
        text: `[${log.createdAt}] (${log.role}): ${log.content}`
      }]
    };
  } else if (request.params.uri.startsWith("ticket://")) {
    const ticket = tickets[id];
    if (!ticket) {
      throw new Error(`Ticket ${id} not found`);
    }
    return {
      contents: [{
        uri: request.params.uri,
        mimeType: "text/plain",
        text: `Title: ${ticket.title}\nStatus: ${ticket.status}\nAssignee: ${ticket.assignee}\nNotes:\n${ticket.notes.join("\n")}`
      }]
    };
  } else if (request.params.uri.startsWith("feedback://")) {
    const fb = feedbacks[id];
    if (!fb) {
      throw new Error(`Feedback ${id} not found`);
    }
    return {
      contents: [{
        uri: request.params.uri,
        mimeType: "text/plain",
        text: `Feedback for log ${fb.logId}\nRating: ${fb.rating}\nComments: ${fb.comments}\nCreated at: ${fb.createdAt}`
      }]
    };
  } else if (request.params.uri.startsWith("problemlink://")) {
    const link = problemLinks[id];
    if (!link) {
      throw new Error(`Problem link ${id} not found`);
    }
    return {
      contents: [{
        uri: request.params.uri,
        mimeType: "text/plain",
        text: `Ticket ID: ${link.ticketId}\nProblem ID: ${link.problemId}\nLink Type: ${link.linkType}\nCreated at: ${link.createdAt}`
      }]
    };
  } else {
    throw new Error("Unknown resource type");
  }
});

// Handler that lists available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "add_chat_log",
        description: "Add a new chat log entry",
        inputSchema: {
          type: "object",
          properties: {
            conversationId: { type: "string", description: "Conversation UUID" },
            role: { type: "string", description: "Role of the speaker (user or agent)" },
            content: { type: "string", description: "Chat message content" },
          },
          required: ["conversationId", "role", "content"],
        },
      },
      {
        name: "update_ticket",
        description: "Update ticket status, assignee, or add notes",
        inputSchema: {
          type: "object",
          properties: {
            ticketId: { type: "string", description: "Ticket ID" },
            status: { type: "string", description: "New status" },
            assignee: { type: "string", description: "Assignee user ID" },
            note: { type: "string", description: "Note to add" },
          },
          required: ["ticketId"],
        },
      },
      {
        name: "search",
        description: "Search chat logs and tickets by keyword",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Search query string" },
            limit: { type: "number", description: "Maximum number of results", default: 10 },
          },
          required: ["query"],
        },
      },
      {
        name: "submit_feedback",
        description: "Submit feedback for a chat log",
        inputSchema: {
          type: "object",
          properties: {
            logId: { type: "string", description: "Chat log ID" },
            rating: { type: "number", description: "Rating (1-5)" },
            comments: { type: "string", description: "Optional comments" },
          },
          required: ["logId", "rating"],
        },
      },
      {
        name: "link_problem",
        description: "Link a ticket to a problem",
        inputSchema: {
          type: "object",
          properties: {
            ticketId: { type: "string", description: "Ticket ID" },
            problemId: { type: "string", description: "Problem ID" },
            linkType: { type: "string", description: "Type of link (e.g., related, root_cause)" },
          },
          required: ["ticketId", "problemId"],
        },
      },
    ],
  };
});

// Handler for the tools
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  switch (request.params.name) {
    case "add_chat_log": {
      const { conversationId, role, content } = request.params.arguments || {};
      if (!conversationId || !role || !content) {
        throw new Error("Missing required parameters");
      }
      const id = String(Object.keys(chatLogs).length + 1);
      chatLogs[id] = {
        conversationId: String(conversationId),
        role: String(role),
        content: String(content),
        createdAt: new Date().toISOString(),
      };
      return {
        content: [{
          type: "text",
          text: `Added chat log ${id} to conversation ${conversationId}`,
        }],
      };
    }
    case "update_ticket": {
      const { ticketId, status, assignee, note } = request.params.arguments || {};
      if (!ticketId) {
        throw new Error("Missing ticketId");
      }
      let ticket = tickets[String(ticketId)];
      if (!ticket) {
        // Create a new ticket if not exists
        ticket = {
          ticketId: String(ticketId),
          title: `Ticket ${String(ticketId)}`,
          status: typeof status === "string" ? status : "Open",
          assignee: typeof assignee === "string" ? assignee : "Unassigned",
          notes: [],
        };
        tickets[String(ticketId)] = ticket;
      }
      if (typeof status === "string") ticket.status = status;
      if (typeof assignee === "string") ticket.assignee = assignee;
      if (typeof note === "string") ticket.notes.push(note);
      return {
        content: [{
          type: "text",
          text: `Updated ticket ${ticketId}`,
        }],
      };
    }
    case "search": {
      const { query, limit } = request.params.arguments || {};
      if (!query) {
        throw new Error("Missing search query");
      }
      const maxResults = typeof limit === "number" ? limit : 10;
      const results = [];

      // Search chat logs
      for (const [id, log] of Object.entries(chatLogs)) {
        if (String(log.content).includes(String(query)) || String(log.conversationId).includes(String(query))) {
          results.push({
            type: "chat_log",
            id,
            conversationId: log.conversationId,
            role: log.role,
            content: log.content,
            createdAt: log.createdAt,
          });
          if (results.length >= maxResults) break;
        }
      }

      // If not enough results, search tickets
      if (results.length < maxResults) {
        for (const [id, ticket] of Object.entries(tickets)) {
          if (
            String(ticket.title).includes(String(query)) ||
            String(ticket.status).includes(String(query)) ||
            String(ticket.assignee).includes(String(query)) ||
            ticket.notes.some(note => String(note).includes(String(query)))
          ) {
            results.push({
              type: "ticket",
              id,
              title: ticket.title,
              status: ticket.status,
              assignee: ticket.assignee,
              notes: ticket.notes,
            });
            if (results.length >= maxResults) break;
          }
        }
      }

      return {
        content: [{
          type: "json",
          json: results,
        }],
      };
    }
    case "submit_feedback": {
      const { logId, rating, comments } = request.params.arguments || {};
      if (!logId || typeof rating !== "number") {
        throw new Error("Missing required parameters");
      }
      const id = String(Object.keys(feedbacks).length + 1);
      feedbacks[id] = {
        logId: String(logId),
        rating,
        comments: comments ? String(comments) : "",
        createdAt: new Date().toISOString(),
      };
      return {
        content: [{
          type: "text",
          text: `Submitted feedback ${id} for log ${logId}`,
        }],
      };
    }
    case "link_problem": {
      const { ticketId, problemId, linkType } = request.params.arguments || {};
      if (!ticketId || !problemId) {
        throw new Error("Missing required parameters");
      }
      const id = String(Object.keys(problemLinks).length + 1);
      problemLinks[id] = {
        ticketId: String(ticketId),
        problemId: String(problemId),
        linkType: linkType ? String(linkType) : "related",
        createdAt: new Date().toISOString(),
      };
      return {
        content: [{
          type: "text",
          text: `Linked ticket ${ticketId} to problem ${problemId} as ${linkType || "related"}`,
        }],
      };
    }
    default:
      throw new Error("Unknown tool");
  }
});

// Start the server using stdio transport
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
</final_file_content>
