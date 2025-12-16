"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [user, setUser] = useState("");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<string[]>([]);
  const [typing, setTyping] = useState(false);

  const router = useRouter();

  useEffect(() => {
    const storedUser = localStorage.getItem("finsense_user");

    if (!storedUser) {
      router.push("/login");
    } else {
      setUser(storedUser);
    }
  }, [router]);

  async function sendMessage() {
    if (!message.trim()) return;

    setMessages((prev) => [...prev, "You: " + message]);
    setTyping(true);

    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    const data = await res.json();

    setTyping(false);
    setMessages((prev) => [...prev, "Bot: " + data.reply]);

    if (data.sanction_letter) {
      setMessages((prev) => [...prev, "DOWNLOAD_SANCTION"]);
    }

    setMessage("");
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#f1f5f9",
        fontFamily: "Arial",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          width: "420px",
          height: "600px",
          background: "#ffffff",
          borderRadius: "12px",
          boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "16px",
            background: "#1e3a8a",
            color: "#ffffff",
            borderTopLeftRadius: "12px",
            borderTopRightRadius: "12px",
          }}
        >
          <strong>FinSense 🤖</strong>
          <div style={{ fontSize: "12px" }}>Hi {user || "there"} 👋</div>
        </div>

        {/* Messages */}
        <div
          style={{
            flex: 1,
            padding: "16px",
            overflowY: "auto",
            background: "#f8fafc",
          }}
        >
          {typing && (
            <div style={{ marginBottom: "10px", color: "#64748b" }}>
              FinSense is typing...
            </div>
          )}

          {messages.map((msg, i) =>
            msg === "DOWNLOAD_SANCTION" ? (
              <a
                key={i}
                href="http://127.0.0.1:8000/download"
                target="_blank"
                style={{
                  display: "inline-block",
                  marginTop: "10px",
                  background: "#1e3a8a",
                  color: "#ffffff",
                  padding: "10px 14px",
                  borderRadius: "8px",
                  textDecoration: "none",
                }}
              >
                📄 Download Sanction Letter
              </a>
            ) : (
              <div
                key={i}
                style={{
                  marginBottom: "10px",
                  display: "flex",
                  justifyContent: msg.startsWith("You:")
                    ? "flex-end"
                    : "flex-start",
                }}
              >
                <div
                  style={{
                    maxWidth: "75%",
                    padding: "10px 14px",
                    borderRadius: "12px",
                    background: msg.startsWith("You:") ? "#1e3a8a" : "#e5e7eb",
                    color: msg.startsWith("You:") ? "#ffffff" : "#0f172a",
                  }}
                >
                  {msg.replace("You:", "").replace("Bot:", "")}
                </div>
              </div>
            )
          )}
        </div>

        {/* Input */}
        <div
          style={{
            padding: "12px",
            borderTop: "1px solid #e5e7eb",
            display: "flex",
            gap: "8px",
          }}
        >
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            style={{
              flex: 1,
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid #cbd5f5",
              color: "#0f172a",
              backgroundColor: "#ffffff",
            }}
          />
          <button
            onClick={sendMessage}
            style={{
              padding: "10px 16px",
              background: "#1e3a8a",
              color: "#ffffff",
              border: "none",
              borderRadius: "8px",
              cursor: "pointer",
            }}
          >
            Send
          </button>
        </div>
      </div>
    </main>
  );
}
