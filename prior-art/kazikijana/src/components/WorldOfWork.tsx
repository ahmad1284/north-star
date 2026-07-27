import React, { useState, useMemo } from "react";
import { 
  Compass, 
  Briefcase, 
  Users, 
  Cpu, 
  Layers, 
  Activity, 
  FileText, 
  ChevronRight, 
  Sparkles, 
  RotateCcw, 
  MapPin, 
  GraduationCap, 
  TrendingUp, 
  BookOpen, 
  Dribbble, 
  Award,
  HelpCircle,
  Lightbulb
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { COURSES, COMBINATIONS, Course, ALevelCombination } from "../data/tcu_data";

// Type definitions
interface SectorDetail {
  id: string;
  name: string;
  color: string;
  textColor: string;
  borderColor: string;
  bgLight: string;
  bgAccent: string;
  hoverBorder: string;
  focus: string;
  icon: React.ComponentType<any>;
  description: string;
  tanzanianContext: string;
  keyTasks: string[];
  streams: string[];
  professions: string[];
  fields: string[];
}

const SECTORS: SectorDetail[] = [
  {
    id: "administration",
    name: "Administration & Sales",
    color: "indigo",
    textColor: "text-indigo-700",
    borderColor: "border-indigo-200",
    bgLight: "bg-indigo-50",
    bgAccent: "bg-indigo-600",
    hoverBorder: "hover:border-indigo-400 hover:ring-2 hover:ring-indigo-100",
    focus: "People & Data",
    icon: FileText,
    description: "Centering on managing organizational records, policy execution, legal compliance, and customer outreach.",
    tanzanianContext: "Managing public services, running courts, ensuring corporate regulation, or leading sales and marketing campaigns in East Africa's growing hub.",
    keyTasks: [
      "Analyzing policy documents and government guidelines",
      "Representing clients in legal proceedings or drafting contracts",
      "Formulating marketing campaigns and managing sales targets",
      "Ensuring regulatory compliance and keeping records"
    ],
    streams: ["HKL", "HGL", "HGK", "ECA", "HGE"],
    professions: ["Lawyer / Advocate", "Public Relations Officer", "Human Resource Manager", "Marketing Manager", "Registrar"],
    fields: ["Management", "Marketing & Sales", "Regulation & Protection", "Personal Services"]
  },
  {
    id: "business",
    name: "Business Operations",
    color: "sky",
    textColor: "text-sky-700",
    borderColor: "border-sky-200",
    bgLight: "bg-sky-50",
    bgAccent: "bg-sky-600",
    hoverBorder: "hover:border-sky-400 hover:ring-2 hover:ring-sky-100",
    focus: "Data & Things",
    icon: TrendingUp,
    description: "Focusing on financial tracking, logistics organization, warehousing, and optimizing system operations.",
    tanzanianContext: "Operating within banks (like NMB, CRDB), managing ports & container shipments, auditing tax declarations, or handling supply chains.",
    keyTasks: [
      "Auditing financial spreadsheets and checking transaction logs",
      "Scheduling logistics dispatch and managing transport networks",
      "Analyzing bank credit reports or financial investments",
      "Maintaining inventory records for major distribution warehouses"
    ],
    streams: ["ECA", "HGE", "EGM"],
    professions: ["Auditor / Accountant", "Supply Chain Manager", "Financial Analyst", "Procurement Officer", "Port Operations Officer"],
    fields: ["Financial Transactions", "Communication & Records", "Distribution & Dispatching"]
  },
  {
    id: "technical",
    name: "Technical & Applied Fields",
    color: "teal",
    textColor: "text-teal-700",
    borderColor: "border-teal-200",
    bgLight: "bg-teal-50",
    bgAccent: "bg-teal-600",
    hoverBorder: "hover:border-teal-400 hover:ring-2 hover:ring-teal-100",
    focus: "Things & Data",
    icon: Cpu,
    description: "Centering on installing hardware, configuring networks, maintaining physical/digital systems, and resource extraction.",
    tanzanianContext: "Managing telecom grids (Vodacom, Tigo), managing commercial agriculture in Morogoro, operating food processing plants, or monitoring mining systems.",
    keyTasks: [
      "Configuring network switches and administering servers",
      "Troubleshooting electronic boards or physical system panels",
      "Supervising farm crops, agro-forestry, and soil diagnostic data",
      "Maintaining production lines or machinery components"
    ],
    streams: ["PCM", "PGM", "PCB", "CBG"],
    professions: ["IT Support Administrator", "Agribusiness Manager", "Production Supervisor", "Telecommunications Technician", "Database Manager"],
    fields: ["Transport Operations", "Ag/Forestry", "Computer Specialities", "Construction & Crafts"]
  },
  {
    id: "stem",
    name: "STEM (Science & Engineering)",
    color: "rose",
    textColor: "text-rose-700",
    borderColor: "border-rose-200",
    bgLight: "bg-rose-50",
    bgAccent: "bg-rose-600",
    hoverBorder: "hover:border-rose-400 hover:ring-2 hover:ring-rose-100",
    focus: "Ideas & Things",
    icon: Layers,
    description: "Focusing on designing physical infrastructure, chemical formulas, software architecture, and executing laboratory procedures.",
    tanzanianContext: "Designing highways (TANROADS), planning solar grids, exploring minerals in Geita, researching vaccine development, or architecting major software systems.",
    keyTasks: [
      "Drafting CAD blueprints for bridges, roads, or power plants",
      "Performing chemical analysis and researching laboratory cultures",
      "Writing complex computer algorithms and software frameworks",
      "Conducting geological surveys and modeling rock resource deposits"
    ],
    streams: ["PCM", "PGM", "PCB"],
    professions: ["Civil Engineer", "Mechanical Engineer", "Geologist / Mining Engineer", "Software Architect", "Lab Research Scientist"],
    fields: ["Engineering & Tech", "Natural Sciences", "Medical Technologies", "Medical Treatment"]
  },
  {
    id: "arts",
    name: "Arts & Communications",
    color: "amber",
    textColor: "text-amber-700",
    borderColor: "border-amber-200",
    bgLight: "bg-amber-50",
    bgAccent: "bg-amber-600",
    hoverBorder: "hover:border-amber-400 hover:ring-2 hover:ring-amber-100",
    focus: "Ideas & People",
    icon: Dribbble,
    description: "Centering on visual presentation, writing, translation, journalism, cultural curation, and creative content creation.",
    tanzanianContext: "Producing educational radio campaigns, translation work (Kiswahili/English), graphic design for agencies, or advocating national arts in Tanzania.",
    keyTasks: [
      "Writing creative articles, novels, or national broadcast scripts",
      "Creating brand identities, graphic illustrations, or user interfaces",
      "Translating complex documents between Kiswahili, English, and other languages",
      "Directing performing arts, drama productions, or musical projects"
    ],
    streams: ["HKL", "HGL", "HGK"],
    professions: ["Journalist / News Writer", "Graphic Designer", "Linguist / Translator", "Creative Director", "Media Producer"],
    fields: ["Visual Arts", "Written & Spoken Arts", "Creative & Performing Arts", "Social Science"]
  },
  {
    id: "social",
    name: "Social & Human Services",
    color: "purple",
    textColor: "text-purple-700",
    borderColor: "border-purple-200",
    bgLight: "bg-purple-50",
    bgAccent: "bg-purple-600",
    hoverBorder: "hover:border-purple-400 hover:ring-2 hover:ring-purple-100",
    focus: "People & Ideas",
    icon: Users,
    description: "Focusing on academic teaching, healthcare delivery, nursing, community development, and public welfare support.",
    tanzanianContext: "Instructing high school combinations, curing patients at Muhimbili Hospital, raising health awareness in rural wards, or organizing community development.",
    keyTasks: [
      "Teaching and evaluating academic combination subjects",
      "Diagnosing physical ailments and prescribing patient treatments",
      "Directing public health outreach and wellness campaigns",
      "Counseling individuals and conducting family welfare sessions"
    ],
    streams: ["PCB", "CBG", "HGL", "HKL", "HGK"],
    professions: ["Doctor / Physician", "High School Teacher", "Registered Nurse", "Community Development Officer", "Social Worker"],
    fields: ["Personal Services", "Community Services", "Education", "Health Care"]
  }
];

// Quiz Questions
interface QuizQuestion {
  id: number;
  text: string;
  dimension: "data" | "things" | "ideas" | "people";
  weight: number; // multiplier for the score
}

const QUIZ_QUESTIONS: QuizQuestion[] = [
  { id: 1, text: "I would enjoy auditing corporate spreadsheets and reconciling financial records.", dimension: "data", weight: 2 },
  { id: 2, text: "I like writing novels, drafting creative articles, or telling rich stories in Kiswahili or English.", dimension: "ideas", weight: 2 },
  { id: 3, text: "I would enjoy assembling hardware, fixing circuit boards, or troubleshooting motor machinery.", dimension: "things", weight: 2 },
  { id: 4, text: "I feel satisfied when teaching students, counseling families, or taking clinical care of sick patients.", dimension: "people", weight: 2 },
  { id: 5, text: "I am interested in analyzing demographic surveys, census figures, or academic statistics.", dimension: "data", weight: 1.5 },
  { id: 6, text: "I like sketching conceptual plans for buildings, modeling prototypes, or inventing software workflows.", dimension: "ideas", weight: 1.5 },
  { id: 7, text: "I enjoy organizing physical storage layouts, scheduling freight logistics, or operating industrial machines.", dimension: "things", weight: 1.5 },
  { id: 8, text: "I would enjoy leading a community development drive, speaking in public, or doing legal counseling.", dimension: "people", weight: 1.5 }
];

export default function WorldOfWork() {
  const [activeSubTab, setActiveSubTab] = useState<"explorer" | "quiz">("explorer");
  const [selectedSectorId, setSelectedSectorId] = useState<string>("stem");

  // Quiz State
  const [answers, setAnswers] = useState<Record<number, number>>({}); // questionId -> response (1-5)
  const [quizFinished, setQuizFinished] = useState(false);
  const [calculatedCoordinates, setCalculatedCoordinates] = useState({ x: 0, y: 0 });
  const [suggestedSector, setSuggestedSector] = useState<SectorDetail | null>(null);

  // polarToCartesian for drawing the wheel
  const polarToCartesian = (cx: number, cy: number, r: number, angleInDegrees: number) => {
    const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
    return {
      x: cx + r * Math.cos(angleInRadians),
      y: cy + r * Math.sin(angleInRadians)
    };
  };

  const describeArc = (cx: number, cy: number, r: number, startAngle: number, endAngle: number) => {
    const start = polarToCartesian(cx, cy, r, endAngle);
    const end = polarToCartesian(cx, cy, r, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
    return [
      "M", start.x, start.y, 
      "A", r, r, 0, largeArcFlag, 0, end.x, end.y,
      "L", cx, cy,
      "Z"
    ].join(" ");
  };

  // Filter courses from tcu_data.ts that align with the selected sector
  const matchingCourses = useMemo(() => {
    const sector = SECTORS.find(s => s.id === selectedSectorId);
    if (!sector) return [];

    return COURSES.filter(course => {
      // Check if course has eligible combinations matching the sector streams
      const hasComboMatch = course.eligibleCombinations.some(combo => 
        sector.streams.includes(combo)
      );

      // Category-based heuristics to perfect the alignment
      let categoryMatch = false;
      const name = course.name.toLowerCase();
      if (sector.id === "stem") {
        categoryMatch = name.includes("engineer") || name.includes("science") || name.includes("geology") || name.includes("computing") || name.includes("architecture");
      } else if (sector.id === "business") {
        categoryMatch = name.includes("account") || name.includes("finance") || name.includes("procurement") || name.includes("logistics") || name.includes("economics");
      } else if (sector.id === "administration") {
        categoryMatch = name.includes("law") || name.includes("administration") || name.includes("relations") || name.includes("marketing") || name.includes("commerce");
      } else if (sector.id === "social") {
        categoryMatch = name.includes("medicine") || name.includes("nurse") || name.includes("education") || name.includes("teach") || name.includes("social work") || name.includes("health");
      } else if (sector.id === "technical") {
        categoryMatch = name.includes("information tech") || name.includes("computer") || name.includes("telecom") || name.includes("agriculture") || name.includes("forestry");
      } else if (sector.id === "arts") {
        categoryMatch = name.includes("kiswahili") || name.includes("literature") || name.includes("arts") || name.includes("journalism") || name.includes("language");
      }

      return hasComboMatch && categoryMatch;
    }).slice(0, 5); // Limit to top 5 matches
  }, [selectedSectorId]);

  const activeSector = useMemo(() => {
    return SECTORS.find(s => s.id === selectedSectorId) || SECTORS[3];
  }, [selectedSectorId]);

  // Quiz Handlers
  const handleAnswerSelect = (questionId: number, value: number) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const handleResetQuiz = () => {
    setAnswers({});
    setQuizFinished(false);
    setSuggestedSector(null);
  };

  const calculateQuizResults = () => {
    // Score buckets
    let dataScore = 0;
    let thingsScore = 0;
    let ideasScore = 0;
    let peopleScore = 0;

    QUIZ_QUESTIONS.forEach(q => {
      const response = answers[q.id] || 3; // default to neutral (3) if unanswered
      // Convert 1-5 scale to -2 to +2 relative scale
      const relativeVal = response - 3;
      const points = relativeVal * q.weight;

      if (q.dimension === "data") dataScore += points;
      if (q.dimension === "things") thingsScore += points;
      if (q.dimension === "ideas") ideasScore += points;
      if (q.dimension === "people") peopleScore += points;
    });

    // Calculate Cartesian coordinate for ACT World of Work Map
    // X-axis: People (left/negative) vs Things (right/positive)
    const x = thingsScore - peopleScore;
    // Y-axis: Ideas (bottom/negative) vs Data (top/positive)
    const y = dataScore - ideasScore;

    setCalculatedCoordinates({ x, y });

    // Find the sector based on Cartesian coordinate angle
    // Math.atan2(y, x) returns angle in radians from -PI to PI
    // We add 90 degrees offset to align with our top-centered 0 degrees system
    let angleDegrees = Math.atan2(x, y) * 180 / Math.PI; // -180 to 180
    if (angleDegrees < 0) angleDegrees += 360; // 0 to 360

    // Match sector angle ranges:
    // Sector 1: Administration (300° to 360°)
    // Sector 2: Business (0° to 60°)
    // Sector 3: Technical (60° to 120°)
    // Sector 4: STEM (120° to 180°)
    // Sector 5: Arts (180° to 240°)
    // Sector 6: Social & Human Services (240° to 300°)
    let recommended: SectorDetail;

    if (angleDegrees >= 300 || angleDegrees < 0) {
      recommended = SECTORS[0]; // Administration
    } else if (angleDegrees >= 0 && angleDegrees < 60) {
      recommended = SECTORS[1]; // Business
    } else if (angleDegrees >= 60 && angleDegrees < 120) {
      recommended = SECTORS[2]; // Technical
    } else if (angleDegrees >= 120 && angleDegrees < 180) {
      recommended = SECTORS[3]; // STEM
    } else if (angleDegrees >= 180 && angleDegrees < 240) {
      recommended = SECTORS[4]; // Arts
    } else {
      recommended = SECTORS[5]; // Social
    }

    setSuggestedSector(recommended);
    setQuizFinished(true);
    setSelectedSectorId(recommended.id); // Also sync the explorer sector
  };

  const isQuizComplete = Object.keys(answers).length === QUIZ_QUESTIONS.length;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Intro section */}
      <div className="mb-10 text-center max-w-3xl mx-auto animate-fade-in">
        <span className="text-xs font-bold text-indigo-700 bg-indigo-50 px-3.5 py-1.5 rounded-full border border-indigo-100">
          ACT World-of-Work Guide
        </span>
        <h2 className="text-3xl font-bold tracking-tight text-slate-900 mt-4 serif-title">
          World of Work Map
        </h2>
        <p className="text-slate-500 mt-2 text-sm sm:text-base leading-relaxed">
          Unlock standard career sectors based on key tasks (Data, Ideas, People, and Things) and explore matching Tanzanian university degree courses.
        </p>
      </div>

      {/* Mode selectors */}
      <div className="flex justify-center mb-8">
        <div className="bg-slate-100/80 p-1.5 rounded-2xl border border-slate-200 flex gap-1">
          <button
            onClick={() => setActiveSubTab("explorer")}
            className={`px-5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeSubTab === "explorer"
                ? "bg-white text-indigo-700 shadow-xs border border-slate-200"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <Compass className="w-4 h-4" /> Map Explorer
          </button>
          <button
            onClick={() => setActiveSubTab("quiz")}
            className={`px-5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeSubTab === "quiz"
                ? "bg-white text-indigo-700 shadow-xs border border-slate-200"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <Sparkles className="w-4 h-4" /> Career Compass Quiz
          </button>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {activeSubTab === "explorer" ? (
          <motion.div
            key="explorer-view"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start"
          >
            {/* Left Col: Interactive Wheel Map (5 cols) */}
            <div className="lg:col-span-5 bg-white p-6 rounded-3xl border border-slate-200 shadow-xs flex flex-col items-center">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6 text-center">
                Interactive World-of-Work Wheel
              </h3>

              {/* The SVG Wheel */}
              <div className="relative w-72 h-72 sm:w-80 sm:h-80">
                <svg viewBox="0 0 300 300" className="w-full h-full drop-shadow-sm overflow-visible">
                  {/* Outer circle decoration */}
                  <circle cx="150" cy="150" r="146" fill="none" stroke="#E2E8F0" strokeWidth="2" strokeDasharray="4 4" />
                  <circle cx="150" cy="150" r="140" fill="none" stroke="#E2E8F0" strokeWidth="1" />

                  {/* 6 Career Sectors (Wedged wedges) */}
                  {/* Wedge 1: Administration (300° to 360°) */}
                  <path 
                    d={describeArc(150, 150, 132, 300, 360)}
                    fill={selectedSectorId === "administration" ? "#EEF2FF" : "#FFFFFF"}
                    stroke={selectedSectorId === "administration" ? "#6366F1" : "#E2E8F0"}
                    strokeWidth={selectedSectorId === "administration" ? "3" : "1"}
                    className="cursor-pointer transition-all hover:fill-indigo-50/50"
                    onClick={() => setSelectedSectorId("administration")}
                  />
                  {/* Wedge 2: Business (0° to 60°) */}
                  <path 
                    d={describeArc(150, 150, 132, 0, 60)}
                    fill={selectedSectorId === "business" ? "#F0F9FF" : "#FFFFFF"}
                    stroke={selectedSectorId === "business" ? "#0EA5E9" : "#E2E8F0"}
                    strokeWidth={selectedSectorId === "business" ? "3" : "1"}
                    className="cursor-pointer transition-all hover:fill-sky-50/50"
                    onClick={() => setSelectedSectorId("business")}
                  />
                  {/* Wedge 3: Technical (60° to 120°) */}
                  <path 
                    d={describeArc(150, 150, 132, 60, 120)}
                    fill={selectedSectorId === "technical" ? "#F0FDF4" : "#FFFFFF"}
                    stroke={selectedSectorId === "technical" ? "#14B8A6" : "#E2E8F0"}
                    strokeWidth={selectedSectorId === "technical" ? "3" : "1"}
                    className="cursor-pointer transition-all hover:fill-teal-50/50"
                    onClick={() => setSelectedSectorId("technical")}
                  />
                  {/* Wedge 4: STEM (120° to 180°) */}
                  <path 
                    d={describeArc(150, 150, 132, 120, 180)}
                    fill={selectedSectorId === "stem" ? "#FFF1F2" : "#FFFFFF"}
                    stroke={selectedSectorId === "stem" ? "#F43F5E" : "#E2E8F0"}
                    strokeWidth={selectedSectorId === "stem" ? "3" : "1"}
                    className="cursor-pointer transition-all hover:fill-rose-50/50"
                    onClick={() => setSelectedSectorId("stem")}
                  />
                  {/* Wedge 5: Arts (180° to 240°) */}
                  <path 
                    d={describeArc(150, 150, 132, 180, 240)}
                    fill={selectedSectorId === "arts" ? "#FFFBEB" : "#FFFFFF"}
                    stroke={selectedSectorId === "arts" ? "#F59E0B" : "#E2E8F0"}
                    strokeWidth={selectedSectorId === "arts" ? "3" : "1"}
                    className="cursor-pointer transition-all hover:fill-amber-50/50"
                    onClick={() => setSelectedSectorId("arts")}
                  />
                  {/* Wedge 6: Social & Human (240° to 300°) */}
                  <path 
                    d={describeArc(150, 150, 132, 240, 300)}
                    fill={selectedSectorId === "social" ? "#FAF5FF" : "#FFFFFF"}
                    stroke={selectedSectorId === "social" ? "#A855F7" : "#E2E8F0"}
                    strokeWidth={selectedSectorId === "social" ? "3" : "1"}
                    className="cursor-pointer transition-all hover:fill-purple-50/50"
                    onClick={() => setSelectedSectorId("social")}
                  />

                  {/* Axis Crosshairs (Compass directions: Data, Things, Ideas, People) */}
                  <line x1="150" y1="20" x2="150" y2="280" stroke="#CBD5E1" strokeWidth="1.5" strokeDasharray="3 3" />
                  <line x1="20" y1="150" x2="280" y2="150" stroke="#CBD5E1" strokeWidth="1.5" strokeDasharray="3 3" />

                  {/* Compass Axis Text Labels with background pill */}
                  <g className="font-bold text-[10px] fill-slate-500 uppercase tracking-widest select-none">
                    {/* Top: DATA */}
                    <rect x="125" y="6" width="50" height="15" rx="4" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1" />
                    <text x="150" y="17" textAnchor="middle" className="font-sans font-bold fill-indigo-800 text-[9px]">Data</text>

                    {/* Right: THINGS */}
                    <rect x="236" y="142" width="58" height="15" rx="4" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1" />
                    <text x="265" y="153" textAnchor="middle" className="font-sans font-bold fill-teal-800 text-[9px]">Things</text>

                    {/* Bottom: IDEAS */}
                    <rect x="125" y="278" width="50" height="15" rx="4" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1" />
                    <text x="150" y="289" textAnchor="middle" className="font-sans font-bold fill-amber-800 text-[9px]">Ideas</text>

                    {/* Left: PEOPLE */}
                    <rect x="6" y="142" width="58" height="15" rx="4" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1" />
                    <text x="35" y="153" textAnchor="middle" className="font-sans font-bold fill-purple-800 text-[9px]">People</text>
                  </g>

                  {/* Internal Core Hexagon Center Compass */}
                  <polygon points="150,132 165,141 165,159 150,168 135,159 135,141" fill="#F1F5F9" stroke="#94A3B8" strokeWidth="1.5" />
                  <circle cx="150" cy="150" r="3" fill="#64748B" />

                  {/* Compass Axis arrows in center */}
                  <path d="M 150,138 L 150,143 M 150,138 L 147,141 M 150,138 L 153,141" fill="none" stroke="#64748B" strokeWidth="1.2" />
                  <path d="M 150,162 L 150,157 M 150,162 L 147,159 M 150,162 L 153,159" fill="none" stroke="#64748B" strokeWidth="1.2" />
                  <path d="M 162,150 L 157,150 M 162,150 L 159,147 M 162,150 L 159,153" fill="none" stroke="#64748B" strokeWidth="1.2" />
                  <path d="M 138,150 L 143,150 M 138,150 L 141,147 M 138,150 L 141,153" fill="none" stroke="#64748B" strokeWidth="1.2" />

                  {/* Text on wedges (Sector Names, abbreviated but clear) */}
                  <g className="text-[8px] font-bold fill-slate-700 pointer-events-none uppercase tracking-wide select-none">
                    <text x="185" y="85" textAnchor="middle">Business</text>
                    <text x="215" y="195" textAnchor="middle">Technical</text>
                    <text x="150" y="245" textAnchor="middle">STEM</text>
                    <text x="85" y="195" textAnchor="middle">Arts</text>
                    <text x="85" y="105" textAnchor="middle">Social Work</text>
                    <text x="150" y="55" textAnchor="middle">Admin</text>
                  </g>
                </svg>
              </div>

              {/* Wedge legend buttons for mobile layout */}
              <div className="mt-8 grid grid-cols-2 gap-2 w-full">
                {SECTORS.map((s) => {
                  const sIcon = s.icon;
                  const isSelected = selectedSectorId === s.id;
                  return (
                    <button
                      key={s.id}
                      onClick={() => setSelectedSectorId(s.id)}
                      className={`flex items-center gap-2 p-2.5 rounded-xl border text-[11px] font-bold transition-all text-left cursor-pointer ${
                        isSelected
                          ? `${s.bgLight} ${s.textColor} ${s.borderColor} ring-1 ring-offset-1 ring-${s.color}-200`
                          : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                      }`}
                    >
                      <span className={`p-1.5 rounded-lg ${isSelected ? "bg-white" : "bg-slate-100"} shrink-0`}>
                        {React.createElement(s.icon, { className: "w-3.5 h-3.5" })}
                      </span>
                      <span className="truncate">{s.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Right Col: Detailed Sector Breakdown (7 cols) */}
            <div className="lg:col-span-7 space-y-6">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeSector.id}
                  initial={{ opacity: 0, x: 15 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -15 }}
                  transition={{ duration: 0.2 }}
                  className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-xs space-y-6"
                >
                  {/* Sector Header */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-5">
                    <div className="flex items-center gap-4">
                      <div className={`p-4 rounded-2xl ${activeSector.bgLight} ${activeSector.textColor} border ${activeSector.borderColor}`}>
                        {React.createElement(activeSector.icon, { className: "w-7 h-7" })}
                      </div>
                      <div>
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${activeSector.bgLight} ${activeSector.textColor} border ${activeSector.borderColor}`}>
                          Task Focus: {activeSector.focus}
                        </span>
                        <h3 className="text-xl font-bold text-slate-900 mt-1">{activeSector.name}</h3>
                      </div>
                    </div>
                  </div>

                  {/* General Description */}
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Sector Overview</h4>
                    <p className="text-sm text-slate-600 leading-relaxed font-medium">
                      {activeSector.description}
                    </p>
                  </div>

                  {/* Tanzanian Context */}
                  <div className="p-4 bg-slate-50 border border-slate-150 rounded-2xl">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <MapPin className="w-4 h-4 text-slate-400" /> Reality in Tanzania
                    </h4>
                    <p className="text-xs text-slate-600 leading-relaxed font-semibold">
                      {activeSector.tanzanianContext}
                    </p>
                  </div>

                  {/* Key Tasks & What you'll do */}
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5">Example Tasks & Responsibilities</h4>
                    <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {activeSector.keyTasks.map((task, idx) => (
                        <li key={idx} className="p-3 bg-white border border-slate-100 shadow-xs rounded-xl flex gap-2">
                          <span className={`text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${activeSector.bgLight} ${activeSector.textColor}`}>
                            {idx + 1}
                          </span>
                          <span className="text-[11px] text-slate-600 leading-normal font-semibold">
                            {task}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Alignment Section */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 pt-2">
                    {/* Ideal Streams */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Ideal A-Level Streams</h4>
                      <div className="flex flex-wrap gap-1.5">
                        {activeSector.streams.map((stream) => (
                          <span 
                            key={stream}
                            className={`px-3 py-1.5 rounded-xl text-xs font-bold border ${activeSector.bgLight} ${activeSector.textColor} ${activeSector.borderColor}`}
                          >
                            {stream} Stream
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Careers */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Popular Careers</h4>
                      <div className="flex flex-wrap gap-1.5">
                        {activeSector.professions.map((prof) => (
                          <span 
                            key={prof}
                            className="bg-slate-100 text-slate-600 border border-slate-200 px-3 py-1.5 rounded-xl text-xs font-bold"
                          >
                            {prof}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Recommended Degrees from TCU Catalog */}
                  <div className="border-t border-slate-100 pt-5 space-y-3">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <GraduationCap className="w-4 h-4 text-slate-400" /> Recommended TCU Degree Programs
                    </h4>
                    {matchingCourses.length > 0 ? (
                      <div className="space-y-2">
                        {matchingCourses.map((course) => (
                          <div 
                            key={course.id}
                            className="p-3.5 bg-white border border-slate-200 hover:border-slate-300 rounded-xl flex items-center justify-between gap-4 transition-all"
                          >
                            <div className="min-w-0">
                              <p className="text-xs font-bold text-slate-900 truncate">{course.name}</p>
                              <p className="text-[10px] text-slate-400 font-bold mt-1">
                                Duration: {course.durationYears} Years • Combinations: {course.eligibleCombinations.join(", ")}
                              </p>
                            </div>
                            <span className="text-[10px] font-bold text-slate-400 shrink-0 bg-slate-50 border border-slate-150 px-2.5 py-1 rounded-lg">
                              {course.code}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-400 italic">No exact degrees matching the filters, explore details in the main Course Explorer.</p>
                    )}
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="quiz-view"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="max-w-3xl mx-auto"
          >
            {/* The Career Compass Assessment Container */}
            <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-xs space-y-6">
              {!quizFinished ? (
                <>
                  {/* Quiz Instructions */}
                  <div className="border-b border-slate-100 pb-5 text-center">
                    <h3 className="text-lg font-bold text-slate-900 flex items-center justify-center gap-2">
                      <Compass className="w-5 h-5 text-indigo-600" /> Career Compass Quiz
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 max-w-lg mx-auto leading-relaxed">
                      Evaluate how you feel about the following activities. Your preferences will plot a dynamic point on the World-of-Work Map to match your personality!
                    </p>
                  </div>

                  {/* List of Questions */}
                  <div className="space-y-6">
                    {QUIZ_QUESTIONS.map((q, idx) => {
                      const selectedVal = answers[q.id] || 0;
                      return (
                        <div key={q.id} className="p-4 sm:p-5 bg-slate-50/50 border border-slate-200/60 rounded-2xl space-y-3.5">
                          <div className="flex items-start gap-3">
                            <span className="bg-indigo-50 border border-indigo-100/50 text-indigo-700 text-xs font-bold w-6 h-6 rounded-lg flex items-center justify-center shrink-0 mt-0.5">
                              {idx + 1}
                            </span>
                            <p className="text-xs sm:text-sm text-slate-800 font-bold leading-normal">
                              {q.text}
                            </p>
                          </div>

                          {/* Likert Scale */}
                          <div className="grid grid-cols-5 gap-1.5 sm:gap-2 pt-1">
                            {[
                              { label: "Dislike Strongly", val: 1 },
                              { label: "Dislike", val: 2 },
                              { label: "Neutral", val: 3 },
                              { label: "Like", val: 4 },
                              { label: "Like Strongly", val: 5 }
                            ].map((option) => (
                              <button
                                key={option.val}
                                type="button"
                                onClick={() => handleAnswerSelect(q.id, option.val)}
                                className={`py-2 px-1 text-[9px] sm:text-[10px] font-bold rounded-xl border text-center transition-all cursor-pointer flex flex-col items-center justify-center min-h-[46px] ${
                                  selectedVal === option.val
                                    ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                                    : "bg-white text-slate-500 border-slate-200 hover:bg-slate-100/60"
                                }`}
                              >
                                <span>{option.label}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Submit Button */}
                  <div className="pt-4 flex justify-end border-t border-slate-100">
                    <button
                      type="button"
                      disabled={!isQuizComplete}
                      onClick={calculateQuizResults}
                      className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-100 disabled:text-slate-400 text-white font-bold text-xs py-3 px-6 rounded-xl transition-all shadow-sm cursor-pointer"
                    >
                      Analyze My Career Compass <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </>
              ) : (
                /* Results screen */
                <div className="space-y-6">
                  {/* Results Header */}
                  <div className="text-center space-y-2 border-b border-slate-100 pb-5">
                    <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100 uppercase tracking-wider">
                      Assessment Complete
                    </span>
                    <h3 className="text-xl font-bold text-slate-900 mt-2">Your Career Compass Results</h3>
                    <p className="text-xs text-slate-500 max-w-md mx-auto">
                      Based on your choices, we have plotted your preferences on the task-coordinate system.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                    {/* Visual Coordinate Compass Plot */}
                    <div className="bg-slate-50 border border-slate-150 p-6 rounded-2xl flex flex-col items-center">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 text-center">
                        Task Coordinate Plot
                      </h4>

                      <div className="relative w-60 h-60 border border-slate-300 rounded-full bg-white flex items-center justify-center overflow-hidden shadow-inner">
                        {/* Grid axes */}
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-full h-[1px] bg-slate-200"></div>
                        </div>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="h-full w-[1px] bg-slate-200"></div>
                        </div>

                        {/* Compass labels inside coordinate */}
                        <span className="absolute top-2 text-[8px] font-bold text-slate-400 uppercase tracking-widest">Data (+Y)</span>
                        <span className="absolute bottom-2 text-[8px] font-bold text-slate-400 uppercase tracking-widest">Ideas (-Y)</span>
                        <span className="absolute right-2 text-[8px] font-bold text-slate-400 uppercase tracking-widest">Things (+X)</span>
                        <span className="absolute left-2 text-[8px] font-bold text-slate-400 uppercase tracking-widest">People (-X)</span>

                        {/* Radial circles representing strengths */}
                        <div className="absolute w-44 h-44 border border-dashed border-slate-150 rounded-full pointer-events-none"></div>
                        <div className="absolute w-24 h-24 border border-dashed border-slate-150 rounded-full pointer-events-none"></div>

                        {/* User Coordinates Glowing Cursor */}
                        <motion.div 
                          className="absolute w-5 h-5 bg-indigo-600 rounded-full border-2 border-white shadow-md flex items-center justify-center"
                          style={{
                            // Map coordinate score values (-10 to 10) to CSS percentages from center
                            // X maps to left, Y maps to bottom (inverse top)
                            left: `calc(50% + ${Math.max(-45, Math.min(45, (calculatedCoordinates.x / 10) * 45))}% - 10px)`,
                            top: `calc(50% - ${Math.max(-45, Math.min(45, (calculatedCoordinates.y / 10) * 45))}% - 10px)`
                          }}
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ type: "spring", delay: 0.3 }}
                        >
                          <span className="absolute w-full h-full bg-indigo-600 rounded-full animate-ping opacity-35"></span>
                        </motion.div>
                      </div>

                      <div className="mt-4 text-center">
                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Coordinates</p>
                        <p className="text-xs font-mono font-bold text-slate-700">
                          Things vs People (X): {calculatedCoordinates.x.toFixed(1)} | Data vs Ideas (Y): {calculatedCoordinates.y.toFixed(1)}
                        </p>
                      </div>
                    </div>

                    {/* Recommendation Card */}
                    {suggestedSector && (
                      <div className="space-y-4">
                        <div className="p-4 bg-indigo-50 border border-indigo-150/40 rounded-2xl">
                          <h4 className="text-[10px] font-bold text-indigo-700 uppercase tracking-wider mb-1 flex items-center gap-1">
                            <Award className="w-3.5 h-3.5" /> Best Match Sector
                          </h4>
                          <h3 className="text-lg font-bold text-indigo-900">{suggestedSector.name}</h3>
                          <p className="text-xs text-indigo-700/80 mt-1 font-semibold leading-relaxed">
                            {suggestedSector.description}
                          </p>
                        </div>

                        <div className="space-y-2">
                          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Ideal Careers For You</p>
                          <div className="flex flex-wrap gap-1.5">
                            {suggestedSector.professions.map((prof) => (
                              <span key={prof} className="bg-slate-100 text-slate-600 border border-slate-200 px-3 py-1.5 rounded-xl text-xs font-bold">
                                {prof}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div className="space-y-2">
                          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">A-Level Combinations Recommended</p>
                          <div className="flex flex-wrap gap-1.5">
                            {suggestedSector.streams.map((stream) => (
                              <span key={stream} className="bg-indigo-50 border border-indigo-150 text-indigo-700 px-3 py-1.5 rounded-xl text-xs font-bold">
                                {stream} Stream
                              </span>
                            ))}
                          </div>
                        </div>

                        <div className="pt-2 flex gap-3">
                          <button
                            type="button"
                            onClick={() => {
                              setActiveSubTab("explorer");
                              setSelectedSectorId(suggestedSector.id);
                            }}
                            className="flex-1 bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs py-3 rounded-xl transition-all text-center cursor-pointer flex items-center justify-center gap-1.5"
                          >
                            Explore Mapped Degrees
                          </button>
                          <button
                            type="button"
                            onClick={handleResetQuiz}
                            className="bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs px-4 rounded-xl transition-all cursor-pointer flex items-center justify-center"
                          >
                            <RotateCcw className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
