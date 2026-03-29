"use client";
import React from "react";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">

      {/* ───────── NAVBAR ───────── */}
      <nav className="flex justify-between items-center px-6 py-4 shadow-sm bg-white">
        <h1 className="font-bold text-xl">FinSense</h1>
        <Link href="/login" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">
          Get Started
        </Link>
      </nav>

      {/* ───────── HERO ───────── */}
      <section className="text-center py-20 bg-gradient-to-br from-blue-900 to-indigo-700 text-white px-6">
        <h1 className="text-5xl font-extrabold mb-6">
          AI-Powered Loan Assistant
        </h1>

        <p className="text-lg mb-8 max-w-xl mx-auto text-blue-100">
          Get instant loan decisions with full transparency, real-time processing,
          and zero paperwork.
        </p>

        <Link
          href="/login"
          className="bg-white text-blue-900 px-6 py-3 rounded-xl font-bold shadow"
        >
          Apply Now →
        </Link>

        {/* TRUST BADGE */}
        <p className="text-xs text-green-300 mt-4">
          ✔ Secure KYC • ✔ Explainable AI • ✔ No Hidden Charges
        </p>
      </section>

      {/* ───────── USP SECTION ───────── */}
      <section className="py-20 px-6 bg-gray-50">
        <h2 className="text-3xl font-bold text-center mb-12">
          Why FinSense is Different 🚀
        </h2>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {[
            {
              title: "Explainable AI",
              desc: "Every loan decision includes rules, confidence scores, and reasoning.",
            },
            {
              title: "Live Processing",
              desc: "Track KYC, underwriting, and approval in real-time.",
            },
            {
              title: "Human + AI Hybrid",
              desc: "Low confidence cases are escalated to human officers.",
            },
          ].map((item, i) => (
            <div key={i} className="bg-white p-6 rounded-xl shadow border">
              <h3 className="font-bold text-lg mb-2">{item.title}</h3>
              <p className="text-gray-500 text-sm">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ───────── HOW IT WORKS ───────── */}
      <section className="py-20 px-6">
        <h2 className="text-3xl font-bold text-center mb-12">
          How It Works ⚙️
        </h2>

        <div className="grid md:grid-cols-5 gap-6 max-w-6xl mx-auto text-center">
          {[
            "Login",
            "Enter Loan Details",
            "KYC Verification",
            "AI Underwriting",
            "Download Sanction",
          ].map((step, i) => (
            <div key={i}>
              <div className="w-14 h-14 mx-auto mb-3 bg-blue-600 text-white rounded-xl flex items-center justify-center font-bold">
                {i + 1}
              </div>
              <p className="text-sm font-medium">{step}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ───────── FEATURES ───────── */}
      <section className="py-20 px-6 bg-gray-50">
        <h2 className="text-3xl font-bold text-center mb-12">
          Powerful Features 💡
        </h2>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {[
            "🤖 AI Chat Assistant",
            "🔒 Secure KYC",
            "📊 Smart Underwriting",
            "📄 Instant PDF Letter",
            "⚡ Real-Time Decisions",
            "📋 Audit Transparency",
          ].map((f, i) => (
            <div key={i} className="bg-white p-6 rounded-xl shadow border text-center">
              <p className="text-lg font-semibold">{f}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ───────── DEMO BUTTON ───────── */}
      <section className="py-16 text-center">
        <h2 className="text-2xl font-bold mb-4">Try Live Demo</h2>

        <button
          onClick={async () => {
            await fetch("http://127.0.0.1:8000/demo", { method: "POST" });
            alert("Demo triggered! Check dashboard 🚀");
          }}
          className="bg-black text-white px-6 py-3 rounded-lg"
        >
          ▶ Run Demo
        </button>
      </section>

      {/* ───────── CTA ───────── */}
      <section className="py-20 bg-blue-900 text-white text-center">
        <h2 className="text-3xl font-bold mb-4">
          Ready to Get Your Loan?
        </h2>

        <p className="mb-6 text-blue-200">
          Experience AI-powered lending in seconds.
        </p>

        <Link
          href="/login"
          className="bg-white text-blue-900 px-6 py-3 rounded-xl font-bold"
        >
          Start Application →
        </Link>
      </section>

      {/* ───────── FOOTER ───────── */}
      <footer className="py-6 text-center text-gray-500 text-sm">
        © 2025 FinSense • AI Loan Assistant • EY Techathon
      </footer>

    </div>
  );
}