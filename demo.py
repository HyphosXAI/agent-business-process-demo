#!/usr/bin/env python3
"""Agent business-process demo: inbound enquiry triage with a human approval gate.

Illustrative sample only. Copyright 2026 HyphosXAI Ltd. MIT licence.
Standard library only; the "agents" are simple rule-based stubs. Nothing is ever sent.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

AUDIT = []  # append-only audit trail of every handoff and decision


def log(actor, action, detail):
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    AUDIT.append((stamp, actor, action, detail))
    print(f"  [{actor}] {action}: {detail}")


# --- Optional LLM hook -------------------------------------------------------
# Replace this function to plug in a language model. It receives a prompt and
# must return text. The default returns None so the rule-based stubs are used.
def llm_hook(prompt):
    return None


# --- Agent 1: intake ---------------------------------------------------------
CATEGORIES = {
    "support": ["broken", "error", "not working", "help", "issue"],
    "sales": ["quote", "buy", "demo", "interested", "trial"],
    "partnership": ["partner", "collaborate", "integration"],
}


def intake_agent(enquiry):
    text = (enquiry["subject"] + " " + enquiry["body"]).lower()
    scores = {cat: sum(word in text for word in words) for cat, words in CATEGORIES.items()}
    category = max(scores, key=scores.get) if any(scores.values()) else "general"
    urgent = any(word in text for word in ("urgent", "asap", "today"))
    result = {"category": category, "urgent": urgent}
    log("intake", "classified", f"{category}{' (urgent)' if urgent else ''}")
    return result


# --- Agent 2: drafting -------------------------------------------------------
TEMPLATES = {
    "support": "Thanks for letting us know about the problem. We're looking into it "
               "and will come back to you with next steps.",
    "sales": "Thanks for your interest. We'd be glad to arrange a short call to "
             "understand what you need.",
    "partnership": "Thanks for reaching out about working together. We'll review "
                   "your note and suggest a time to talk.",
    "general": "Thanks for your message. We'll review it and get back to you.",
}


def drafting_agent(enquiry, triage):
    first_name = enquiry["name"].split()[0]
    body = llm_hook(f"Draft a short, polite reply to: {enquiry['body']}")
    if body is None:
        body = TEMPLATES[triage["category"]]
    if triage["urgent"]:
        body += " We've marked this as a priority."
    questions = [q.strip() + "?" for q in enquiry["body"].split("?")[:-1]]
    if questions:  # naive stub: echo the customer's last question back
        body += f'\n\nOn your question "{questions[-1].split(". ")[-1]}": we\'ll cover it in full.'
    draft = {
        "to": enquiry["email"],
        "subject": "Re: " + enquiry["subject"],
        "body": f"Hi {first_name},\n\n{body}\n\nKind regards,\nThe Team",
    }
    log("drafting", "drafted reply", draft["subject"])
    return draft


# --- Agent 3: reviewer -------------------------------------------------------
BANNED_PHRASES = ["guarantee", "free", "refund", "price"]  # never promise these
MAX_WORDS = 120


def reviewer_agent(draft):
    issues = []
    lowered = draft["body"].lower()
    issues += [f"contains '{p}'" for p in BANNED_PHRASES if p in lowered]
    if len(draft["body"].split()) > MAX_WORDS:
        issues.append(f"longer than {MAX_WORDS} words")
    if not draft["to"].endswith("@example.com"):
        issues.append("recipient outside the demo domain")
    verdict = "pass" if not issues else "flag"
    log("reviewer", verdict, "; ".join(issues) or "all rules met")
    return {"verdict": verdict, "issues": issues}


# --- Human approval gate -----------------------------------------------------
def human_gate(draft, review, auto=None):
    print("\n    ---- draft for human review ----")
    print("    To: " + draft["to"] + "\n    Subject: " + draft["subject"])
    print("\n".join("    | " + line for line in draft["body"].splitlines()))
    print(f"    Reviewer verdict: {review['verdict']}")
    if auto is not None:
        decision = auto(draft, review)
    else:
        decision = input("    Approve? [y/N] ").strip().lower() == "y"
    log("human", "approved" if decision else "rejected", draft["subject"])
    return decision


def run(enquiries, auto=None):
    for enquiry in enquiries:
        print(f"\n=== Enquiry {enquiry['id']}: {enquiry['subject']} ===")
        log("system", "received", f"{enquiry['id']} from {enquiry['email']}")
        triage = intake_agent(enquiry)
        draft = drafting_agent(enquiry, triage)
        review = reviewer_agent(draft)
        if human_gate(draft, review, auto):
            # In a real system this is where the send would happen. Not here.
            log("system", "queued (NOT sent)", "demo never sends anything")
        else:
            log("system", "held", "returned for rework")


def main():
    interactive = "--interactive" in sys.argv
    data = Path(__file__).with_name("sample_enquiries.json")
    enquiries = json.loads(data.read_text())
    # Non-interactive default: a simulated human approves only reviewer-passed drafts.
    auto = None if interactive else (lambda d, r: r["verdict"] == "pass")
    print("HyphosXAI agent business-process demo (illustrative sample)")
    run(enquiries, auto)
    print("\n=== Audit trail ===")
    for i, (stamp, actor, action, detail) in enumerate(AUDIT, 1):
        print(f"{i:02d} {stamp}Z {actor:<9} {action:<18} {detail}")
    print("\nNothing was sent.")


if __name__ == "__main__":
    main()
