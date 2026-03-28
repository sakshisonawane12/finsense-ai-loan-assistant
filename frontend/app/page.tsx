"use client";

import React, { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

type Message = {
  id: number;
  from: "user" | "bot";
  text: string;
  ts: string;
  isDownload?: boolean;
};

const QUICK_REPLIES = [
  "I want a loan",
  "5 lakh",
  "5 years",
  "50000",
];

function timestamp() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ChatPage() {
  const router = useRouter();
  const [user, setUser] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [typing, setTyping] = useState(false);
  const [idCounter, setIdCounter] = useState(0);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const stored = localStorage.getItem("finsense_user");
    if (!stored) { router.push("/login"); return; }
    setUser(stored);
    // Welcome message
    setMessages([{
      id: 0,
      from: "bot",
      text: `Hi ${stored} 👋 I'm FinSense, your AI loan assistant. Type "I want a loan" to get started!`,
      ts: timestamp(),
    }]);
    setIdCounter(1);
  }, [router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  function logout() {
    localStorage.removeItem("finsense_user");
    router.push("/login");
  }

  async function send(text?: string) {
    const msg = (text ?? input).trim();
    if (!msg) return;

    const uid = idCounter;
    setIdCounter(c => c + 2);
    setMessages(prev => [...prev, { id: uid, from: "user", text: msg, ts: timestamp() }]);
    setInput("");
    setTyping(true);
    inputRef.current?.focus();

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });
      const data = await res.json();

      setMessages(prev => [
        ...prev,
        { id: uid + 1, from: "bot", text: data.reply ?? "I'm here to help 😊", ts: timestamp() },
        ...(data.sanction_letter ? [{ id: uid + 2, from: "bot" as const, text: "", ts: timestamp(), isDownload: true }] : []),
      ]);
    } catch {
      setMessages(prev => [...prev, { id: uid + 1, from: "bot", text: "⚠️ Couldn't reach the server. Make sure the backend is running.", ts: timestamp() }]);
    } finally {
      setTyping(false);
    }
  }

  function onKey(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f0f4ff] to-[#e8f0fe] flex flex-col">

      {/* ── Top bar ── */}
      <header className="bg-white border-b border-gray-100 shadow-sm px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white font-bold text-sm shadow-md">F</div>
          <div>
            <p className="font-bold text-gray-900 text-sm">FinSense AI</p>
            <p className="text-xs text-green-500 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full inline-block" />
              Online · Powered by Mistral-7B
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500 hidden sm:block">👤 {user}</span>
          <button onClick={logout} className="text-xs text-gray-400 hover:text-red-500 transition border border-gray-200 px-3 py-1.5 rounded-lg hover:border-red-200">
            Logout
          </button>
        </div>
      </header>

      {/* ── Messages ── */}
      <main className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl w-full mx-auto space-y-4">
        {messages.map(m => (
          <div key={m.id} className={`flex gap-3 ${m.from === "user" ? "flex-row-reverse" : "flex-row"} animate-fade-in-up`}>
            {/* Avatar */}
            <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-sm font-bold shadow-sm ${m.from === "bot" ? "bg-gradient-to-br from-blue-600 to-indigo-700 text-white" : "bg-gradient-to-br from-gray-200 to-gray-300 text-gray-600"}`}>
              {m.from === "bot" ? "🤖" : user[0]?.toUpperCase() ?? "U"}
            </div>

            {/* Bubble */}
            {m.isDownload ? (
              <a
                href="http://127.0.0.1:8000/download"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-2xl rounded-tl-sm shadow-md hover:shadow-lg hover:scale-105 transition-all font-semibold text-sm"
              >
                📄 Download Sanction Letter
              </a>
            ) : (
              <div className={`max-w-[75%] group`}>
                <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                  m.from === "user"
                    ? "bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-tr-sm"
                    : "bg-white text-gray-800 rounded-tl-sm border border-gray-100"
                }`}>
                  {m.text}
                </div>
                <p className={`text-[10px] text-gray-400 mt-1 ${m.from === "user" ? "text-right" : "text-left"}`}>{m.ts}</p>
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {typing && (
          <div className="flex gap-3 animate-fade-in-up">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-sm">🤖</div>
            <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
              <div className="dot-flashing flex items-center gap-1 h-4">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </main>

      {/* ── Quick replies ── */}
      <div className="max-w-3xl w-full mx-auto px-4 pb-2 flex gap-2 flex-wrap">
        {QUICK_REPLIES.map(q => (
          <button
            key={q}
            onClick={() => send(q)}
            className="text-xs px-3 py-1.5 bg-white border border-blue-200 text-blue-600 rounded-full hover:bg-blue-50 hover:border-blue-400 transition font-medium shadow-sm"
          >
            {q}
          </button>
        ))}
      </div>

      {/* ── Input bar ── */}
      <div className="bg-white border-t border-gray-100 px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3 items-center">
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={onKey}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 rounded-xl border border-gray-200 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition"
          />
          <button
            onClick={() => send()}
            disabled={!input.trim() || typing}
            className="w-11 h-11 bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-xl flex items-center justify-center hover:opacity-90 transition disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-blue-200 flex-shrink-0"
          >
            <svg className="w-5 h-5 rotate-90" fill="currentColor" viewBox="0 0 24 24">
              <path d="M2 21l21-9L2 3v7l15 2-15 2z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
