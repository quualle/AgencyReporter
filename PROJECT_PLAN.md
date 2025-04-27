# PROJECT INSTRUCTIONS — MVP AGENTUR‑REPORT (DUE IN 2 WEEKS)

> **Audience:** OpenAI o3 agent in Cursor
> **Repo:** `agentur-report/`
> **Commit prefix for this phase:** `mvp/`

---

## 1 — PURPOSE
Create a *click‑ready* MVP that delivers the key performance & problem metrics for our Polish partner agencies in a form my CEO can grasp in minutes, while laying the groundwork for future XORA integration.

---

## 2 — CONTEXT SNAPSHOT
| Area | Current State |
|------|--------------|
| **Data** | 32+ parametrised SQL queries hitting BigQuery; raw JSON payloads via internal Node/Express API. |
| **Domain** | Senior‑care staffing. 79 current clients; we track agency quality & failure modes. |
| **Analysis Depth** | Need at least Level‑2 metrics (e.g. deployment aborts split <3 d / 3‑7 d / >7 d). Level‑3 (root‑cause via LLM) is *out of scope* for MVP. |
| **Target Stack** | Node/Express API · BigQuery · Looker Studio or lightweight React dashboard · PDF/CSV export. |
| **Future** | XORA MCP, Unstructured Workflow Endpoint, LightRAG, Gemini 2.5 Pro. |

---

## 3 — HIGH‑LEVEL DELIVERABLES (D‑14 ➜ D‑0)
1. **Metric Views** – Three SQL views `vw_abort_t1|t2|t3` + consolidated `vw_abort_all`.
2. **Reporting API** – REST route `GET /v1/reporting/agency/{id}?from=&to=` returns JSON & optional PDF/CSV.
3. **Dashboard** – Minimal Looker or React page listing agencies with traffic‑light KPI tiles & drill‑down table.
4. **CI Checks** – ESLint + Jest for API, dbt‑style tests for SQL views.
5. **Docs** – Swagger/OpenAPI spec, README quick‑start.

> *Stretch:* PoC folder `ingestion/` with `workflow.json` for Unstructured ingest of 50 E‑mails to Chroma.

---

## 4 — ACCEPTANCE CRITERIA
- Dashboard opens with ≤1 s TTFB (cached payload).
- CEO can export full PDF of all agencies ≤2 clicks.
- Metrics include *at least*:
  - Total deployments
  - Abort counts & % (split into the 3 time buckets)
  - Average response time to urgent replacements (hrs)
  - Current active placements
  - Churn rate (rolling 30 d)
- Code passes all lint/tests (`npm run ci`).

---

## 5 — ARCHITECTURE & DIRECTORY LAYOUT
```
agentur-report/
  ├─ api/
  │   ├─ routes/
  │   ├─ controllers/
  │   └─ index.ts
  ├─ sql/
  │   ├─ views/
  │   └─ seeds/
  ├─ dashboard/
  │   ├─ src/
  │   └─ build/
  ├─ ingestion/          # ← stretch goal
  ├─ docs/
  └─ tests/
```

---

## 6 — TASK BOARD (K = Kanban Column)
| ID | Task | Owner | Est h | K |
|----|------|-------|-------|---|
| T‑01 | Create SQL views for abort buckets | o3 AI | 4 | Backlog |
| T‑02 | Build `/v1/reporting/agency/:id` route | o3 AI | 6 | Backlog |
| T‑03 | Write Swagger spec | o3 AI | 2 | Backlog |
| T‑04 | Jest tests for controllers | o3 AI | 3 | Backlog |
| T‑05 | React dashboard scaffold | o3 AI | 5 | Backlog |
| T‑06 | PDF/CSV exporter util | o3 AI | 2 | Backlog |
| T‑07 | Docker compose for local dev | o3 AI | 2 | Backlog |
| T‑08 | README + quick‑start docs | o3 AI | 1 | Backlog |
| T‑09 | PoC `workflow.json` (stretch) | o3 AI | 4 | Backlog |

> **Rule:** After each task, open PR referencing the ID and include `mvp/<task>` branch.

---

## 7 — CODING STANDARDS
- TypeScript strict mode, Node 18.
- Prettier, 2‑space indent.
- Env vars via `.env.sample` → no secrets committed.
- SQL formatted with `sql‑formatter` (`npm run format:sql`).

---

## 8 — TIMELINE & MILESTONES
| Day | Goal |
|-----|------|
| D‑14 (Today) | Project setup, directory scaffold, README stub. |
| D‑10 | SQL views + unit tests done; sample JSON result visible. |
| D‑7  | API endpoint & Swagger live; Postman collection committed. |
| D‑4  | Dashboard MVP (table + KPI tiles) deployable locally. |
| D‑2  | Export to PDF/CSV implemented; end‑to‑end smoke test green. |
| D‑0  | CEO demo; tag `v0.1.0`. |

---

## 9 — COLLAB RULES FOR o3 AGENT
1. Ask clarifying questions **only** via TODO comments if spec gap blocks progress.
2. Prefer small iterative commits over monolith PRs.
3. Keep all hard‑coded IDs or sample data under `sql/seeds/`.
4. When unsure, implement **interfaces** first – e.g. `IRetriever` for future LightRAG.

---

## 10 — FUTURE BACKLOG (POST‑MVP)
- Level‑3 root‑cause analysis using Gemini 2.5 Pro + Unstructured ingest.
- Nightly vector refresh cron via MCP.
- Graph‑augmented retrieval with LightRAG.
- Role‑based access control & SSO.

---

**End of Instructions**

