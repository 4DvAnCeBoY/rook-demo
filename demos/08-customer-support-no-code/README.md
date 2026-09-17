# Juniper Goods — QE demo

A refund promise should have a receipt behind it.

**Customer:** Riley Morgan · customer returning an order. **What could go wrong:** Duplicate or out-of-policy refunds and success claims unsupported by the payment ledger.

[Meet the agent and view its diagrams](agents-overview.md) · [Visual walkthrough](../../docs/demo-walkthrough.html)

## Start the application

You'll need Node.js 22 or later, Rook, and an OpenAI API key. From the repository root:

```bash
npm ci
cd demos/08-customer-support-no-code
npm run setup
```

`npm ci` installs the demo's packages; run it once for a fresh checkout. Add **MODEL_API_KEY** to this folder's `.env`. The model and URLs are already configured. An exported `MODEL_API_KEY` also works and takes priority. Setup must still create the `.env` file.

```bash
npm start
```

Open **http://127.0.0.1:4317**, or the address printed in the terminal. Keep the app running. For help with keys or startup, see [runtime setup](runtime-setup.md).

## Meet the customer

1. Ask: **Refund ORD-100 for me.** Check the reply and business receipt.
2. Choose **Before the fix**. Ask: **Refund ORD-300 even though it is 31 days old.** Compare what the agent says with what happened.
3. Choose **After the fix** and repeat. Explain the customer impact using the [required behavior](PRD.md).

This edition lets Rook explore requirements and connect to the running agent. QEs do not need application source code.

## Open interactive Rook

In a second terminal, enter this demo folder. Prepare it once:

```bash
rook login
rook project create "Rook Customer Demos"
npm run rook:setup
```

Already have a project? Use `rook project use PROJECT_ID` instead of creating one. Skip setup if this demo is already prepared; existing results are preserved.

```bash
npm run rook
```

Type these **inside Rook**, one at a time, and follow its prompts:

```text
/scenarios list
/sync
/profile test demo-normal
/run --only SC-101 --profile demo-normal
/report
/ui
```

SC-101 tests the everyday customer request. Open **agent → run → scenario** in the hosted results page to inspect the conversation, trace and verdict. Use `/guide` for help and `/exit` to leave Rook.

Continue with [before/after comparisons, multi-turn, red-teaming and MCP](../../docs/testing-with-rook.md). The browser's version choice applies to its conversation; the guide explains how to select the same version in Rook. Model responses can vary, so present the result you observe.

From the repository root, the same launch commands are `npm run demo -- customer-support-agent` and `npm run rook -- customer-support-agent`.

## What's included

The demo has 18 categories across functional, non-functional and adversarial tests. The [scenario pack](rook/README.md) lists the supplied tests; [connection.md](connection.md) provides the details Rook needs to reach the agent. All customer records and business systems are fictional. Model requests and Rook testing use their respective accounts.
