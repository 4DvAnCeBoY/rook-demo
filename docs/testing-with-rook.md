# Give an interactive Rook demo

Start the customer application using the selected demo's README. Keep it running, then open a second terminal in that demo folder:

```bash
npm run rook
```

This opens [interactive Rook](https://www.testmuai.com/support/docs/rook-command-start/). If this is your first run, follow the README's one-time Rook setup first. Type the commands below **inside Rook**, one at a time, and follow its prompts. Use `/guide` for help.

## Start with a customer request

```text
/scenarios list
/sync
/profile test demo-normal
/run --only SC-101 --profile demo-normal
/report
/ui
```

`/sync` records the prepared agent and scenarios in the hosted project. The connection check calls the agent once. SC-101 tests its everyday customer journey. In the hosted results page, open **agent → run → scenario** to see the request, reply, tool trace and business receipt.

Explain **Pass**, **Fail** and **Unable to Verify** using the evidence shown. The supplied scenarios are authored examples; exploring and generating new tests is a separate demonstration described in [integration details](rook-integration.md).

## Show an issue, then the fix

Choose a test your audience will recognize:

| Demo | Customer concern | Enter inside Rook |
|---|---|---|
| Banking | A transfer exceeds the approval limit | `/run --only SC-117 --profile demo-normal` |
| Healthcare | An urgent request goes to routine scheduling | `/run --only SC-117 --profile demo-normal` |
| Insurance | A failed payment is reported as a completed settlement | `/run --only SC-104 --profile demo-dependency-error` |
| Customer Support | A failed refund is reported as successful | `/run --only SC-104 --profile demo-dependency-error` |

Read the report and compare the reply with the recorded business action. Model responses vary; explain the result that actually occurred.

To test **After the fix**, leave Rook with `/exit`. In the same demo folder, reopen it with:

```bash
DEMO_VARIANT=hardened npm run rook
```

Run the same test again, then use `/report` and `/ui` to compare. The browser's Before/After choice controls its own conversation; this command selects the version tested by Rook.

## Show more capabilities

Choose a short follow-up rather than running the entire collection during a presentation:

| Capability | What the audience sees | Enter inside Rook |
|---|---|---|
| Multi-turn conversation | The agent remembers the previous customer request | `/run --only SC-105 --profile demo-normal` |
| Reliability | Repeated requests preserve consistent business records | `/run --only SC-108 --profile demo-normal` |
| Red-teaming | A role-play attack tries to bypass the business rule | `/run --only SC-111 --profile demo-normal` |
| Prompt injection | Instructions hidden in a retrieved note challenge the agent | `/run --only SC-110 --profile demo-poisoned-context` |
| Traces | A slow service appears in the tool trace | `/run --only SC-106 --profile demo-slow-tool` |
| MCP | Rook calls the agent through MCP and reads its evidence | `/run --only SC-101,SC-105 --profile demo-mcp` |

Before the MCP example, enter `/profile test demo-mcp`. After each example, inspect the report. Cost tests need complete provider usage; the supplied profiles leave them disabled until that information is available.

## Run the full collection

Use the connection matching each test's service condition:

```text
/run --tag fault-none --profile demo-normal
/run --category integration --profile demo-dependency-error
/run --category performance --profile demo-slow-tool
/run --category prompt_injection --profile demo-poisoned-context
/report
/ui
```

There are 18 categories in each demo. Some cases intentionally fail, and missing evidence must remain unverified. The illustrative speed and token budgets are demonstration settings.

The commands above record runs in the hosted project timeline. For a separate local experiment, `--test` keeps a run out of that timeline and `/ui --local` opens its local results. Model requests and Rook judging use their respective accounts. Use `/exit` when finished.
