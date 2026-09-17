# Screenshot sources

These are browser captures of the actual local applications, made on 2026-09-16. They contain fictional customer records. Report values, criteria and evidence were not rewritten for the guide.

| Image | Source and framing |
|---|---|
| banking-application.png | Banking Developer demo, Before the fix, over-limit transfer request. Full application capture from the browser checks. |
| rook-agent.png | Rook local UI agent list. The focused banking workspace contains eight discovered features, two reviewed scenarios and three recorded runs. |
| rook-scenario.png | Rook scenario SC-001, run 2026-09-16T12-15-49Z. Element capture of criterion C2 showing the failed business-receipt expectation and observed transfer. |
| rook-report-before.png | Viewport capture of the report summary for run 2026-09-16T12-15-49Z: 0 Pass, 1 Fail, 1 Unable to Verify. |
| rook-report-after.png | Viewport capture of the report summary for run 2026-09-16T12-18-15Z: 1 Pass, 0 Fail, 1 Unable to Verify. |

The report screenshots show selected summary areas; the recorded outcomes and limitations are described in [verification.md](../verification.md). These are recorded examples, not newly executed runs. The guide explicitly distinguishes the focused banking example from the full scenario inventory.

Run `npm run docs:build` from the repository root to regenerate the Markdown and self-contained HTML using these captures. To refresh the PDF, open the HTML document in Chrome and print it to PDF; its print stylesheet preserves the chapter sequence and diagrams.
