# Ground-truth labeling protocol

`ground_truth_labels.csv` was written by hand **before** any classifier code existed,
from the Crunchbase short description of each company only (no website visits).
Labels are human/analyst judgment, not verified facts about the companies.

| segment | rule |
|---|---|
| `security_for_ai` | Product protects AI systems, models, agents, or employee AI usage (AI firewall/guardrails, AI-SPM, agent identity, AI red teaming, AI DLP, deepfake protection). A bare "AI security company" claim is labelled here. |
| `ai_for_security` | A cybersecurity product whose description says AI / agents / ML are the mechanism doing the security work (autonomous SOC, AI pentest, AI AppSec, AI detection). |
| `ai_governance` | Governance, risk, compliance, oversight of AI, without an explicit security-control claim. |
| `adjacent` | Security company where AI is not claimed, or AI/IT company where security is incidental, or physical-security AI. |
| `out_of_scope` | Neither cybersecurity nor AI governance. |

`label_confidence=low` marks rows where the description was ambiguous between two segments.
The 15 public incumbents were labelled from their Crunchbase description only, which is why
e.g. Microsoft and Zscaler are `adjacent`: their descriptions do not mention AI security,
not because they lack such products.
