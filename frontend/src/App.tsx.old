import React, { useEffect, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader } from "@/components/ui/dialog";
import { ChevronDoubleUpIcon } from "lucide-react";
import { v4 as uuid } from "uuid";
import clsx from "clsx";

/**
 * Environment
 * --------------------------------------------------
 * Set VITE_API_URL in your `.env` to the FastAPI base URL, e.g.
 *   VITE_API_URL="http://localhost:8000"
 * --------------------------------------------------
 */
const API_URL = import.meta.env.VITE_API_URL ?? "";

/** ------------------------------------------------------------------------
 * Types
 * --------------------------------------------------------------------- */

export type Role = "user" | "assistant";

export interface Citation {
  chunk_id: string;
  source: string;
  page?: number;
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  citations?: Citation[];
}

/** ------------------------------------------------------------------------
 * Utility: stream response as it comes (Server‑Sent Events or fetch/ReadableStream)
 * --------------------------------------------------------------------- */
async function* streamChat(
  body: { query: string; filters?: Record<string, string[]> },
): AsyncGenerator<string, void, unknown> {
  const resp = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok || !resp.body) throw new Error("Network error");
  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let done = false;
  while (!done) {
    const { value, done: doneReading } = await reader.read();
    if (value) yield decoder.decode(value, { stream: true });
    done = doneReading;
  }
}

/** ------------------------------------------------------------------------
 * Chat UI Component
 * --------------------------------------------------------------------- */
export default function App() {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeCitations, setActiveCitations] = useState<Citation[] | null>(
    null,
  );
  const [metadata, setMetadata] = useState<Record<string, string[]>>({});
  const [filters, setFilters] = useState<Record<string, string[]>>({});

  // load filter metadata on mount
  useEffect(() => {
    fetch(`${API_URL}/metadata`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((data) => setMetadata(data))
      .catch(() => {
        /* ignore */
      });
  }, []);

  /** auto‑scroll chat */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  /** Submit query */
  const handleSubmit = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = { id: uuid(), role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    let assistantMsg: Message = {
      id: uuid(),
      role: "assistant",
      content: "", // will stream
    };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      for await (const token of streamChat({ query: input, filters })) {
        assistantMsg = {
          ...assistantMsg,
          content: assistantMsg.content + token,
        } as Message;
        setMessages((prev) => {
          const list = [...prev];
          list[list.length - 1] = assistantMsg;
          return list;
        });
      }
      // fetch citations after stream complete
      const citResp = await fetch(`${API_URL}/chat/citations/${assistantMsg.id}`);
      if (citResp.ok) {
        assistantMsg = {
          ...assistantMsg,
          citations: await citResp.json(),
        };
        setMessages((prev) => {
          const list = [...prev];
          list[list.length - 1] = assistantMsg;
          return list;
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  /** keyboard: Enter = send, Shift+Enter = newline */
  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="h-screen w-screen grid grid-cols-[320px_1fr] divide-x">
      {/* ------------- Left Rail (Search & Filters) ------------- */}
      <aside className="p-4 flex flex-col gap-6">
        <h1 className="text-xl font-semibold">Search</h1>
        <Input
          placeholder="Keyword or natural‑language query…"
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSubmit();
          }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <div className="space-y-3">
          <h2 className="text-sm font-medium text-muted-foreground">Filters</h2>
          {Object.entries(metadata).map(([group, values]) => (
            <div key={group} className="space-y-1">
              <p className="text-xs capitalize text-muted-foreground">{group}</p>
              {values.map((val) => (
                <label key={val} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    className="border-muted"
                    checked={filters[group]?.includes(val) || false}
                    onChange={(e) => {
                      setFilters((prev) => {
                        const current = prev[group] || [];
                        if (e.target.checked) {
                          return {
                            ...prev,
                            [group]: [...current, val],
                          };
                        }
                        return {
                          ...prev,
                          [group]: current.filter((v) => v !== val),
                        };
                      });
                    }}
                  />
                  {val}
                </label>
              ))}
            </div>
          ))}
        </div>
      </aside>

      {/* ------------- Right Pane (Chat Thread) ------------- */}
      <section className="relative flex flex-col h-full">
        {/* Chat history */}
        <ScrollArea className="flex-1 p-6 space-y-4 overflow-y-auto">
          {messages.map((msg) => (
            <Card
              key={msg.id}
              className={clsx(
                "w-fit max-w-[75%]",
                msg.role === "user" ? "ml-auto" : "mr-auto",
              )}
            >
              <CardContent className="whitespace-pre-wrap p-4 text-sm">
                {msg.content}
                {msg.citations && msg.citations.length > 0 && (
                  <Button
                    variant="link"
                    className="mt-2 text-xs"
                    onClick={() => setActiveCitations(msg.citations!)}
                  >
                    {msg.citations.length} source
                    {msg.citations.length > 1 ? "s" : ""}
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
          {loading && (
            <Card className="mr-auto animate-pulse opacity-70">
              <CardContent className="p-4 text-sm">…</CardContent>
            </Card>
          )}
          <div ref={bottomRef} />
        </ScrollArea>

        {/* Composer */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          className="p-4 border-t flex items-end gap-2 bg-background"
        >
          <Input
            placeholder="Ask me anything about the knowledge base…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKey}
            className="flex-1"
          />
          <Button type="submit" disabled={loading || !input.trim()}>
            <ChevronDoubleUpIcon className="w-4 h-4" />
          </Button>
        </form>
      </section>

      {/* ------------- Citation Drawer ------------- */}
      <Dialog open={!!activeCitations} onOpenChange={() => setActiveCitations(null)}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>Citations</DialogHeader>
          <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
            {activeCitations?.map((c) => (
              <Card key={c.chunk_id} className="border-muted">
                <CardContent className="p-4 space-y-2">
                  <p className="text-xs font-mono text-muted-foreground">
                    {c.source} — chunk {c.chunk_id}
                  </p>
                  <p className="text-sm leading-relaxed">
                    {/* placeholder: the backend should return snippet */}
                    Snippet preview will appear here…
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
