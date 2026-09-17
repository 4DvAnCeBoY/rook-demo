# Rook demo agents

See how Rook tests AI agents through everyday customer journeys: moving money, booking appointments, settling claims and processing refunds. Each demo includes a chat application, agent diagrams, and examples of issues Rook can find.

Choose **Developer** to explore the agent's code, or **QE** to work from requirements and the agent connection. Both use interactive Rook.

| Industry | Developer | QE |
|---|---|---|
| Banking | [banking-agent-code](demos/01-banking-code/README.md) | [banking-agent](demos/02-banking-no-code/README.md) |
| Healthcare | [healthcare-agent-code](demos/03-healthcare-code/README.md) | [healthcare-agent](demos/04-healthcare-no-code/README.md) |
| Insurance | [insurance-agent-code](demos/05-insurance-code/README.md) | [insurance-agent](demos/06-insurance-no-code/README.md) |
| Customer Support | [customer-support-agent-code](demos/07-customer-support-code/README.md) | [customer-support-agent](demos/08-customer-support-no-code/README.md) |

## Start here

You'll need Node.js 22 or later, [Rook](https://github.com/LambdaTest/rook), and an OpenAI API key. Open a terminal in this repository:

```bash
npm ci
npm run setup
```

`npm ci` installs the packages this demo needs, using the versions recorded in the repository. You only need to install them once for a fresh checkout.

For the insurance example, add your key to `demos/05-insurance-code/.env`. The model and URLs are already filled in. An existing exported `MODEL_API_KEY` also works and takes priority over the file.

```bash
npm run demo -- insurance-agent-code
```

Open the address printed in the terminal and try: **“Settle claim CLM-100 for USD 1500.”** Keep this terminal running.

## Open interactive Rook

In a second terminal at the repository root, prepare the demo once:

```bash
rook login
rook project create "Rook Customer Demos"
npm run rook:setup -- insurance-agent-code
```

If you already have a project, use `rook project use PROJECT_ID` instead of creating one. Skip setup when this demo is already prepared.

Open Rook for this demo:

```bash
npm run rook -- insurance-agent-code
```

This opens Rook's interactive terminal. Type the following **inside Rook**, one at a time:

```text
/scenarios list
/profile test demo-normal
/run --test --only SC-101 --profile demo-normal
/report
/ui --local
```

Follow Rook's prompts. The last command opens the local results page, where you can inspect the conversation, tool trace and report. Use `/guide` for help and `/exit` to leave Rook. Testing uses your model and Rook accounts.

## Continue the demo

- [Interactive demo guide](docs/testing-with-rook.md): compare before and after a fix, test multi-turn conversations, red-team attacks and MCP.
- [Visual walkthrough](docs/demo-walkthrough.html) · [PDF](docs/demo-walkthrough.pdf): introduce the agents and explain their results.
- [Setup help](docs/runtime-setup.md): key configuration and common startup issues.
- [Red-teaming handout](docs/red-teaming.pdf): a two-page introduction with customer examples and diagrams.
- [Recorded runs in CI](docs/sample-runs.md): inspect saved results and demonstrate a blocking check.

Every demo folder includes its own instructions and **agents-overview.md** with diagrams and functions. There are 18 scenario categories per demo across functional, non-functional and adversarial testing; see [coverage](docs/category-coverage.md). All customer records and business systems are fictional.

For contributors: [integration details](docs/rook-integration.md) and [verification notes](docs/verification.md).
