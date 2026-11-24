"""Capability taxonomy for evaluating AI security vendors.

The taxonomy covers the two halves of the "AI security" market:

* **Security for AI** - products that protect AI systems, models, agents and
  employee AI usage.
* **AI for security** - cybersecurity products where AI / agents are the
  mechanism doing the security work.

plus **AI governance** (risk / compliance / oversight of AI).

Every domain carries regular-expression evidence patterns that are matched
against vendor text, and a mapping to public reference frameworks:

* OWASP Top 10 for LLM Applications (2025 edition) risk IDs
* NIST AI RMF 1.0 core functions (Govern, Map, Measure, Manage)
* NIST CSF 2.0 functions (Govern, Identify, Protect, Detect, Respond, Recover)

The framework mappings are the framework author's judgement of which risks /
functions a capability addresses. They are not endorsed by OWASP or NIST and
should be reviewed by the team adopting the framework.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

SECURITY_FOR_AI = "security_for_ai"
AI_FOR_SECURITY = "ai_for_security"
AI_GOVERNANCE = "ai_governance"
ADJACENT = "adjacent"
OUT_OF_SCOPE = "out_of_scope"

IN_SCOPE_SEGMENTS = (SECURITY_FOR_AI, AI_FOR_SECURITY, AI_GOVERNANCE)
ALL_SEGMENTS = IN_SCOPE_SEGMENTS + (ADJACENT, OUT_OF_SCOPE)

OWASP_LLM_2025 = {
    "LLM01": "Prompt Injection",
    "LLM02": "Sensitive Information Disclosure",
    "LLM03": "Supply Chain",
    "LLM04": "Data and Model Poisoning",
    "LLM05": "Improper Output Handling",
    "LLM06": "Excessive Agency",
    "LLM07": "System Prompt Leakage",
    "LLM08": "Vector and Embedding Weaknesses",
    "LLM09": "Misinformation",
    "LLM10": "Unbounded Consumption",
}
NIST_AI_RMF = ("Govern", "Map", "Measure", "Manage")
NIST_CSF_2 = ("Govern", "Identify", "Protect", "Detect", "Respond", "Recover")


def _rx(*patterns: str) -> tuple[re.Pattern, ...]:
    return tuple(re.compile(p, re.IGNORECASE) for p in patterns)


@dataclass(frozen=True)
class Domain:
    id: str
    name: str
    segment: str  # which segment this capability belongs to
    description: str
    patterns: tuple[re.Pattern, ...]
    owasp_llm: tuple[str, ...] = ()
    nist_ai_rmf: tuple[str, ...] = ()
    nist_csf: tuple[str, ...] = ()
    weight: float = 1.0
    # Patterns that, if present in the same text, cancel a match (false-positive guards).
    exclude: tuple[re.Pattern, ...] = field(default=())


# Shorthand fragments
_AI_OBJ = r"(?:AI|A\.I\.|artificial intelligence|LLMs?|GenAI|generative AI|models?|agents?|agentic|copilots?|MCPs?|chatbots?)"

DOMAINS: tuple[Domain, ...] = (
    # ---------------------------------------------------------------- Security for AI
    Domain(
        "ai_discovery_posture", "AI discovery, inventory & posture (AI-SPM)", SECURITY_FOR_AI,
        "Finds AI apps, models, agents and shadow AI; assesses their security posture.",
        _rx(r"shadow AI", r"AI[- ]SPM", r"\bposture\b",
            rf"\b(?:discover|inventor|visibility|observability)\w*\b(?:\W+\w+){{0,6}}?\W+{_AI_OBJ}\b",
            rf"\b{_AI_OBJ}\W+(?:\w+\W+){{0,3}}(?:discovery|inventory|visibility)\b",
            r"\bAI usage\b", r"use of AI"),
        owasp_llm=("LLM03", "LLM06"), nist_ai_rmf=("Map", "Govern"),
    ),
    Domain(
        "ai_runtime_protection", "AI runtime protection (AI firewall / guardrails)", SECURITY_FOR_AI,
        "Inspects prompts, responses and model/agent traffic at runtime and blocks attacks.",
        _rx(r"prompt[- ]injection", r"jailbreak", r"guardrail", r"\bAI firewall", r"\bfirewalls?\b",
            r"\bruntime\b", r"real[- ]time (?:monitoring|protection|controls?|firewall)", r"in-?line protection",
            r"hallucination", r"\bintercept", r"LLM workloads", r"\bimmune to prompt"),
        owasp_llm=("LLM01", "LLM02", "LLM05", "LLM07", "LLM09"), nist_ai_rmf=("Manage",),
    ),
    Domain(
        "ai_red_teaming", "AI red teaming, testing & evaluation", SECURITY_FOR_AI,
        "Adversarially tests models, apps and agents before and after deployment.",
        _rx(r"red[- ]?team", r"adversarial", r"vulnerability testing", r"security testing",
            rf"\btest\w*\b(?:\W+\w+){{0,4}}?\W+{_AI_OBJ}", r"\bevaluation\b",
            rf"offensive security for {_AI_OBJ}", r"\bassurance\b"),
        owasp_llm=("LLM01", "LLM04", "LLM07", "LLM09"), nist_ai_rmf=("Measure",),
    ),
    Domain(
        "agent_security", "AI agent & MCP security", SECURITY_FOR_AI,
        "Controls what autonomous agents, tools, plugins and MCP servers can do.",
        _rx(r"\bAI agents?\b", r"\bagentic (?:AI|workflows?|systems?|workforce)", r"\bMCPs?\b",
            r"\bplugins?\b", r"subagents?", r"autonomous (?:agent|AI|systems)", r"agent actions",
            r"\bagents? (?:security|identit|assurance)", r"AI that acts", r"coding agents"),
        owasp_llm=("LLM06", "LLM01"), nist_ai_rmf=("Manage",),
    ),
    Domain(
        "ai_identity_access", "Identity & access control for AI / non-human identities", SECURITY_FOR_AI,
        "Gives agents identities, enforces least privilege and authorises actions.",
        _rx(r"\bidentit", r"least privilege", r"\bauthori[sz]", r"\bNHI\b", r"non-human identit",
            r"\bpermissions?\b", r"\baccess (?:control|polic)", r"granular access", r"tool access"),
        owasp_llm=("LLM06",), nist_ai_rmf=("Manage", "Govern"), nist_csf=("Protect",),
    ),
    Domain(
        "ai_data_protection", "Data protection for AI (AI-DLP, leakage, privacy)", SECURITY_FOR_AI,
        "Stops sensitive data flowing into or out of AI systems.",
        _rx(r"data leak", r"sensitive data", r"exfiltration", r"\bDLP\b", r"data security",
            r"data protection", r"\bprivacy\b", r"encryption", r"vector database", r"data exposure"),
        owasp_llm=("LLM02", "LLM08"), nist_ai_rmf=("Manage",), nist_csf=("Protect",),
    ),
    Domain(
        "model_supply_chain", "Model & AI supply-chain security", SECURITY_FOR_AI,
        "Scans models, packages and datasets for tampering, poisoning or malware.",
        _rx(r"supply[- ]chain", r"model scanning", r"malicious (?:open-source )?packages", r"poisoning",
            r"model integrity", r"\bprovenance\b"),
        owasp_llm=("LLM03", "LLM04"), nist_ai_rmf=("Map", "Measure"),
    ),
    Domain(
        "ai_resource_abuse", "AI consumption & abuse controls", SECURITY_FOR_AI,
        "Rate limiting, bot protection and cost/consumption limits for AI endpoints.",
        _rx(r"rate[- ]limit", r"bot (?:protection|detection)", r"denial[- ]of[- ](?:wallet|service)",
            r"token (?:budget|usage|limits?)", r"(?:cost|consumption) (?:controls?|limits?)"),
        owasp_llm=("LLM10",), nist_ai_rmf=("Manage",),
    ),
    Domain(
        "deepfake_content_integrity", "Deepfake & content-integrity protection", SECURITY_FOR_AI,
        "Detects or prevents synthetic-media abuse and AI-generated fraud.",
        _rx(r"deepfake", r"synthetic media", r"content authenticity", r"integrity checks", r"voice clon"),
        owasp_llm=("LLM09",), nist_ai_rmf=("Manage",),
    ),
    # ---------------------------------------------------------------- AI governance
    Domain(
        "ai_governance_compliance", "AI governance, risk & compliance", AI_GOVERNANCE,
        "Policies, risk assessment, regulatory mapping (e.g. EU AI Act, ISO/IEC 42001), audit.",
        _rx(r"governance", r"\bgovern(?:s|ed|ing)?\b", r"\bcompliance\b", r"\bcompliant\b", r"risk management",
            r"\bAI risk", r"\boversight\b", r"\baudit", r"responsible AI", r"\bregulat", r"AI Act",
            r"\bISO\b", r"\bGRC\b", r"\bpolicy\b", r"\bobligations\b", r"accountab"),
        nist_ai_rmf=("Govern", "Map"), nist_csf=("Govern",),
    ),
    # ---------------------------------------------------------------- AI for security
    Domain(
        "autonomous_soc", "AI-driven / autonomous security operations", AI_FOR_SECURITY,
        "AI agents that triage, investigate and respond to alerts (AI SOC, AI SIEM).",
        _rx(r"security operations", r"\bSOC\b", r"\bSIEM\b", r"\btriage", r"\binvestigat",
            r"\balerts?\b", r"detection and response", r"\banalysts?\b", r"co-?pilot", r"\bCISO\b"),
        nist_csf=("Detect", "Respond"),
    ),
    Domain(
        "ai_offensive_security", "AI-driven offensive security / pentesting", AI_FOR_SECURITY,
        "Autonomous penetration testing and attack-surface validation.",
        _rx(r"pen(?:etration)?[- ]?test", r"attack surface", r"\bexploit", r"offensive", r"ethical hacking",
            r"\bhackers?\b", r"find(?:s)? security flaws"),
        nist_csf=("Identify",),
    ),
    Domain(
        "ai_appsec", "AI-driven application & API security", AI_FOR_SECURITY,
        "Secures code, pipelines, APIs and cloud applications using AI.",
        _rx(r"\bAppSec\b", r"\bcode(?:base)?s?\b", r"\bPR\b", r"software (?:development|delivery)",
            r"\bAPIs?\b", r"code to cloud", r"cloud applications", r"web application"),
        nist_csf=("Protect", "Identify"),
    ),
    Domain(
        "ai_threat_detection", "AI-driven threat detection & prevention", AI_FOR_SECURITY,
        "ML/AI detection of threats in email, network, endpoint, SaaS and human behaviour.",
        _rx(r"threat (?:detection|intelligence)", r"detects? threats", r"email security", r"\bphishing",
            r"behavio(?:u)?r", r"network security", r"\banomal", r"security awareness", r"cyber threats",
            r"identity theft", r"\bdeception\b", r"autonomous defen[cs]e", r"targeted cyber threats"),
        nist_csf=("Detect", "Protect"),
    ),
    Domain(
        "exposure_management", "AI-driven exposure & vulnerability management", AI_FOR_SECURITY,
        "Prioritises and remediates vulnerabilities, misconfigurations and exposures.",
        _rx(r"exposure", r"\bCTEM\b", r"vulnerabilit", r"remediat", r"risk quantification", r"\bEASM\b",
            r"third-party risk"),
        nist_csf=("Identify", "Protect"),
    ),
)

DOMAIN_BY_ID = {d.id: d for d in DOMAINS}


def domains_for_segment(segment: str) -> tuple[Domain, ...]:
    """Domains used as the denominator of breadth for a company in `segment`.

    Security-for-AI vendors are measured against the security-for-AI domains plus
    governance (governance is a common adjunct). AI-for-security vendors against
    the AI-for-security domains plus data protection and identity, which AI-native
    security vendors also deliver. Governance vendors against governance plus the
    discovery and identity domains that governance products commonly include.
    """
    if segment == SECURITY_FOR_AI:
        return tuple(d for d in DOMAINS if d.segment in (SECURITY_FOR_AI, AI_GOVERNANCE))
    if segment == AI_FOR_SECURITY:
        return tuple(d for d in DOMAINS if d.segment == AI_FOR_SECURITY
                     or d.id in ("ai_data_protection", "ai_identity_access"))
    if segment == AI_GOVERNANCE:
        return tuple(d for d in DOMAINS if d.id in
                     ("ai_governance_compliance", "ai_discovery_posture", "ai_identity_access", "ai_red_teaming"))
    return ()


# ------------------------------------------------------------------ segment signals
# Signals used to decide *whether* a company is an AI security company and which segment.

AI_TERMS = re.compile(
    r"\bAI\b|\bA\.I\.|artificial intelligence|machine learning|\bML\b|\bLLMs?\b|GenAI|generative AI|"
    r"\bagentic\b|\bAI[- ]\w+|\bneural\b|deepfake|\bprompts?\b|\bMCPs?\b|language models?|\bagents?\b",
    # NB: case-sensitive for the bare token "AI" so that words like "said"/"air" never match.
)
AI_TERMS_CI = re.compile(r"artificial intelligence|machine learning|generative ai|agentic|deepfake|"
                         r"language model|prompt injection", re.IGNORECASE)

SECURITY_TERMS = re.compile(
    r"secur|cyber|threat|attack|vulnerab|pen(?:etration)?[- ]?test|red[- ]?team|firewall|exfiltration|"
    r"\bDLP\b|guardrail|\bprotect|\bSOC\b|\bSIEM\b|detection and response|AppSec|exploit|least privilege|"
    r"zero[- ]trust|prompt[- ]injection|deception|malicious|jailbreak|offensive|hack|deepfake misuse|"
    r"\bunsafe actions|authori[sz]ation|safe to deploy|\bsafety\b",
    re.IGNORECASE,
)

GOVERNANCE_TERMS = re.compile(
    r"governance|\bgovern(?:s|ing)?\b|compliance|compliant|risk management|\bAI risk|oversight|\baudit|responsible AI|"
    r"\bregulat|AI Act|ISO 42001|\bGRC\b|accountab|\btrust\b|obligations",
    re.IGNORECASE,
)

# "AI is the thing being protected".
# Strong signals name AI/agents/models as the explicit object of protection.
SECURITY_FOR_AI_SIGNALS = _rx(
    r"security for AI", r"cybersecurity for AI", r"AI(?: and| &)? agent security", r"\bAI (?:and|&) API security",
    r"\bsecur(?:e|es|ing)\W+(?:\w+\W+){0,5}?(?:AI|LLM|GenAI|generative AI|artificial intelligence|agents?|agentic|"
    r"models?|MCPs?|copilots?)\b",
    r"protect\w*\W+(?:\w+\W+){0,5}?(?:AI|LLM|artificial intelligence|agents?|models?)\b",
    r"\bAI (?:and )?(?:agent )?risks?\b", r"risks? (?:associated with|of|from) AI", r"shadow AI",
    r"prompt[- ]injection", r"\bjailbreak", r"\bguardrails?\b", r"\bAI firewall",
    r"red[- ]?team\w*", r"\bMCPs?\b", r"agent (?:identit|actions|assurance)", r"AI agents? (?:with|and their)",
    r"(?:monitor|control|govern)\w*\W+(?:\w+\W+){0,4}?(?:AI|agents)\b(?:\W+\w+){0,6}?\W+(?:secur|risk)",
    r"least privilege for (?:every )?AI", r"control\w*\W+(?:\w+\W+){0,3}?(?:use|usage) of AI", r"safety and security of", r"safe to deploy", r"AI usage control",
    r"deepfake misuse", r"LLM (?:security|workloads)", r"for AI that acts",
    r"authori[sz]ation (?:layer|infrastructure) for AI",
    r"(?:authori[sz]ation|control) (?:layer|plane)\W+(?:\w+\W+){0,5}?(?:AI|agent)",
    r"security control plane", r"enterprise AI security",
)
# Weak signal: the bare phrase "AI security" is used both for "security of AI" and
# "security done by AI", so it counts half.
WEAK_SECURITY_FOR_AI_SIGNALS = _rx(r"\bAI security\b(?! (?:engineer|agents?))")
WEAK_WEIGHT = 0.5

# "AI is the mechanism doing security work"
AI_FOR_SECURITY_SIGNALS = _rx(
    r"AI[- ](?:native|powered|driven|first|enabled)\W+(?:\w+\W+){0,4}?(?:secur|cyber|AppSec|data security|"
    r"protection|defen[cs]e)",
    r"(?:agentic|autonomous)\W+(?:\w+\W+){0,3}?(?:security operations|SOC|security agents?|defen[cs]e|"
    r"exposure|remediation|security platform)",
    r"agentic (?:email )?security", r"agentic AI (?:platform that executes|security mesh)",
    r"AI security agents?", r"AI agents? that (?:do|automate|perform)", r"uses? (?:agentic )?(?:artificial intelligence|AI|ML)",
    r"using (?:artificial intelligence|AI|machine learning)", r"(?:artificial intelligence|AI|machine learning) and human",
    r"uniting AI and human", r"Security Awareness with Agentic AI", r"AI Security Engineer",
    r"security co-?pilot", r"AI-powered behavioural", r"exploit-based agentic", r"autonomous agents to",
    r"autonomous agents and", r"Agentic AI Security and Compliance Officer",
)

PHYSICAL_SECURITY = re.compile(
    r"\bgun\b|firearm|camera|surveillance|\brobot|physical security|property-management", re.IGNORECASE)
