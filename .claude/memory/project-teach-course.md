---
name: project-teach-course
description: teach/ is a self-paced learning course (Copilot Studio Field Manual) built from research/; how to maintain and extend it
metadata:
  type: project
---

`teach/` is a teach-skill workspace: an 11-lesson interactive HTML course ("Copilot
Studio Field Manual") built from [[project-sharepoint-rag-findings]] and the
`research/` sets, created 2026-07-21. Course A = fundamentals (lessons 0001–0004),
Course B = SharePoint RAG (0005–0010), Course C = capstone from the build review
(0011); `reference/` holds glossary, limits cheat-sheet, decision flowcharts.

**Maintenance rules (non-obvious):**
- Every lesson/reference file is **single-file HTML** — `assets/course.css` and
  `assets/quiz.js` are the source of truth but are **inlined** into each file. A
  style/behavior change means editing assets, then re-inlining into all files.
- Quiz convention: answer options within a question have identical word counts;
  exactly one `data-correct` per question.
- Mission, teaching preferences, and curriculum map live in `teach/MISSION.md` and
  `teach/NOTES.md`; trusted sources + open research gaps in `teach/RESOURCES.md`.
- `teach/learning-records/` intentionally doesn't exist yet — create lazily when
  the user first demonstrates learning (see teach skill's learning-record format).
