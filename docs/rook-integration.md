# Connection and prepared-workspace details

The [interactive workflow](testing-with-rook.md) starts with exploration and local artifacts. Use this page for connection details or a shorter session with the supplied scenario pack.

## Explore and generate interactively

Keep the app running. From the repository root, prepare a new, empty workspace:

```bash
npm run rook:prepare -- insurance-agent-code /tmp/insurance-exploration
cd /tmp/insurance-exploration
rook
```

For the QE edition, use `insurance-agent` and a different empty directory. The Developer workspace includes agent source; the QE workspace contains requirements and connection information.

Inside Rook, select a project with `/project` and follow `/guide`. Then enter:

```text
/explore . Read PRD.md as the required behavior and inspect the supplied agent material.
/agent
/generate --class functional,non_functional,adversarial --total 18
/scenarios list
/profile add http --from connection.md
/profile test http
/run --test --profile http
/report
```

Review the discovered agent and generated tests. For the connection, provide `connection.md` and ask Rook to reuse one conversation across all turns. Test the profile using the name Rook creates before running its scenarios. Generating 18 tests does not guarantee every category is covered; compare against the [category list](category-coverage.md).

This workflow discovers and generates new material. The quick start instead loads the supplied authored examples for a repeatable presentation.

## Use the prepared scenario pack

Select a Rook project in the repository root or edition folder, then run `npm run rook:setup` in the edition folder. This creates a separate workspace with 18 authored scenarios and the supplied HTTP and MCP profiles. Open it with `npm run rook`.

```text
/scenarios list
/profile show demo-normal
/profile test demo-normal
/run --test --only SC-101 --profile demo-normal
/report
```

This path reuses reviewed definitions; it does not represent a new exploration or generation. Existing workspaces and evidence are preserved.

## Optional settings

Export these in the relevant terminal before starting the app or Rook:

| Setting | When to use it |
|---|---|
| `DEMO_VARIANT=hardened` | Test the repaired agent in Rook. |
| `DEMO_PORT=14320` | Use another local port; set it in both terminals. |
| `ROOK_DEMO_WORKSPACE=/absolute/path` | Prepare or open a separate Rook workspace. Preparation requires an empty directory. |
| `MODEL_BASE_URL`, `MODEL_NAME` | Use another provider compatible with Chat Completions and tool calling. Check it with `npm run check:llm`. |
| `DEMO_API_TOKEN` | Protect an API-only target. Leave unset for the browser demo. |

Exported values override the selected demo's .env. Other folders' .env files are not read, and values in .env do not expand shell commands. A custom DEMO_BASE_URL takes priority over the URL inferred from DEMO_PORT. Model credentials stay with the app and are not forwarded to the Rook launcher.

## MCP and evidence

The prepared `demo-mcp` profile can call the agent and collect its evidence. The read-only verification tools are `inspect_session` and `read_business_effects`; they read the same conversation's records without performing a business action.

To connect a separate MCP client, use `node /absolute/path/to/rook-demo/scripts/mcp.mjs insurance-agent-code`. Add `--target` for agent invocation tools. Use Node directly so npm's banner does not enter the MCP connection.

The connection guide in each demo describes the five stages: prepare, open, execute, close and collect. Each scenario gets its own conversation. Tool calls, local traces and business receipts are collected into the Rook report; the demo does not export OpenTelemetry data.

The hooks return both `output` and `agent_reply` for compatibility and save a separate evidence file per conversation. Provider usage must be complete before enabling cost tests. Some Rook versions may show native call assertions as Unable to Verify even when receipt criteria can be judged; retain that distinction in the report.

## Optional hosted review

Inspect the local files and `/report` first. To share the prepared pack, run `/sync`, then `/run --only SC-101 --profile demo-normal`, and open `/ui`. This creates a new shared run. An earlier `--test` run remains local and is not promoted by sync. Exploration, generation and local test artifacts remain under `.testmuai/rook/`; `/ui --local` can display those files when wanted.

The demo launcher includes a compatibility adapter for the current CLI and hosted API: it sends hand-authored scenario origin as `manual`, retaining `author: user`, the original YAML and content hash. It also preserves the recorded authorship of unchanged insurance features. This addresses the hosted sync HTTP 500 observed on 2026-09-17; it does not alter test criteria or results. Use `npm run rook -- DEMO_NAME` so interactive sync receives the adapter.

## Rebuild and check the repository

```bash
node scripts/build-catalog.mjs
npm run docs:build
npm test
npm run check
npm run rook:coverage
```

The catalogue builder updates all eight demo guides and templates. It preserves private .env files. Open the generated walkthrough HTML in Chrome and print to PDF to refresh the shareable presentation.

Product references: [interactive terminal](https://www.testmuai.com/support/docs/rook-command-start/), [exploration](https://www.testmuai.com/support/docs/rook-command-explore/), [profiles](https://www.testmuai.com/support/docs/rook-command-profile/), [MCP](https://www.testmuai.com/support/docs/rook-command-mcp/).
