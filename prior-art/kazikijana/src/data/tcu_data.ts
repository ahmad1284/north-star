export interface University {
  id: string;
  name: string;
  abbreviation: string;
  location: string;
  description: string;
  established: number;
}

export interface Course {
  id: string;
  name: string;
  code: string;
  universityId: string;
  durationYears: number;
  minimumRequirements: string;
  eligibleCombinations: string[];
  whatToExpect: {
    studying: string;
    graduation: string;
  };
  dayToDay: string;
  marketTrends: {
    demand: "High" | "Medium" | "Moderate";
    averageStartingSalaryTsh: number;
    salaryTrend: string;
    topLocalEmployers: string[];
    keyJobRoles: string[];
  };
}

export interface ALevelCombination {
  code: string;
  name: string;
  subjects: string[];
  description: string;
}

export const UNIVERSITIES: University[] = [
  {
    id: "udsm",
    name: "University of Dar es Salaam",
    abbreviation: "UDSM",
    location: "Dar es Salaam (Mlimani)",
    description: "The oldest and largest public university in Tanzania, renowned for its academic excellence, premium engineering facilities (CoET), and computing sciences (CoICT).",
    established: 1961
  },
  {
    id: "muhas",
    name: "Muhimbili University of Health and Allied Sciences",
    abbreviation: "MUHAS",
    location: "Dar es Salaam (Upanga / Mloganzila)",
    description: "The premier public medical university in Tanzania, specializing in medicine, pharmacy, dentistry, nursing, and medical laboratory sciences.",
    established: 2007
  },
  {
    id: "sua",
    name: "Sokoine University of Agriculture",
    abbreviation: "SUA",
    location: "Morogoro",
    description: "The leading agricultural university in East Africa, focusing on crop science, veterinary medicine, forestry, wildlife management, and agribusiness.",
    established: 1984
  },
  {
    id: "udom",
    name: "University of Dodoma",
    abbreviation: "UDOM",
    location: "Dodoma",
    description: "A modern, massive campus located in the capital city, offering strong programs in ICT, social sciences, earth sciences, and education.",
    established: 2007
  },
  {
    id: "aru",
    name: "Ardhi University",
    abbreviation: "ARU",
    location: "Dar es Salaam",
    description: "A specialized university focusing on land planning, architecture, environmental engineering, quantity surveying, and geospatial sciences.",
    established: 2007
  },
  {
    id: "mzumbe",
    name: "Mzumbe University",
    abbreviation: "MZUMBE",
    location: "Morogoro (Main) & Dar es Salaam",
    description: "Famous for producing top administrators, judicial professionals, and corporate leaders. Specializes in Law, Public Administration, and Business.",
    established: 2001
  },
  {
    id: "must",
    name: "Mbeya University of Science and Technology",
    abbreviation: "MUST",
    location: "Mbeya",
    description: "A leading public university in the southern highlands, preparing highly skilled engineering and technology graduates for industrial development.",
    established: 2012
  }
];

export const COMBINATIONS: ALevelCombination[] = [
  {
    code: "PCM",
    name: "Physics, Chemistry, Mathematics",
    subjects: ["Physics", "Chemistry", "Advanced Mathematics"],
    description: "A highly prestigious combination opening doors to premium engineering courses, computer science, software engineering, and architecture."
  },
  {
    code: "PCB",
    name: "Physics, Chemistry, Biology",
    subjects: ["Physics", "Chemistry", "Biology"],
    description: "The primary health sciences pipeline. Essential for students aiming to study Doctor of Medicine, Pharmacy, Dentistry, or Biotechnology."
  },
  {
    code: "CBG",
    name: "Chemistry, Biology, Geography",
    subjects: ["Chemistry", "Biology", "Geography"],
    description: "A versatile science combination leading to environmental sciences, general agriculture, nursing, laboratory sciences, and geology."
  },
  {
    code: "CBA",
    name: "Chemistry, Biology, Agriculture",
    subjects: ["Chemistry", "Biology", "Agriculture"],
    description: "A specialized applied sciences combination that is highly suited for agricultural engineering, agronomy, and animal science pathways at SUA."
  },
  {
    code: "EGM",
    name: "Economics, Geography, Mathematics",
    subjects: ["Economics", "Geography", "Advanced Mathematics"],
    description: "Bridges sciences and commerce. Prepares students for actuarial sciences, economics, accounting, finance, urban planning, and computer science."
  },
  {
    code: "ECA",
    name: "Economics, Commerce, Accountancy",
    subjects: ["Economics", "Commerce", "Accountancy"],
    description: "The elite business and finance stream. Perfect for Bachelor of Commerce, banking, finance, audit, taxation, and business administration."
  },
  {
    code: "HGE",
    name: "History, Geography, Economics",
    subjects: ["History", "Geography", "Economics"],
    description: "A solid arts and commercial blend. Ideal for courses in economics, development studies, law, regional planning, and tourism management."
  },
  {
    code: "HKL",
    name: "History, Kiswahili, Language (English)",
    subjects: ["History", "Kiswahili", "English Language"],
    description: "The humanities foundation. Opens pathways to Bachelor of Laws, education, public administration, linguistics, media, and foreign relations."
  },
  {
    code: "HGK",
    name: "History, Geography, Kiswahili",
    subjects: ["History", "Geography", "Kiswahili"],
    description: "Arts stream suited for secondary education, Kiswahili literature, public relations, cultural studies, and community development."
  },
  {
    code: "HGL",
    name: "History, Geography, Language (English)",
    subjects: ["History", "Geography", "English Language"],
    description: "Humanities combination highly favored for law, international relations, mass communication, sociology, and social work."
  },
  {
    code: "PGM",
    name: "Physics, Geography, Mathematics",
    subjects: ["Physics", "Geography", "Advanced Mathematics"],
    description: "Geospatial and earth science focused. Prepares students for meteorology, civil engineering, land surveying, and geomatics."
  }
];

export const COURSES: Course[] = [
  {
    id: "udsm-cs",
    name: "Bachelor of Science in Computer Science",
    code: "UD001",
    universityId: "udsm",
    durationYears: 3,
    minimumRequirements: "Two principal passes in Advanced Mathematics and Physics at A-Level with a minimum of 4.0 cut-off points.",
    eligibleCombinations: ["PCM", "PGM", "EGM"],
    whatToExpect: {
      studying: "You will spend long hours in computer laboratories at CoICT (Kijitonyama). Expect theoretical mathematics (discrete math, calculus) in the first year, transitioning into web development, database design, operating systems, and computer networks. Practical training (PT) in Tanzanian tech firms is required during the second-year recess.",
      graduation: "The Tanzanian tech space is growing rapidly. While jobs are plentiful, hands-on skills (portfolios on GitHub) matter more than your GPA. You can work as a developer, IT administrator, or build your own startup. Many graduates find work in Dar es Salaam, though remote international freelancing is becoming popular."
    },
    dayToDay: "Writing and reviewing code, debugging production databases, designing API endpoints, meeting with business stakeholders to understand software requirements, and configuring server firewalls.",
    marketTrends: {
      demand: "High",
      averageStartingSalaryTsh: 1200000,
      salaryTrend: "Rising steadily due to corporate digitization. Senior engineers in banks can exceed 4,500,000 TSh.",
      topLocalEmployers: ["Vodacom Tanzania", "CRDB Bank", "NMB Bank", "Tigo", "Airtel", "Selcom", "Maxcom Africa", "Startups"],
      keyJobRoles: ["Software Developer", "Database Administrator", "IT Support Engineer", "Network Engineer", "Systems Analyst"]
    }
  },
  {
    id: "udsm-se",
    name: "Bachelor of Science in Software Engineering",
    code: "UD002",
    universityId: "udsm",
    durationYears: 4,
    minimumRequirements: "Two principal passes in Advanced Mathematics and Physics with grade 'C' or higher at A-Level.",
    eligibleCombinations: ["PCM", "PGM"],
    whatToExpect: {
      studying: "A rigorous 4-year curriculum that delves deeper into software design patterns, project management, software testing, and systems architecture. Includes a comprehensive 4th-year final project where you build a real-world enterprise system.",
      graduation: "Software engineering graduates are highly sought after by banks, fintechs, and consulting firms. The extra year provides deep engineering frameworks making you highly competitive for corporate technical lead positions."
    },
    dayToDay: "Architecting large software systems, establishing CI/CD deployment pipelines, code quality reviews, writing automated testing scripts, and mentoring junior programmers.",
    marketTrends: {
      demand: "High",
      averageStartingSalaryTsh: 1500000,
      salaryTrend: "Strongest starting salaries in the local tech sector, with rapid promotion cycles.",
      topLocalEmployers: ["NMB Bank", "CRDB Bank", "Halopesa", "Selcom", "PwC Tanzania", "E&Y Tanzania", "Government e-GA"],
      keyJobRoles: ["Software Architect", "Full-Stack Engineer", "DevOps Engineer", "QA Automation Engineer"]
    }
  },
  {
    id: "muhas-md",
    name: "Doctor of Medicine (MD)",
    code: "MU001",
    universityId: "muhas",
    durationYears: 5,
    minimumRequirements: "Three principal passes in Chemistry, Biology, and Physics with a minimum of 6.0 points (C in Chemistry, C in Biology, D in Physics).",
    eligibleCombinations: ["PCB"],
    whatToExpect: {
      studying: "An incredibly demanding 5-year journey. First two years are pre-clinical (biochemistry, anatomy dissections, physiology) with heavy memorization. Years 3 to 5 are clinical rotations at Muhimbili National Hospital or Mloganzila. You will experience 24-hour shifts, emergency room duties, and intensive bedside teaching.",
      graduation: "After graduating, you MUST undergo a mandatory 1-year clinical internship at a government-approved regional hospital to get licensed by the Medical Council of Tanzania (MCT). While employment by the government is stable, initial salaries are standardized."
    },
    dayToDay: "Rounding on admitted patients, diagnosing complex conditions, prescribing medications, performing minor surgeries, attending to maternal emergencies, and writing comprehensive case histories.",
    marketTrends: {
      demand: "High",
      averageStartingSalaryTsh: 1600000,
      salaryTrend: "Standardized civil service scale for public facilities. High earnings potential in premium private hospitals (Aga Khan, Regency) or medical NGOs.",
      topLocalEmployers: ["Ministry of Health", "Muhimbili National Hospital", "Aga Khan Hospital", "KCMC Hospital", "Bugando Medical Centre"],
      keyJobRoles: ["Medical Doctor", "General Practitioner", "Medical Officer of Health", "Clinical Researcher"]
    }
  },
  {
    id: "muhas-pharm",
    name: "Bachelor of Pharmacy (BPharm)",
    code: "MU002",
    universityId: "muhas",
    durationYears: 4,
    minimumRequirements: "Two principal passes in Chemistry and Biology at A-Level with a minimum of 4.5 cut-off points.",
    eligibleCombinations: ["PCB", "CBG"],
    whatToExpect: {
      studying: "Expect heavy chemistry (organic, analytical, medicinal) and pharmacology. You will study how drugs interact with the human body, drug formulations in laboratories, and toxicology. Practical assignments involve apothecary labs and community pharmacy rotations.",
      graduation: "Pharmacy has excellent market liquidity in Tanzania. Graduates work in pharmaceutical manufacturing, clinical pharmacy in major hospitals, regulatory bodies (TMDA), wholesale drug distribution, or open private pharmacy shops (Duara/Duka la Dawa)."
    },
    dayToDay: "Reviewing physician prescriptions, compounding medications, counseling patients on dosage and side effects, managing inventory, and quality checking pharmaceutical imports.",
    marketTrends: {
      demand: "High",
      averageStartingSalaryTsh: 1200000,
      salaryTrend: "Stable, driven by local healthcare expansion and private community pharmacy entrepreneurship.",
      topLocalEmployers: ["Tanzania Medicines and Medical Devices Authority (TMDA)", "Medical Stores Department (MSD)", "Keko Pharmaceuticals", "Aga Khan Health Services", "Private Pharmacies"],
      keyJobRoles: ["Clinical Pharmacist", "Regulatory Affairs Officer", "Medical Representative", "Pharmacy Manager", "Quality Assurance Chemist"]
    }
  },
  {
    id: "sua-agri",
    name: "Bachelor of Science in Agriculture General",
    code: "SU001",
    universityId: "sua",
    durationYears: 3,
    minimumRequirements: "Two principal passes in Biology and Chemistry, or Biology and Agriculture at A-Level.",
    eligibleCombinations: ["CBG", "CBA", "PCB"],
    whatToExpect: {
      studying: "Morogoro is your home. You will balance classroom lectures with muddy fieldwork. You will study soil physics, entomology (pest control), animal husbandry, crop pathology, and agricultural economics. Field training in agricultural communities is highly practical and physical.",
      graduation: "Tanzania's economy relies heavily on agriculture (Kilimo Kwanza). While government extensions are available, the highest financial success comes from private commercial farming, consulting, international NGOs, or starting an agribusiness processing value-add crops."
    },
    dayToDay: "Testing soil samples, advising smallholder farmers on fertilizer usage and irrigation, designing crop spray schedules, writing developmental grant proposals, and analyzing commodity crop market prices.",
    marketTrends: {
      demand: "High",
      averageStartingSalaryTsh: 800000,
      salaryTrend: "Moderate starting salaries in NGO/Government sector, but unlimited business potential in private commercial farming.",
      topLocalEmployers: ["Ministry of Agriculture", "FAO Tanzania", "Tanzania Agricultural Research Institute (TARI)", "Export Trading Group (ETG)", "Agribusiness Startups", "USAID programs"],
      keyJobRoles: ["Agricultural Extension Officer", "Farm Manager", "Agronomist", "Agribusiness Consultant", "Agricultural Researcher"]
    }
  },
  {
    id: "sua-vet",
    name: "Bachelor of Veterinary Medicine (BVM)",
    code: "SU002",
    universityId: "sua",
    durationYears: 5,
    minimumRequirements: "Two principal passes in Biology and Chemistry with a principal pass in Physics or Geography at A-Level.",
    eligibleCombinations: ["PCB", "CBG"],
    whatToExpect: {
      studying: "An intensive 5-year science course. You will study animal anatomy, pathology, pharmacology, and surgery. You will work with farm livestock (cattle, goats) and domestic animals. Clinical rotations require handling live animal emergencies and farm visits around Morogoro.",
      graduation: "Very high placement rates. Tanzania is a leading livestock keeper in Africa. You can work as a government veterinary inspector, in livestock NGOs, dairy/poultry corporations, or establish a lucrative private veterinary clinic."
    },
    dayToDay: "Diagnosing and treating sick animals, performing veterinary surgeries, administering herd vaccinations, inspecting abattoirs for meat safety, and advising dairy farms on milk hygiene.",
    marketTrends: {
      demand: "High",
      averageStartingSalaryTsh: 1300000,
      salaryTrend: "Strong, supported by the growing commercial poultry and dairy demand in urban centres.",
      topLocalEmployers: ["Ministry of Livestock and Fisheries", "Tanzania Veterinary Laboratory Agency (TVLA)", "Asas Dairies", "Brookside Dairy", "National Parks (TANAPA)", "Private Veterinary Clinics"],
      keyJobRoles: ["Veterinary Doctor", "Livestock Consultant", "Veterinary Surgeon", "Public Health Inspector"]
    }
  },
  {
    id: "aru-arch",
    name: "Bachelor of Architecture",
    code: "AR001",
    universityId: "aru",
    durationYears: 5,
    minimumRequirements: "Two principal passes in Advanced Mathematics and Physics or Chemistry or Geography, with a total of 4.5 points.",
    eligibleCombinations: ["PCM", "PGM", "EGM"],
    whatToExpect: {
      studying: "Expect sleepless nights in the design studio. You will learn architectural drawing, CAD modeling, structural design, and building materials. Core of the evaluation is the 'Studio Crit', where you present your design concepts to a panel of critical professors.",
      graduation: "Requires 5 years of study plus 2 years of structured mentorship in a registered architectural firm to qualify for the Board of Architects and Quantity Surveyors (AQRB) licensing exam. Lucrative in the private real estate sector in major cities."
    },
    dayToDay: "Drawing building blueprints, creating 3D digital walkthroughs, collaborating with structural engineers, reviewing municipal building codes, and presenting design proposals to real estate developers.",
    marketTrends: {
      demand: "Medium",
      averageStartingSalaryTsh: 1100000,
      salaryTrend: "Cyclical. Strongly tied to Dar es Salaam's high-rise construction and real estate booms.",
      topLocalEmployers: ["NHC (National Housing Corporation)", "Ministry of Lands", "Private Architectural Firms", "Real Estate Development Firms"],
      keyJobRoles: ["Architect", "Urban Designer", "Design Consultant", "Project Manager"]
    }
  },
  {
    id: "mzumbe-law",
    name: "Bachelor of Laws (LLB)",
    code: "MZ001",
    universityId: "mzumbe",
    durationYears: 4,
    minimumRequirements: "Two principal passes in any subjects at A-Level with a minimum of 4.0 cut-off points, plus a pass in English at O-Level.",
    eligibleCombinations: ["HKL", "HGL", "HGE", "HGK"],
    whatToExpect: {
      studying: "Mzumbe's law school has a fierce academic reputation. Expect to read massive amounts of statutes, legal cases, and international treaties. You will participate in intense Moot Court debates, write briefs, and study constitutional, criminal, land, and corporate laws.",
      graduation: "Graduating is just the first step. To practice in Tanzania, you MUST attend the Law School of Tanzania (LST) in Dar es Salaam for 1 year to pass the bar exam and become an Advocate. Competition is intense but successful lawyers command high fees."
    },
    dayToDay: "Conducting legal research, drafting litigation papers, counseling clients on commercial disputes, representing corporate clients in arbitration, and appearing before magistrates or high court judges.",
    marketTrends: {
      demand: "Medium",
      averageStartingSalaryTsh: 900000,
      salaryTrend: "Extremely polarized; low in public service but very high in corporate finance/mining legal departments in Dar es Salaam.",
      topLocalEmployers: ["Law Firms (ALN Tanzania, Rex Advocates, IMMMA)", "Government Judiciary", "Corporate Banks", "Mining Corporations", "NGOs (LHRC)"],
      keyJobRoles: ["Legal Officer", "Corporate Legal Counsel", "Advocate of the High Court", "State Attorney", "Magistrate"]
    }
  },
  {
    id: "udsm-fin",
    name: "Bachelor of Commerce in Finance",
    code: "UD003",
    universityId: "udsm",
    durationYears: 3,
    minimumRequirements: "Two principal passes at A-Level in commercial or science combinations, including Advanced Mathematics or Economics with 4.0 points.",
    eligibleCombinations: ["ECA", "EGM", "HGE"],
    whatToExpect: {
      studying: "Studied at the prestigious UDSM Business School (UDBS). Focuses on financial markets, corporate investment, quantitative finance, microeconomics, and taxation. Students are strongly advised to start studying for the Professional CPA (T) or CFA exams concurrently.",
      graduation: "Highly competitive. Dar es Salaam is the financial hub of Tanzania. Graduates find roles in commercial banking, corporate treasury, investment advisory, and public audit offices. Holding a CPA or CFA certification speeds up growth dramatically."
    },
    dayToDay: "Analyzing corporate financial statements, managing liquid assets, preparing cash-flow forecasts, writing investment memos, calculating tax liabilities, and advising on capital budgeting.",
    marketTrends: {
      demand: "High",
      averageStartingSalaryTsh: 1000000,
      salaryTrend: "Very strong for candidates with professional credentials (CPA/CFA) and good quantitative skills.",
      topLocalEmployers: ["NMB Bank", "CRDB Bank", "PwC", "EY", "Deloitte", "KPMG", "National Audit Office (NAOT)", "Social Security Funds (NSSF, PSSSF)"],
      keyJobRoles: ["Financial Analyst", "Credit Officer", "Internal Auditor", "Investment Banker", "Tax Consultant"]
    }
  }
];
