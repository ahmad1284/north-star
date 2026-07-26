import React, { useState, useRef, useEffect } from "react";
import { MessageSquare, Send, Sparkles, Loader2, ArrowRight, BookOpen, HeartHandshake, User } from "lucide-react";
import { COMBINATIONS } from "../data/tcu_data";
import { motion, AnimatePresence } from "motion/react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const CHIPS = [
  "Which TCU courses fit PCM with B in Math, C in Physics?",
  "What is the day-to-day of a Muhimbili MD?",
  "Tell me about agribusiness prospects in Morogoro",
  "Is CPA needed after a Finance degree at UDSM?",
  "Which universities offer Law, and what is LST like?"
];

export default function AdvisorChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `Habari! Hongera sana on completing your Form 6 examinations! 🎓 

I am **Sama**, your dedicated AI Career & Academic Advisor. I am here to help you match your Advanced Level combination with the official TCU course catalogs, explore starting salary rates in Tanzanian Shillings (TSh), and understand what university life is like.

How can I help you today? You can type your combination and grades, or click any of the quick suggestions below!`
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Automatically scroll to bottom when messages list grows
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = { role: "user", content: text };
    const updatedMessages = [...messages, userMsg];
    
    setMessages(updatedMessages);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: updatedMessages }),
      });

      if (!response.ok) {
        throw new Error("Advisory service is temporarily taking a tea break. Please try again!");
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.content }]);
    } catch (err: any) {
      console.error("Chat API error:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Samahani! I encountered an error connecting to the advisory server: **${err.message}**. \n\nPlease ensure your GEMINI_API_KEY secret is configured in the **Settings > Secrets** panel, or try again soon!`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Parsing markdown-like headers/bullets in simple render helper
  const renderMessageContent = (content: string) => {
    return content.split("\n").map((line, idx) => {
      // Check for main bullet points
      if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
        return (
          <li key={idx} className="text-sm text-slate-700 ml-5 list-disc leading-relaxed mt-1">
            {line.replace(/^[-*]\s+/, "")}
          </li>
        );
      }
      // Check for bold sections or headers
      if (line.trim().startsWith("## ") || line.trim().startsWith("### ")) {
        return (
          <h4 key={idx} className="text-sm font-bold text-slate-900 mt-4 mb-2 first:mt-0">
            {line.replace(/^#{2,3}\s+/, "")}
          </h4>
        );
      }
      // Default paragraphs
      return (
        <p key={idx} className="text-sm text-slate-700 leading-relaxed mt-1.5 first:mt-0">
          {line}
        </p>
      );
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Page header */}
      <div className="mb-12 text-center max-w-3xl mx-auto animate-fade-in">
        <span className="text-xs font-bold text-indigo-700 bg-indigo-50 px-3.5 py-1.5 rounded-full border border-indigo-100">
          Empathetic AI Guidance
        </span>
        <h2 className="text-3xl font-bold tracking-tight text-slate-900 mt-4 serif-title">
          Chat with Advisor Sama
        </h2>
        <p className="text-slate-500 mt-2 text-sm sm:text-base leading-relaxed">
          Get real-time personalized degree recommendations, clarify TCU admissions criteria, and learn the day-to-day realities of different professions in Tanzania.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
        {/* LEFT COMPONENT: Advisory info Card */}
        <div className="lg:col-span-1 space-y-4 hidden lg:block">
          <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
              <HeartHandshake className="w-4 h-4 text-indigo-600" /> Professional Code
            </div>
            <p className="text-xs text-slate-500 leading-relaxed font-medium">
              Advisor Sama holds strict context of the Tanzania Commission for Universities (TCU) curriculum and national employment datasets.
            </p>
            <div className="p-4 bg-indigo-50/50 rounded-2xl border border-indigo-150/40">
              <h5 className="text-[11px] font-bold text-indigo-800 uppercase tracking-wider">Useful Inputs to provide:</h5>
              <ul className="text-[10px] text-slate-605 mt-1.5 space-y-1.5 font-bold">
                <li>• Your A-level combination</li>
                <li>• Exact subject grades</li>
                <li>• Strengths & interests</li>
                <li>• Career aspirations</li>
              </ul>
            </div>
          </div>

          <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-xs">
            <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5">Available Streams</h5>
            <div className="flex flex-wrap gap-1.5">
              {COMBINATIONS.map((c) => (
                <span key={c.code} className="bg-slate-50 text-slate-600 text-[10px] font-bold px-2 py-1 rounded-lg border border-slate-150">
                  {c.code}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT COMPONENT: Chat box */}
        <div className="lg:col-span-3 flex flex-col h-[600px] bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
          {/* Box Header */}
          <div className="bg-slate-50 border-b border-slate-150 px-5 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-indigo-100 border border-indigo-200 text-indigo-700 font-bold rounded-full flex items-center justify-center relative">
                S
                <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-indigo-500 rounded-full border-2 border-white animate-pulse"></span>
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900">Advisor Sama</h4>
                <p className="text-[10px] text-indigo-600 font-bold tracking-wider uppercase">Online • Academic Mentor</p>
              </div>
            </div>

            <div className="text-[10px] bg-slate-150 text-slate-500 font-bold px-3 py-1 rounded-full">
              Sama Version 1.2
            </div>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/15">
            {messages.map((m, idx) => {
              const isAsst = m.role === "assistant";
              return (
                <div
                  key={idx}
                  className={`flex gap-3 max-w-2xl ${isAsst ? "mr-auto" : "ml-auto flex-row-reverse"}`}
                >
                  <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center font-bold text-xs border ${
                    isAsst
                      ? "bg-indigo-50 text-indigo-700 border-indigo-100"
                      : "bg-slate-800 text-white border-transparent"
                  }`}>
                    {isAsst ? "S" : <User className="w-4 h-4" />}
                  </div>

                  <div className={`p-4 rounded-2xl text-xs sm:text-sm shadow-xs border ${
                    isAsst
                      ? "bg-white border-slate-150 text-slate-800"
                      : "bg-indigo-600 border-transparent text-white"
                  }`}>
                    {isAsst ? (
                      <div className="space-y-1">{renderMessageContent(m.content)}</div>
                    ) : (
                      <p className="leading-relaxed whitespace-pre-wrap">{m.content}</p>
                    )}
                  </div>
                </div>
              );
            })}

            {isLoading && (
              <div className="flex gap-3 max-w-lg mr-auto">
                <div className="w-8 h-8 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100 flex items-center justify-center font-bold text-xs">
                  S
                </div>
                <div className="bg-white border border-slate-150 p-4 rounded-2xl shadow-xs flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-indigo-600 animate-spin" />
                  <span className="text-xs text-slate-400 font-bold uppercase tracking-wider">
                    Sama is formulating advice...
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick chips suggestions */}
          <div className="px-5 py-3 border-t border-slate-100 overflow-x-auto flex gap-2 scrollbar-none bg-slate-50/15 shrink-0 select-none">
            {CHIPS.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(chip)}
                disabled={isLoading}
                className="whitespace-nowrap bg-white hover:bg-slate-50 border border-slate-200 px-3.5 py-2 rounded-full text-[11px] font-bold text-slate-600 cursor-pointer transition-all shrink-0 hover:border-indigo-300 hover:text-indigo-800 disabled:opacity-50"
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Chat form */}
          <div className="p-4 border-t border-slate-100 bg-white shrink-0">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend(inputValue);
              }}
              className="flex gap-2"
            >
              <input
                id="input-advisor-chat"
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={isLoading}
                placeholder="Type your combination, grades, or career questions..."
                className="flex-1 bg-slate-50 hover:bg-slate-50 border border-slate-200 focus:bg-white rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-slate-800"
              />
              <button
                id="btn-send-chat"
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-105 text-white disabled:text-slate-400 p-3.5 rounded-xl transition-all shadow-sm shrink-0 cursor-pointer flex items-center justify-center"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
