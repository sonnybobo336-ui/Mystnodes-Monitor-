# NodeForge Dashboard (Crypto Ops) — plan.md

## 1. Objectives
- Deliver a real-time operations dashboard for crypto node/validator-style operations focused on **Mysterium (Mystnodes)** nodes, enriched with **Tailscale** device connectivity and **CoinGecko** price data.
- Provide consolidated views of **status/uptime/host online state**, **earnings summaries** (24h/30d/annualized/lifetime), and **AI insights** (underperformance + estimated revenue loss + rebalancing/yield suggestions) using **Claude Sonnet 4.5** via Emergent.
- Ship an MVP that is stable, fast, and polished (dark crypto-ops UI), with caching to avoid rate limits.

## 2. Implementation Steps

### Phase 1 — Core POC (isolation; must pass before app work)
**Goal:** Prove all external integrations work end-to-end with real credentials/data.

**User stories (POC)**
1. As a user, I want to fetch live BTC/ETH/SOL/MYST prices so I can contextualize my node earnings.
2. As a user, I want to pull Mystnodes node status + earnings for my node keys so I can verify the dashboard is reading real data.
3. As a user, I want to list Tailscale devices and see online/offline/last-seen so I can correlate node health with host connectivity.
4. As a user, I want a single merged “node health snapshot” object so downstream UI can render without extra glue.
5. As a user, I want Claude to generate actionable insights from that snapshot so I can confirm AI output quality early.

**Steps**
1. Websearch (quick) best practices + current endpoints for:
   - CoinGecko simple price endpoint for multi-token + 24h change.
   - Mystnodes/Mysterium node stats & earnings endpoints using `nodekey`.
   - Tailscale API: device listing endpoints, auth header format, pagination.
   - Emergent LLM usage pattern for Claude Sonnet 4.5.
2. Create `/app/backend/poc_integrations.py` that:
   - Fetches CoinGecko prices for `bitcoin,ethereum,solana,mysterium`.
   - Fetches Mystnodes data for the two node keys (status + sessions + earnings where available).
   - Calls Tailscale API to list devices; attempts best-effort match to nodes (by hostname/IP if available; otherwise just include full device list).
   - Calls Emergent Claude Sonnet 4.5 with a structured prompt returning JSON: `{underperformers:[], revenue_loss_estimate_usd, recommendations:[]}`.
   - Prints a final merged JSON blob to stdout and exits non-zero on any integration failure.
3. Run the script locally in the environment; iterate until:
   - All 4 integrations succeed reliably.
   - Response schemas are stable enough to build API models around.

**Exit gate (mandatory)**
- POC returns success and prints merged snapshot with: prices + 2 nodes + tailscale devices + AI JSON.

---

### Phase 2 — V1 App Development (build around proven core)
**User stories (V1 dashboard)**
1. As a user, I want a top price ticker (BTC/ETH/SOL/MYST) with 24h change so I can glance market context.
2. As a user, I want a KPI row (earnings 24h/30d/annualized/lifetime, nodes online, avg uptime) so I can assess operations quickly.
3. As a user, I want a nodes table/cards view showing node status, sessions, earnings, and mapped host online status so I can find issues fast.
4. As a user, I want a 30-day earnings chart/sparkline so I can see trend and volatility.
5. As a user, I want an AI Insights panel with a refresh button so I can get updated underperformance + rebalancing suggestions on demand.

**Backend (FastAPI + Mongo; `/api`)**
1. Add config via env:
   - `TAILSCALE_API_KEY`, `MYST_NODE_KEYS` (comma-separated), (optional) `TAILNET_NAME`.
2. Create integration clients:
   - `services/coingecko.py`, `services/mystnodes.py`, `services/tailscale.py`, `services/ai.py`.
3. Add Mongo caching collections with TTL indexes (30–60s) for:
   - prices, mystnodes snapshot, tailscale devices, ai insights.
4. Implement endpoints:
   - `GET /api/prices`
   - `GET /api/nodes` (merged Mystnodes + best-effort tailscale mapping)
   - `GET /api/earnings/summary` (24h/30d/annualized/lifetime from Mystnodes data)
   - `GET /api/earnings/timeseries?days=30` (if Mystnodes supports; else derive from available history)
   - `POST /api/ai/insights` (optionally accepts latest snapshot; otherwise server refreshes + caches)
   - `POST /api/refresh` (forces refresh ignoring cache)
5. Define Pydantic response models for stable frontend contracts.

**Frontend (React + shadcn/ui + recharts)**
1. Replace placeholder Home with `DashboardPage`.
2. Build layout (dark theme):
   - PriceTicker (chips w/ 24h change)
   - KPIStatsRow
   - NodesTable (status pills, last seen, sessions, earnings)
   - EarningsChart (30d)
   - AIInsightsCard (bullets + loss estimate + refresh)
3. Data fetching:
   - `lib/api.js` axios client with base URL.
   - React hooks: `usePrices`, `useNodes`, `useEarningsSummary`, `useEarningsSeries`, `useAiInsights`.
4. UX states:
   - Skeletons while loading, inline error banners, empty states when APIs return none.
   - Manual refresh buttons for each panel + global refresh.

**Phase 2 test checkpoint**
- Run `testing_agent_v3` for an end-to-end pass: dashboard loads, panels populate, refresh works, error handling visible.

---

### Phase 3 — MVP hardening + quality improvements
**User stories (hardening)**
1. As a user, I want graceful partial-data rendering so one failing API doesn’t blank the whole dashboard.
2. As a user, I want consistent node identity + mapping so I can trust which host corresponds to which node.
3. As a user, I want AI insights to be structured and stable so I can act on them.
4. As a user, I want faster load times via caching so the dashboard feels real-time but doesn’t hit rate limits.
5. As a user, I want a clear audit of “data as of” timestamps so I know freshness.

**Steps**
1. Improve mapping between Mystnodes and Tailscale:
   - Heuristics (hostname/IP matching), optional manual mapping config stored in Mongo.
2. Add “data freshness” timestamps per panel.
3. Add retries/backoff and clearer backend error messages.
4. Tighten AI prompt + JSON schema validation; fall back to safe “no insights” state.
5. Re-run `testing_agent_v3` and fix regressions.

---

### Phase 4+ — Post-MVP (only as requested)
- Optional auth, multi-tailnet support, alerting (email/discord), scheduled refresh, historical storage, multi-chain expansion.

## 3. Next Actions
1. Implement and run **Phase 1 POC script** with the provided keys (store as env vars; do not hardcode in git).
2. Lock down the exact response shapes from Mystnodes + Tailscale and finalize Pydantic models.
3. Build Phase 2 backend endpoints + frontend dashboard in one integrated pass.
4. Run `testing_agent_v3`, fix issues, then proceed to Phase 3 hardening.

## 4. Success Criteria
- Phase 1: POC succeeds with real calls to CoinGecko + Mystnodes + Tailscale + Claude and outputs merged JSON.
- Phase 2: Dashboard renders live prices, node list, earnings summary/chart, and AI insights; refresh works; UI handles loading/error states.
- Phase 3: Partial failures don’t break the page; caching reduces external calls; AI output is validated + actionable; tests pass end-to-end.
