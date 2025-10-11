import math
from datetime import datetime, timezone

LOW_WORDS = {"later", "nice to have", "whenever"}
HIGH_WORDS = {"urgent", "asap", "eod", "priority", "blocker", "critical", "today"}


def heuristic_priority_score(action: dict) -> float:
    desc = (action.get("description") or "").lower()
    score = 0.3
    if any(w in desc for w in HIGH_WORDS):
        score += 0.4
    if any(w in desc for w in LOW_WORDS):
        score -= 0.2
    due = action.get("due_date") or action.get("dueDate")
    if due:
        try:
            dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
            hours = (dt - datetime.now(timezone.utc)).total_seconds() / 3600.0
            if hours <= 24:
                score += 0.3
            elif hours <= 72:
                score += 0.15
            else:
                score += 0.05
        except Exception:
            pass
    score = max(0.0, min(1.0, score))
    return score


def label_from_score(s: float) -> str:
    if s >= 0.75:
        return "high"
    if s >= 0.45:
        return "medium"
    return "low"


