# Agent Assurance — ROOK

Explore an agent, generate tests, prove its connection and inspect the evidence. The applications cover banking, healthcare, insurance and customer support, with separate workflows for Developers and Quality Engineers.

| Industry | Developer: source and requirements | QE: requirements and connection |
|---|---|---|
| Banking | [banking-agent-code](demos/01-banking-code/README.md) | [banking-agent](demos/02-banking-no-code/README.md) |
| Healthcare | [healthcare-agent-code](demos/03-healthcare-code/README.md) | [healthcare-agent](demos/04-healthcare-no-code/README.md) |
| Insurance | [insurance-agent-code](demos/05-insurance-code/README.md) | [insurance-agent](demos/06-insurance-no-code/README.md) |
| Customer Support | [customer-support-agent-code](demos/07-customer-support-code/README.md) | [customer-support-agent](demos/08-customer-support-no-code/README.md) |

## Watch the recorded walkthroughs

The [video library](delivery/README.md) includes all nine generated MP4s: the workflow overview and eight industry editions, narrated by Andrew in American English with no added scene pauses. Captions, chapter markers and posters are included.

Run `npm run videos` and open <http://127.0.0.1:65213> to use the playback library, or download individual videos from the library's file table.

## Start an application

You need Node.js 22 or later, Rook and an OpenAI API key. From a fresh checkout:

```bash
npm ci
npm run setup -- insurance-agent-code
```

`npm ci` installs the saved package versions. Add `MODEL_API_KEY` to `demos/05-insurance-code/.env`; the model and URLs are already configured. An exported key also works and takes priority.

```bash
npm start -- insurance-agent-code
```

Open the printed address. Meet the customer, inspect the tools and follow the agent diagram before testing. Use any edition name from the table in place of `insurance-agent-code`.

## Discover and test in interactive Rook

Keep the application running. Prepare an empty workspace in a second terminal:

```bash
npm run rook:prepare -- insurance-agent-code /tmp/insurance-agent-code
cd /tmp/insurance-agent-code
rook login
rook project create "Agent Assurance — Insurance"
rook
```

Choose another empty directory if this one already exists. Use `rook project use PROJECT_ID` when reusing a project.

Inside Rook, review the prompts as you proceed:

```text
/explore . Read PRD.md as the required behavior and inspect the supplied agent material.
/generate --class functional,non_functional,adversarial --total 18
/scenarios list
/profile add http --from connection.md
/profile test http
/run --test --profile http
/report
```

Review the generated tests before running them. Rook writes agent definitions, features, scenarios, profiles and evidence under **.testmuai/rook/** in this workspace. Inspect those files and the local report first.

## Share a reviewed run, if needed

```text
/sync
/run --profile http
/ui
```

Sync records the project definitions. The next run creates a **new shared result** in the hosted Web UI. The earlier `--test` run remains local. Rook's optional `/ui --local` viewer reads files on this machine.

[Interactive workflow](docs/testing-with-rook.md) · [Agent architecture and walkthrough](docs/demo-walkthrough.html) · [Recorded results and limits](docs/verification.md)

Every edition includes an agent overview, connected diagrams, setup instructions and an authored pack covering 18 categories. [Coverage](docs/category-coverage.md) describes that inventory; executed results establish what passed or failed. The [prepared-pack workflow](docs/rook-integration.md) provides a shorter starting point with existing scenarios and profiles.

All customer records and business systems are fictional. Model requests and Rook judging use their respective services.
