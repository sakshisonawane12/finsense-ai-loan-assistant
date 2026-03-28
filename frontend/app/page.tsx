"use client";

import React, { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

type Message = {
  id: number; from: "user" | "bot"; text: string; ts: string;
  isDownload?: boolean; isEscalated?: boolean;
  confidence?: number; kycConfidence?: number;
};

type PipelineEvent = {
  stage: string; agent: string; status: string;
  confidence?: number; detail: string; ts: string;
};

type AuditEntry = {
  ts: string; event: string; detail: string; status: string;
  confidence?: number; rule?: string; explanation?: string;
};

type EmiData = {
  emi: number; total_payable: number; total_interest: number;
  tenure_months: number; annual_rate: number;
};

type RuleCheck = {
  rule: string; description: string; actual: string; passed: boolean;
};

// All pipeline stages in order
const PIPELINE_STAGES = [
  { key: "start",        label: "Session Started",     agent: "Orchestrator",      icon: "🚀" },
  { key: "amount",       label: "Amount Captured",      agent: "Orchestrator",      icon: "💰" },
  { key: "doc_verify",   label: "Aadhaar Verified",     agent: "VerificationAgent", icon: "🪪" },
  { key: "tenure",       label: "Tenure Captured",      agent: "Orchestrator",      icon: "📅" },
  { key: "salary",       label: "Salary Captured",      agent: "Orchestrator",      icon: "💼" },
  { key: "kyc",          label: "KYC Verification",     agent: "VerificationAgent", icon: "🔍" },
  { key: "underwriting", label: "Underwriting",         agent: "UnderwritingAgent", icon: "📐" },
  { key: "sanction",     label: "Sanction Letter",      agent: "SanctionAgent",     icon: "📄" },
  { key: "escalation",   label: "Escalated",            agent: "EscalationHandler", icon: "⚠️" },
];

const QUICK_REPLIES = ["I want a loan", "5 lakh", "1234", "5 years", "50000", "yes"];

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
  const [audit, setAudit] = useState<AuditEntry[]>([]);
  const [emiData, setEmiData] = useState<EmiData | null>(null);
  const [rulesChecked, setRulesChecked] = useState<RuleCheck[]>([]);
  const [tab, setTab] = useState<"process" | "why" | "audit">("process");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const userId = useRef("default");

  useEffect(() => {
    const stored = localStorage.getItem("finsense_user");
    if (!stored) { router.push("/login"); return; }
    setUser(stored);
    userId.current = stored.toLowerCase().replace(/\s+/g, "_");
    setMessages([{
      id: 0, from: "bot", ts: ts(),
      text: `Hi ${stored} 👋 I'm FinSense, your AI loan assistant.\n\nType "I want a loan" to begin. I'll show you exactly what's happening at every step!`,
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

  function applyPipelineEvents(events: PipelineEvent[]) {
    if (!events?.length) return;
    setPipelineEvents(prev => [...prev, ...events]);
    setActiveStage(events[events.length - 1].stage);
  }

  async function send(text?: string) {
    const msg = (text ?? input).trim();
    if (!msg) return;

    const uid = idCounter;
    setIdCounter(c => c + 3);
    setMessages(prev => [...prev, { id: uid, from: "user", text: msg, ts: ts() }]);
    setInput("");
    setTyping(true);
    inputRef.current?.focus();

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg, user_id: userId.current }),
      });
      const data = await res.json();

      setMessages(prev => [
        ...prev,
        {
          id: uid + 1, from: "bot", text: data.reply ?? "I'm here to help 😊",
          ts: ts(), isEscalated: !!data.escalated,
          confidence: data.confidence, kycConfidence: data.kyc_confidence,
        },
        ...(data.sanction_letter
          ? [{ id: uid + 2, from: "bot" as const, text: "", ts: ts(), isDownload: true }]
          : []),
      ]);

      if (data.pipeline_events?.length) {
        applyPipelineEvents(data.pipeline_events);
        setTab("process");
      }
      if (data.audit?.length) setAudit(data.audit);
      if (data.emi) { setEmiData(data.emi); setTab("why"); }
      if (data.rules_checked?.length) setRulesChecked(data.rules_checked);

    } catch {
      setMessages(prev => [...prev, {
        id: uid + 1, from: "bot", ts: ts(),
        text: "⚠️ Couldn't reach the server. Make sure the backend is running on port 8000.",
      }]);
    } finally {
      setTyping(false);
    }
  }

  function onKey(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  }

  function getStageStatus(key: string) {
    const evts = pipelineEvents.filter(e => e.stage === key);
    return evts.length ? evts[evts.length - 1].status : "PENDING";
  }

  function getStageConf(key: string) {
    const evts = pipelineEvents.filter(e => e.stage === key && e.confidence);
    return evts.length ? evts[evts.length - 1].confidence! : null;
  }

  function getStageDetail(key: string) {
    const evts = pipelineEvents.filter(e => e.stage === key);
    return evts.length ? evts[evts.length - 1].detail : "";
  }

  const auditIcon: Record<string, string> = {
    OK: "✅", APPROVED: "✅", COMPLETED: "✅",
    REJECTED: "❌", FAILED: "❌", FAIL: "❌",
    ESCALATE: "⚠️", ESCALATED: "⚠️", INFO: "ℹ️",
  };

  const auditColor: Record<string, string> = {
    OK: "text-green-600", APPROVED: "text-green-600",
    REJECTED: "text-red-500", FAIL: "text-red-500",
    ESCALATE: "text-orange-500", INFO: "text-blue-500",
  };

  return (
    <div className="h-screen bg-[#f0f4ff] flex flex-col overflow-hidden">

      {/* Header */}
      <header className="bg-white border-b border-gray-100 shadow-sm px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white font-bold text-sm">F</div>
          <div>
            <p className="font-bold text-gray-900 text-sm">FinSense AI Loan Assistant</p>
            <p className="text-xs text-green-500 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full inline-block animate-pulse" />
              Online · Mistral-7B · Multi-Agent
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/dashboard" className="text-xs px-3 py-1.5 bg-gray-50 text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-100 transition">
            📊 Dashboard
          </Link>
          <span className="text-sm text-gray-500 hidden sm:block">👤 {user}</span>
          <button onClick={logout} className="text-xs text-gray-400 hover:text-red-500 border border-gray-200 px-3 py-1.5 rounded-lg transition">
            Logout
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">

        {/* ── LEFT: Chat ── */}
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          <div className="flex-1 overflow-y-auto px-4 py-5 space-y-4">
            {messages.map(m => (
              <div key={m.id} className={`flex gap-3 ${m.from === "user" ? "flex-row-reverse" : "flex-row"} animate-fade-in-up`}>
                <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-sm font-bold ${
                  m.from === "bot" ? "bg-gradient-to-br from-blue-600 to-indigo-700 text-white" : "bg-gray-200 text-gray-700"
                }`}>
                  {m.from === "bot" ? "🤖" : user[0]?.toUpperCase() ?? "U"}
                </div>

                {m.isDownload ? (
                  <a href="http://127.0.0.1:8000/download" target="_blank" rel="noreferrer"
                    className="flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-2xl rounded-tl-sm shadow-md hover:scale-105 transition-all font-semibold text-sm">
                    📄 Download Sanction Letter
                  </a>
                ) : (
                  <div className="max-w-[78%]">
                    <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm whitespace-pre-line ${
                      m.from === "user"
                        ? "bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-tr-sm"
                        : m.isEscalated
                          ? "bg-orange-50 border border-orange-200 text-orange-900 rounded-tl-sm"
                          : "bg-white text-gray-800 rounded-tl-sm border border-gray-100"
                    }`}>
                      {m.text}
                    </div>
                    {/* Confidence badges on bot messages */}
                    {(m.confidence || m.kycConfidence) && (
                      <div className="flex gap-2 mt-1.5 flex-wrap">
                        {m.kycConfidence && (
                          <span className="text-[10px] px-2 py-0.5 bg-green-50 border border-green-200 text-green-700 rounded-full font-medium">
                            KYC {m.kycConfidence}%
                          </span>
                        )}
                        {m.confidence && (
                          <span className="text-[10px] px-2 py-0.5 bg-blue-50 border border-blue-200 text-blue-700 rounded-full font-medium">
                            Underwriting {m.confidence}%
                          </span>
                        )}
                      </div>
                    )}
                    <p className={`text-[10px] text-gray-400 mt-1 ${m.from === "user" ? "text-right" : "text-left"}`}>{m.ts}</p>
                  </div>
                )}
              </div>
            ))}

            {typing && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-sm">🤖</div>
                <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                  <div className="dot-flashing flex items-center gap-1 h-4"><span /><span /><span /></div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Quick replies */}
          <div className="px-4 pb-2 flex gap-2 flex-wrap">
            {QUICK_REPLIES.map(q => (
              <button key={q} onClick={() => send(q)}
                className="text-xs px-3 py-1.5 bg-white border border-blue-200 text-blue-600 rounded-full hover:bg-blue-50 transition font-medium shadow-sm">
                {q}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="bg-white border-t border-gray-100 px-4 py-3">
            <div className="flex gap-3 items-center">
              <input ref={inputRef} value={input}
                onChange={e => setInput(e.target.value)} onKeyDown={onKey}
                placeholder="Type your message..."
                className="flex-1 px-4 py-3 rounded-xl border border-gray-200 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm transition" />
              <button onClick={() => send()} disabled={!input.trim() || typing}
                className="w-11 h-11 bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-xl flex items-center justify-center hover:opacity-90 transition disabled:opacity-40 shadow-md flex-shrink-0">
                <svg className="w-5 h-5 rotate-90" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M2 21l21-9L2 3v7l15 2-15 2z" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* ── RIGHT: What's Happening Panel ── */}
        <div className="w-80 bg-white border-l border-gray-100 flex flex-col flex-shrink-0 overflow-hidden">

          {/* Tabs */}
          <div className="flex border-b border-gray-100 flex-shrink-0">
            {([
              { key: "process", label: "⚙️ Process" },
              { key: "why",     label: "📊 Decision" },
              { key: "audit",   label: "📋 Audit" },
            ] as const).map(t => (
              <button key={t.key} onClick={() => setTab(t.key)}
                className={`flex-1 py-2.5 text-xs font-semibold transition ${
                  tab === t.key
                    ? "text-blue-600 border-b-2 border-blue-600 bg-blue-50"
                    : "text-gray-400 hover:text-gray-600"
                }`}>
                {t.label}
              </button>
            ))}
          </div>

          {/* ── PROCESS TAB: Live pipeline ── */}
          {tab === "process" && (
            <div className="flex-1 overflow-y-auto p-4">
              <p className="text-xs font-semibold text-gray-500 mb-1">What's happening right now</p>
              <p className="text-[10px] text-gray-400 mb-4">Each agent activates as your loan is processed</p>

              <div className="space-y-1">
                {PIPELINE_STAGES.map((s, i) => {
                  const status = getStageStatus(s.key);
                  const conf = getStageConf(s.key);
                  const detail = getStageDetail(s.key);
                  const isActive = activeStage === s.key;
                  const isDone = ["COMPLETED", "APPROVED", "FAILED", "REJECTED", "ESCALATED"].includes(status);
                  const isFailed = ["FAILED", "REJECTED", "ESCALATED"].includes(status);
                  const isPending = status === "PENDING";

                  return (
                    <div key={s.key}>
                      <div className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-300 ${
                        isActive ? "bg-blue-50 border border-blue-200 shadow-sm" :
                        isFailed ? "bg-red-50 border border-red-100" :
                        isDone   ? "bg-green-50 border border-green-100" :
                                   "bg-gray-50 border border-gray-100"
                      }`}>
                        {/* Animated dot */}
                        <div className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${
                          isActive  ? "bg-blue-500 animate-pulse" :
                          isFailed  ? "bg-red-400" :
                          isDone    ? "bg-green-500" :
                                      "bg-gray-300"
                        }`} />

                        <span className="text-lg flex-shrink-0">{s.icon}</span>

                        <div className="flex-1 min-w-0">
                          <p className={`text-xs font-bold truncate ${
                            isActive ? "text-blue-700" :
                            isFailed ? "text-red-600" :
                            isDone   ? "text-green-700" :
                                       "text-gray-400"
                          }`}>{s.label}</p>
                          <p className="text-[10px] text-gray-400 truncate">
                            {detail || s.agent}
                          </p>
                        </div>

                        {/* Confidence pill */}
                        {conf && (
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full flex-shrink-0 ${
                            conf >= 90 ? "bg-green-100 text-green-700" :
                            conf >= 75 ? "bg-yellow-100 text-yellow-700" :
                                         "bg-red-100 text-red-700"
                          }`}>{conf}%</span>
                        )}

                        {isDone && <span className="text-sm flex-shrink-0">{isFailed ? "❌" : "✅"}</span>}
                      </div>

                      {/* Confidence bar */}
                      {conf && (
                        <div className="mx-3 mt-0.5 mb-1">
                          <div className="w-full bg-gray-100 rounded-full h-1">
                            <div className={`h-1 rounded-full transition-all duration-700 ${
                              conf >= 90 ? "bg-green-500" : conf >= 75 ? "bg-yellow-400" : "bg-red-400"
                            }`} style={{ width: `${conf}%` }} />
                          </div>
                        </div>
                      )}

                      {i < PIPELINE_STAGES.length - 1 && (
                        <div className="w-px h-2 bg-gray-200 mx-auto" />
                      )}
                    </div>
                  );
                })}
              </div>

              {/* EMI card shown in process tab too */}
              {emiData && (
                <div className="mt-5 p-4 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl text-white">
                  <p className="text-xs font-bold mb-3 opacity-80 uppercase tracking-wide">💰 Your Loan Summary</p>
                  {[
                    ["Monthly EMI",    `₹${emiData.emi.toLocaleString()}`],
                    ["Total Payable",  `₹${emiData.total_payable.toLocaleString()}`],
                    ["Total Interest", `₹${emiData.total_interest.toLocaleString()}`],
                    ["Rate",           `${emiData.annual_rate}% p.a.`],
                  ].map(([l, v]) => (
                    <div key={l} className="flex justify-between text-xs py-1 border-b border-white/10 last:border-0">
                      <span className="opacity-70">{l}</span>
                      <span className="font-bold">{v}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ── DECISION TAB: Why approved/rejected ── */}
          {tab === "why" && (
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              <p className="text-xs font-semibold text-gray-500 mb-1">Why was your loan approved or rejected?</p>
              <p className="text-[10px] text-gray-400 mb-4">Every rule the AI checked, with your actual values</p>

              {rulesChecked.length === 0 ? (
                <div className="text-center mt-10">
                  <p className="text-3xl mb-2">📐</p>
                  <p className="text-xs text-gray-400">Decision rules will appear<br />after you submit your salary.</p>
                </div>
              ) : rulesChecked.map((r, i) => (
                <div key={i} className={`p-3 rounded-xl border ${
                  r.passed ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"
                }`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span>{r.passed ? "✅" : "❌"}</span>
                    <span className="text-xs font-bold text-gray-800">{r.rule}</span>
                  </div>
                  <p className="text-xs text-gray-600 mb-1">{r.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-gray-400">Your value</span>
                    <span className={`text-xs font-bold ${r.passed ? "text-green-600" : "text-red-500"}`}>
                      {r.actual}
                    </span>
                  </div>
                </div>
              ))}

              {emiData && (
                <div className="mt-2 p-4 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl text-white">
                  <p className="text-xs font-bold mb-3 opacity-80 uppercase tracking-wide">📊 EMI Breakdown</p>
                  {[
                    ["Monthly EMI",    `₹${emiData.emi.toLocaleString()}`],
                    ["Tenure",         `${emiData.tenure_months} months`],
                    ["Total Payable",  `₹${emiData.total_payable.toLocaleString()}`],
                    ["Total Interest", `₹${emiData.total_interest.toLocaleString()}`],
                    ["Interest Rate",  `${emiData.annual_rate}% p.a.`],
                  ].map(([l, v]) => (
                    <div key={l} className="flex justify-between text-xs py-1 border-b border-white/10 last:border-0">
                      <span className="opacity-70">{l}</span>
                      <span className="font-bold">{v}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ── AUDIT TAB: Full decision log ── */}
          {tab === "audit" && (
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              <p className="text-xs font-semibold text-gray-500 mb-1">Full Decision Log</p>
              <p className="text-[10px] text-gray-400 mb-4">Every action taken by every agent</p>

              {audit.length === 0 ? (
                <div className="text-center mt-10">
                  <p className="text-3xl mb-2">📋</p>
                  <p className="text-xs text-gray-400">Audit log will appear<br />as your application progresses.</p>
                </div>
              ) : audit.map((a, i) => (
                <div key={i} className="border border-gray-100 rounded-xl p-3 bg-gray-50">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-gray-700">
                      {auditIcon[a.status] ?? "•"} {a.event}
                    </span>
                    <span className="text-[10px] text-gray-400">{a.ts}</span>
                  </div>
                  <p className={`text-xs ${auditColor[a.status] ?? "text-gray-600"}`}>{a.detail}</p>
                  {a.rule && (
                    <p className="text-[10px] text-gray-400 mt-0.5 font-mono bg-gray-100 px-1.5 py-0.5 rounded inline-block">{a.rule}</p>
                  )}
                  {a.explanation && (
                    <p className="text-[10px] text-gray-500 mt-1 italic">{a.explanation}</p>
                  )}
                  {a.confidence !== undefined && (
                    <div className="mt-2">
                      <div className="flex justify-between text-[10px] text-gray-400 mb-0.5">
                        <span>Confidence</span><span className="font-bold">{a.confidence}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div className={`h-1.5 rounded-full transition-all duration-500 ${
                          a.confidence >= 80 ? "bg-green-500" :
                          a.confidence >= 60 ? "bg-yellow-400" : "bg-red-400"
                        }`} style={{ width: `${a.confidence}%` }} />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
