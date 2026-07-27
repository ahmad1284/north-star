import React, { useState } from "react";
import Header from "./components/Header";
import CourseDirectory from "./components/CourseDirectory";
import RoadmapBuilder from "./components/RoadmapBuilder";
import WorldOfWork from "./components/WorldOfWork";
import Forum from "./components/Forum";
import AdvisorChat from "./components/AdvisorChat";
import { BookOpen, Map, Compass, MessageSquare, GraduationCap } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

export default function App() {
  const [activeTab, setActiveTab] = useState("courses");

  return (
    <div id="main-app" className="min-h-screen flex flex-col bg-[#FAF9F6] text-slate-800 antialiased selection:bg-emerald-100 selection:text-emerald-800">
      {/* Dynamic Header Component */}
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-7xl mx-auto pb-16">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            className="w-full h-full"
          >
            {activeTab === "courses" && <CourseDirectory />}
            {activeTab === "roadmap" && <RoadmapBuilder />}
            {activeTab === "work" && <WorldOfWork />}
            {activeTab === "forum" && <Forum />}
            {activeTab === "chat" && <AdvisorChat />}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Footer credits and info */}
      <footer className="w-full bg-white border-t border-slate-100 py-8 px-6 text-center text-xs text-slate-400 font-medium">
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="flex items-center gap-1.5 justify-center">
            <GraduationCap className="w-4 h-4 text-emerald-600/75" />
            <span>KaziKijana Tanzania Commission for Universities (TCU) Career Guide © 2026</span>
          </p>
          <div className="flex gap-4">
            <a href="https://tcu.go.tz" target="_blank" rel="noopener noreferrer" className="hover:text-emerald-600 transition-colors">
              Official TCU Guide
            </a>
            <span>•</span>
            <span className="text-slate-300">Inspired by CareerVillage.org</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

