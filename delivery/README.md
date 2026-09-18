# Agent Assurance — ROOK

Open [the video library](index.html), or run `npm run videos` from the repository root. Nine narrated 1080p films include burned-in captions and separate SRT files. The player is unmuted; click Play to hear Andrew’s American English voiceover. Chapter buttons jump to each stage.

| Film | Audience | Length | Files |
|---|---|---|---|
| Workflow overview | QE + Developer | 5:20 | [Watch](rook-overview/rook-overview.mp4) · [Captions](rook-overview/rook-overview.srt) |
| Northstar Bank | Developer | 4:19 | [Watch](banking-agent-code/banking-agent-code.mp4) · [Captions](banking-agent-code/banking-agent-code.srt) |
| Northstar Bank | QE | 4:16 | [Watch](banking-agent/banking-agent.mp4) · [Captions](banking-agent/banking-agent.srt) |
| Harbor Care | Developer | 4:16 | [Watch](healthcare-agent-code/healthcare-agent-code.mp4) · [Captions](healthcare-agent-code/healthcare-agent-code.srt) |
| Harbor Care | QE | 4:12 | [Watch](healthcare-agent/healthcare-agent.mp4) · [Captions](healthcare-agent/healthcare-agent.srt) |
| Atlas Cover | Developer | 4:22 | [Watch](insurance-agent-code/insurance-agent-code.mp4) · [Captions](insurance-agent-code/insurance-agent-code.srt) |
| Atlas Cover | QE | 4:20 | [Watch](insurance-agent/insurance-agent.mp4) · [Captions](insurance-agent/insurance-agent.srt) |
| Juniper Goods | Developer | 4:11 | [Watch](customer-support-agent-code/customer-support-agent-code.mp4) · [Captions](customer-support-agent-code/customer-support-agent-code.srt) |
| Juniper Goods | QE | 4:10 | [Watch](customer-support-agent/customer-support-agent.mp4) · [Captions](customer-support-agent/customer-support-agent.srt) |

[Agent responsibilities and connected diagrams](agent-assurance-guide.pdf) · [Red-teaming guide](red-teaming-guide.pdf)

Each edition introduces its agent, tools and business flow, then shows actual interactive Rook exploration, generation, profile creation and connection testing. Selected --test runs, reports and local files precede optional sync and a separate shared run in the hosted Web UI.

The eight workflows contain 40 selected checks: 25 Pass and 15 Fail. Banking's approval check passed before and after; healthcare, insurance and support failed their original business check and passed the same reviewed criterion after repair. Before/after scenario snapshots match exactly. The prepared inventory remains 144 cases across 18 categories; these selected recordings do not establish that all cases passed.

The healthcare Developer MCP test passes its context criteria despite the separately detected capacity defect. The healthcare QE MCP check retains that capacity failure. Earlier native-observation gaps and test-definition corrections remain in the working evidence; the overview explains one gap. Collected tool traces are JSON evidence, not an OpenTelemetry export or native MCP-proxy observation.

Run IDs, scenario IDs and conversation IDs are listed in recorded-runs.json. Customer-app conversations are separate from Rook test conversations. Each hosted chapter shows the edition's new shared run, not its earlier --test run. Local-first describes artifact ownership and review; inference and judging may still use remote services.

The edit removes idle processing. Terminal frames come from real PTY output, with contrast adjusted and the lower status area cropped. Workspace cards display selected fields from the actual files, with excerpts marked. Hosted navigation was recorded from the signed-in service; account controls were blurred. Original captures and complete artifacts remain in artifacts/local/agent-assurance.

The repository includes the nine final MP4s, captions, posters and this playback library. Run `npm run videos` from the repository root and open <http://127.0.0.1:65213> to watch locally.
