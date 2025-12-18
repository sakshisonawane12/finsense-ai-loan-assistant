"use client";

import React from "react";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation Header */}
      <nav className="flex justify-between items-center px-8 py-6 bg-white shadow-sm">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-teal-500 rounded"></div>
          <span className="text-xl font-bold text-gray-800">FinSense</span>
        </div>

        <div className="hidden md:flex gap-8 text-gray-700">
          <a href="#product" className="hover:text-teal-500">
            Product
          </a>
          <a href="#how-it-works" className="hover:text-teal-500">
            How it Works
          </a>
          <a href="#features" className="hover:text-teal-500">
            Features
          </a>
          <a href="#team" className="hover:text-teal-500">
            Team
          </a>
        </div>

        <Link
          href="/login"
          className="px-6 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600"
        >
          Login
        </Link>
      </nav>

      {/* Hero Section */}
      <section className="px-8 py-20 max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              The Emotionally <br />
              Intelligent Loan <br />
              Assistant
            </h1>
            <p className="text-gray-600 text-lg mb-8">
              Experience a lending process that understands your context,
              respects your dignity, and guides you with compassion. AI that
              truly cares.
            </p>
            <div className="flex gap-4">
              <Link
                href="/login"
                className="px-8 py-3 bg-teal-500 text-white rounded-lg hover:bg-teal-600 font-semibold"
              >
                Start Now
              </Link>
              <button className="px-8 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:border-gray-400 font-semibold">
                How it Works
              </button>
            </div>
          </div>

          <div className="flex justify-center">
            <div className="relative w-80 h-96 bg-gradient-to-br from-green-400 to-green-500 rounded-3xl shadow-2xl flex items-center justify-center">
              <div className="text-center text-white p-8">
                <div className="text-6xl mb-4">💬</div>
                <p className="text-xl font-semibold">
                  Your Personal Loan Assistant
                </p>
                <p className="text-sm mt-2 opacity-90">
                  Available 24/7 to help you
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why Traditional Loans Fail */}
      <section id="product" className="bg-gray-50 px-8 py-20">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Why Traditional Loans Fail
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Card 1 */}
            <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition">
              <div className="text-4xl mb-4">😰</div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                High Stress
              </h3>
              <p className="text-gray-600">
                Applicants often feel lost and overwhelmed by complex
                terminology, lengthy forms, and uncertain timelines.
              </p>
            </div>

            {/* Card 2 */}
            <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition">
              <div className="text-4xl mb-4">😕</div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Confusion
              </h3>
              <p className="text-gray-600">
                Hidden clauses and unclear requirements leave customers
                bewildered about the true cost of their loan.
              </p>
            </div>

            {/* Card 3 */}
            <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition">
              <div className="text-4xl mb-4">🚫</div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Impersonal Rejection
              </h3>
              <p className="text-gray-600">
                Automated systems reject applications without offering guidance
                on whether applicants might have better options.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Compassionate AI Section */}
      <section className="px-8 py-20 max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-4xl font-bold text-gray-900 mb-8">
              Compassionate AI for Human Problems
            </h2>
            <p className="text-gray-600 mb-8">
              FinSense uses a multi-agent AI system to understand your unique
              financial situation. Rather than a one-size-fits-all approach, we
              analyze:
            </p>
            <ul className="space-y-4">
              <li className="flex gap-4">
                <span className="text-teal-500 font-bold">✓</span>
                <span className="text-gray-700">
                  <strong>Context-aware analysis</strong> of spending habits
                </span>
              </li>
              <li className="flex gap-4">
                <span className="text-teal-500 font-bold">✓</span>
                <span className="text-gray-700">
                  <strong>Employment: </strong>communication data
                </span>
              </li>
              <li className="flex gap-4">
                <span className="text-teal-500 font-bold">✓</span>
                <span className="text-gray-700">
                  <strong>Alternative:</strong>budgets for non-peak years
                </span>
              </li>
            </ul>
          </div>

          <div className="bg-gradient-to-br from-blue-900 to-blue-800 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-8">
              Master Agent: Empathy Core
            </h3>
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <span className="font-semibold">
                  Risk
                  <br />
                  Analysis
                </span>
                <span className="text-3xl">📊</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-semibold">
                  Cash
                  <br />
                  Flow
                </span>
                <span className="text-3xl">💰</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-semibold">
                  Monthly
                  <br />
                  Insights
                </span>
                <span className="text-3xl">📈</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="bg-gray-50 px-8 py-20">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            How It Works
          </h2>
          <p className="text-center text-gray-600 mb-16 max-w-2xl mx-auto">
            A simple, transparent 5-step process from application to approval
          </p>

          <div className="grid md:grid-cols-5 gap-8">
            {[
              {
                num: "1",
                title: "Connect",
                desc: "Link your accounts securely",
              },
              {
                num: "2",
                title: "Chat",
                desc: "Chat with your personal agent",
              },
              {
                num: "3",
                title: "Analyze",
                desc: "Agents analyze your financial data",
              },
              { num: "4", title: "Offer", desc: "Receive personalized offers" },
              { num: "5", title: "Fund", desc: "Money in your account" },
            ].map((step, idx) => (
              <div key={idx} className="text-center">
                <div className="w-16 h-16 bg-teal-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-2xl">
                  {step.num}
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-sm text-gray-600">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Intelligent Features */}
      <section id="features" className="px-8 py-20 max-w-7xl mx-auto">
        <h2 className="text-4xl font-bold text-center text-gray-900 mb-4">
          Intelligent Features
        </h2>
        <p className="text-center text-gray-600 mb-16 max-w-2xl mx-auto">
          Built to serve your financial needs, not just the bank's bottom line
        </p>

        <div className="grid md:grid-cols-2 gap-12">
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Secure Data Handling
            </h3>
            <p className="text-gray-600">
              Bank-grade encryption ensures your personal information remains
              private and protected at all times.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              24/7 AI Assistance
            </h3>
            <p className="text-gray-600">
              Get answers to your questions anytime, anywhere, with intelligent
              responses tailored to your situation.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Financial Health Score
            </h3>
            <p className="text-gray-600">
              Understand your financial health with a detailed analysis and
              actionable insights for improvement.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Instant Pre-approval
            </h3>
            <p className="text-gray-600">
              Know within minutes if you qualify for a loan without affecting
              your credit score.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-gradient-to-r from-blue-900 to-blue-800 px-8 py-20">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 text-center text-white">
            <div>
              <h3 className="text-4xl font-bold mb-2">$50M+</h3>
              <p className="text-blue-200">Loans Funded</p>
            </div>
            <div>
              <h3 className="text-4xl font-bold mb-2">15k+</h3>
              <p className="text-blue-200">Happy Customers</p>
            </div>
            <div>
              <h3 className="text-4xl font-bold mb-2">2 min</h3>
              <p className="text-blue-200">Average Approval</p>
            </div>
            <div>
              <h3 className="text-4xl font-bold mb-2">99%</h3>
              <p className="text-blue-200">Customer Satisfaction</p>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section id="team" className="px-8 py-20 max-w-7xl mx-auto">
        <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
          Meet the Team
        </h2>

        <div className="grid md:grid-cols-4 gap-8">
          {[
            {
              name: "Sakshi Sonawane",
              role: "AI Lead",
              desc: "AI-human interaction specialist",
            },
            {
              name: "Srushti Mane",
              role: "Lead Developer",
              desc: "Full-stack AI engineering",
            },
            {
              name: "Sanika Mohite",
              role: "Design Lead",
              desc: "Design focused on user empathy",
            },
            {
              name: "Shreya Phalke",
              role: "Finance Lead",
              desc: "Full-stack product building",
            },
          ].map((member, idx) => (
            <div key={idx} className="text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full mx-auto mb-4 flex items-center justify-center text-3xl">
                👤
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-1">
                {member.name}
              </h3>
              <p className="text-sm text-teal-600 font-semibold mb-2">
                {member.role}
              </p>
              <p className="text-sm text-gray-600">{member.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-900 to-blue-800 px-8 py-20">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-4xl font-bold mb-4">
            Ready to find your financial balance?
          </h2>
          <p className="text-xl text-blue-200 mb-8">
            Join thousands of users who have discovered a better way to borrow
          </p>
          <Link
            href="/login"
            className="inline-block px-8 py-4 bg-white text-blue-900 rounded-lg hover:bg-gray-100 font-bold text-lg"
          >
            Get Started Now
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 px-8 py-12 text-center">
        <p>© 2025 FinSense Inc. All rights reserved.</p>
      </footer>
    </div>
  );
}
