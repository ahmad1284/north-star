# Inputs & References (raw capture)

> Elaboration-phase collection. Verbatim log of inputs provided by Ahmad. No design decisions here yet — this is source material only.

## Files in `inputs/`
- `letter-to-form-6-graduates.txt` — Ahmad Sadri's letter to Form 6 graduates (Swahili). Input #1.

## Pending file uploads
- **TCU undergraduate handbook** — PDF (not yet uploaded). Source page: https://tcu.go.tz/services/admissions-coordination-and-database-management/admission-guidebooks/undergraduate
- **"World of work"** — image (**still not uploaded**). Link: https://davetgc.com/Worldwork.htm (site: https://davetgc.com/)
  - Interim: `web/dunia-ya-kazi.html` renders the map as inline SVG using ACT's own
    structure fetched from that page — both axes as documented opposites, the 6 clusters,
    all 26 job families under their real A–Z names, with Swahili glosses added. Drawn
    rather than embedded because the client forbids external requests (test-enforced), the
    labels must be in Swahili, and the original is ACT's copyrighted artwork.
  - If the image is supplied, embed it as a data URI (keeps the no-external-requests rule)
    and decide whether it replaces the SVG or sits above it.

## References & ideas provided
- **careervillage.org** — reference product/site.
- **The letter** — (see `letter-to-form-6-graduates.txt`).
- **80,000 Hours** — but adapted to **local priorities** (Tanzania-specific, not Western defaults).
- **WhatsApp delivery** — idea: a custom LLM accessed via WhatsApp. Rationale: for some students WhatsApp is easier than a website or app. Open question raised: "if there is RAG?" (user notes they don't yet know what RAG is).
- **NECTA gradings for A-levels** — Tanzanian A-level grading system (source data).
- **Constraint: simplify for the end user** — keep the user experience simple regardless of backend complexity.
- **NACTVET** — National Council for Technical and Vocational Education and Training (Tanzania) — vocational/technical pathways, source data.
- **Expert system design** — considering building this AI-*less* (a rules-based expert system) rather than / alongside an LLM. Reference book: *Systems Analysis and Design* — Kendall & Kendall (to confirm).
- **Links provided:**
  - https://davetgc.com/Worldwork.htm — "World of work" resource.
  - https://davetgc.com/ — parent site.
  - https://tcu.go.tz/services/admissions-coordination-and-database-management/admission-guidebooks/undergraduate — TCU undergraduate admission guidebooks (official source).
- **Cal Newport books (career philosophy):**
  - *How to Be a High School Superstar* — idea: add a track on the platform for students **still in school** to become better students (Newport's example of a "B student" who got into Stanford). Expands audience beyond just Form 6 graduates.
  - *So Good They Can't Ignore You* — "career capital / skills over passion" thesis.
- **Dr. Tareq Al-Suwaidan** — talks/ideas on choosing a career; a channel/video where he speaks with university students. To-do: get a summary of his career-choice advice.

## Open questions to revisit (not answered here)
- Delivery channel: WhatsApp vs web app vs mobile app.
- Backend approach: LLM + RAG vs rules-based expert system vs hybrid.
- Which official data sources to ingest (TCU, NECTA, NACTVET).
