import express from "express";
import path from "path";
import fs from "fs";
import dotenv from "dotenv";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json());

// Initialize Gemini SDK with telemetry header
const apiKey = process.env.GEMINI_API_KEY;
const ai = new GoogleGenAI({
  apiKey: apiKey || "MOCK_KEY",
  httpOptions: {
    headers: {
      "User-Agent": "aistudio-build",
    },
  },
});

// In-memory store for Q&A forum
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

const initialQuestions: Question[] = [
  {
    id: "q-1",
    authorName: "Khalfan M.",
    combination: "PCM",
    title: "How hard is the transition from PCM in high school to Computer Science at UDSM?",
    content: "I did PCM at Kibaha Secondary School and got Division 1. I am planning to select Computer Science at UDSM (CoICT) but I've never programmed before. Is it overwhelming? What should I expect in my first semester?",
    createdAt: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
    answers: [
      {
        id: "ans-1",
        authorName: "Erick John",
        authorTitle: "Senior Software Engineer at Selcom | UDSM CoICT Alumnus",
        content: "Karibu sana Mlimani! The transition is definitely a big jump but very manageable. In high school PCM, mathematics is purely abstract paper-and-pencil. In CS, you will start applying logic on day one. First semester has Intro to Programming (usually Java/Python) and Discrete Mathematics. Since you already have a strong mathematical foundation from PCM, you'll find logic and algorithms highly intuitive. Don't worry about having no coding experience; the university starts from scratch. My advice: make sure you join study groups at CoICT, buy a decent laptop, and build personal projects outside the classroom. Best of luck!",
        createdAt: new Date(Date.now() - 36 * 60 * 60 * 1000).toISOString(),
        isMentor: true,
        likes: 12,
      },
      {
        id: "ans-2",
        authorName: "Neema Swai",
        authorTitle: "Systems Analyst at e-GA (Government e-Government Authority)",
        content: "I entered UDSM with PCM as well, with zero programming knowledge. My first two weeks were intimidating because some classmates from tech schools already knew HTML. But by second semester, everything balanced out. PCM teaches you analytical patience. When your code fails (and it will), your math-trained brain will find debugging easier. Keep calm and use the library!",
        createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        isMentor: true,
        likes: 8,
      }
    ]
  },
  {
    id: "q-2",
    authorName: "Zubeda S.",
    combination: "PCB",
    title: "Doctor of Medicine at MUHAS vs Bachelor of Pharmacy. Which one has better local prospects?",
    content: "I scored Division 1 (PCB) and I love medical sciences. But I am confused between choosing MD (5 years) or Pharmacy (4 years). Which path is more flexible and has better job market trends in Tanzania?",
    createdAt: new Date(Date.now() - 72 * 60 * 60 * 1000).toISOString(),
    answers: [
      {
        id: "ans-3",
        authorName: "Dr. Beatrice Temu",
        authorTitle: "Medical Officer at Muhimbili National Hospital | MUHAS Graduate",
        content: "Both are incredible choices, but they fit completely different lifestyles and professional ambitions. Medicine (MD) is a deep clinical calling. You will deal with patients face-to-face, handle intense ward rounds, and experience overnight calls at Mloganzila. It takes 5 years of study plus a tough 1-year internship to get your MCT license. Job security in public hospitals is guaranteed, but salary growth can be slow unless you specialize. Pharmacy (BPharm) is highly flexible. It is 4 years and doesn't involve clinical shifts. You can work in industrial drug manufacture, pharmaceutical regulation at TMDA, procurement at MSD, or start a private retail pharmacy enterprise. If you want clinical prestige and direct patient care, pick MD. If you want entrepreneurial flexibility and structured hours, choose Pharmacy.",
        createdAt: new Date(Date.now() - 60 * 60 * 60 * 1000).toISOString(),
        isMentor: true,
        likes: 15,
      }
    ]
  },
  {
    id: "q-3",
    authorName: "Joseph J.",
    combination: "CBG",
    title: "What are the opportunities for CBG students who choose Sokoine University (SUA)?",
    content: "My combinations are Chemistry, Biology, and Geography. Most people tell me only medicine is good, but I didn't get PCB. What interesting environmental or agricultural courses can I study at SUA and make a strong impact?",
    createdAt: new Date(Date.now() - 96 * 60 * 60 * 1000).toISOString(),
    answers: [
      {
        id: "ans-4",
        authorName: "Josephat Mtangi",
        authorTitle: "Agribusiness Consultant at ETG Tanzania | SUA Alumnus",
        content: "Don't let anyone discourage you! CBG is a goldmine for agricultural and environmental programs. At SUA, you can choose Bachelor of Science in Environmental Sciences and Management, Agronomy, or Biotechnology. Tanzania's economy is agricultural, and the 'Kilimo Kwanza' initiative has opened huge paths in modern value chains. Major development organizations (FAO, USAID, TARI) are constantly looking for researchers to study climate-resilient crops and soil health. If you choose Environmental Sciences, mining firms and regional councils will hire you for Environmental Impact Assessments (EIAs). There is life beyond MD!",
        createdAt: new Date(Date.now() - 80 * 60 * 60 * 1000).toISOString(),
        isMentor: true,
        likes: 19,
      }
    ]
  }
];

let questionsStore: Question[] = [...initialQuestions];

// API: Get all questions
app.get("/api/forum/questions", (req, res) => {
  res.json(questionsStore);
});

// API: Get the real TCU catalog data
app.get("/api/courses", (req, res) => {
  try {
    const catalogPath = path.join(process.cwd(), "src", "data", "tcu_catalog.json");
    if (fs.existsSync(catalogPath)) {
      const rawData = fs.readFileSync(catalogPath, "utf-8");
      res.json(JSON.parse(rawData));
    } else {
      res.status(404).json({ error: "TCU Catalog JSON file not found." });
    }
  } catch (err: any) {
    console.error("Error reading TCU Catalog JSON:", err);
    res.status(500).json({ error: "Failed to read TCU Catalog: " + err.message });
  }
});

// API: Post a question and get simulated mentor answers
app.post("/api/forum/questions", async (req, res) => {
  const { authorName, combination, title, content } = req.body;
  if (!title || !content) {
    return res.status(400).json({ error: "Title and content are required." });
  }

  const newQuestion: Question = {
    id: `q-${Date.now()}`,
    authorName: authorName || "Form 6 Graduate",
    combination: combination || "General",
    title,
    content,
    createdAt: new Date().toISOString(),
    answers: [],
  };

  questionsStore.unshift(newQuestion);

  // If API key is available, simulate a mentor responding in real-time
  if (apiKey) {
    try {
      const response = await ai.models.generateContent({
        model: "gemini-3.5-flash",
        contents: `A Tanzanian Form 6 graduate student (${newQuestion.authorName}) with A-Level combination ${newQuestion.combination} has asked a career question on our portal CareerVillage TZ.
Question Title: ${newQuestion.title}
Question Content: ${newQuestion.content}

Act as an encouraging, expert professional mentor or university alumnus from Tanzania who works in the relevant industry.
Provide an inspiring, highly practical, and detailed reply with Tanzanian reference points (e.g. key ministries, specific local organizations/employers, salary ranges, licensing boards like ERB, AQRB, MCT, CPA, Law School of Tanzania).
Write in English, but feel free to start with a friendly greeting like 'Mambo vipi!', 'Habari!', or 'Hongera sana!' to keep it authentic.

Return your response in a clean JSON format matching this schema:
{
  "authorName": "Full Name of simulated mentor",
  "authorTitle": "Realistic job title and organization + university alumnus info (e.g. Software Engineer at Vodacom | UDSM Alumna)",
  "content": "Rich, multi-paragraph, encouraging and constructive advice answering their query"
}`,
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              authorName: { type: Type.STRING },
              authorTitle: { type: Type.STRING },
              content: { type: Type.STRING },
            },
            required: ["authorName", "authorTitle", "content"],
          },
        },
      });

      if (response.text) {
        const generatedData = JSON.parse(response.text.trim());
        const simulatedAnswer: Answer = {
          id: `ans-${Date.now()}`,
          authorName: generatedData.authorName || "Advisor Sama",
          authorTitle: generatedData.authorTitle || "Tanzania Career Advisor",
          content: generatedData.content,
          createdAt: new Date().toISOString(),
          isMentor: true,
          likes: 0,
        };
        newQuestion.answers.push(simulatedAnswer);
      }
    } catch (err) {
      console.error("Failed to generate simulated mentor answer:", err);
      // Fallback response
      newQuestion.answers.push({
        id: `ans-fallback-${Date.now()}`,
        authorName: "System Career Advisor",
        authorTitle: "TCU Career Portal Team",
        content: "Thank you for asking! Our mentoring panel has been notified. In the meantime, you can use our AI Chat Assistant for instant personalized roadmap recommendations.",
        createdAt: new Date().toISOString(),
        isMentor: true,
        likes: 1,
      });
    }
  } else {
    // Local fallback if no key
    newQuestion.answers.push({
      id: `ans-fallback-${Date.now()}`,
      authorName: "Advisor Sama (Local Simulator)",
      authorTitle: "Tanzania Career Guide Mentor",
      content: `Hongera kwa kuuliza swali hili! Direct answer simulation requires configuring your GEMINI_API_KEY. However, as an advisor, I can tell you that choosing a course based on your combination of ${newQuestion.combination} is a major step. Research the minimum requirements on the TCU guide and check local trends carefully. We hope you connect with more physical mentors at your university!`,
      createdAt: new Date().toISOString(),
      isMentor: true,
      likes: 2,
    });
  }

  res.status(201).json(newQuestion);
});

// API: Answer a question as a user/mentor
app.post("/api/forum/questions/:id/answers", (req, res) => {
  const { id } = req.params;
  const { authorName, authorTitle, content, isMentor } = req.body;

  if (!content) {
    return res.status(400).json({ error: "Content is required." });
  }

  const question = questionsStore.find((q) => q.id === id);
  if (!question) {
    return res.status(404).json({ error: "Question not found." });
  }

  const newAnswer: Answer = {
    id: `ans-${Date.now()}`,
    authorName: authorName || "Community Member",
    authorTitle: authorTitle || "Alumni / Student",
    content,
    createdAt: new Date().toISOString(),
    isMentor: !!isMentor,
    likes: 0,
  };

  question.answers.push(newAnswer);
  res.status(201).json(newAnswer);
});

// API: Like an answer
app.post("/api/forum/answers/:id/like", (req, res) => {
  const { id } = req.params;
  let found = false;

  for (const q of questionsStore) {
    const ans = q.answers.find((a) => a.id === id);
    if (ans) {
      ans.likes += 1;
      found = true;
      return res.json(ans);
    }
  }

  if (!found) {
    res.status(404).json({ error: "Answer not found." });
  }
});


// API: AI Chat Career Advisor
app.post("/api/chat", async (req, res) => {
  const { messages, studentProfile } = req.body;

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: "Invalid messages array." });
  }

  const conversation = messages.map((m: any) => ({
    role: m.role === "assistant" ? "model" : "user",
    parts: [{ text: m.content }],
  }));

  // Build context summary from profile to insert in system instructions
  let profileContext = "";
  if (studentProfile) {
    profileContext = `The student's profile context:
- Combination: ${studentProfile.combination || "Not specified"}
- Grades: ${studentProfile.grades ? JSON.stringify(studentProfile.grades) : "Not specified"}
- Strengths: ${studentProfile.strengths || "Not specified"}
- Interests/Wishes: ${studentProfile.interests || "Not specified"}
- Target University: ${studentProfile.targetUniversity || "Undecided"}`;
  }

  const systemInstruction = `You are 'Sama', an empathetic, friendly, and expert Tanzanian Academic & Career Advisor guiding Form 6 (Advanced Level) graduates who are transitioning to university in Tanzania.
Use an encouraging, structured, and warm tone. Sprinkle in occasional polite Swahili phrases where natural (e.g., 'Habari', 'Karibu', 'Hongera', 'Asante') to create a supportive local environment, but write primarily in English so detailed requirements are clear.
Help students match their high school A-Level combinations with official TCU university courses.
Give realistic insights on Tanzanian industry demand, starting salaries (in Tanzanian Shillings TSh), top employers (e.g. Vodacom, Halopesa, CRDB, NMB, Selcom, TANROADS, TARURA, e-GA, Muhimbili, MSD, Aga Khan, ETG, private schools), and what the day-to-day work is like.
${profileContext}

Provide clear, brief, scannable advice. Do not output massive walls of text. Use bullet points and bold headers.`;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: conversation,
      config: {
        systemInstruction,
        temperature: 0.7,
      }
    });

    res.json({ content: response.text || "I was unable to formulate a response. Please try again!" });
  } catch (err: any) {
    console.error("Gemini API Error in /api/chat:", err);
    res.status(500).json({ error: "Failed to query Gemini API: " + err.message });
  }
});

// API: Generate Tailored Roadmap
app.post("/api/roadmap", async (req, res) => {
  const { studentProfile } = req.body;

  if (!studentProfile) {
    return res.status(400).json({ error: "Student profile is required." });
  }

  const prompt = `Develop a detailed academic and professional development roadmap for a Tanzanian Form 6 graduate with the following background:
- High School A-Level Combination: ${studentProfile.combination}
- Grades Obtained: ${JSON.stringify(studentProfile.grades)}
- Student's Strengths: ${studentProfile.strengths}
- Interests & Desired Skills: ${studentProfile.interests}
- Target University choice: ${studentProfile.targetUniversity || "Undecided"}

Provide specific advice matching TCU university directories, local Tanzanian industry regulations (like registering with boards like ERB for engineers, MCT for doctors, CPA for finance, AQRB for architects), and key employers in Tanzania.

Ensure you recommend exactly 3 specific Tanzanian degree options that align with this profile, detailing why they fit, and outline 3 successive academic phases (e.g. Year 1, Year 2, Year 3) and 4 major sequential milestones (from TCU application in 2026 to career placement).`;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        systemInstruction: "You are an advanced academic planning system for Tanzanian higher education. Generate a fully structured academic and professional roadmap based strictly on the JSON schema.",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            summary: { type: Type.STRING, description: "Personalized summary of the roadmap for the student." },
            recommendedTCUCourses: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  universityAbbreviation: { type: Type.STRING, description: "University abbreviation e.g. UDSM, MUHAS, SUA, UDOM, ARU, MZUMBE, MUST" },
                  courseName: { type: Type.STRING, description: "Full degree course name from TCU" },
                  relevanceReason: { type: Type.STRING, description: "Why this course matches their grades, combination, and interests." }
                },
                required: ["universityAbbreviation", "courseName", "relevanceReason"]
              }
            },
            academicPlan: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  phase: { type: Type.STRING, description: "E.g. Year 1: Foundation, Year 2: Specialization, Year 3: Practical Application" },
                  focus: { type: Type.STRING, description: "Primary academic focal point." },
                  skillsToBuild: {
                    type: Type.ARRAY,
                    items: { type: Type.STRING }
                  }
                },
                required: ["phase", "focus", "skillsToBuild"]
              }
            },
            professionalPlan: {
              type: Type.OBJECT,
              properties: {
                certifications: {
                  type: Type.ARRAY,
                  items: { type: Type.STRING },
                  description: "Tanzanian boards (ERB, MCT, AQRB, CPA-T, LST) or standard professional certs."
                },
                internshipTargets: {
                  type: Type.ARRAY,
                  items: { type: Type.STRING },
                  description: "Specific Tanzanian organizations, corporations, ministries, or banks."
                },
                advice: { type: Type.STRING, description: "Practical career advice for entering the local job market." }
              },
              required: ["certifications", "internshipTargets", "advice"]
            },
            milestones: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  title: { type: Type.STRING },
                  timeline: { type: Type.STRING, description: "Expected month/year" },
                  actionItems: {
                    type: Type.ARRAY,
                    items: { type: Type.STRING }
                  }
                },
                required: ["title", "timeline", "actionItems"]
              }
            }
          },
          required: ["summary", "recommendedTCUCourses", "academicPlan", "professionalPlan", "milestones"]
        }
      }
    });

    if (response.text) {
      res.json(JSON.parse(response.text.trim()));
    } else {
      throw new Error("Empty response from AI model.");
    }
  } catch (err: any) {
    console.error("Gemini API Error in /api/roadmap:", err);
    res.status(500).json({ error: "Failed to generate roadmap: " + err.message });
  }
});

// Vite server integration or static file serving
const startServer = async () => {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server is running at http://0.0.0.0:${PORT}`);
  });
};

startServer().catch((err) => {
  console.error("Error starting server:", err);
});
