# AI Security Vendor Landscape — Evaluation Run

## Provenance

- Evaluation date: 2026-11-24
- Input `crunchbase_ai_security_2026-11-24.json`: 200 records
- Input `crunchbase_public_cyber_2026-11-24.json`: 15 records

## What these scores are (and are not)

- **Segment** and **capabilities** are derived from text the vendor wrote about itself (evidence level L1) unless an evidence file adds higher-level evidence. They are *claims*, not verified capabilities.
- **Capability index** = 0.4 × breadth + 0.4 × assurance + 0.2 × framework coverage (weights configurable). With L1-only evidence, assurance is 25 for every claimed capability, so the index mostly reflects how many capabilities a one-line description mentions.
- **Maturity tier** comes only from structured fields (employees, funding, IPO status). Unknown data → `unknown`, not a low tier.
- A missing capability means *not evidenced in the sources used*, not *absent from the product*.

## Landscape summary

- Companies evaluated: **215**
- In scope (security for AI / AI for security / AI governance): **160**

| Segment | Companies |
|---|---|
| security_for_ai | 72 |
| ai_governance | 55 |
| ai_for_security | 33 |
| out_of_scope | 28 |
| adjacent | 27 |

| Maturity tier (in scope) | Companies |
|---|---|
| early | 93 |
| nascent | 38 |
| growth | 24 |
| scale_up | 4 |
| established | 1 |

### Claimed capability prevalence (in-scope companies)

| Domain | Companies |
|---|---|
| AI governance, risk & compliance | 76 |
| AI agent & MCP security | 23 |
| Identity & access control for AI / non-human identities | 11 |
| Data protection for AI (AI-DLP, leakage, privacy) | 10 |
| AI-driven threat detection & prevention | 9 |
| AI discovery, inventory & posture (AI-SPM) | 9 |
| AI red teaming, testing & evaluation | 9 |
| AI runtime protection (AI firewall / guardrails) | 9 |
| AI-driven / autonomous security operations | 8 |
| AI-driven offensive security / pentesting | 5 |
| AI-driven exposure & vulnerability management | 3 |
| AI-driven application & API security | 3 |
| Deepfake & content-integrity protection | 2 |

### OWASP Top 10 for LLM Applications 2025 — share of security-for-AI vendors whose description claims a mapped capability

| Risk | Name | Vendors | % |
|---|---|---|---|
| LLM01 | Prompt Injection | 32 | 44.40 |
| LLM02 | Sensitive Information Disclosure | 14 | 19.40 |
| LLM03 | Supply Chain | 4 | 5.60 |
| LLM04 | Data and Model Poisoning | 8 | 11.10 |
| LLM05 | Improper Output Handling | 9 | 12.50 |
| LLM06 | Excessive Agency | 28 | 38.90 |
| LLM07 | System Prompt Leakage | 16 | 22.20 |
| LLM08 | Vector and Embedding Weaknesses | 7 | 9.70 |
| LLM09 | Misinformation | 18 | 25.00 |
| LLM10 | Unbounded Consumption | 0 | 0.00 |

### Data-quality flags raised

| Flag | Count |
|---|---|
| missing_funding | 27 |
| in_scope_but_no_specific_capability_claimed | 26 |
| description_too_short | 10 |
| missing_founded_year | 3 |
| missing_employee_count | 3 |
| source_record_name_mismatch | 3 |
| name_description_mismatch | 2 |

## Validation against hand-labelled ground truth

Labelled: 215, matched to scorecards: 215.
Labels are analyst judgement from the same descriptions (see `validation/LABELING.md`). `heldout` rows were not inspected while refining patterns.

| Split | n | Segment accuracy | Segment macro-F1 | In-scope precision | In-scope recall | In-scope F1 |
|---|---|---|---|---|---|---|
| all | 215 | 0.81 | 0.79 | 0.92 | 0.96 | 0.94 |
| dev | 108 | 0.84 | 0.82 | 0.91 | 0.97 | 0.94 |
| heldout | 107 | 0.78 | 0.75 | 0.93 | 0.95 | 0.94 |
| high_confidence_labels_only | 194 | 0.85 | 0.83 | 0.93 | 0.98 | 0.95 |

Per-segment (all labelled rows):

| Segment | Support | Precision | Recall | F1 |
|---|---|---|---|---|
| security_for_ai | 72 | 0.85 | 0.85 | 0.85 |
| ai_for_security | 37 | 0.97 | 0.86 | 0.91 |
| ai_governance | 44 | 0.76 | 0.95 | 0.85 |
| adjacent | 38 | 0.78 | 0.55 | 0.65 |
| out_of_scope | 24 | 0.64 | 0.75 | 0.69 |

Most frequent confusions (gold → predicted):

- adjacent->out_of_scope: 6
- adjacent->security_for_ai: 6
- security_for_ai->ai_governance: 6
- adjacent->ai_governance: 5
- ai_for_security->security_for_ai: 4
- out_of_scope->adjacent: 4
- out_of_scope->ai_governance: 2
- security_for_ai->adjacent: 2
- security_for_ai->out_of_scope: 2
- ai_for_security->out_of_scope: 1

## In-scope scorecards (grouped by segment, ranked by capability index within segment)

Each segment is measured against its own set of capability domains, so the index is only comparable *within* a segment, not across segments.

| Company | Segment | Index | Breadth % | Maturity | Claimed capabilities | Flags |
|---|---|---|---|---|---|---|
| Kastra AI | security_for_ai | 38.00 | 40.00 | nascent | ai_runtime_protection, agent_security, ai_identity_access, ai_governance_compliance | — |
| Capsule Security | security_for_ai | 36.00 | 30.00 | early | ai_runtime_protection, agent_security, ai_data_protection | — |
| NeuralTrust | security_for_ai | 36.00 | 30.00 | early | ai_runtime_protection, agent_security, ai_data_protection | — |
| Aim Intelligence | security_for_ai | 30.00 | 20.00 | early | ai_runtime_protection, ai_red_teaming | — |
| BotGauge | security_for_ai | 28.00 | 20.00 | early | ai_red_teaming, agent_security | — |
| Mace Ai | security_for_ai | 28.00 | 20.00 | early | ai_red_teaming, agent_security | — |
| Method Security | security_for_ai | 28.00 | 20.00 | early | ai_red_teaming, agent_security | — |
| Secure AI LLC | security_for_ai | 28.00 | 20.00 | early | ai_runtime_protection, ai_governance_compliance | — |
| Verno Labs | security_for_ai | 28.00 | 20.00 | nascent | ai_red_teaming, agent_security | description_too_short |
| Outerlimit | security_for_ai | 26.00 | 30.00 | early | agent_security, ai_identity_access, ai_governance_compliance | — |
| Preemptics | security_for_ai | 26.00 | 20.00 | nascent | ai_red_teaming, ai_governance_compliance | missing_founded_year, missing_employee_count |
| Unosecur | security_for_ai | 26.00 | 30.00 | early | agent_security, ai_identity_access, ai_governance_compliance | — |
| Impart Security | security_for_ai | 24.00 | 10.00 | early | ai_runtime_protection | — |
| Levo.ai | security_for_ai | 24.00 | 10.00 | early | ai_runtime_protection | — |
| Silmaril | security_for_ai | 24.00 | 10.00 | nascent | ai_runtime_protection | — |
| Uindow | security_for_ai | 24.00 | 10.00 | early | ai_runtime_protection | description_too_short |
| Autnhive | security_for_ai | 22.00 | 20.00 | early | ai_data_protection, ai_governance_compliance | missing_funding |
| Bay | security_for_ai | 22.00 | 20.00 | growth | ai_discovery_posture, ai_governance_compliance | — |
| CyberX - The Ethical Hacking Services | security_for_ai | 22.00 | 10.00 | early | ai_red_teaming | — |
| Endeem | security_for_ai | 22.00 | 20.00 | nascent | agent_security, ai_identity_access | — |
| Harmonic Security | security_for_ai | 22.00 | 20.00 | growth | ai_discovery_posture, ai_governance_compliance | — |
| Indora Labs | security_for_ai | 22.00 | 20.00 | nascent | ai_data_protection, ai_governance_compliance | — |
| Mindgard | security_for_ai | 22.00 | 10.00 | early | ai_red_teaming | — |
| Noma Security | security_for_ai | 22.00 | 20.00 | growth | agent_security, ai_governance_compliance | — |
| Pinta AI | security_for_ai | 22.00 | 20.00 | early | agent_security, ai_governance_compliance | — |
| Reco | security_for_ai | 22.00 | 20.00 | growth | agent_security, ai_identity_access | — |
| Zenity | security_for_ai | 22.00 | 20.00 | growth | agent_security, ai_governance_compliance | — |
| FERZ, Inc. | security_for_ai | 20.00 | 20.00 | early | ai_identity_access, ai_governance_compliance | missing_funding |
| AIBound | security_for_ai | 18.00 | 10.00 | early | ai_discovery_posture | missing_funding |
| AIR Security | security_for_ai | 18.00 | 10.00 | growth | agent_security | — |
| BlackFog | security_for_ai | 18.00 | 10.00 | early | ai_data_protection | — |
| Cynsta AI | security_for_ai | 18.00 | 10.00 | nascent | agent_security | description_too_short |
| Dam Secure | security_for_ai | 18.00 | 10.00 | nascent | agent_security | — |
| IronCore Labs | security_for_ai | 18.00 | 10.00 | early | ai_data_protection | — |
| Metano | security_for_ai | 18.00 | 10.00 | early | agent_security | missing_founded_year, missing_employee_count |
| Neo Security | security_for_ai | 18.00 | 10.00 | growth | agent_security | — |
| Opsin | security_for_ai | 18.00 | 10.00 | early | agent_security | — |
| PoliRail | security_for_ai | 18.00 | 10.00 | nascent | agent_security | description_too_short |
| QueryLift | security_for_ai | 18.00 | 10.00 | nascent | ai_discovery_posture | — |
| RealAI | security_for_ai | 18.00 | 10.00 | early | ai_data_protection | — |
| Trent AI | security_for_ai | 18.00 | 10.00 | early | agent_security | — |
| nolabs | security_for_ai | 18.00 | 10.00 | nascent | agent_security | — |
| Dheemai Inc | security_for_ai | 16.00 | 10.00 | nascent | deepfake_content_integrity | — |
| StealCut | security_for_ai | 16.00 | 10.00 | nascent | deepfake_content_integrity | — |
| Asenion | security_for_ai | 14.00 | 10.00 | early | ai_governance_compliance | — |
| Cranium AI | security_for_ai | 14.00 | 10.00 | growth | ai_governance_compliance | — |
| Lumia Security | security_for_ai | 14.00 | 10.00 | early | ai_governance_compliance | — |
| PointGuard AI | security_for_ai | 14.00 | 10.00 | early | ai_governance_compliance | missing_funding |
| Polygraf | security_for_ai | 14.00 | 10.00 | early | ai_governance_compliance | — |
| PromptArmor | security_for_ai | 14.00 | 10.00 | early | ai_governance_compliance | — |
| Speakeasy | security_for_ai | 14.00 | 10.00 | early | ai_governance_compliance | — |
| Verax AI | security_for_ai | 14.00 | 10.00 | early | ai_governance_compliance | — |
| Aeye Security Lab | security_for_ai | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| Aurascape | security_for_ai | 0.00 | 0.00 | growth | — | in_scope_but_no_specific_capability_claimed |
| Bespin Global | security_for_ai | 0.00 | 0.00 | scale_up | — | in_scope_but_no_specific_capability_claimed |
| Blindsight | security_for_ai | 0.00 | 0.00 | nascent | — | description_too_short, missing_funding, in_scope_but_no_specific_capability_claimed |
| Cranium | security_for_ai | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| DeepKeep | security_for_ai | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| Firetail | security_for_ai | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| Gray Swan | security_for_ai | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| Helmet Security | security_for_ai | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| HiddenLayer | security_for_ai | 0.00 | 0.00 | growth | — | in_scope_but_no_specific_capability_claimed |
| Lasso Security | security_for_ai | 0.00 | 0.00 | growth | — | in_scope_but_no_specific_capability_claimed |
| Mileva Security Labs | security_for_ai | 0.00 | 0.00 | nascent | — | description_too_short, in_scope_but_no_specific_capability_claimed |
| Obsidian Security | security_for_ai | 0.00 | 0.00 | growth | — | in_scope_but_no_specific_capability_claimed |
| Realm Labs | security_for_ai | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| SpeedyCloud | security_for_ai | 0.00 | 0.00 | growth | — | in_scope_but_no_specific_capability_claimed |
| TigerByte Cyber | security_for_ai | 0.00 | 0.00 | nascent | — | in_scope_but_no_specific_capability_claimed |
| Tolmo | security_for_ai | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| Veriom | security_for_ai | 0.00 | 0.00 | nascent | — | in_scope_but_no_specific_capability_claimed |
| Watchful | security_for_ai | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| Zaun | security_for_ai | 0.00 | 0.00 | early | — | description_too_short, in_scope_but_no_specific_capability_claimed |
| Aura | ai_for_security | 33.80 | 42.90 | growth | ai_identity_access, ai_data_protection, ai_threat_detection | missing_funding |
| Mave | ai_for_security | 31.40 | 28.60 | early | autonomous_soc, ai_threat_detection | — |
| Strix | ai_for_security | 28.10 | 28.60 | early | ai_offensive_security, ai_appsec | — |
| TrendAI | ai_for_security | 28.10 | 28.60 | established | ai_data_protection, ai_threat_detection | missing_funding |
| Adaptive Security | ai_for_security | 25.70 | 14.30 | growth | ai_threat_detection | — |
| Foresee Security | ai_for_security | 25.70 | 14.30 | early | exposure_management | — |
| Mycroft | ai_for_security | 25.70 | 14.30 | early | autonomous_soc | — |
| Rad Security | ai_for_security | 25.70 | 14.30 | early | autonomous_soc | — |
| Abnormal AI | ai_for_security | 22.40 | 14.30 | scale_up | ai_threat_detection | — |
| Cyera | ai_for_security | 22.40 | 14.30 | scale_up | ai_data_protection | — |
| Dropzone AI | ai_for_security | 22.40 | 14.30 | growth | autonomous_soc | — |
| Embed Security | ai_for_security | 22.40 | 14.30 | early | autonomous_soc | — |
| Exaforce | ai_for_security | 22.40 | 14.30 | growth | autonomous_soc | — |
| HackerOne | ai_for_security | 22.40 | 14.30 | growth | exposure_management | — |
| Mangosta | ai_for_security | 22.40 | 14.30 | nascent | autonomous_soc | — |
| Mate | ai_for_security | 22.40 | 14.30 | growth | autonomous_soc | — |
| Orvanta | ai_for_security | 22.40 | 14.30 | early | ai_appsec | — |
| Ossprey Security | ai_for_security | 22.40 | 14.30 | nascent | ai_threat_detection | — |
| Quantum Cyber | ai_for_security | 22.40 | 14.30 | early | ai_threat_detection | missing_funding, source_record_name_mismatch |
| Remedio | ai_for_security | 22.40 | 14.30 | growth | exposure_management | — |
| Right-Hand Cybersecurity | ai_for_security | 22.40 | 14.30 | early | ai_threat_detection | — |
| Skyld | ai_for_security | 22.40 | 14.30 | nascent | ai_threat_detection | — |
| Xygeni | ai_for_security | 22.40 | 14.30 | early | ai_appsec | — |
| AISafe Labs | ai_for_security | 19.00 | 14.30 | nascent | ai_offensive_security | — |
| CodeAnt AI | ai_for_security | 19.00 | 14.30 | early | ai_offensive_security | — |
| Indiesecurity | ai_for_security | 19.00 | 14.30 | nascent | ai_offensive_security | — |
| MindFort AI | ai_for_security | 19.00 | 14.30 | nascent | ai_offensive_security | — |
| Arrakis Security | ai_for_security | 3.30 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| EVIDION.pl | ai_for_security | 3.30 | 0.00 | nascent | — | in_scope_but_no_specific_capability_claimed |
| NineID | ai_for_security | 3.30 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| Kai | ai_for_security | 0.00 | 0.00 | growth | — | in_scope_but_no_specific_capability_claimed |
| Tuskira | ai_for_security | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| Vero Security | ai_for_security | 0.00 | 0.00 | early | — | in_scope_but_no_specific_capability_claimed |
| Barndoor AI | ai_governance | 55.00 | 75.00 | early | ai_discovery_posture, ai_identity_access, ai_governance_compliance | — |
| CloudEagle.ai | ai_governance | 45.00 | 50.00 | early | ai_identity_access, ai_governance_compliance | missing_funding |
| Corridor Platforms | ai_governance | 45.00 | 50.00 | early | ai_red_teaming, ai_governance_compliance | — |
| Geordie AI | ai_governance | 45.00 | 50.00 | early | ai_discovery_posture, ai_governance_compliance | — |
| Keyboard | ai_governance | 45.00 | 50.00 | nascent | ai_identity_access, ai_governance_compliance | — |
| OpenBox AI | ai_governance | 45.00 | 50.00 | early | ai_identity_access, ai_governance_compliance | — |
| Peridot | ai_governance | 40.00 | 50.00 | early | ai_discovery_posture, ai_governance_compliance | — |
| Tideshiftai | ai_governance | 40.00 | 50.00 | early | ai_discovery_posture, ai_governance_compliance | — |
| Velatir | ai_governance | 40.00 | 50.00 | early | ai_discovery_posture, ai_governance_compliance | — |
| APERION | ai_governance | 35.00 | 25.00 | early | ai_governance_compliance | — |
| Credo AI | ai_governance | 35.00 | 25.00 | early | ai_governance_compliance | — |
| Graph Research Labs | ai_governance | 35.00 | 25.00 | nascent | ai_governance_compliance | — |
| Lexic.ai | ai_governance | 35.00 | 25.00 | early | ai_governance_compliance | — |
| LightBeam.ai | ai_governance | 35.00 | 25.00 | early | ai_governance_compliance | — |
| QYNTARI | ai_governance | 35.00 | 25.00 | nascent | ai_governance_compliance | missing_funding |
| TrustWorks | ai_governance | 35.00 | 25.00 | early | ai_governance_compliance | — |
| 2021.AI | ai_governance | 30.00 | 25.00 | growth | ai_governance_compliance | — |
| ALIGNMT AI | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Adeptiv AI | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | name_description_mismatch |
| Asher Informatics | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | — |
| Atrewwise | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Authentrics.ai | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | — |
| Cognitive View | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| DAIKI | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| DDAT Holdings | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | — |
| EPC Group | ai_governance | 30.00 | 25.00 | growth | ai_governance_compliance | missing_funding |
| Enzai | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| FinbotsAI | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Impact AI | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | — |
| JetStream Security | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Kihan | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | missing_funding |
| Kong | ai_governance | 30.00 | 25.00 | scale_up | ai_governance_compliance | — |
| Kosli | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Kriptos | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| LuminosAI | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Magier AI | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | — |
| MantaRAI | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | — |
| ModelOp | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Modulos | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | description_too_short |
| Monitaur | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| OnboardAI | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | missing_founded_year |
| Preamble | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | description_too_short |
| Produktiv | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Regbase | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | — |
| Regolyn | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Rencore | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| SYNCYR | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | — |
| Saidot | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| SunnyData | ai_governance | 30.00 | 25.00 | growth | ai_governance_compliance | — |
| Userfront | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| ValidMind | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Verapath | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| ZYTRA TECHSOLUTIONS PRIVATE LIMITED | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |
| Zenolabs AI | ai_governance | 30.00 | 25.00 | nascent | ai_governance_compliance | — |
| Zertia | ai_governance | 30.00 | 25.00 | early | ai_governance_compliance | — |

## Excluded by the scope gate

| Company | Segment | Why |
|---|---|---|
| AIVault | adjacent | ai_terms=no; security_terms='secur'; governance_terms=none |
| AOCyber | adjacent | ai_terms=yes; security_terms='Cyber'; governance_terms=none; security mentioned but AI not tied to the security claim |
| Akamai | adjacent | ai_terms=no; security_terms='secur'; governance_terms=none |
| ArcadianAI | adjacent | ai_terms=yes; security_terms='Secur'; governance_terms=none; physical_security='Physical Security' |
| Arcjet | adjacent | ai_terms=yes; security_terms='secur'; governance_terms=none; security mentioned but AI not tied to the security claim |
| ChillStack | adjacent | ai_terms=yes; security_terms='secur'; governance_terms=none; security mentioned but AI not tied to the security claim |
| DECTRAX | adjacent | ai_terms=no; security_terms='deception'; governance_terms=none |
| Forest | adjacent | ai_terms=no; security_terms=none; governance_terms='Regulat' |
| Gen | adjacent | ai_terms=no; security_terms='cyber'; governance_terms=none |
| KB-eye | adjacent | ai_terms=yes; security_terms='secur'; governance_terms=none; weak_security_for_ai_signals=['AI security']; physical_security='camera' |
| Kewei Robotics | adjacent | ai_terms=yes; security_terms='secur'; governance_terms=none; weak_security_for_ai_signals=['AI security']; physical_security='Robot' |
| Nexchain | adjacent | ai_terms=yes; security_terms='secur'; governance_terms=none; security mentioned but AI not tied to the security claim |
| Quantinuum | adjacent | ai_terms=no; security_terms='cyber'; governance_terms=none |
| RiskQ | adjacent | ai_terms=no; security_terms='cyber'; governance_terms='risk management' |
| Rubrik | adjacent | ai_terms=no; security_terms='secur'; governance_terms=none |
| SEALRIGOBERTO GONZALEZ DE JESUS | adjacent | ai_terms=no; security_terms='secur'; governance_terms=none |
| Sai Security Printers | adjacent | ai_terms=no; security_terms='Secur'; governance_terms=none |
| Sonrai Security | adjacent | ai_terms=no; security_terms='Secur'; governance_terms=none |
| Sweet Security | adjacent | ai_terms=no; security_terms='Secur'; governance_terms=none |
| Vidoc Security Lab | adjacent | ai_terms=no; security_terms='Secur'; governance_terms=none |
| Willow | adjacent | ai_terms=yes; security_terms='secur'; governance_terms=none; security mentioned but AI not tied to the security claim |
| Xage Security | adjacent | ai_terms=no; security_terms='protect'; governance_terms=none |
| YourFinestOut | IDC™ | adjacent | ai_terms=no; security_terms=none; governance_terms='accountab' |
| Yubico | adjacent | ai_terms=no; security_terms='protect'; governance_terms=none |
| ZeroEyes | adjacent | ai_terms=yes; security_terms=none; governance_terms=none; physical_security='gun' |
| Zscaler | adjacent | ai_terms=no; security_terms='cyber'; governance_terms='trust' |
| eMudhra | adjacent | ai_terms=no; security_terms='Zero Trust'; governance_terms='Trust' |
| 31 CONCEPT | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| AdaptMMS | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Alpha Q - Algoritmus | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Anvaya Insights | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| CARPL.ai | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| CLUSH | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Certus Core | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| DAXA | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| EBI Labs | out_of_scope | ai_terms=no; security_terms=none; governance_terms=none |
| Experian | out_of_scope | ai_terms=no; security_terms=none; governance_terms=none |
| GotYu | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| HAIEC | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| HoundDog.ai | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| IBM | out_of_scope | ai_terms=no; security_terms=none; governance_terms=none |
| Inforcer | out_of_scope | ai_terms=no; security_terms=none; governance_terms=none |
| Iroun & Company | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Istreno | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Metaworkers.AI | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Microsoft | out_of_scope | ai_terms=no; security_terms=none; governance_terms=none |
| Netomi | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Nokia | out_of_scope | ai_terms=no; security_terms=none; governance_terms=none |
| Nuvoryn | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Optical Standard Technology | out_of_scope | ai_terms=no; security_terms=none; governance_terms=none |
| SARTI - Striker AI Research Tech Inc | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| ServiceNow | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Tigera | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Unloq AI | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none |
| Vivox AI | out_of_scope | ai_terms=yes; security_terms=none; governance_terms=none; ai_for_security_signals=['AI agents that automate'] |
