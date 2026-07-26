import React, { useState, useMemo, useEffect } from "react";
import { COURSES, UNIVERSITIES, COMBINATIONS, Course } from "../data/tcu_data";
import { Search, GraduationCap, Clock, Award, Building, TrendingUp, Landmark, MapPin, ChevronDown, ChevronUp, DollarSign, Briefcase, FileText } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

export default function CourseDirectory() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCombo, setSelectedCombo] = useState("ALL");
  const [selectedUni, setSelectedUni] = useState("ALL");
  const [expandedCourseId, setExpandedCourseId] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<"career" | "official">("career");
  const [apiCourses, setApiCourses] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);
    fetch("/api/courses")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load official TCU catalog.");
        return res.json();
      })
      .then((data) => {
        setApiCourses(data);
        setApiError(null);
      })
      .catch((err) => {
        console.error("Failed to load catalog:", err);
        setApiError("Unable to connect to the TCU server database. Check process environment.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  // Dynamically compute the universities list based on the active tab
  const dynamicUniversities = useMemo(() => {
    if (activeTab === "official" && apiCourses.length > 0) {
      // Get unique institutions from apiCourses
      const institutions = Array.from(new Set<string>(apiCourses.map((c) => String(c.Institution || ""))))
        .filter(Boolean)
        .sort((a, b) => a.localeCompare(b));
      
      return institutions.map((inst) => ({
        id: inst,
        name: inst,
        abbreviation: inst,
      }));
    }
    return UNIVERSITIES;
  }, [activeTab, apiCourses]);

  // Filter courses based on selections
  const filteredCourses = useMemo(() => {
    return COURSES.filter((course) => {
      const matchesSearch =
        course.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        course.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        course.minimumRequirements.toLowerCase().includes(searchQuery.toLowerCase()) ||
        course.dayToDay.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCombo =
        selectedCombo === "ALL" ||
        course.eligibleCombinations.includes(selectedCombo);

      const matchesUni =
        selectedUni === "ALL" ||
        course.universityId === selectedUni;

      return matchesSearch && matchesCombo && matchesUni;
    });
  }, [searchQuery, selectedCombo, selectedUni]);

  // Filter API courses with intelligent cross-catalog parameters
  const filteredApiCourses = useMemo(() => {
    return apiCourses.filter((course) => {
      const matchesSearch =
        course.Programme.toLowerCase().includes(searchQuery.toLowerCase()) ||
        course.Code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        course["Admission Requirements"].toLowerCase().includes(searchQuery.toLowerCase()) ||
        course.Institution.toLowerCase().includes(searchQuery.toLowerCase());

      let matchesCombo = true;
      if (selectedCombo !== "ALL") {
        const comboObj = COMBINATIONS.find((c) => c.code === selectedCombo);
        if (comboObj) {
          const subjects = comboObj.subjects;
          const requirementText = course["Admission Requirements"].toLowerCase();
          matchesCombo = subjects.some((sub) => requirementText.includes(sub.toLowerCase()));
        }
      }

      let matchesUni = true;
      if (selectedUni !== "ALL") {
        const uniObj = UNIVERSITIES.find((u) => u.id === selectedUni);
        if (uniObj) {
          const uniAbbr = uniObj.abbreviation.toLowerCase();
          const uniName = uniObj.name.toLowerCase();
          matchesUni =
            course.Institution.toLowerCase().includes(uniAbbr) ||
            course.Institution.toLowerCase().includes(uniName);
        } else {
          // Check dynamic name match exactly
          matchesUni = course.Institution === selectedUni;
        }
      }

      return matchesSearch && matchesCombo && matchesUni;
    });
  }, [searchQuery, selectedCombo, selectedUni, apiCourses]);

  const toggleExpand = (id: string) => {
    setExpandedCourseId(expandedCourseId === id ? null : id);
  };

  const getUniversityDetails = (uniId: string) => {
    return UNIVERSITIES.find((u) => u.id === uniId);
  };

  const formatTsh = (amount: number) => {
    return new Intl.NumberFormat("en-US").format(amount) + " TSh";
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Intro section */}
      <div className="mb-12 text-center max-w-3xl mx-auto animate-fade-in">
        <span className="text-xs font-bold text-indigo-700 bg-indigo-50 px-3.5 py-1.5 rounded-full border border-indigo-100">
          Official TCU Course Directory & Market Trends
        </span>
        <h2 className="text-3xl font-bold tracking-tight text-slate-900 mt-4 serif-title">
          Explore Degree Paths in Tanzania
        </h2>
        <p className="text-slate-500 mt-2 text-sm sm:text-base leading-relaxed">
          Find your dream course, inspect the strict entry requirements, and analyze local salary ranges and employers before locking in your TCU choices.
        </p>
      </div>

      {/* Directory Tab Selectors */}
      <div className="flex justify-center mb-8">
        <div className="bg-slate-100 p-1.5 rounded-2xl flex items-center gap-1.5 border border-slate-200/50 shadow-xs">
          <button
            onClick={() => {
              setActiveTab("career");
              setSearchQuery("");
              setSelectedUni("ALL");
            }}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === "career"
                ? "bg-white text-indigo-700 shadow-sm"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            Interactive Career Map
          </button>
          <button
            onClick={() => {
              setActiveTab("official");
              setSearchQuery("");
              setSelectedUni("ALL");
            }}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === "official"
                ? "bg-white text-indigo-700 shadow-sm"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <GraduationCap className="w-4 h-4" />
            Official 2026/2027 TCU Guidebook ({apiCourses.length || "..."})
          </button>
        </div>
      </div>

      {/* Filter and Search Panel */}
      <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search Box */}
          <div className="relative">
            <Search className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by course name, requirements..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-slate-50/50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-slate-800"
            />
          </div>

          {/* Combination Selector */}
          <div>
            <select
              value={selectedCombo}
              onChange={(e) => setSelectedCombo(e.target.value)}
              className="w-full px-4 py-3 bg-slate-50/50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-slate-700"
            >
              <option value="ALL">All A-Level Combinations</option>
              {COMBINATIONS.map((combo) => (
                <option key={combo.code} value={combo.code}>
                  {combo.code} - {combo.name}
                </option>
              ))}
            </select>
          </div>

          {/* University Selector */}
          <div>
            <select
              value={selectedUni}
              onChange={(e) => setSelectedUni(e.target.value)}
              className="w-full px-4 py-3 bg-slate-50/50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-slate-700"
            >
              <option value="ALL">All Universities</option>
              {dynamicUniversities.map((uni) => (
                <option key={uni.id} value={uni.id}>
                  {uni.abbreviation === uni.name ? uni.name : `${uni.abbreviation} - ${uni.name}`}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Selected combination explanation if filtered */}
        {selectedCombo !== "ALL" && (
          <div className="mt-4 p-4 bg-indigo-50/50 border border-indigo-100/50 rounded-2xl flex items-start gap-3">
            <Award className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-indigo-800 uppercase tracking-wide">
                A-Level Stream: {selectedCombo}
              </p>
              <p className="text-xs text-slate-600 mt-1">
                {COMBINATIONS.find((c) => c.code === selectedCombo)?.description}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Courses List Container */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-16 bg-white rounded-3xl border border-slate-200">
            <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <h3 className="text-lg font-bold text-slate-700">Connecting to TCU database...</h3>
            <p className="text-slate-400 text-sm mt-1 max-w-md mx-auto">
              Pulling live, verified degree catalog with minimum requirements from CareerVillage TZ API...
            </p>
          </div>
        ) : activeTab === "official" ? (
          <div className="space-y-4 animate-fade-in">
            {apiError && (
              <div className="p-4 bg-amber-50 border border-amber-200 text-amber-800 text-xs sm:text-sm rounded-2xl flex items-center gap-3">
                <FileText className="w-5 h-5 shrink-0" />
                <span>{apiError} Showing offline snapshot from catalog data.</span>
              </div>
            )}
            {filteredApiCourses.length > 0 ? (
              filteredApiCourses.map((course, idx) => {
                const isExpanded = expandedCourseId === `${course.Code}-${idx}`;
                return (
                  <div
                    id={`api-course-card-${course.Code}-${idx}`}
                    key={`${course.Code}-${idx}`}
                    className={`bg-white rounded-3xl border transition-all duration-200 ${
                      isExpanded ? "border-indigo-300 ring-2 ring-indigo-50/70 shadow-md" : "border-slate-200 hover:border-slate-300 shadow-xs"
                    }`}
                  >
                    {/* Compact Header */}
                    <div
                      onClick={() => toggleExpand(`${course.Code}-${idx}`)}
                      className="p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 cursor-pointer select-none"
                    >
                      <div className="flex items-start gap-4">
                        <div className="p-3 bg-indigo-50 text-indigo-700 rounded-xl border border-indigo-100 hidden sm:block">
                          <GraduationCap className="w-6 h-6" />
                        </div>
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="mono-tag text-[10px] font-bold tracking-wider text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded uppercase border border-indigo-100">
                              {course.Code || "TCU"}
                            </span>
                            <span className="text-xs text-slate-500 font-semibold flex items-center gap-1">
                              <Building className="w-3.5 h-3.5 text-slate-400" /> {course.Institution}
                            </span>
                          </div>
                          <h3 className="text-base sm:text-lg font-bold text-slate-900 mt-2">
                            {course.Programme}
                          </h3>
                          <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5 text-slate-400" /> Duration: {course["Programme Duration (Yrs)"]} Years • TCU Book Page {course.Page || "N/A"}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 self-stretch sm:self-center justify-between sm:justify-end border-t sm:border-t-0 pt-3 sm:pt-0 border-slate-50 shrink-0">
                        <div className="flex items-center gap-3">
                          <div className="text-right">
                            <p className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Capacity</p>
                            <p className="text-xs sm:text-sm font-bold text-indigo-700">{course["Admission Capacity"] || "N/A"}</p>
                          </div>
                          <div className="h-6 w-px bg-slate-200"></div>
                          <div className="text-right">
                            <p className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Min Points</p>
                            <p className="text-xs sm:text-sm font-bold text-slate-800">{course["Minimum Institutional Admission Points"] || "4.0"}</p>
                          </div>
                        </div>
                        <button className="p-2 text-slate-400 hover:text-slate-600 rounded-xl hover:bg-slate-50 transition-colors ml-2">
                          {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>

                    {/* Expanded Requirements Details */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden border-t border-slate-100"
                        >
                          <div className="p-6 bg-slate-50/40 space-y-4">
                            <div className="space-y-2">
                              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                                <GraduationCap className="w-4 h-4 text-indigo-600" /> Official Minimum Admission & Eligibility Requirements
                              </h4>
                              <p className="text-sm text-slate-700 leading-relaxed bg-white p-5 rounded-2xl border border-slate-100 shadow-xs">
                                {course["Admission Requirements"]}
                              </p>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                              <div className="bg-white p-4 rounded-xl border border-slate-100">
                                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Minimum Admission GPA/Points</span>
                                <span className="text-sm font-bold text-slate-800 mt-1 block">{course["Minimum Institutional Admission Points"] || "4.0"} Points</span>
                              </div>
                              <div className="bg-white p-4 rounded-xl border border-slate-100">
                                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Annual Admission Capacity</span>
                                <span className="text-sm font-bold text-indigo-700 mt-1 block">{course["Admission Capacity"] || "N/A"} Student Slots</span>
                              </div>
                              <div className="bg-white p-4 rounded-xl border border-slate-100">
                                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Official Guidebook Page</span>
                                <span className="text-sm font-bold text-slate-800 mt-1 block">Page {course.Page || "N/A"} (TCU 2026/27)</span>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-16 bg-white rounded-3xl border border-slate-200">
                <GraduationCap className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <h3 className="text-lg font-bold text-slate-700">No matching official courses found</h3>
                <p className="text-slate-400 text-sm mt-1 max-w-md mx-auto">
                  Try typing another keyword or clearing your search criteria.
                </p>
                <button
                  onClick={() => {
                    setSearchQuery("");
                    setSelectedCombo("ALL");
                    setSelectedUni("ALL");
                  }}
                  className="mt-5 px-6 py-3 bg-indigo-600 text-white text-xs font-bold rounded-xl hover:bg-indigo-700 transition-all shadow-sm cursor-pointer"
                >
                  Reset Filters
                </button>
              </div>
            )}
          </div>
        ) : (
          /* Original rich course rendering list */
          filteredCourses.length > 0 ? (
            filteredCourses.map((course) => {
              const isExpanded = expandedCourseId === course.id;
              const uni = getUniversityDetails(course.universityId);
              const demandColors =
                course.marketTrends.demand === "High"
                  ? "bg-emerald-50 text-emerald-700 border-emerald-150"
                  : course.marketTrends.demand === "Medium"
                  ? "bg-amber-50 text-amber-700 border-amber-150"
                  : "bg-blue-50 text-blue-700 border-blue-150";

              return (
                <div
                  id={`course-card-${course.id}`}
                  key={course.id}
                  className={`bg-white rounded-3xl border transition-all duration-200 ${
                    isExpanded ? "border-indigo-300 ring-2 ring-indigo-50/70 shadow-md" : "border-slate-200 hover:border-slate-300 shadow-xs"
                  }`}
                >
                  {/* Compact Card Header */}
                  <div
                    onClick={() => toggleExpand(course.id)}
                    className="p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 cursor-pointer select-none"
                  >
                    <div className="flex items-start gap-4">
                      <div className="p-3 bg-slate-50 text-slate-600 rounded-xl border border-slate-100 hidden sm:block">
                        <GraduationCap className="w-6 h-6" />
                      </div>
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="mono-tag text-[10px] font-bold tracking-wider text-slate-400 bg-slate-100 px-2 py-0.5 rounded uppercase">
                            {course.code}
                          </span>
                          <span className="text-xs text-slate-500 font-semibold flex items-center gap-1">
                            <Building className="w-3.5 h-3.5 text-slate-400" /> {uni?.name} ({uni?.abbreviation})
                          </span>
                        </div>
                        <h3 className="text-lg font-bold text-slate-900 mt-1 hover:text-indigo-700 transition-colors">
                          {course.name}
                        </h3>
                        <p className="text-xs text-slate-500 mt-1.5 flex flex-wrap items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-slate-400" /> {course.durationYears} Years Duration •
                          <span className="font-bold text-slate-700">Eligible Streams:</span>
                          {course.eligibleCombinations.map((c, idx) => (
                            <span key={`${c}-${idx}`} className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded text-[10px] font-bold">
                              {c}
                            </span>
                          ))}
                        </p>
                      </div>
                    </div>

                    {/* Summary badges */}
                    <div className="flex items-center gap-2 self-stretch sm:self-center justify-between sm:justify-end border-t sm:border-t-0 pt-3 sm:pt-0 border-slate-50">
                      <div className="flex items-center gap-3">
                        <div className={`px-3 py-1 rounded-full text-xs font-bold border ${demandColors}`}>
                          {course.marketTrends.demand} Market Demand
                        </div>
                        <div className="text-right hidden md:block">
                          <p className="text-[10px] text-slate-400 font-bold uppercase">Avg Salary</p>
                          <p className="text-sm font-bold text-slate-800">{formatTsh(course.marketTrends.averageStartingSalaryTsh)}</p>
                        </div>
                      </div>
                      <button className="p-2 text-slate-400 hover:text-slate-600 rounded-xl hover:bg-slate-50 transition-colors">
                        {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  {/* Expanded Details Panel */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden border-t border-slate-100"
                      >
                        <div className="p-6 bg-slate-50/40 grid grid-cols-1 lg:grid-cols-3 gap-8">
                          {/* Column 1: Academic expectations */}
                          <div className="lg:col-span-2 space-y-6">
                            <div>
                              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2 mb-2.5">
                                <GraduationCap className="w-4 h-4 text-indigo-600" /> What is studying this course like?
                              </h4>
                              <p className="text-sm text-slate-600 leading-relaxed bg-white p-5 rounded-2xl border border-slate-100 shadow-xs">
                                {course.whatToExpect.studying}
                              </p>
                            </div>

                            <div>
                              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2 mb-2.5">
                                <Award className="w-4 h-4 text-indigo-600" /> After Graduation & Industry Entry
                              </h4>
                              <p className="text-sm text-slate-600 leading-relaxed bg-white p-5 rounded-2xl border border-slate-100 shadow-xs">
                                {course.whatToExpect.graduation}
                              </p>
                            </div>

                            <div>
                              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2 mb-2.5">
                                <Briefcase className="w-4 h-4 text-indigo-600" /> Day-to-Day on the Job
                              </h4>
                              <p className="text-sm text-slate-600 leading-relaxed bg-white p-5 rounded-2xl border border-slate-100 shadow-xs">
                                {course.dayToDay}
                              </p>
                            </div>

                            <div className="p-5 bg-amber-50/40 border border-amber-100/70 rounded-2xl">
                              <h5 className="text-xs font-bold text-amber-800 uppercase tracking-wider mb-1.5">
                                Official TCU Minimum Eligibility Criteria
                              </h5>
                              <p className="text-xs text-slate-600 font-medium leading-relaxed">
                                {course.minimumRequirements}
                              </p>
                            </div>
                          </div>

                          {/* Column 2: Market trend insights */}
                          <div className="space-y-6 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs h-fit animate-fade-in">
                            <div>
                              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 mb-3">
                                <TrendingUp className="w-3.5 h-3.5 text-slate-400" /> Local Market Trends
                              </h4>
                              <div className="space-y-4">
                                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                                  <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                                    Average Entry Salary
                                  </span>
                                  <span className="text-xl font-bold text-slate-900 mt-1 block">
                                    {formatTsh(course.marketTrends.averageStartingSalaryTsh)} <span className="text-xs text-slate-400 font-normal">/ month</span>
                                  </span>
                                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                                    {course.marketTrends.salaryTrend}
                                  </p>
                                </div>

                                <div>
                                  <span className="text-xs font-bold text-slate-500 block mb-1.5 uppercase tracking-wide">
                                    Key Professional Job Roles
                                  </span>
                                  <div className="flex flex-wrap gap-1.5">
                                    {course.marketTrends.keyJobRoles.map((role) => (
                                      <span key={role} className="bg-slate-50 border border-slate-150 text-slate-700 text-xs px-2.5 py-1 rounded-lg font-medium">
                                        {role}
                                      </span>
                                    ))}
                                  </div>
                                </div>

                                <div className="border-t border-slate-100 pt-4">
                                  <span className="text-xs font-bold text-slate-500 block mb-2 flex items-center gap-1 uppercase tracking-wide">
                                    <Landmark className="w-3.5 h-3.5 text-slate-400" /> Major Local Employers
                                  </span>
                                  <ul className="space-y-1.5">
                                    {course.marketTrends.topLocalEmployers.map((emp) => (
                                      <li key={emp} className="text-xs text-slate-600 font-semibold flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full"></span>
                                        {emp}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                            </div>

                            <div className="border-t border-slate-100 pt-4 text-center">
                              <p className="text-[10px] text-slate-400 font-bold uppercase">University Info</p>
                              <p className="text-xs font-bold text-slate-800 mt-1">{uni?.name}</p>
                              <p className="text-[11px] text-slate-400 flex items-center justify-center gap-1 mt-0.5">
                                <MapPin className="w-3 h-3 text-slate-400" /> {uni?.location} • Est. {uni?.established}
                              </p>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })
          ) : (
            <div className="text-center py-16 bg-white rounded-3xl border border-slate-200">
              <GraduationCap className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-slate-700">No matching courses found</h3>
              <p className="text-slate-400 text-sm mt-1 max-w-md mx-auto">
                Try typing another keyword, selecting a different A-Level combination, or clearing your search criteria.
              </p>
              <button
                onClick={() => {
                  setSearchQuery("");
                  setSelectedCombo("ALL");
                  setSelectedUni("ALL");
                }}
                className="mt-5 px-6 py-3 bg-indigo-600 text-white text-xs font-bold rounded-xl hover:bg-indigo-700 transition-all shadow-sm cursor-pointer"
              >
                Reset Filters
              </button>
            </div>
          )
        )}
      </div>
    </div>
  );
}
