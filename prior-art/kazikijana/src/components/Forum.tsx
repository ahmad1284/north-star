import React, { useState, useEffect } from "react";
import { MessageSquare, Search, Compass, Award, Calendar, ThumbsUp, Send, User, ChevronRight, ArrowLeft, PlusCircle, Sparkles, Loader2, Bookmark } from "lucide-react";
import { COMBINATIONS } from "../data/tcu_data";
import { motion, AnimatePresence } from "motion/react";

interface Answer {
  id: string;
  authorName: string;
  authorTitle: string;
  content: string;
  createdAt: string;
  isMentor: boolean;
  likes: number;
}

interface Question {
  id: string;
  authorName: string;
  combination: string;
  title: string;
  content: string;
  createdAt: string;
  answers: Answer[];
}

export default function Forum() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selectedQuestionId, setSelectedQuestionId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCombo, setSelectedCombo] = useState("ALL");
  
  // Ask Question Form state
  const [isAsking, setIsAsking] = useState(false);
  const [formName, setFormName] = useState("");
  const [formCombo, setFormCombo] = useState("PCM");
  const [formTitle, setFormTitle] = useState("");
  const [formContent, setFormContent] = useState("");
  const [isSubmittingQuestion, setIsSubmittingQuestion] = useState(false);

  // Write Answer Form state
  const [answerName, setAnswerName] = useState("");
  const [answerTitle, setAnswerTitle] = useState("");
  const [answerContent, setAnswerContent] = useState("");
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);

  const [isLoading, setIsLoading] = useState(true);

  // Load questions
  const fetchQuestions = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/forum/questions");
      if (res.ok) {
        const data = await res.json();
        setQuestions(data);
      }
    } catch (err) {
      console.error("Failed to load forum questions:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, []);

  const handleLike = async (ansId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const res = await fetch(`/api/forum/answers/${ansId}/like`, { method: "POST" });
      if (res.ok) {
        const updatedAns = await res.json();
        setQuestions((prevQuestions) =>
          prevQuestions.map((q) => ({
            ...q,
            answers: q.answers.map((a) => (a.id === ansId ? { ...a, likes: updatedAns.likes } : a)),
          }))
        );
      }
    } catch (err) {
      console.error("Failed to upvote answer:", err);
    }
  };

  const handleAskQuestionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formTitle.trim() || !formContent.trim()) return;

    setIsSubmittingQuestion(true);
    try {
      const res = await fetch("/api/forum/questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          authorName: formName.trim() || "Form 6 Graduate",
          combination: formCombo,
          title: formTitle.trim(),
          content: formContent.trim(),
        }),
      });

      if (res.ok) {
        const newQuestion = await res.json();
        setQuestions((prev) => [newQuestion, ...prev]);
        setIsAsking(false);
        setFormTitle("");
        setFormContent("");
        // Instantly select this newly asked question to show the answer!
        setSelectedQuestionId(newQuestion.id);
      }
    } catch (err) {
      console.error("Failed to post question:", err);
    } finally {
      setIsSubmittingQuestion(false);
    }
  };

  const handleAnswerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedQuestionId || !answerContent.trim()) return;

    setIsSubmittingAnswer(true);
    try {
      const res = await fetch(`/api/forum/questions/${selectedQuestionId}/answers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          authorName: answerName.trim() || "Graduate Alumnus",
          authorTitle: answerTitle.trim() || "Mentor / Volunteer",
          content: answerContent.trim(),
          isMentor: true,
        }),
      });

      if (res.ok) {
        const newAnswer = await res.json();
        setQuestions((prevQuestions) =>
          prevQuestions.map((q) => {
            if (q.id === selectedQuestionId) {
              return { ...q, answers: [...q.answers, newAnswer] };
            }
            return q;
          })
        );
        setAnswerContent("");
        setAnswerName("");
        setAnswerTitle("");
      }
    } catch (err) {
      console.error("Failed to post answer:", err);
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  // Filters
  const filteredQuestions = questions.filter((q) => {
    const matchesSearch =
      q.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      q.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      q.answers.some((a) => a.content.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCombo = selectedCombo === "ALL" || q.combination === selectedCombo;

    return matchesSearch && matchesCombo;
  });

  const selectedQuestion = questions.find((q) => q.id === selectedQuestionId);

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Intro section */}
      <div className="mb-12 text-center max-w-3xl mx-auto animate-fade-in">
        <span className="text-xs font-bold text-indigo-700 bg-indigo-50 px-3.5 py-1.5 rounded-full border border-indigo-100">
          CareerVillage Tanzania • Student-Mentor Forum
        </span>
        <h2 className="text-3xl font-bold tracking-tight text-slate-900 mt-4 serif-title">
          Connect with Professional Mentors
        </h2>
        <p className="text-slate-500 mt-2 text-sm sm:text-base leading-relaxed">
          Stuck on university options? Post your questions and receive immediate, high-quality guidance from simulated Tanzanian professional mentors, engineers, doctors, and alumni.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* LEFT COLUMN: Sidebar Filters & Ask Button */}
        <div className="lg:col-span-1 space-y-6">
          <button
            id="btn-ask-forum"
            onClick={() => {
              setIsAsking(true);
              setSelectedQuestionId(null);
            }}
            className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs py-3.5 px-4 rounded-xl transition-all shadow-sm cursor-pointer"
          >
            <PlusCircle className="w-5 h-5" /> Ask a Career Question
          </button>

          <div className="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-xs space-y-5">
            <div>
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2.5">
                Stream Filter
              </h4>
              <div className="space-y-1.5">
                <button
                  onClick={() => setSelectedCombo("ALL")}
                  className={`w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer border ${
                    selectedCombo === "ALL"
                      ? "bg-indigo-50 text-indigo-800 border-indigo-100"
                      : "text-slate-600 hover:bg-slate-50 border-transparent hover:text-slate-900"
                  }`}
                >
                  All Combinations
                </button>
                {COMBINATIONS.map((c) => (
                  <button
                    key={c.code}
                    onClick={() => setSelectedCombo(c.code)}
                    className={`w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-between cursor-pointer border ${
                      selectedCombo === c.code
                        ? "bg-indigo-50 text-indigo-800 border-indigo-100"
                        : "text-slate-600 hover:bg-slate-50 border-transparent hover:text-slate-900"
                    }`}
                  >
                    <span>{c.code} Stream</span>
                    <span className="text-[10px] bg-slate-100 border border-slate-200/40 px-1.5 py-0.2 text-slate-500 rounded-md font-semibold">
                      {questions.filter((q) => q.combination === c.code).length}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div className="border-t border-slate-100 pt-4">
              <div className="p-4 bg-amber-50/50 border border-amber-100/70 rounded-2xl flex items-start gap-2.5">
                <Sparkles className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <p className="text-[11px] text-slate-655 leading-relaxed font-semibold">
                  <strong>Instant Answers:</strong> Posting questions leverages server-side Gemini to simulate answers from actual career experts in Tanzania!
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Question List or Question Detail */}
        <div className="lg:col-span-3">
          <AnimatePresence mode="wait">
            {/* WRITE / ASK QUESTION FORM */}
            {isAsking && (
              <motion.div
                key="ask-form"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm"
              >
                <div className="flex items-center justify-between mb-6 border-b border-slate-100 pb-4">
                  <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                    <Compass className="w-5 h-5 text-indigo-600" /> Ask a New Career Question
                  </h3>
                  <button
                    onClick={() => setIsAsking(false)}
                    className="text-slate-400 hover:text-slate-600 text-xs font-bold cursor-pointer"
                  >
                    Cancel
                  </button>
                </div>

                <form onSubmit={handleAskQuestionSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-bold text-slate-600 block mb-1 uppercase tracking-wide">
                        Your Name (Optional)
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Rachel K."
                        value={formName}
                        onChange={(e) => setFormName(e.target.value)}
                        className="w-full px-4 py-2.5 border border-slate-250 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium text-slate-800"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-bold text-slate-600 block mb-1 uppercase tracking-wide">
                        Your A-Level Combination
                      </label>
                      <select
                        value={formCombo}
                        onChange={(e) => setFormCombo(e.target.value)}
                        className="w-full px-4 py-2.5 border border-slate-250 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 font-bold text-slate-700"
                      >
                        {COMBINATIONS.map((c) => (
                          <option key={c.code} value={c.code}>
                            {c.code} - {c.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-bold text-slate-600 block mb-1 uppercase tracking-wide">
                      Question Title / Summary
                    </label>
                    <input
                      id="input-question-title"
                      type="text"
                      required
                      placeholder="e.g. Is entering Civil Engineering at MUST difficult for female students?"
                      value={formTitle}
                      onChange={(e) => setFormTitle(e.target.value)}
                      className="w-full px-4 py-2.5 border border-slate-250 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium text-slate-800"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-bold text-slate-600 block mb-1 uppercase tracking-wide">
                      Question Details
                    </label>
                    <textarea
                      id="input-question-content"
                      required
                      rows={5}
                      placeholder="Describe what choices you are confused about, your grades or target universities, and what you would like to know about study life or future job prospects..."
                      value={formContent}
                      onChange={(e) => setFormContent(e.target.value)}
                      className="w-full px-4 py-2.5 border border-slate-250 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium text-slate-800"
                    />
                  </div>

                  <div className="flex justify-end pt-2">
                    <button
                      id="btn-submit-question"
                      type="submit"
                      disabled={isSubmittingQuestion}
                      className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-bold text-xs px-6 py-3 rounded-xl transition-all shadow-xs cursor-pointer"
                    >
                      {isSubmittingQuestion ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" /> Generating Expert Answers...
                        </>
                      ) : (
                        <>
                          Publish Question & Get Advice <Sparkles className="w-4 h-4 text-indigo-100" />
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </motion.div>
            )}

            {/* VIEW A SELECTED QUESTION DETAILS */}
            {!isAsking && selectedQuestionId && selectedQuestion && (
              <motion.div
                key="question-detail"
                initial={{ opacity: 0, x: -15 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 15 }}
                className="space-y-6"
              >
                {/* Back link */}
                <button
                  onClick={() => setSelectedQuestionId(null)}
                  className="flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-slate-800 transition-all bg-slate-100 py-2 px-4 rounded-xl border border-slate-200/50 cursor-pointer"
                >
                  <ArrowLeft className="w-4 h-4" /> Back to Q&A Board
                </button>

                {/* Original Question Card */}
                <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4">
                  <div className="flex items-center gap-2">
                    <span className="bg-indigo-50 text-indigo-700 border border-indigo-100 text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase">
                      {selectedQuestion.combination} Stream
                    </span>
                    <span className="text-[10px] text-slate-400 font-bold uppercase flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" /> Posted {formatDate(selectedQuestion.createdAt)}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 serif-title">
                    {selectedQuestion.title}
                  </h3>

                  <p className="text-sm text-slate-600 leading-relaxed bg-slate-50/50 p-5 rounded-2xl border border-slate-200/60 font-medium">
                    {selectedQuestion.content}
                  </p>

                  <div className="flex items-center gap-2 text-xs text-slate-400 border-t border-slate-100 pt-4 font-bold">
                    <User className="w-4 h-4" /> Asked by {selectedQuestion.authorName}
                  </div>
                </div>

                {/* List of Answers */}
                <div className="space-y-4">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                    Mentors & Alumni Answers ({selectedQuestion.answers.length})
                  </h4>

                  {selectedQuestion.answers.map((answer) => (
                    <div
                      key={answer.id}
                      className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4 relative overflow-hidden"
                    >
                      {/* Ribbon if mentor */}
                      {answer.isMentor && (
                        <div className="absolute right-0 top-0 bg-indigo-600 text-white text-[9px] font-bold tracking-widest px-3.5 py-1.5 uppercase rounded-bl-xl">
                          Verified Mentor
                        </div>
                      )}

                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-indigo-50 text-indigo-700 border border-indigo-100 rounded-full flex items-center justify-center font-bold text-sm">
                          {answer.authorName.split(" ").map(n => n[0]).join("") || "M"}
                        </div>
                        <div>
                          <p className="text-sm font-bold text-slate-900">{answer.authorName}</p>
                          <p className="text-[11px] text-slate-400 font-bold">{answer.authorTitle}</p>
                        </div>
                      </div>

                      <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line font-medium">
                        {answer.content}
                      </p>

                      <div className="flex items-center justify-between border-t border-slate-100 pt-4 text-xs text-slate-400 font-bold">
                        <span>Answered on {formatDate(answer.createdAt)}</span>

                        <button
                          onClick={(e) => handleLike(answer.id, e)}
                          className="flex items-center gap-1.5 font-bold text-slate-550 hover:text-indigo-600 bg-slate-50 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-100 px-3 py-1.5 rounded-xl transition-all cursor-pointer"
                        >
                          <ThumbsUp className="w-3.5 h-3.5 text-slate-400 hover:text-indigo-600" />
                          <span>Helpful ({answer.likes})</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Write your own Answer form */}
                <div className="bg-slate-50 p-6 rounded-3xl border border-slate-200 space-y-4">
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                    <PlusCircle className="w-4 h-4 text-indigo-600" /> Share Your Advice
                  </h4>

                  <form onSubmit={handleAnswerSubmit} className="space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <input
                        type="text"
                        placeholder="Your Name"
                        value={answerName}
                        onChange={(e) => setAnswerName(e.target.value)}
                        className="bg-white border border-slate-200 px-3.5 py-2.5 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 font-semibold"
                      />
                      <input
                        type="text"
                        placeholder="Your Profession/Title (e.g. UDSM Alumnus / Engineer)"
                        value={answerTitle}
                        onChange={(e) => setAnswerTitle(e.target.value)}
                        className="bg-white border border-slate-200 px-3.5 py-2.5 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 font-semibold"
                      />
                    </div>

                    <textarea
                      required
                      rows={3}
                      placeholder="Write encouraging, specific, and actionable advice to help this student..."
                      value={answerContent}
                      onChange={(e) => setAnswerContent(e.target.value)}
                      className="w-full bg-white border border-slate-200 px-3.5 py-2.5 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 font-semibold"
                    />

                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={isSubmittingAnswer}
                        className="flex items-center gap-1.5 bg-slate-850 hover:bg-slate-950 text-white font-bold text-xs px-5 py-2.5 rounded-xl transition-all shadow-xs cursor-pointer"
                      >
                        {isSubmittingAnswer ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <>
                            Submit Answer <Send className="w-3 h-3" />
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </motion.div>
            )}

            {/* DEFAULT VIEW: LIST OF QUESTIONS */}
            {!isAsking && !selectedQuestionId && (
              <motion.div
                key="questions-list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-4"
              >
                {/* Search Bar */}
                <div className="relative mb-6">
                  <Search className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search Q&A forum by keyword..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-white border border-slate-250 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-xs"
                  />
                </div>

                {isLoading ? (
                  <div className="text-center py-16">
                    <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-2" />
                    <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">
                      Loading Mentorship Board...
                    </p>
                  </div>
                ) : filteredQuestions.length > 0 ? (
                  filteredQuestions.map((q) => (
                    <div
                      id={`forum-card-${q.id}`}
                      key={q.id}
                      onClick={() => setSelectedQuestionId(q.id)}
                      className="bg-white p-6 rounded-3xl border border-slate-200/80 hover:border-indigo-300 hover:ring-2 hover:ring-indigo-50/50 shadow-xs cursor-pointer transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                    >
                      <div className="space-y-3 max-w-xl">
                        <div className="flex items-center gap-2">
                          <span className="bg-slate-100 text-slate-600 text-[9px] font-bold px-2 py-0.5 rounded uppercase">
                            {q.combination} Stream
                          </span>
                          <span className="text-[10px] text-slate-400 font-bold uppercase flex items-center gap-1">
                            <Calendar className="w-3 h-3" /> {formatDate(q.createdAt)}
                          </span>
                        </div>

                        <h4 className="text-base font-bold text-slate-900 group-hover:text-indigo-700">
                          {q.title}
                        </h4>

                        <p className="text-xs text-slate-550 line-clamp-2 leading-relaxed">
                          {q.content}
                        </p>

                        <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-bold uppercase">
                          <User className="w-3.5 h-3.5 text-slate-450" />
                          <span>Asked by {q.authorName}</span>
                        </div>
                      </div>

                      {/* Answers Count Badge */}
                      <div className="flex items-center gap-1.5 bg-slate-50/50 border border-slate-200/60 py-2.5 px-4 rounded-2xl text-center shrink-0 w-full sm:w-auto justify-center">
                        <MessageSquare className="w-4 h-4 text-slate-450" />
                        <div>
                          <p className="text-xs font-bold text-slate-800">{q.answers.length}</p>
                          <p className="text-[9px] text-slate-400 font-bold uppercase">Answers</p>
                        </div>
                        <ChevronRight className="w-4 h-4 text-slate-300 ml-1.5 hidden sm:block" />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-16 bg-white rounded-3xl border border-slate-200 shadow-xs animate-fade-in">
                    <Compass className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                    <h4 className="text-md font-bold text-slate-700">No questions found</h4>
                    <p className="text-slate-400 text-sm mt-1 max-w-sm mx-auto">
                      There are no active threads for this filter. Be the first to ask!
                    </p>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
