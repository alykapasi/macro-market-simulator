# macro-market-simulator

**Version:** 0.1.0 — draft
**License:** MIT
**Status:** Pre-development

---

## Table of contents

1. [Overview](#overview)
2. [Motivation](#motivation)
3. [Core concepts](#core-concepts)
4. [Agent model](#agent-model)
5. [Cultural modifier system](#cultural-modifier-system)
6. [Markov transition system](#markov-transition-system)
7. [Scenario library](#scenario-library)
8. [System architecture](#system-architecture)
9. [Data architecture](#data-architecture)
10. [Repo structure](#repo-structure)
11. [Stack](#stack)
12. [LLM integration](#llm-integration)
13. [Output layer](#output-layer)
14. [Open questions](#open-questions)
15. [ADR index](#adr-index)

---

## Overview

`macro-market-simulator` is an open-source, web-based agent-based economic simulation. It models macro-level economic dynamics through a swarm of autonomous agents — households, firms, banks, a government, a central bank, investors, and an informal sector — each governed by Markov state machines whose transition probabilities are modulated by cultural modifiers derived from real national data.

The primary output is a visual: a live D3-rendered swarm showing agent states cascading in real time, alongside macro indicator charts. Users can select a country profile, choose or describe a scenario, tune parameters interactively, and export a PDF report of the run.

It is not an economic forecasting tool. It is a system for developing intuition about how macro-level collapse, recovery, and structural dynamics emerge from micro-level agent behaviour under different cultural and institutional conditions.

---

## Motivation

Most economic simulations are either too academic (inaccessible, headless, paper-bound) or too simplified (GDP sliders with no underlying model). There is a gap for something that is:

- **Grounded** — agent rules and cultural modifiers sourced from real behavioural economics data
- **Visual** — the output is something you want to watch, not just read
- **Interactive** — parameters are live-tweakable, not just set-and-run
- **Cultural** — the same shock plays out differently in different national contexts
- **Open** — MIT licensed, local-first, bring your own model

---

## Core concepts

### Agent-based modelling (ABM)

Agents are autonomous entities with local state and simple rules. They do not have global knowledge — they respond to neighbours and local signals. Macro behaviour (recessions, bubbles, hyperinflation, recovery) emerges from micro interactions rather than being imposed top-down.

### Swarm topology

Agents are arranged in a spatial grid. Each agent's neighbourhood is defined by proximity. Transition probabilities are influenced by the states of neighbouring agents, creating contagion dynamics — a cluster of distressed households raises the transition probability of adjacent firms moving toward contraction.

### Markov state machines

Each actor type has a finite set of macro states. At every tick, each agent computes transition probabilities to adjacent states based on: its current state, local neighbourhood state, global macro indicators, and cultural modifier weights. The transition is sampled stochastically.

### Cultural modifiers

A set of continuous parameters (0–1 scale) derived from real national data sources (World Values Survey, OECD, World Bank) that modulate transition probabilities. The same scenario loaded with a Japanese cultural profile vs a Brazilian one produces meaningfully different dynamics.

### Macro indicators

Per-tick aggregations computed from the full agent population: GDP proxy, unemployment rate, CPI proxy, credit stress index, Gini coefficient proxy, informal sector absorption rate. These feed back into agent transition probabilities and are rendered as live D3 charts.

---

## Agent model

Six actor types. Each has a named set of macro states, allowed transitions, and recovery paths. Recovery probability is always modulated by cultural modifiers.

### Household

| State | Description |
|---|---|
| `thriving` | Income positive, savings growing |
| `stable` | Income covers expenses, flat savings |
| `stressed` | Income covers expenses, savings depleting |
| `speculative` | Over-leveraged, income positive |
| `distressed` | Income below expenses, drawing down savings |
| `defaulted` | Cannot service debt obligations |
| `bankrupt` | Formal insolvency declared |
| `recovering` | Post-bankruptcy, limited credit access |
| `informal` | Exited formal economy |

Recovery path: `bankrupt → recovering → stable`
Cultural gate: `bankruptcy_stigma` weight on `bankrupt → recovering` probability

### Firm

| State | Description |
|---|---|
| `expanding` | Revenue growing, hiring |
| `stable` | Revenue flat, headcount stable |
| `contracting` | Revenue declining, headcount reducing |
| `distressed` | Cash flow negative |
| `speculative` | High leverage, high growth |
| `zombie` | Technically insolvent, kept alive by bank forbearance |
| `restructuring` | Formal debt restructuring in progress |
| `bankrupt` | Formal insolvency |
| `dormant` | Post-bankruptcy, inactive |

Recovery path: `bankrupt → dormant → stable`
Cultural gate: `ease_of_doing_business` on `dormant → stable`; `institutional_trust` on `distressed → zombie`

### Bank

| State | Description |
|---|---|
| `healthy` | Capital ratios strong, lending freely |
| `cautious` | Tightening lending standards |
| `constrained` | Capital ratios under pressure |
| `stressed` | Active regulatory concern |
| `forbearing` | Knowingly holding non-performing loans |
| `illiquid` | Cannot meet short-term obligations |
| `insolvent` | Liabilities exceed assets |

Cultural gate: `institutional_trust` on `constrained → forbearing`; `central_bank_independence` on `illiquid` intervention probability

### Government

| State | Description |
|---|---|
| `surplus` | Revenue exceeds expenditure |
| `balanced` | Revenue meets expenditure |
| `deficit` | Expenditure exceeds revenue |
| `structural_deficit` | Persistent deficit, rising debt |
| `austerity` | Forced spending cuts |
| `crisis` | Debt service consuming primary budget |
| `default` | Sovereign debt default |
| `restructuring` | Post-default debt restructuring |

Cultural gate: `institutional_trust` on `crisis → default` probability

### Central bank

| State | Description |
|---|---|
| `accommodative` | Rates low, QE active |
| `neutral` | Rates at neutral, no active programme |
| `tightening` | Raising rates, reducing balance sheet |
| `emergency_easing` | Emergency rate cuts, crisis response |
| `credibility_crisis` | Markets no longer trust rate signals |

Cultural gate: `central_bank_independence` governs whether government can force `tightening → emergency_easing`

### Investor class

| State | Description |
|---|---|
| `risk_on` | Allocating to equities, high-yield, EM |
| `cautious` | Rotating toward safer assets |
| `risk_off` | Selling risk assets, building cash |
| `flight` | Capital flight, exiting currency/market |

### Informal sector

| State | Description |
|---|---|
| `absorbing` | Capacity available, taking in displaced households and firms |
| `saturated` | At capacity, wages and conditions declining |
| `collapsing` | No longer functional as safety net |

Cultural gate: `informality_index` governs sector size and absorption speed. Not all country profiles include an active informal sector.

---

## Cultural modifier system

Cultural modifiers are continuous parameters on a 0–1 scale. They are defined per country profile in YAML and validated against a JSON Schema on load.

| Modifier | Description | Source |
|---|---|---|
| `bankruptcy_stigma` | Social and legal cost of personal bankruptcy | World Bank, WVS |
| `social_safety_net` | Strength of public welfare and unemployment systems | OECD |
| `institutional_trust` | Population trust in banks and government institutions | WVS |
| `central_bank_independence` | Degree of independence from government | BIS, academic indices |
| `informality_index` | Size and role of informal economy | World Bank |
| `risk_tolerance` | Cultural propensity for leverage and speculation | WVS, behavioural data |
| `collectivism` | Preference for group outcomes vs individual outcomes | Hofstede |
| `ease_of_doing_business` | Regulatory ease of firm creation and recovery | World Bank |

Country profiles combine these modifiers with a base population distribution and sector size ratios.

---

## Markov transition system

### Transition probability computation

At each tick, for each agent `a` of type `T` in state `s`:

1. Look up the base transition matrix for type `T`, state `s` → a probability vector over all reachable next states
2. Apply neighbourhood modifier: sample the states of `k` nearest neighbours, compute a stress/optimism signal, adjust probabilities
3. Apply global macro modifier: read current macro indicators (unemployment rate, CPI, credit stress index), adjust probabilities
4. Apply cultural modifier weights: for culturally-gated transitions, multiply probability by the relevant modifier value
5. Normalise the probability vector and sample the next state

### Transition matrix format

Each actor type ships with a base transition matrix defined in code as a Pydantic model. The matrix is not stored in YAML — it is logic, not config. Scenario configs can supply `parameter_overrides` that shift the base probabilities for a given scenario's starting conditions.

### Macro feedback loop

Aggregated macro indicators from tick `n` feed into transition probabilities at tick `n+1`. This creates the feedback loops that drive emergent dynamics: rising unemployment increases household stress transition probabilities, which increases firm contraction probabilities, which increases unemployment — the classic recessionary spiral.

---

## Scenario library

Each scenario ships as a YAML config file in `configs/scenarios/`. The schema is validated on load.

### Schema

```yaml
id: gfc_2008
name: "2008 global financial crisis"
description: >
  The collapse of the US subprime mortgage market triggers a global
  credit freeze. Banks become illiquid, firms contract, households
  default. Central banks respond with emergency easing.
tags:
  - credit
  - banking
  - contagion
  - fiscal
country_profile: usa_2008
parameter_overrides:
  bank_initial_state_distribution:
    healthy: 0.3
    cautious: 0.4
    constrained: 0.2
    stressed: 0.1
  household_leverage_modifier: 1.6
  credit_availability: 0.2
llm_prompt: >
  You are narrating an agent-based simulation of the 2008 global
  financial crisis. The simulation begins with banks under stress
  from subprime exposure. Describe what is happening in the economy
  as the user watches the simulation unfold. Focus on the macro
  dynamics — credit contraction, firm distress, household defaults —
  rather than specific institutions or people.
```

### v1 scenario list

| ID | Name | Primary dynamics |
|---|---|---|
| `covid_2020` | 2020 COVID shock | Demand collapse, fiscal stimulus, informal sector stress |
| `gfc_2008` | 2008 global financial crisis | Credit freeze, bank insolvency, contagion |
| `dotcom_2000` | Dot-com crash | Investor flight, speculative firm collapse, mild household impact |
| `asian_crisis_1997` | 1997 Asian financial crisis | Capital flight, currency crisis, IMF austerity |
| `gulf_war_1990` | Gulf War 1990–91 | Oil shock, fiscal expansion, inflation |
| `war_on_terror_2001` | Post-9/11 war on terror | Defence fiscal surge, deficit expansion, oil shock, low-rate environment |

---

## System architecture

### Layers

```
frontend (React + Tailwind + shadcn)
    ↕ REST + WebSocket
backend (FastAPI)
    ├── api/          route handlers
    ├── schemas/      Pydantic data contracts
    ├── sim/          pure simulation logic
    └── services/     LLM bridge, PDF export
```

### Request flow — sim run

1. User selects country + scenario in frontend
2. `POST /api/sim/start` → backend validates config, initialises agent population, stores in session
3. Backend starts tick loop, emits `TickSnapshot` per tick over WebSocket
4. Frontend `useSimSocket` hook receives frames, updates D3 swarm render and macro charts
5. User adjusts parameters via controls → `POST /api/sim/params` → engine applies on next tick
6. User pauses → `POST /api/sim/pause`
7. User exports → `POST /api/export/pdf` → Jinja template rendered, WeasyPrint produces PDF

### Request flow — custom scenario via LLM

1. User pastes scenario description in free-text input
2. `POST /api/llm/compile` → LLM bridge sends description + system prompt to Ollama or BYOT endpoint
3. LLM returns structured JSON matching `ScenarioConfig` schema
4. Backend validates with Pydantic, returns compiled config to frontend
5. User reviews and confirms → normal sim start flow

### WebSocket tick payload

```json
{
  "tick": 142,
  "agents": [
    {"id": "hh_0042", "type": "household", "state": "distressed", "x": 0.34, "y": 0.71},
    ...
  ],
  "macro": {
    "gdp_index": 94.2,
    "unemployment_rate": 0.087,
    "cpi_index": 103.1,
    "credit_stress": 0.61,
    "gini_proxy": 0.44,
    "informal_absorption": 0.12
  },
  "events": [
    {"tick": 142, "type": "bank_failure", "actor_id": "bank_003"}
  ]
}
```

---

## Data architecture

### Principles

- **Schema-first** — every data boundary is a Pydantic model. No raw dicts cross layer boundaries.
- **Immutable snapshots** — sim state mutates in place per tick; emitted `TickSnapshot` objects are frozen Pydantic models. The replay engine and live dashboard consume the same contract.
- **Config validation on load** — YAML configs are validated against Pydantic schemas at startup. Malformed configs fail fast, not at runtime.
- **One-way data flow** — `config → agent init → tick loop → snapshot → aggregator → outputs`. No circular references between layers.
- **Typed primitives** — `AgentId`, `Tick`, `CountryCode` are `NewType` wrappers, not bare strings.
- **State–behaviour separation** — agent state is pure data; transition logic lives in `sim/engine.py` and `sim/markov.py`. Agents do not contain their own transition logic.

### Key Pydantic models

| Model | Location | Description |
|---|---|---|
| `AgentState` | `schemas/agent.py` | Current state, position, type, id |
| `TickSnapshot` | `schemas/tick.py` | Frozen per-tick population + macro snapshot |
| `MacroIndicators` | `schemas/tick.py` | GDP index, unemployment, CPI, credit stress |
| `SimConfig` | `schemas/config.py` | Full resolved sim configuration |
| `ScenarioConfig` | `schemas/config.py` | Scenario YAML contract |
| `CountryProfile` | `schemas/config.py` | Country YAML contract |
| `WsTickPayload` | `schemas/ws_payload.py` | WebSocket message contract |
| `LlmCompileRequest` | `schemas/llm.py` | Free-text → scenario compile request |
| `LlmCompileResponse` | `schemas/llm.py` | Validated compiled ScenarioConfig |

### YAML config schemas

Country and scenario YAML files are validated against JSON Schema files in `configs/schemas/` at startup. This is a separate validation layer from Pydantic — it allows contributors to validate their YAML locally without running the full app.

---

## Repo structure

```
macro-market-simulator/
├── backend/
│   ├── main.py                  # app entrypoint, lifespan, CORS
│   ├── api/
│   │   └── routes/
│   │       ├── sim.py           # sim control endpoints
│   │       ├── llm.py           # scenario compile endpoint
│   │       └── export.py        # PDF export endpoint
│   ├── schemas/                 # Pydantic — all data boundaries
│   │   ├── agent.py
│   │   ├── tick.py
│   │   ├── config.py
│   │   ├── ws_payload.py
│   │   └── llm.py
│   ├── sim/                     # pure sim logic, zero I/O
│   │   ├── engine.py            # tick loop, swarm step
│   │   ├── markov.py            # transition matrix builder
│   │   ├── aggregator.py        # macro indicators per tick
│   │   └── agents/              # one file per actor type
│   │       ├── household.py
│   │       ├── firm.py
│   │       ├── bank.py
│   │       ├── government.py
│   │       ├── central_bank.py
│   │       ├── investor.py
│   │       └── informal.py
│   └── services/
│       ├── llm_service.py       # Ollama + BYOT router
│       └── pdf_service.py       # Jinja + WeasyPrint
├── configs/
│   ├── countries/               # usa.yaml, japan.yaml, india.yaml …
│   ├── scenarios/               # gfc_2008.yaml, covid_2020.yaml …
│   └── schemas/                 # JSON Schema for YAML validation
├── frontend/
│   ├── components/
│   │   ├── SimCanvas.tsx        # D3 swarm render
│   │   ├── MacroDash.tsx        # live D3 charts
│   │   ├── ScenarioPanel.tsx    # library + custom input
│   │   └── Controls.tsx         # sliders, speed, reset
│   ├── hooks/
│   │   ├── useSimSocket.ts      # WebSocket tick stream
│   │   └── useScenario.ts       # scenario state management
│   └── types/                   # TypeScript mirrors of backend schemas
└── docs/
    ├── design_doc.md            # this document
    └── adr/                     # architecture decision records
        ├── 001-in-memory-state.md
        ├── 002-yaml-for-configs.md
        ├── 003-markov-macro-only.md
        └── 004-llm-outside-sim-loop.md
```

---

## Stack

| Layer | Technology | Rationale |
|---|---|---|
| Backend | Python + FastAPI | async WebSocket support, Pydantic-native, fast to prototype |
| Simulation | Pure Python | no runtime dependencies, independently testable |
| Frontend | React + Tailwind + shadcn | composable UI, good D3 integration |
| Visualisation | D3.js | best-in-class for data-driven SVG rendering |
| LLM | Ollama (local) + BYOT (cloud) | local-first, no mandatory API key |
| PDF export | Jinja2 + WeasyPrint | HTML-to-PDF, full CSS control over report layout |
| Config | YAML + JSON Schema | human-readable, contributor-friendly, validated |
| Package management | uv (Python), pnpm (Node) | fast, reproducible |

---

## LLM integration

The LLM is used in two modes only. It does not touch the running simulation.

### Mode 1 — scenario library commentary

Each scenario ships with a `llm_prompt` field. When the user enables narrative mode, this prompt is sent to the LLM at the start of the run and at configurable tick intervals. The LLM receives the current macro snapshot and returns a short narrative paragraph rendered in the UI alongside the simulation.

### Mode 2 — custom scenario compilation

The user pastes a free-text scenario description. The system prompt instructs the LLM to return a JSON object matching the `ScenarioConfig` schema with no preamble. The response is parsed and validated with Pydantic before being shown to the user for confirmation.

System prompt skeleton:

```
You are a macro-economic scenario compiler. The user will describe an economic scenario
in natural language. Return ONLY a valid JSON object matching the following schema.
Do not include any preamble, explanation, or markdown formatting.

Schema:
{ScenarioConfig.model_json_schema()}

If the user's description is ambiguous, make reasonable assumptions and note them
in the `description` field of your response.
```

### LLM router

`llm_service.py` implements a simple router:
- If `OLLAMA_BASE_URL` is set → use Ollama with the configured model
- If `LLM_API_KEY` is set → use the configured BYOT endpoint (OpenAI-compatible)
- If neither → narrative mode is disabled, custom scenario compilation shows a configuration prompt

---

## Output layer

### Live simulation view

- D3 force-directed swarm, nodes coloured by actor type, node border intensity encoding state severity
- Macro indicator charts: GDP index, unemployment rate, CPI, credit stress — all live-updating per tick
- Event log: significant state transitions (bank failures, sovereign default, central bank interventions) surfaced as timestamped events

### PDF report

Generated from a Jinja2 template rendered by WeasyPrint. Contents:

- Scenario summary (name, country, parameters used)
- Run metadata (ticks, wall time, seed)
- Macro indicator time series charts (rendered as SVG, embedded)
- State distribution over time per actor type (stacked area charts)
- Key events log
- Cultural modifier values used
- Optional LLM narrative transcript

### Scenario export

The full resolved `SimConfig` for any run can be exported as a YAML snapshot, allowing runs to be reproduced exactly or shared with other users.

---

## Open questions

- **Tick rate and population size** — what is the right default population size for visual legibility vs sim fidelity? Needs empirical testing during development.
- **Neighbourhood definition** — fixed radius vs k-nearest? Fixed radius is more spatially intuitive but k-nearest is more computationally stable at varying densities.
- **Inter-actor interaction rules** — the current model defines intra-type state machines. The interaction rules between types (e.g. how a bank state affects firm transition probabilities) need to be specified explicitly before implementation.
- **Cultural modifier data sources** — exact data sources and normalisation methodology for each modifier need to be documented and cited before the first country profile ships.
- **WebSocket session management** — multiple concurrent sessions (multiple browser tabs, multiple users on a shared instance) need a session ID scheme. Currently assumed single-session.

---

## ADR index

| ID | Decision | Status |
|---|---|---|
| 001 | In-memory session state, no database | Accepted |
| 002 | YAML for human-edited configs, JSON for wire payloads | Accepted |
| 003 | Markov macro-state machines only, no microeconomic price theory | Accepted |
| 004 | LLM runs outside the sim tick loop | Accepted |

---

*This document is the source of truth for design intent. Implementation details that diverge from this document should be reflected here before merging.*