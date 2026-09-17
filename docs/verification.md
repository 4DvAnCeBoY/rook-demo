# Recorded checks and known limits

Recorded on 2026-09-17 for Banking, Healthcare, Insurance and Customer Support, with Developer and QE editions.

| Check | Result |
|---|---|
| Runtime, configuration and evidence checks | 35 passed |
| Demo folder checks | Eight demos include setup, diagrams, functions and all 18 categories |
| Scenario inventory | 144 authored scenarios validated |
| Desktop/mobile browser checks | 128 checks passed across all eight apps |
| Controlled application rehearsals | 288 scenario/version results across 384 samples; deliberate failures retained |
| Insurance model and Rook runs | 72 HTTP results and six MCP results |
| Insurance evidence review | 102 distinct captured samples matched their original observations |
| Interactive Rook smoke check | Terminal opened, 18 scenarios listed, connection checked and one insurance scenario passed |
| Fresh local Rook checks across all eight editions | 48 selected results: 42 Pass, 6 Fail, 0 Unable to Verify; 40 HTTP and 8 MCP |
| Model-backed browser recordings | 32 customer conversations across all eight editions, including two-turn journeys |
| Fresh hosted Rook checks for videos | 32 runs across all eight editions: 48 selected results, 42 Pass, 6 Fail, 0 Unable to Verify |
| Fresh checkout and GitHub CI | Node 22 workflow passed after setup, tests, inventory and recorded-evidence checks |

The fresh local checks cover normal requests, context, role-play, a selected business-rule case before and after a fix, and MCP. They do not rerun all 18 categories. Banking's approval case passed in both versions because the model refused the request. Healthcare, insurance and support retained their original failing behavior and passed the selected repaired check. The [sample index](../artifacts/reference/sample-runs.json) preserves these results separately from the earlier runs.

Application tests and controlled rehearsals check the demo implementation. Rook runs assess the agent using the selected model. The [insurance results](insurance-validation.md) retain their original date and scope.

## Findings to present honestly

The insurance payment-failure case changed from **Fail before the fix to Pass after it** in both editions. One repaired Developer run still repeated a protected marker from an untrusted note. The illustrative speed and token budgets also failed; six MCP scenarios passed.

The [recorded banking screenshots](assets/README.md) show an unauthorized-transfer case changing from Fail to Pass. A separate native call assertion remained Unable to Verify. These examples do not establish that every category passes.

Cost checks require complete provider usage. A provider may count reasoning tokens beyond the connector's input/output sum. Missing or partial usage cannot establish a passing cost result.

## Recheck your checkout

```bash
npm test
npm run check
npm run rook:coverage
```

For new model and Rook results, follow the [interactive demo guide](testing-with-rook.md). Documentation checks do not rerun historical agent judgments. Working conversations and workspaces remain excluded from Git. Selected dated reports and evidence are included as [CI samples](sample-runs.md), alongside the [portable insurance summary](../artifacts/reference/insurance-validation-summary.json).

The interactive smoke check used the existing insurance Developer workspace and model configuration. It verified SC-101 through Rook's confirmation prompt and generated a report; it was not a fresh full-suite run. Automated launcher checks cover all eight demo names, conversation-state isolation and credential handling.

The [successful CI run](https://github.com/4DvAnCeBoY/rook-demo/actions/runs/35239565040) used commit `4e9f340`. A separate fresh local checkout passed the same setup and checks without copying private configuration. CI verifies recorded evidence; it makes no new model calls.

The [hosted video validation](../artifacts/reference/hosted-video-validation.json) records a separate set of 32 non-test runs in eight hosted projects. All 48 collected samples used the model, retained separate scenario conversations, and matched the expected before/after configuration; the context checks retained two turns. Videos use Rook’s hosted web UI. The supplied hook traces are collected evidence, not an OpenTelemetry export.
