"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const DEMO_USERS: Record<string, string> = {
  sakshi: "pass123",
  srushti: "pass123",
  sanika: "pass123",
  shreya: "pass123",
};

export default function LoginPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function validate() {
    if (!name.trim()) return "Please enter your name.";
    if (name.trim().length < 2) return "Name must be at least 2 characters.";
    if (!password) return "Please enter your password.";
    if (password.length < 4) return "Password must be at least 4 characters.";
    return "";
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const err = validate();
    if (err) {
      setError(err);
      return;
    }

    setLoading(true);
    await new Promise((r) => setTimeout(r, 800)); // simulate auth

    const key = name.trim().toLowerCase();
    if (DEMO_USERS[key] && DEMO_USERS[key] === password) {
      localStorage.setItem("finsense_user", name.trim());
      router.push("/");
    } else if (!DEMO_USERS[key]) {
      // allow any new user with password >= 4 chars
      localStorage.setItem("finsense_user", name.trim());
      router.push("/");
    } else {
      setError("Incorrect password. Try: pass123");
    }
    setLoading(false);
  }

  return (
    <main className="min-h-screen flex bg-gradient-to-br from-[#0f172a] via-[#1e3a8a] to-[#1d4ed8] relative overflow-hidden">
      {/* Background blobs */}
      <div className="absolute top-10 left-10 w-72 h-72 bg-blue-500/20 rounded-full blur-3xl" />
      <div className="absolute bottom-10 right-10 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl" />

      {/* Left panel — visible on md+ */}
      <div className="hidden md:flex flex-col justify-center px-16 flex-1 relative z-10">
        <Link href="/landing" className="flex items-center gap-2 mb-16">
          <div className="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center text-white font-bold">
            F
          </div>
          <span className="text-white text-xl font-bold">FinSense</span>
        </Link>
        <h1 className="text-5xl font-extrabold text-white leading-tight mb-6">
          Your AI Loan
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-300">
            Journey Starts Here
          </span>
        </h1>
        <p className="text-blue-200 text-lg max-w-sm leading-relaxed">
          Get a personal loan in minutes with our empathetic AI assistant. No
          paperwork. No stress.
        </p>
        <div className="mt-12 space-y-4">
          {[
            "Instant KYC verification",
            "AI-powered eligibility check",
            "PDF sanction letter on approval",
          ].map((f, i) => (
            <div key={i} className="flex items-center gap-3 text-blue-100">
              <div className="w-5 h-5 rounded-full bg-green-400/30 border border-green-400/50 flex items-center justify-center text-green-300 text-xs">
                ✓
              </div>
              <span className="text-sm">{f}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Right panel — login form */}
      <div className="flex items-center justify-center flex-1 px-6 py-12 relative z-10">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl p-8">
          {/* Mobile logo */}
          <div className="flex md:hidden items-center gap-2 mb-8">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
              F
            </div>
            <span className="text-xl font-bold text-gray-900">FinSense</span>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-1">
            Welcome back
          </h2>
          <p className="text-gray-500 text-sm mb-8">
            Sign in to continue your loan journey
          </p>

          <form onSubmit={handleLogin} className="space-y-5" noValidate>
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  setError("");
                }}
                placeholder=""
                autoComplete="name"
                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPass ? "text" : "password"}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setError("");
                  }}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowPass((p) => !p)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-lg"
                  tabIndex={-1}
                >
                  {showPass ? "🙈" : "👁️"}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-3 rounded-xl">
                <span>⚠️</span> {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm shadow-lg shadow-blue-200"
            >
              {loading ? (
                <>
                  <svg
                    className="animate-spin w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v8z"
                    />
                  </svg>
                  Signing in...
                </>
              ) : (
                "Sign In →"
              )}
            </button>
          </form>

          <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-100">
            <p className="text-xs text-blue-600">
              Name: <span className="font-mono">Sakshi</span> · Password:{" "}
              <span className="font-mono">pass123</span>
            </p>
          </div>

          <p className="text-center text-xs text-gray-400 mt-6">
            <Link href="/landing" className="hover:text-blue-600 transition">
              ← Back to Home
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
