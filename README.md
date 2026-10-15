# HyphosXAI · Agent Business-Process Demo

A minimal, runnable example of a business process carried out by small cooperating
agents, with a **human approval gate** and an **audit trail**.

> **Illustrative sample only.** This repository is a simplified teaching example. It is
> not HyphosXAI Ltd's product and does not reflect any production system.

## What it shows

An *inbound enquiry triage* flow, using fictional enquiries:

1. **Intake agent**: classifies each enquiry (support, sales, partnership, general) and flags urgency.
2. **Drafting agent**: drafts a reply from simple templates.
3. **Reviewer agent**: checks the draft against plain rules (no promises such as
   "guarantee" or "refund", a length limit, recipient in the demo domain).
4. **Human approval gate**: a person approves or rejects each draft before anything
   could be sent.
5. **Audit trail**: every handoff and decision is recorded and printed at the end.

**Nothing is ever sent.** Approved drafts are only marked "queued (NOT sent)".

## How to run

Requires Python 3.8+ and the standard library only. No API keys, no network.

```bash
python3 demo.py                # simulated human approves only reviewer-passed drafts
python3 demo.py --interactive  # you are the human: approve each draft with y/N
```

The sample data is in `sample_enquiries.json`. All names and `example.com` addresses are fictional.

## Design idea

- **Small agents, one job each.** Each agent is a plain function with a clear input and output.
- **Clear handoffs.** Data passes as simple dictionaries, so every step can be inspected and tested.
- **A human approval gate.** Agents propose, people decide. Nothing leaves the system without a person's approval.
- **An audit trail.** Every step is logged with time, actor, action and detail.

## Extending it

- **Plug in a model.** `llm_hook()` in `demo.py` is a clearly marked hook. Return text
  from any language model there and the drafting agent will use it in place of the templates.
- Add agents, for example language detection, sentiment or routing to a team queue.
- Load reviewer rules from a config file, or add a "rework" loop that sends flagged drafts back to drafting.
- Write the audit trail to a file or database, and use a real inbox and approval UI.

## About

Built by HyphosXAI Ltd · [hyphosxai.com](https://hyphosxai.com)

Copyright 2026 HyphosXAI Ltd. Released under the MIT License (see `LICENSE`).
