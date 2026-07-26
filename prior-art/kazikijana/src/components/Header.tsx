import React from "react";
import { BookOpen, Map, MessageSquare, Compass, GraduationCap, Users, Briefcase } from "lucide-react";

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function Header({ activeTab, setActiveTab }: HeaderProps) {
  const tabs = [
    { id: "courses", label: "Course Explorer", icon: BookOpen },
    { id: "roadmap", label: "Roadmap Builder", icon: Map },
    { id: "work", label: "World of Work", icon: Briefcase },
    { id: "forum", label: "Mentor Q&A", icon: Users },
    { id: "chat", label: "AI Career Advisor", icon: MessageSquare },
  ];

  return (
    <header id="app-header" className="sticky top-0 z-40 w-full bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4 transition-all">
      <div className="flex items-center gap-3">
        <div className="p-2.5 bg-indigo-50 text-indigo-700 rounded-xl border border-indigo-100">
          <GraduationCap className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Kazi<span className="text-indigo-600 font-bold">Kijana</span>
          </h1>
          <p className="text-[10px] text-slate-400 font-bold tracking-wider uppercase">Tanzania University & Career Guide</p>
        </div>
      </div>

      <nav className="flex items-center gap-1.5 bg-slate-50 p-1.5 rounded-2xl border border-slate-200">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              id={`tab-btn-${tab.id}`}
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold rounded-xl transition-all ${
                isActive
                  ? "bg-indigo-50 text-indigo-700 shadow-xs border border-indigo-100"
                  : "text-slate-500 hover:text-slate-800 hover:bg-slate-100/60 border border-transparent"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
              <span className="hidden md:inline">{tab.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="hidden lg:flex items-center gap-2 text-xs font-bold text-slate-500 bg-indigo-50/60 px-3.5 py-1.5 rounded-full border border-indigo-100/50">
        <span className="w-2 h-2 bg-indigo-600 rounded-full animate-pulse"></span>
        <span>Form 6 Portal • TCU Admissions 2026</span>
      </div>
    </header>
  );
}
