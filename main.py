# main.py
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class CustomQuestion:
    qid: str
    prompt: str
    domain: str
    is_safety_item: bool = False


@dataclass
class Facility:
    name: str
    location: str
    services: str
    contact: str


SCALE_LABELS = {
    0: "Not at all",
    1: "Several days",
    2: "More than half the days",
    3: "Nearly every day",
}

CUSTOM_QUESTIONS: list[CustomQuestion] = [
    CustomQuestion("q1", "Over the last two weeks, how often have you felt little interest or spark in things you usually enjoy?", "interest"),
    CustomQuestion("q2", "Over the last two weeks, how often have you felt weighed down, low, or discouraged?", "mood"),
    CustomQuestion("q3", "Over the last two weeks, how often have you had trouble sleeping well or woken up exhausted?", "sleep"),
    CustomQuestion("q4", "Over the last two weeks, how often have you felt low on physical or mental energy?", "energy"),
    CustomQuestion("q5", "Over the last two weeks, how often have your eating habits or appetite shifted noticeably?", "appetite"),
    CustomQuestion("q6", "Over the last two weeks, how often have you been overly hard on yourself or felt like a burden?", "self_worth"),
    CustomQuestion("q7", "Over the last two weeks, how often have you struggled to stay focused on tasks or reading?", "focus"),
    CustomQuestion("q8", "Over the last two weeks, how often have you felt unusually restless, keyed up, or slowed down?", "pacing"),
    CustomQuestion(
        "q9",
        "Over the last two weeks, how often have you had thoughts of self-harm or not wanting to be here?",
        "safety",
        is_safety_item=True,
    ),
]

SEVERITY_ACTIONS: dict[str, list[str]] = {
    "Minimal": [
        "Keep steady daily anchors (consistent sleep, movement, and regular check-ins with people you trust).",
        "Log a quick note on what is working well right now so you can revisit it later.",
    ],
    "Mild": [
        "Choose one low-effort reset today (a short walk outside, hydration, or stepping away from screens).",
        "Check in again in a week or two to see if stress is easing or building.",
    ],
    "Moderate": [
        "Consider booking a visit with a counselor, primary care clinician, or campus/community support service.",
        "Break tasks into small steps and let a trusted friend, family member, or mentor know you need extra backing.",
    ],
    "Moderately Severe": [
        "Reach out promptly to a healthcare provider or behavioral health clinic for timely support.",
        "Avoid isolating—connect with a trusted person or support line today.",
    ],
    "Severe": [
        "Seek prompt professional care or behavioral health support as soon as possible.",
        "If you feel overwhelmed or unsafe, call or text 988 (U.S. Suicide & Crisis Lifeline, available 24/7).",
    ],
}

DOMAIN_ACTIONS: dict[str, str] = {
    "sleep": "Sleep focus: Set a consistent wind-down cue and keep screens out of reach right before bed.",
    "focus": "Focus focus: Use a single 15-minute timer on one small task instead of juggling everything at once.",
    "energy": "Energy focus: Lower the bar for today—prioritize essentials and rest without guilt.",
}

DEFAULT_FACILITIES: list[Facility] = [
    Facility(
        name="988 Suicide & Crisis Lifeline",
        location="Nationwide (US)",
        services="24/7 free, confidential crisis support by call or text",
        contact="Call or text 988",
    ),
    Facility(
        name="Pierce County Crisis Line / Behavioral Health Support",
        location="Tacoma / Pierce County, WA",
        services="Local crisis response and behavioral health resource routing",
        contact="Call 988 or local crisis services",
    ),
]


def get_severity_band(total_score: int) -> str:
    """Map a 0-27 score to a severity tier."""
    if total_score < 0 or total_score > 27:
        raise ValueError(f"Score out of expected 0-27 range: {total_score}")
    if total_score <= 4:
        return "Minimal"
    if total_score <= 9:
        return "Mild"
    if total_score <= 14:
        return "Moderate"
    if total_score <= 19:
        return "Moderately Severe"
    return "Severe"


def prompt_rating(
    question: CustomQuestion,
    index: int,
    total_questions: int,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int:
    """Prompt until a valid integer from 0 to 3 is entered."""
    scale_line = " | ".join(f"{k}={v}" for k, v in SCALE_LABELS.items())
    prompt_msg = f"\n[{index}/{total_questions}] {question.prompt}\n{scale_line}\n> "

    while True:
        raw = input_fn(prompt_msg).strip()
        try:
            value = int(raw)
        except ValueError:
            output_fn("Invalid input: please enter a whole number from 0 to 3.")
            continue

        if 0 <= value <= 3:
            return value
        output_fn("Out of range: enter a whole number from 0 to 3.")


def filter_facilities(facilities: list[Facility], location_query: Optional[str]) -> list[Facility]:
    """Filter facilities by case-insensitive substring match on location; fallback to full list if empty."""
    if not location_query or not location_query.strip():
        return facilities
    needle = location_query.strip().lower()
    matches = [f for f in facilities if needle in f.location.lower()]
    return matches if matches else facilities


def evaluate_checkin(
    questions: list[CustomQuestion],
    scores: list[int],
    facilities: Optional[list[Facility]] = None,
    location_query: Optional[str] = None,
) -> dict:
    """Evaluate responses, severity band, safety trigger, actions, and facilities."""
    if len(questions) != len(scores):
        raise ValueError("Questions and scores must have the same length.")

    total = sum(scores)
    severity = get_severity_band(total)
    safety_triggered = any(
        q.is_safety_item and score > 0 for q, score in zip(questions, scores)
    )

    actions = list(SEVERITY_ACTIONS[severity])

    for q, score in zip(questions, scores):
        if score >= 2 and q.domain in DOMAIN_ACTIONS:
            tip = DOMAIN_ACTIONS[q.domain]
            if tip not in actions:
                actions.append(tip)

    if safety_triggered:
        actions.insert(
            0,
            "URGENT SAFETY SUPPORT: You indicated distress or self-harm thoughts. Call or text 988 (24/7, free, confidential in the U.S.), or call 911 / go to the nearest emergency room if you are in immediate danger.",
        )

    facility_pool = facilities if facilities is not None else DEFAULT_FACILITIES
    matched_facilities = filter_facilities(facility_pool, location_query)

    return {
        "total": total,
        "max_score": len(questions) * 3,
        "severity": severity,
        "safety_triggered": safety_triggered,
        "actions": actions,
        "facilities": matched_facilities,
    }


def format_summary(evaluation: dict) -> str:
    """Format the check-in evaluation as a readable terminal report."""
    lines = [
        "\n=== Check-In Summary ===",
        f"Score: {evaluation['total']} / {evaluation['max_score']} ({evaluation['severity']})",
    ]
    if evaluation["safety_triggered"]:
        lines.append("Safety Alert: Triggered (immediate support options prioritized above)")

    lines.append("\nRecommended Actions:")
    for action in evaluation["actions"]:
        lines.append(f"- {action}")

    lines.append("\nSupport & Care Options:")
    for fac in evaluation["facilities"]:
        lines.append(f"- {fac.name} ({fac.location}) — {fac.services} | {fac.contact}")

    return "\n".join(lines)


def run_session() -> None:
    """Run an interactive wellness check-in session."""
    print("=== Revamped PHQ-9 Wellness Check-In ===")
    print("Disclaimer: This program is for self-reflection and resource routing, not a clinical diagnosis.")

    scores: list[int] = []
    total_q = len(CUSTOM_QUESTIONS)
    for idx, question in enumerate(CUSTOM_QUESTIONS, start=1):
        scores.append(prompt_rating(question, idx, total_q))

    location = input("\nOptional city, state, or ZIP filter for care resources (press Enter to skip): ").strip()
    evaluation = evaluate_checkin(CUSTOM_QUESTIONS, scores, location_query=location)
    print(format_summary(evaluation))


def main() -> None:
    """Entry point with clean interrupt handling."""
    try:
        run_session()
    except KeyboardInterrupt:
        print("\nSession ended. If you need immediate support, call or text 988.")


if __name__ == "__main__":
    main()

def main():
    """Entry point with clean interrupt handling."""
    try:
        run_session()
    except KeyboardInterrupt:
        print("\nSession ended. If you need immediate support, call or text 988.")


if __name__ == "__main__":
    main()