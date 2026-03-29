"use client";
import React, { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

type Message = {
  id: number;
  from: "user" | "bot";
  text: string;
  ts: string;
  isDownload?: boolean;
  isEscalated?: boolean;
  confidence?: number;
  kycConfidence?: number;
};

type PipelineEvent = {
  stage: string;
  agent: string;
  status: string;
  confidence?: number;
  detail: string;
  ts: string;
};

function ts() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ChatPage() {
  const router = useRouter();

  const [user, setUser] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [typing, setTyping] = useState(false);
  const [idCounter, setIdCounter] = useState(0);

  const [pipelineEvents, setPipelineEvents] = useState<PipelineEvent[]>([]);
  const [activeStage, setActiveStage] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const userId = useRef("default");

  // 🔹 INIT
  useEffect(() => {
    const stored = localStorage.getItem("finsense_user");
    if (!stored) {
      router.push("/login");
      return;
    }

    setUser(stored);
    userId.current = stored.toLowerCase().replace(/\s+/g, "_");

    setMessages([
      {
        id: 0,
        from: "bot",
        ts: ts(),
        text: `Hi ${stored} 👋 I'm FinSense.\n\nType "I want a loan" to begin.`,
      },
    ]);

    setIdCounter(1);
  }, [router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  function applyPipelineEvents(events: PipelineEvent[]) {
    if (!events?.length) return;
    setPipelineEvents(prev => [...prev, ...events]);
    setActiveStage(events[events.length - 1].stage);
  }

  // 🔥 FINAL SEND FUNCTION
  async function send(text?: string) {
    const msg = (text ?? input).trim();
    if (!msg) return;

    const uid = idCounter;
    setIdCounter(c => c + 3);

    // ✅ RESET PIPELINE ON NEW LOAN START
    if (msg.toLowerCase().includes("loan")) {
      setPipelineEvents([]);
      setActiveStage(null);
    }

    setMessages(prev => [
      ...prev,
      { id: uid, from: "user", text: msg, ts: ts() }
    ]);

    setInput("");
    setTyping(true);
    inputRef.current?.focus();

    // ✅ FAILSAFE: prevent infinite loader
    setTimeout(() => setTyping(false), 10000);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: msg,
          user_id: userId.current,
        }),
      });

      const data = await res.json();

      setMessages(prev => [
        ...prev,
        {
          id: uid + 1,
          from: "bot",
          text: data.reply ?? "I'm here to help 😊",
          ts: ts(),
          isEscalated: !!data.escalated,
          confidence: data.confidence,
          kycConfidence: data.kyc_confidence,
        },

        // ✅ PREVENT DUPLICATE SANCTION BUTTON
        ...(data.sanction_letter && !prev.some(m => m.isDownload)
          ? [
              {
                id: uid + 2,
                from: "bot" as const,
                text: "",
                ts: ts(),
                isDownload: true,
              },
            ]
          : []),
      ]);

      // ✅ PIPELINE UPDATE
      if (data.pipeline_events?.length) {
        applyPipelineEvents(data.pipeline_events);
      }

    } catch {
      setMessages(prev => [
        ...prev,
        {
          id: uid + 1,
          from: "bot",
          ts: ts(),
          text: "⚠️ Backend not reachable",
        },
      ]);
    } finally {
      setTyping(false);
    }
  }

  function onKey(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  function logout() {
    localStorage.removeItem("finsense_user");
    router.push("/login");
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">

      {/* HEADER */}
      <div className="bg-white px-6 py-3 flex justify-between items-center shadow">
        <h1 className="font-bold">🤖 FinSense AI</h1>
        <button onClick={logout} className="text-sm text-red-500">Logout</button>
      </div>

      {/* CHAT */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(m => (
          <div key={m.id} className={`flex ${m.from === "user" ? "justify-end" : "justify-start"}`}>
            
            {m.isDownload ? (
              <a
                href="http://127.0.0.1:8000/download"
                target="_blank"
                className="bg-green-600 text-white px-4 py-2 rounded-lg"
              >
                📄 Download Sanction Letter
              </a>
            ) : (
              <div className={`px-4 py-2 rounded-xl max-w-[70%] ${
                m.from === "user" ? "bg-blue-600 text-white" : "bg-white border"
              }`}>
                {m.text}

                {(m.confidence || m.kycConfidence) && (
                  <div className="text-xs mt-1 opacity-70">
                    {m.kycConfidence && `KYC: ${m.kycConfidence}% `}
                    {m.confidence && `| Score: ${m.confidence}%`}
                  </div>
                )}
              </div>
            )}

          </div>
        ))}

        {typing && <p className="text-sm text-gray-400">Typing...</p>}

        <div ref={bottomRef} />
      </div>

      {/* INPUT */}
      <div className="p-4 bg-white border-t flex gap-2">
        <input
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKey}
          placeholder="Type your message..."
          className="flex-1 border px-3 py-2 rounded-lg"
        />

        <button
          onClick={() => send()}
          disabled={!input.trim() || typing}
          className="bg-blue-600 text-white px-4 rounded-lg disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}