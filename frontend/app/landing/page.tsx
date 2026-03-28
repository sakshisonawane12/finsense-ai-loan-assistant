"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";

const NAV_LINKS = [
  { label: "Product", href: "#product" },
  { label: "How it Works", href: "#how-it-works" },
  { label: "Features", href: "#features" },
  { label: "Team", href: "#team" },
];

const PAIN_POINTS = [
  { emoji: "😰", title: "High Stress", desc: "Complex forms, jargon-heavy documents, and uncertain timelines leave applicants overwhelmed." },
  { emoji: "😕", title: "Zero Transparency", desc: "Hidden clauses and unclear requirements make it impossible to understand the true cost." },
  { emoji: "🚫", title: "Cold Rejections", desc: "Automated systems reject without explanation, leaving applicants with no path forward." },
];

const STEPS = [
  { num: "01", title: "Login", desc: "Securely sign in to your FinSense account" },
  { num: "02", title: "Chat", desc: "Talk to your AI loan assistant naturally" },
  { num: "03", title: "Verify", desc: "KYC check happens instantly in the background" },
  { num: "04", title: "Decide", desc: "AI underwrites your eligibility in seconds" },
  { num: "05", title: "Download", desc: "Get your sanction letter instantly as PDF" },
];

const FEATURES = [
  { icon: "🔒", title: "Secure KYC", desc: "Instant identity verification with bank-grade security." },
  { icon: "🤖", title: "Mistral-7B LLM", desc: "Empathetic, human-like responses powered by Mistral AI." },
  { icon: "📊", title: "Smart Underwriting", desc: "Rule-based eligibility engine using salary and credit score." },
  { icon: "📄", title: "Instant PDF Letter", desc: "Auto-generated sanction letter downloadable on approval." },
  { icon: "💬", title: "24/7 Assistant", desc: "Always available to guide you through your loan journey." },
  { icon: "✅", title: "Input Validation", desc: "Real-time checks on amount, tenure, and salary inputs." },
];

const TEAM = [
  { name: "Sakshi Sonawane", role: "AI Lead", color: "from-violet-500 to-purple-600" },
  { name: "Srushti Mane", role: "Lead Developer", color: "from-blue-500 to-cyan-500" },
  { name: "Sanika Mohite", role: "Design Lead", color: "from-pink-500 to-rose-500" },
  { name: "Shreya Phalke", role: "Finance Lead", color: "from-emerald-500 to-teal-500" },
];

const STATS = [
  { value: "2 min", label: "Avg. Approval Time" },
  { value: "100%", label: "AI Powered" },
  { value: "0 Fees", label: "No Hidden Charges" },
  { value: "24/7", label: "Always Available" },
];

function useInView(threshold = 0.15) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true); }, { threshold });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, [threshold]);
  return { ref, visible };
}

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const hero = useInView(0.1);
  const pain = useInView();
  const ai = useInView();
  const steps = useInView();
  const features = useInView();
  const team = useInView();

  return (
    <div className="min-h-screen bg-[#f8fafc] text-gray-900 overflow-x-hidden">

      {/* ── Navbar ── */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? "bg-white/90 backdrop-blur-md shadow-sm" : "bg-transparent"}`}>
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white font-bold text-sm">F</div>
            <span className="text-xl font-bold text-gray-900">FinSense</span>
          </div>
          <div className="hidden md:flex gap-8">
            {NAV_LINKS.map(l => (
              <a key={l.href} href={l.href} className="text-gray-600 hover:text-blue-600 text-sm font-medium transition-colors">{l.label}</a>
            ))}
          </div>
          <Link href="/login" className="px-5 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-md shadow-blue-200">
            Get Started
          </Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="min-h-screen flex items-center bg-gradient-to-br from-[#0f172a] via-[#1e3a8a] to-[#1d4ed8] relative overflow-hidden pt-20">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-indigo-400 rounded-full blur-3xl" />
        </div>
        <div ref={hero.ref} className={`max-w-7xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-16 items-center transition-all duration-700 ${hero.visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
          <div>
            <span className="inline-block px-3 py-1 bg-blue-500/20 text-blue-200 text-xs font-semibold rounded-full mb-6 border border-blue-400/30">
              EY Techathon 2025 🏆
            </span>
            <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight mb-6">
              The Emotionally<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-300">Intelligent</span><br />
              Loan Assistant
            </h1>
            <p className="text-blue-100 text-lg mb-10 leading-relaxed max-w-md">
              AI that understands your financial context, guides you with empathy, and delivers instant loan decisions — no paperwork, no stress.
            </p>
            <div className="flex gap-4 flex-wrap">
              <Link href="/login" className="px-8 py-3.5 bg-white text-blue-900 font-bold rounded-xl hover:bg-blue-50 transition shadow-lg shadow-blue-900/30">
                Apply for Loan →
              </Link>
              <a href="#how-it-works" className="px-8 py-3.5 border border-white/30 text-white font-semibold rounded-xl hover:bg-white/10 transition">
                See How It Works
              </a>
            </div>
          </div>

          {/* Chat preview card */}
          <div className="flex justify-center">
            <div className="w-80 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-2xl overflow-hidden">
              <div className="bg-white/10 px-4 py-3 flex items-center gap-3 border-b border-white/10">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center text-sm">🤖</div>
                <div>
                  <p className="text-white text-sm font-semibold">FinSense AI</p>
                  <p className="text-green-300 text-xs flex items-center gap-1"><span className="w-1.5 h-1.5 bg-green-400 rounded-full inline-block" />Online</p>
                </div>
              </div>
              <div className="p-4 space-y-3">
                {[
                  { from: "bot", text: "Hi! 👋 I'm FinSense. Ready to help you with a personal loan?" },
                  { from: "user", text: "Yes, I want a loan of 5 lakhs" },
                  { from: "bot", text: "Great! For how many years would you like the loan?" },
                  { from: "user", text: "5 years" },
                  { from: "bot", text: "🎉 Congratulations! You're eligible. Generating your sanction letter..." },
                ].map((m, i) => (
                  <div key={i} className={`flex ${m.from === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[80%] px-3 py-2 rounded-xl text-xs ${m.from === "user" ? "bg-blue-500 text-white" : "bg-white/20 text-white"}`}>
                      {m.text}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats ── */}
      <section className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {STATS.map((s, i) => (
            <div key={i}>
              <p className="text-3xl font-extrabold text-blue-700">{s.value}</p>
              <p className="text-sm text-gray-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Pain Points ── */}
      <section id="product" className="py-24 bg-[#f8fafc]">
        <div ref={pain.ref} className={`max-w-7xl mx-auto px-6 transition-all duration-700 ${pain.visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
          <p className="text-center text-blue-600 font-semibold text-sm mb-3 uppercase tracking-widest">The Problem</p>
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">Why Traditional Loans Fail</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {PAIN_POINTS.map((p, i) => (
              <div key={i} className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md hover:-translate-y-1 transition-all duration-200">
                <div className="text-4xl mb-4">{p.emoji}</div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{p.title}</h3>
                <p className="text-gray-500 leading-relaxed">{p.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── AI Section ── */}
      <section className="py-24 bg-white">
        <div ref={ai.ref} className={`max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-16 items-center transition-all duration-700 ${ai.visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
          <div>
            <p className="text-blue-600 font-semibold text-sm mb-3 uppercase tracking-widest">Our Solution</p>
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Multi-Agent AI Orchestration</h2>
            <p className="text-gray-500 mb-8 leading-relaxed">
              FinSense uses a pipeline of specialized AI agents — each handling a distinct part of your loan journey — coordinated by an empathy-first LLM core.
            </p>
            <div className="space-y-4">
              {[
                { icon: "🔍", label: "Verification Agent", desc: "Instant KYC check" },
                { icon: "📐", label: "Underwriting Agent", desc: "Salary + credit score rules" },
                { icon: "📝", label: "Sanction Agent", desc: "Auto PDF generation" },
                { icon: "🧠", label: "LLM Core (Mistral-7B)", desc: "Empathetic response rewriting" },
              ].map((a, i) => (
                <div key={i} className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl border border-gray-100">
                  <span className="text-2xl">{a.icon}</span>
                  <div>
                    <p className="font-semibold text-gray-900 text-sm">{a.label}</p>
                    <p className="text-gray-500 text-xs">{a.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-gradient-to-br from-[#0f172a] to-[#1e3a8a] rounded-2xl p-8 text-white">
            <h3 className="text-xl font-bold mb-6 text-blue-200">Agent Pipeline</h3>
            <div className="space-y-4">
              {["User Input", "Validation Layer", "KYC Verification", "Underwriting Engine", "LLM Response", "PDF Sanction"].map((step, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-blue-500/30 border border-blue-400/40 flex items-center justify-center text-xs font-bold text-blue-200">{i + 1}</div>
                  <div className="flex-1 h-px bg-blue-500/20" />
                  <span className="text-sm text-blue-100 font-medium">{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section id="how-it-works" className="py-24 bg-[#f8fafc]">
        <div ref={steps.ref} className={`max-w-7xl mx-auto px-6 transition-all duration-700 ${steps.visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
          <p className="text-center text-blue-600 font-semibold text-sm mb-3 uppercase tracking-widest">Process</p>
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-4">How It Works</h2>
          <p className="text-center text-gray-500 mb-16 max-w-xl mx-auto">From login to sanction letter in under 2 minutes</p>
          <div className="grid md:grid-cols-5 gap-6">
            {STEPS.map((s, i) => (
              <div key={i} className="relative text-center group">
                {i < STEPS.length - 1 && (
                  <div className="hidden md:block absolute top-8 left-[60%] w-full h-px bg-blue-200 z-0" />
                )}
                <div className="relative z-10 w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-2xl flex items-center justify-center mx-auto mb-4 font-bold text-lg shadow-lg shadow-blue-200 group-hover:scale-110 transition-transform">
                  {s.num}
                </div>
                <h3 className="font-bold text-gray-900 mb-1">{s.title}</h3>
                <p className="text-xs text-gray-500">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="py-24 bg-white">
        <div ref={features.ref} className={`max-w-7xl mx-auto px-6 transition-all duration-700 ${features.visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
          <p className="text-center text-blue-600 font-semibold text-sm mb-3 uppercase tracking-widest">Capabilities</p>
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">Intelligent Features</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {FEATURES.map((f, i) => (
              <div key={i} className="p-6 rounded-2xl border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-200 group">
                <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-2xl mb-4 group-hover:bg-blue-100 transition-colors">{f.icon}</div>
                <h3 className="font-bold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Team ── */}
      <section id="team" className="py-24 bg-[#f8fafc]">
        <div ref={team.ref} className={`max-w-7xl mx-auto px-6 transition-all duration-700 ${team.visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
          <p className="text-center text-blue-600 font-semibold text-sm mb-3 uppercase tracking-widest">The Team</p>
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">Meet the Builders</h2>
          <div className="grid md:grid-cols-4 gap-8">
            {TEAM.map((m, i) => (
              <div key={i} className="text-center group">
                <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${m.color} mx-auto mb-4 flex items-center justify-center text-3xl shadow-lg group-hover:scale-105 transition-transform`}>
                  👤
                </div>
                <h3 className="font-bold text-gray-900">{m.name}</h3>
                <p className="text-sm text-blue-600 font-medium mt-1">{m.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-24 bg-gradient-to-br from-[#0f172a] via-[#1e3a8a] to-[#1d4ed8] relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 right-20 w-64 h-64 bg-cyan-400 rounded-full blur-3xl" />
        </div>
        <div className="max-w-3xl mx-auto px-6 text-center relative z-10">
          <h2 className="text-4xl font-extrabold text-white mb-4">Ready to get your loan?</h2>
          <p className="text-blue-200 text-lg mb-10">Join FinSense and experience AI-powered lending that actually cares.</p>
          <Link href="/login" className="inline-block px-10 py-4 bg-white text-blue-900 font-bold rounded-xl hover:bg-blue-50 transition shadow-xl shadow-blue-900/30 text-lg">
            Start Your Application →
          </Link>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="bg-[#0f172a] text-gray-500 px-6 py-8 text-center text-sm">
        <p>© 2025 FinSense · EY Techathon · Built with Next.js + FastAPI + Mistral-7B</p>
      </footer>
    </div>
  );
}
