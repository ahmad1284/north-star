---
status: pending
depends_on: [unit-03-ranking]
branch: claude/tanzania-career-guidance-murut8
discipline: backend
workflow: ""
ticket: ""
---

# Unit 04: Backend API

## Description
FastAPI app exposing the engine: POST /match (student profile → grouped ranked results),
GET /programmes, GET /subjects + combinations (for clients to build input UIs), GET /health.
Thin transport layer only — all logic stays in the core modules.

## Success Criteria
- [ ] POST /match validates input (unknown subjects/grades → clear 422)
- [ ] Response = grouped ranked JSON with reasons and checklist fields
- [ ] Reference endpoints for subjects/combinations/programmes
- [ ] Runnable locally (uvicorn), demonstrated via curl
- [ ] API tests pass (happy path + validation errors)
