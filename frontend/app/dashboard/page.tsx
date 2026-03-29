"use client";
import { useEffect, useState } from "react";

type Stats = {
  total_applications: number;
  approved: number;
  rejected: number;
  approval_rate: number;
  rejection_rate: number;
  kyc_failures: number;
  escalations: number;
  sla_breaches: number;
  avg_processing_ms: number;
};

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);

  async function fetchStats() {
    try {
      const res = await fetch("http://127.0.0.1:8000/dashboard");
      const data = await res.json();
      setStats(data);
    } catch {
      console.error("Dashboard fetch failed");
    }
  }

  useEffect(() => {
    fetchStats();

    // 🔁 REAL-TIME AUTO REFRESH
    const interval = setInterval(fetchStats, 3000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) return <p className="p-6">Loading dashboard...</p>;

  const cards = [
    { label: "Total Applications", value: stats.total_applications, color: "border-blue-500" },
    { label: "Approved", value: stats.approved, color: "border-green-500" },
    { label: "Rejected", value: stats.rejected, color: "border-red-500" },
    { label: "Approval Rate", value: stats.approval_rate + "%", color: "border-green-400" },
    { label: "KYC Failures", value: stats.kyc_failures, color: "border-orange-400" },
    { label: "Escalations", value: stats.escalations, color: "border-yellow-400" },
    { label: "SLA Breaches", value: stats.sla_breaches, color: "border-red-400" },
    { label: "Avg Time (ms)", value: stats.avg_processing_ms, color: "border-purple-500" },
  ];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">📊 FinSense Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {cards.map((c, i) => (
          <div key={i} className={`p-4 bg-white rounded-xl shadow border-l-4 ${c.color}`}>
            <p className="text-xs text-gray-500">{c.label}</p>
            <p className="text-xl font-bold">{c.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}