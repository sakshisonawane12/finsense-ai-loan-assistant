"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type Stats = {
  total_applications: number;
  approved: number;
  rejected: number;
  approval_rate: number;
  rejection_rate: number;
  kyc_failures: number;
  escalations: number;
  avg_processing_ms: number;
};

const EMPTY: Stats = {
  total_applications: 0, approved: 0, rejected: 0,
  approval_rate: 0, rejection_rate: 0,
  kyc_failures: 0, escalations: 0, avg_processing_ms: 0,
};

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats>(EMPTY);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function fetchStats() {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/dashboard");
      setStats(await res.json());
      setError("");
    } catch {
      setError("Backend not reachable. Start the FastAPI server.");
    } finally {
      setLoading(false);
    }
  }

  async function runDemo() {
    await fetch("http://127.0.0.1:8000/demo", { method: "POST" });
    fetchStats();
  }

  useEffect(() => { fetchStats(); }, []);

  const cards = [
    { label: "Total Applications", value: stats.total_applications, icon: "📋", color: "from-blue-500 to-indigo-600" },
    { label: "Approved", value: stats.approved, icon: "✅", color: "from-green-500 to-emerald-600" },
    { label: "Rejected", value: stats.rejected, icon: "❌", color: "from-red-500 to-rose-600" },
    { label: "KYC Failures", value: stats.kyc_failures, icon: "🔍", color: "from-yellow-500 to-orange-500" },
    { label: "Escalations", value: stats.escalations, icon: "⚠️", color: "from-orange-500 to-red-500" },
    { label: "Avg Processing", value: `${stats.avg_processing_ms}ms`, icon: "⚡", color: "from-purple-500 to-violet-600" },
    { label: "SLA Breaches", value: (stats as any).sla_breaches ?? 0, icon: "🚨", color: "from-rose-500 to-pink-600" },
  ];

  return (
    <div className="min-h-screen bg-[#f8fafc]">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 shadow-sm px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white font-bold text-sm">F</div>
          <div>
            <p className="font-bold text-gray-900 text-sm">FinSense · Workflow Dashboard</p>
            <p className="text-xs text-gray-400">Real-time agent monitoring</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={runDemo} className="text-xs px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-semibold shadow-md shadow-indigo-200">
            ▶ Run Auto Demo
          </button>
          <button onClick={fetchStats} className="text-xs px-3 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition">
            🔄 Refresh
          </button>
          <Link href="/" className="text-xs px-3 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition">
            ← Chat
          </Link>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-10">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-xl text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Stat cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-5 mb-10">
          {cards.map((c, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${c.color} flex items-center justify-center text-lg mb-3 shadow-sm`}>
                {c.icon}
              </div>
              <p className="text-2xl font-extrabold text-gray-900">{loading ? "—" : c.value}</p>
              <p className="text-xs text-gray-500 mt-1">{c.label}</p>
            </div>
          ))}
        </div>

        {/* Approval / Rejection rate bars */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6">
          <p className="font-bold text-gray-900 mb-5">Decision Rate</p>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-green-600 font-medium">Approval Rate</span>
                <span className="font-bold text-gray-900">{stats.approval_rate}%</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="h-3 rounded-full bg-gradient-to-r from-green-400 to-emerald-500 transition-all duration-700" style={{ width: `${stats.approval_rate}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-red-500 font-medium">Rejection Rate</span>
                <span className="font-bold text-gray-900">{stats.rejection_rate}%</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="h-3 rounded-full bg-gradient-to-r from-red-400 to-rose-500 transition-all duration-700" style={{ width: `${stats.rejection_rate}%` }} />
              </div>
            </div>
          </div>
        </div>

        {/* Agent pipeline status */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <p className="font-bold text-gray-900 mb-5">Agent Pipeline Health</p>
          <div className="space-y-3">
            {[
              { agent: "VerificationAgent", status: stats.kyc_failures === 0 ? "Healthy" : "Degraded", ok: stats.kyc_failures === 0 },
              { agent: "UnderwritingAgent", status: "Healthy", ok: true },
              { agent: "SanctionAgent", status: "Healthy", ok: true },
              { agent: "LLM Core (Mistral-7B)", status: "Healthy", ok: true },
              { agent: "EscalationHandler", status: stats.escalations > 0 ? `${stats.escalations} escalated` : "Idle", ok: stats.escalations === 0 },
            ].map((a, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100">
                <span className="text-sm font-medium text-gray-700">{a.agent}</span>
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${a.ok ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                  {a.ok ? "●" : "●"} {a.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
