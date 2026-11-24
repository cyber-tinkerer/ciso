# ciso — AI Security Vendor Evaluation Framework (`aisec_eval`)

A framework for evaluating the capabilities of AI security companies, from established incumbents
to brand-new startups. It is evidence-driven: every score can be traced to a phrase in a cited source,
and each score carries the evidence level behind it.

```bash
python3 -m aisec_eval evaluate --input <companies.json|csv> [--input ...] \
    [--evidence evidence.json] [--labels validation/ground_truth_labels.csv] \
    [--config config.json] --out output/ --as-of 2026-11-24
```

Outputs: `scorecards.json` (full, traceable), `scorecards.csv`, `summary.json`, `report.md`.
It uses only the Python 3.11+ standard library. Tests need `pytest`.

## The framework

### 1. Scope gate: what counts as an "AI security company"
Each company is placed in one of five segments:

| Segment | Meaning |
|---|---|
| `security_for_ai` | Protects AI systems, models, agents or employee AI usage |
| `ai_for_security` | Cybersecurity where AI/agents are the mechanism doing the work |
| `ai_governance` | Governance, risk and compliance of AI |
| `adjacent` | Security without an AI claim, or AI where security is incidental (including physical-security AI) |
| `out_of_scope` | Neither |

Only the first three are scored. The rationale (which signals fired) is recorded on every scorecard.

### 2. Capability domains (15)
Defined in `aisec_eval/taxonomy.py`, each with evidence patterns and mappings to reference frameworks:

* **Security for AI:** discovery & posture (AI-SPM), runtime protection (AI firewall/guardrails), red teaming & testing,
  agent & MCP security, identity & access for AI/NHI, data protection for AI, model & AI supply chain,
  consumption & abuse controls, deepfake & content integrity
* **AI governance:** governance, risk & compliance
* **AI for security:** autonomous SOC, offensive security / pentesting, AppSec & API security, threat detection, exposure management

Mappings: **OWASP Top 10 for LLM Applications 2025** (LLM01–LLM10), **NIST AI RMF** (Govern/Map/Measure/Manage),
**NIST CSF 2.0**. These mappings are the framework author's judgement. OWASP and NIST have not endorsed them,
and they should be reviewed before anyone relies on them.

### 3. Evidence levels
| Level | Source | Default weight |
|---|---|---|
| L1 | Vendor self-description (e.g. Crunchbase blurb) | 0.25 |
| L2 | Vendor technical documentation | 0.50 |
| L3 | Independent third party (analyst, customer reference) | 0.75 |
| L4 | Independently tested / audited | 1.00 |

Higher-level evidence is supplied through an evidence file (see `examples/evidence_incumbents.json`).

### 4. Scores (kept separate on purpose)
* **Capability index (0–100)** = 0.4 × breadth + 0.4 × assurance + 0.2 × framework coverage. The weights are configurable and must sum to 1.
  * *breadth*: share of the segment's capability domains that have evidence
  * *assurance*: mean evidence weight across the evidenced domains
  * *framework coverage*: OWASP LLM risks covered (security for AI), NIST CSF functions (AI for security), or NIST AI RMF functions (governance)
  * The index is **only comparable within a segment**.
* **Maturity tier** (`established` / `scale_up` / `growth` / `early` / `nascent` / `unknown`) comes only from employees,
  funding and IPO status. It never affects the capability index.
* **Confidence**, **data-quality flags** (missing data, future founding dates, name/record mismatches) and
  **limitations** are attached to every scorecard.

Design rules, each enforced by a test: findings are traceable to source text; missing data → `unknown`, never 0;
stronger evidence never lowers assurance; capability and maturity are independent; outputs are deterministic.

## Test run on real data (2026-11-24)

**Sample:** 215 companies from Crunchbase:
* 200 operating companies whose description mentions AI security, security for AI, LLM security, AI red teaming,
  prompt injection, AI agent security, agentic security or AI governance, ordered by total funding.
  Crunchbase reported 3,988 matches for a similar keyword search, so the sample is about 5% of that population and leans towards better-funded companies.
* The top 15 public companies in Crunchbase's Cyber Security category, by CB rank (240 matches), to cover incumbents.

The sample runs from companies founded in 1865 (Nokia) to companies founded in 2026, and from 1–10 employees to 10,001+.

**Validation:** 215 hand-labelled companies (`validation/ground_truth_labels.csv`). The labels were committed before any classifier code was written.
Patterns were refined using errors from the `dev` half only. The `heldout` half was used only for metrics.

| Split | n | Segment accuracy | In-scope precision | In-scope recall |
|---|---|---|---|---|
| dev | 108 | 0.843 | 0.912 | 0.973 |
| **heldout** | 107 | **0.776** | **0.925** | **0.949** |
| high-confidence labels only | 194 | 0.845 | 0.932 | 0.978 |

The full report is in `results/2026-11-24/report.md`.

### What the test showed
* The scope gate excluded clear false positives that the Crunchbase keyword search returned: a label printer, a wearable maker, an optical-chip maker, a radiology platform and a Web3 company.
* Data-quality checks flagged corrupted or merged records. One is a SEALSQ record whose name field holds a person's name; another is a "Quantum Cyber" record that sits on a `mainz-biomed` profile.
* Incumbents are under-rated by L1 data. Zscaler's and Microsoft's one-line descriptions do not mention AI security, so they score out of scope.
  Adding four L2 documentation excerpts reclassifies both as `security_for_ai`. That is the reason for the evidence-level design.
* The weakest areas are the boundaries `adjacent` ↔ `out_of_scope` and `security_for_ai` ↔ `ai_governance`. Adjacent recall is 0.55.

## Limitations
* The test used L1 evidence (vendor self-descriptions) only. Capability results are **claims, not verified capabilities**.
* The ground-truth labels are one analyst's judgement based on the same descriptions, and nobody else has reviewed them.
* The patterns were written by someone who had seen the sample's descriptions. Labels were fixed first, and the dev/held-out split
  limits but does not remove over-fitting. Expect lower accuracy on new data.
* The sample is not the full universe. The Crunchbase plan used caps searches at 15 rows with no pagination,
  and the data-token allowance was the binding limit.
* Raw Crunchbase data is not committed because this repository is public and the data is licensed.
  The tests that need it skip when `data/raw/` is absent.

## Layout
```
aisec_eval/        taxonomy, ingest, evaluate, validate, report, cli
tests/             unit + end-to-end tests (real-data tests skip without data/raw/)
validation/        ground-truth labels + labelling protocol
examples/          L2 evidence file example (Zscaler, Microsoft)
results/2026-11-24 report, summary and scorecards from the test run
```
