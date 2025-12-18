"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Login() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  function handleLogin() {
    if (!name || !phone) return;
    localStorage.setItem("finsense_user", name);
    router.push("/");
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(135deg, #0f172a, #1e3a8a)",
        fontFamily: "Arial",
      }}
    >
      <div
        style={{
          width: "380px",
          background: "#ffffff",
          padding: "32px",
          borderRadius: "12px",
          boxShadow: "0 20px 40px rgba(0,0,0,0.2)",
        }}
      >
        <h1 style={{ marginBottom: "8px", color: "#1e3a8a" }}>FinSense</h1>
        <p style={{ marginBottom: "24px", color: "#475569" }}>
          Login to continue your loan journey
        </p>

        <input
          placeholder="Full Name"
          value={name}
          autoComplete="name"
          onChange={(e) => setName(e.target.value)}
          style={{
            width: "100%",
            padding: "12px",
            marginBottom: "12px",
            borderRadius: "6px",
            border: "1px solid #cbd5f5",
            color: "#0f172a",
            backgroundColor: "#ffffff",
          }}
        />

        <input
          type="password"
          placeholder="Password"
          value={phone}
          autoComplete="new-password"
          inputMode="numeric"
          maxLength={10}
          onChange={(e) => setPhone(e.target.value)}
          style={{
            width: "100%",
            padding: "12px",
            marginBottom: "20px",
            borderRadius: "6px",
            border: "1px solid #cbd5f5",
            color: "#0f172a",
            backgroundColor: "#ffffff",
          }}
        />

        <button
          onClick={handleLogin}
          style={{
            width: "100%",
            padding: "12px",
            backgroundColor: "#1e3a8a",
            color: "#ffffff",
            border: "none",
            borderRadius: "6px",
            fontSize: "16px",
            cursor: "pointer",
          }}
        >
          Continue
        </button>
      </div>
    </main>
  );
}
