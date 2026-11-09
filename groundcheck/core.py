"""Offline heuristics, safe parsing, and benchmark utilities."""
from __future__ import annotations
import json
import re
from dataclasses import dataclass
from typing import Any

LABELS = ("supported", "unsupported", "insufficient_evidence")

@dataclass
class Evaluation:
    label: str
    explanation: str
    evidence: list[str]
    claims: list[dict[str, Any]]
    method: str
    raw: str = ""


def parse_evaluation(raw: str) -> Evaluation:
    """Parse a model response; fail closed if schema or label is invalid."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I).strip()
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("Model did not return valid JSON") from exc
    if not isinstance(obj, dict) or obj.get("label") not in LABELS:
        raise ValueError("Model returned an invalid overall label")
    claims = obj.get("claims", [])
    evidence = obj.get("evidence", [])
    if not isinstance(claims, list) or not isinstance(evidence, list):
        raise ValueError("Model returned invalid claims or evidence")
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("label") not in LABELS:
            raise ValueError("Model returned an invalid claim")
    return Evaluation(obj["label"], str(obj.get("explanation", "")),
                      [str(e) for e in evidence], claims, "claude", raw)


def evidence_is_verbatim(source: str, quote: str) -> bool:
    """Ensure alleged evidence appears in source (whitespace-insensitive)."""
    normalize = lambda s: " ".join(s.casefold().split())
    return bool(quote.strip()) and normalize(quote) in normalize(source)


def verify_quotes(evaluation: Evaluation, source: str) -> list[str]:
    """Return model evidence snippets that are NOT present in source."""
    quotes = evaluation.evidence[:]
    for claim in evaluation.claims:
        quote = claim.get("evidence_quote")
        if isinstance(quote, str) and quote.strip():
            quotes.append(quote)
    return [q for q in quotes if not evidence_is_verbatim(source, q)]


def naive_baseline(source: str, answer: str) -> Evaluation:
    """Deliberately weak lexical baseline; NOT a trustworthy hallucination detector."""
    def words(s: str) -> set[str]:
        return set(re.findall(r"\b[a-zA-Z]{4,}\b", s.casefold()))
    tokens = words(answer)
    overlap = len(tokens & words(source)) / len(tokens) if tokens else 0.0
    label = "supported" if overlap >= 0.65 else "insufficient_evidence"
    return Evaluation(label, f"Lexical overlap {overlap:.0%}. This is only a weak baseline, not factual verification.", [], [], "lexical_baseline")


def classification_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    """Calculate binary unsupported detection metrics; other classes count as negative."""
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("Provide equally sized, non-empty label lists")
    if any(x not in LABELS for x in y_true + y_pred):
        raise ValueError("Unknown class label")
    tp = sum(a == b == "unsupported" for a, b in zip(y_true, y_pred))
    fp = sum(a != "unsupported" and b == "unsupported" for a, b in zip(y_true, y_pred))
    fn = sum(a == "unsupported" and b != "unsupported" for a, b in zip(y_true, y_pred))
    tn = len(y_true) - tp - fp - fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"n": len(y_true), "accuracy": (tp + tn) / len(y_true), "precision": precision,
            "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn, "tn": tn}
