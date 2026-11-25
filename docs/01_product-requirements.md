# Product Requirements Document

## Problem
People doing a quick mental health self-check often face rigid clinical wording, raw scores without clear context, and extra friction when looking for practical next steps or immediate support during stressful moments. Today, completing a standard questionnaire alone leaves users with a number rather than personalized actions or clear care routing.

## Desired outcome
Users complete a calm, structured check-in using revamped PHQ-9-style questions on a `0–3` frequency scale and immediately receive plain-language severity feedback, actionable next steps tailored to their responses, and prominent crisis and care facility resources.

## Scope
- **Users:** Individuals conducting personal mental wellness check-ins, as well as instructors and peers evaluating the application.
- **Use cases:** Answering custom PHQ-9-style items, calculating total scores and severity tiers, triggering safety alerts when self-harm or distress items are endorsed, and filtering care/support options.
- **Features:** Custom question set, validated `0–3` input loop, score and severity calculation, domain- and tier-based custom actions, safety override banner, and location-filtered support/facility output.

## Out of Scope
- Clinical diagnosis, medical prescriptions, or licensed therapy replacement.
- Multi-user accounts, cloud databases, or social features.
- Live emergency dispatch replacing `911` or `988`.

## Requirements

### The product must
- Present all 9 custom questionnaire items with clear `0–3` frequency labels and reject invalid or out-of-range inputs without crashing.
- Accurately sum scores (`0–27`), assign standard severity bands (`Minimal`, `Mild`, `Moderate`, `Moderately Severe`, `Severe`), and detect any positive response (`> 0`) on the safety/self-harm item.
- Display urgent crisis support guidance (`988` Suicide & Crisis Lifeline and `911` / emergency room guidance) prominently whenever the safety item is triggered or scores are severe.
- Output tailored follow-up actions and support/facility options matched to the user's results.

### The product should
- Keep custom questions, severity actions, domain tips, and facility entries separated into clean Python data structures so content is easy to maintain.
- Display a clear non-clinical disclaimer at startup.
- Handle missing or malformed optional data files gracefully by falling back to built-in default support resources.

### The product could
- Load custom questions or care facility lists from an external JSON file.
- Offer an opt-in option to export a local plain-text summary report.
- Support filtering facilities by service type in addition to location.