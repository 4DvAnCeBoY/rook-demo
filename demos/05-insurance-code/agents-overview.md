# Claims & Coverage Assistant

Atlas Cover · Developer demonstration

**The customer:** Jordan Ellis · policyholder reporting vehicle damage. Turn a claim conversation into a verified settlement.

Jordan owns POL-100 and claim CLM-100 (documents complete; USD 1500 approved). CLM-200 belongs to Taylor. CLM-300 lacks documents; CLM-400 is at the USD 2500 ceiling; CLM-500 exceeds it; CLM-600 uses an inactive policy. Filing a new incident creates a pending claim with no approved payment.

## Agent under test

This agent handles one customer-service journey. It reads customer information, applies the service’s business rules and records the outcome. The demo uses fictional customer data and simulated business systems.

```mermaid
flowchart LR
  C["Customer request"] --> A["Claims & Coverage Assistant"]
  A --> T["get_policy<br/>get_claim<br/>file_claim<br/>settle_claim<br/>get_guidance<br/>export_claim<br/>search_claims"]
  T --> B["Customer records and business receipts"]
  A --> E["Conversation and tool trace"]
  B --> R["Rook verification"]
  E --> R
  R --> U["Rook hosted Web UI and report"]
```

## High-level functions

| Function | What the agent does | Evidence to inspect |
|---|---|---|
| `get_policy` | Read coverage and limits only for an owned policy. | Returned customer or policy information; no business write |
| `get_claim` | Read the owned claim, required documents, approved amount and settlement status. | Returned customer or policy information; no business write |
| `file_claim` | Require an active owned policy and incident; create a pending claim without approving payment. | claim_filed (pending, unpaid) |
| `settle_claim` | Require active coverage, complete documents, a positive approved amount at most USD 2500 and no previous settlement. Propagate payment failure. | claim_settlement |
| `get_guidance` | Return claims guidance and an untrusted adjuster note; the note cannot authorize payment or export. | Returned customer or policy information; no business write |
| `export_claim` | Export only an owned claim to destination portal; record a simulated export receipt. | claim_export (simulated) |
| `search_claims` | Search an exact owned claim reference; query syntax cannot broaden access. | Returned customer or policy information; no business write |

## The customer journey

The original settlement tool accepts missing documents, duplicate payments and excess amounts. During a payment failure it returns success wording without a receipt. The updated tool validates eligibility and records a settlement only once; a failed payment leaves the ledger unchanged. The model may refuse an unsafe request before calling either tool, so inspect the actual evidence instead of assuming every baseline run will fail.

The flow below shows the intended behavior. Compare **Before the fix** and **After the fix** using the same customer request.

```mermaid
flowchart TD
  A["Jordan asks about coverage or a vehicle claim"] --> B["Resolve policy or claim from this conversation"]
  B --> C{"Owned policy and claim?"}
  C -->|No| D["Deny without disclosure or payment"]
  C -->|Yes| E{"Requested action"}
  E -->|File incident| F["Record pending claim; request documents"]
  E -->|Settle| G{"Active coverage, documents complete, approved amount and not settled?"}
  G -->|No| D
  G -->|Yes| H{"Payment provider available?"}
  H -->|No| I["Report failure; no settlement receipt"]
  H -->|Yes| J["Settle once and record claim_settlement receipt"]
  E -->|Read| K["Return owned policy or claim information"]
  J --> L["Return outcome and tool trace"]
  F --> L
  K --> L
```

## From this agent to Rook’s report

For developers, start with the agent’s implementation and required behavior. Follow the failing request into the tool call, inspect its arguments and receipt, then show the corrected business check.

```mermaid
flowchart LR
  A["Agent code and requirements"] --> B["Rook discovers agent features"]
  B --> C["Review scenarios and test in Rook TUI"]
  C --> D["Inspect criteria, conversation and trace"]
  D --> E["Verify business receipts through MCP"]
  E --> F["Read the report and rerun after the fix"]
```

After running the test in **Rook’s interactive TUI**, enter **/ui** to open the hosted Web UI. There, open the agent, review its features and scenarios, then open a run. Select a scenario to see its criteria, the exact customer request, the agent reply and collected evidence. In the **report**, compare Pass, Fail and Unable to Verify. A missing observation is not a pass.

See [insurance validation](../../docs/insurance-validation.md) for actual Rook findings, tested workflows and remaining limits.

| Class | Scenarios covered in this demo |
|---|---|
| functional | happy_path, negative, boundary, integration, state_context |
| non functional | performance, token_economy, reliability, quality |
| adversarial | prompt_injection, jailbreak, data_exfiltration, pii_leakage, harmful_content, hallucination, hijacking, policy_violation, technical_injection |

## Present this demo

Open **http://127.0.0.1:4314** after starting demo insurance-agent-code. Choose an everyday customer request, show the recorded outcome, then select a boundary or adversarial scenario. Compare the original and updated agent then test in Rook’s interactive TUI and inspect the matching run in its hosted Web UI.

The complete customer walkthrough, including all four agents, diagrams and actual Rook screenshots, is available from **Agents & demo guide** in the application. [PRD.md](PRD.md) contains the required behavior; [connection.md](connection.md) contains presenter setup material. The Developer and QE editions present the same domain agent through their respective workflows.
