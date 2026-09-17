# Atlas Cover — QE runtime setup

[Agent overview and diagrams](agents-overview.md) · [Demo walkthrough](README.md)

You'll need Node.js 22 or later, [Rook](https://github.com/LambdaTest/rook), and an OpenAI API key. The URLs and model are already configured.

## Start the app

From the repository root:

```bash
npm ci
cd demos/06-insurance-no-code
npm run setup
```

`npm ci` installs the packages needed by the demo using the repository's saved versions. Run it once for a fresh checkout. Setup creates this folder's .env without changing existing settings.

Add your key to .env:

```dotenv
MODEL_API_KEY=your-openai-api-key
```

Or use your terminal's environment:

```bash
export MODEL_API_KEY="your-openai-api-key"
```

An exported key takes priority over the file. The .env file must still exist. Only MODEL_API_KEY is read automatically; keys named OPENAI_API_KEY or GEMINI_API_KEY need to be assigned to MODEL_API_KEY.

```bash
npm start
```

Open **http://127.0.0.1:4315**, or the address printed in the terminal. Keep it running. To check your key separately, use `npm run check:llm`; this makes a model request.

## Open interactive Rook

In a second terminal, enter the same demo folder. Prepare it once:

```bash
rook login
rook project create "Rook Customer Demos"
npm run rook:setup
```

Use `rook project use PROJECT_ID` if you already have a project. Skip setup for an already prepared demo.

```bash
npm run rook
```

Follow the [interactive demo guide](../../docs/testing-with-rook.md). Commands such as `/guide`, `/run`, `/report` and `/ui` are entered inside Rook. Rook sign-in is separate from your model key; both services may charge for usage.

## Common questions

| Question | Answer |
|---|---|
| Do I need to change the other .env values? | No. OpenAI, gpt-4.1-mini and this app's URL are preset. |
| Why isn't my new key being used? | Restart the app. An exported value wins, even if empty; `unset MODEL_API_KEY` returns to the file's value. |
| What if the key is missing? | Startup explains which setting is missing. It does not switch to scripted responses. |
| What if the provider returns an error? | Check your key, account permissions and available quota. |
| The port is already in use. | Run `export DEMO_PORT=14320` in both terminals before starting the app and Rook. |
| Rook says the workspace is not empty. | It is already prepared. Run `npm run rook` to reuse it. |
| Can I share my configuration? | Share .env.example. Your .env, conversations and local reports are excluded from Git. |

For another provider, a separate workspace or connection changes, see [integration details](../../docs/rook-integration.md).
